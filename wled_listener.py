from threading import Thread
from wled_common_client import Wleds, Wled
from scripts.local_env import default_wled_ip
import socket
from time import time
import logging
logger = logging.getLogger(__name__)

wleds = []
try:
    wleds = Wleds.from_one_ip(default_wled_ip())
except Exception as e:
    logger.exception(f"Intializing wleds as empty list due to: {e}\nHoping to get some updates via WledListener, if it is being launched")
# requests.exceptions.ConnectionError: HTTPConnectionPool(host='192.168.0.4', port=80): Max retries exceeded with url: /edit?list (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0xb592d2d0>: Failed to establish a new connection: [Errno 113] No route to host'))

class WledListener:
    # https://github.com/Aircoookie/WLED/blob/master/wled00/udp.cpp#L9 — WLEDPACKETSIZE 
    # https://github.com/Aircoookie/WLED/blob/master/wled00/FX.h#L57 — MAX_NUM_SEGMENTS 
    # https://github.com/Aircoookie/WLED/blob/v0.13.0-b5/wled00/udp.cpp#L7
    # C:\Users\okdim\YandexDisk\coding_leisure\Arduino\WLED\wled00\udp.cpp:L7
    # sometimes udp sys info is bigger than UDP sync
    # but buffer size should be just big
    
    _max_packet_size: int = 64 
    _ip_update_times: dict = dict()

    def __init__(self, port=65506, parse_callback=None):
        self.datasock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.datasock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.datasock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.datasock.bind(("0.0.0.0", port))
        for ip in self._get_known_ips():
            self._ip_update_times[ip] = time()
        self._listen_thread = Thread(target=self.recv, name=f"{self.__class__.__name__}_{port}_listen_thread")
        self._listen_thread.start()
        self.parse_callback = parse_callback


    def _rcv_udp_simple(self):
        bts, addr = self.datasock.recvfrom(self._max_packet_size)
        ip = addr[0]
        port = addr[1]
        if (bts[0] != 0xFF): return bts, ip, port, None
        name = bts[6:6+32].decode("utf-8").rstrip('\x00')
        return bts, ip, port, name


    def recv(self):
        while True:
            bts, ip, port, name = self._rcv_udp_simple()
            # In principle, we need to check, if we know about ip-name pair
            # If we do know, we just need to update the last notification time
            # If we don't know
                # If we know about any pair, containing elements of this pair, we should invalidate it
                # If we don't know, we should add a wled and (probably), cache its FS

            logger.debug(f"Got update from {ip}, {name}")
            self._ip_update_times[ip] = time()
            if (name is not None): # this is an update of proper type
                if not WledListener.check_if_ip_name_pair_is_in_wleds(ip, name, wleds): # there is some novelty
                    if ip in self._get_known_ips(): # the ip is known, but the name has changed
                        self._remove_all_by_ip(ip, new_name = name) # removing the old wled from wleds
                    if name in self._get_known_names(): # the ip is known, but the name has changed
                        self._remove_all_by_name(name, new_ip=ip) # removing the old wled from wleds
                    try:
                        new_wled = Wled.from_one_ip(ip, name)
                        wleds.append(new_wled)
                        wleds.sort()
                        logger.info(f"adding new wled: {new_wled}")
                        logger.debug(f"new wleds: {wleds}")
                    except:
                        pass
            if self.parse_callback is not None:
                self.parse_callback(bts, ip=ip, port=port, name=name)
            

    @classmethod
    def check_if_ip_name_pair_is_in_wleds(cls, ip, name, wleds):
        for wled in wleds.filter(lambda w: w.ip == ip):
            if wled.name == name:
                return True
        return False

    def _remove_all_by_ip(cls, ip, new_name):
        for wled in wleds.filter(lambda w: w.ip == ip):
            logger.warning(f"A new WLED name with the same IP ({ip}): {wled.name} → {new_name}")
            wleds.remove(wled)

    def _remove_all_by_name(cls, name, new_ip):
        for wled in wleds.filter(lambda w: w.name == name):
            logger.warning(f"A WLED name with the same name ({name}) but a different IP: {wled.ip} → {new_ip}")
            wleds.remove(wled)


    def _get_known_ips(self):
        return wleds.get_ips()

    def _get_known_names(self):
        return wleds.get_names()


    

if __name__ == "__main__":
    try:
        import coloredlogs
        coloredlogs.install(logging.DEBUG)
    except:
        pass

    logger.setLevel(logging.DEBUG)

    def parse_and_print(bts, ip, port, name):
        if bts[0] == 0xFF: return
        logger.debug(f"Callback for {name} at {ip}:{port}" )
        v = Wled.parse_udp_sync(bts)
        logger.debug(v)
    
    logger.debug("Starting the WledListener")
    listener = WledListener(port=65506, parse_callback=parse_and_print) # just listen
    state_tracker = WledListener(port=21324, parse_callback=parse_and_print)
    listener._listen_thread.join()
    state_tracker._listen_thread.join()
