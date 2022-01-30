from threading import Thread
from wled_common_client import Wleds, Wled
from scripts.local_env import default_wled_ip
import socket
from time import time
import logging
logger = logging.getLogger(__name__)

wleds = Wleds.from_one_ip(default_wled_ip())
# requests.exceptions.ConnectionError: HTTPConnectionPool(host='192.168.0.4', port=80): Max retries exceeded with url: /edit?list (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0xb592d2d0>: Failed to establish a new connection: [Errno 113] No route to host'))

class WledListener:
    # https://github.com/Aircoookie/WLED/blob/master/wled00/udp.cpp#L9 — WLEDPACKETSIZE 
    # https://github.com/Aircoookie/WLED/blob/master/wled00/FX.h#L57 — MAX_NUM_SEGMENTS 
    _max_packet_size: int = 41 + 16*28
    _ip_update_times: dict = dict()

    def __init__(self, port=65506):
        self.datasock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.datasock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.datasock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.datasock.bind(("0.0.0.0", port))
        for ip in self._get_known_ips():
            self._ip_update_times[ip] = time()
        self._listen_thread = Thread(target=self.recv)
        self._listen_thread.start()


    def _rcv_udp_simple(self, ):
            bts, addr = self.datasock.recvfrom(self._max_packet_size)
            name = bts[6:6+32].decode("utf-8").rstrip('\x00')
            ip = addr[0]
            port = addr[1]
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
            if not WledListener.check_if_ip_name_pair_is_in_wleds(ip, name, wleds): # there is some novelty
                if ip in self._get_known_ips(): # the ip is known, but the name has changed
                    wled_to_remove = wleds.get_by_ip(ip)
                    wleds.remove(wled_to_remove) # removing the old wled from wleds
                    logger.warning(f"A new WLED name with the same IP ({ip}): {wled_to_remove.name} → {name}")
                if name in self._get_known_names(): # the ip is known, but the name has changed
                    wled_to_remove = wleds.get_by_name(name)
                    wleds.remove(wled_to_remove) # removing the old wled from wleds
                    logger.warning(f"A WLED name with the same name ({name}) but a different IP: {wled_to_remove.ip} → {ip}")
                try:
                    new_wled = Wled.from_one_ip(ip, name)
                    wleds.append(new_wled)
                    wleds.sort()
                    logger.info(f"adding new wled: {new_wled}")
                    logger.debug(f"new wleds: {wleds}")
                except:
                    pass
            

    @classmethod
    def check_if_ip_name_pair_is_in_wleds(cls, ip, name, wleds):
        wled = wleds.get_by_ip(ip)
        if wled is None:
            return False
        return wled.name == name

    def _get_known_ips(self):
        return wleds.get_ips()

    def _get_known_names(self):
        return wleds.get_names()


    

if __name__ == "__main__":
    listener = WledListener()
    listener._listen_thread.join()
