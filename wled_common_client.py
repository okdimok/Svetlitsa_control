import requests
import time
import tdutils as tdu
import json
import hydra
import os
from omegaconf import DictConfig, OmegaConf, ListConfig
import dictdiffer as dd

dbg = tdu.debug.debug


FS_DUMP_DIR="config_dump/{name}"
DEFAULT_OMAEGACONFS=["default_cfg.yaml", "important_default_cfg.yaml"]
DEFAULT_PRESETS=["default_presets.yaml"]

# https://github.com/Aircoookie/WLED/wiki/HTTP-request-API
# https://github.com/Aircoookie/WLED/wiki/JSON-API
# https://github.com/Aircoookie/WLED/wiki/Sync-WLED-devices-(UDP-Notifier)
# https://github.com/Aircoookie/WLED/blob/master/wled00/udp.cpp

import socket
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP


class Wleds:
    def __init__(self, wleds=[]):
        self.wleds = wleds
    
    @classmethod
    def from_udp_multicast_table(cls, box):
        return cls(wleds = list(Wled.from_udp_multicast(row) for row in box.rows()))

    @classmethod
    def from_one_node(cls, wled):
        wleds = [wled]
        for node in wled.get_nodes():
            w = Wled(node.ip)
            w.name = node.name
            wleds.append(w)
        return cls(wleds = wleds)

    @classmethod
    def to_omegaconf(self):
        pass

    def get_by_ip(self, ip):
        wleds = list(wled for wled in self if wled.ip == ip)
        if len(wleds) == 1:
            return wleds[0]
        elif len(wleds) == 0:
            return None
        else:
            raise ValueError(f"More than one ({len(wleds)}) wled with IP {ip} found")

    def get_by_name(self, name):
        wleds = list(wled for wled in self if wled.name == name)
        if len(wleds) == 1:
            return wleds[0]
        elif len(wleds) == 0:
            return None
        else:
            raise ValueError(f"More than one ({len(wleds)}) wled with name '{name}' found")

    def get_names(self):
        return list(wled.name for wled in self)

    def __getitem__(self, item):
        return self.get_by_name(item)

    def __iter__(self):
        return self.wleds.__iter__()


class Wled:
    def __init__(self, ip):
        self.ip = ip
        self.udp_port = None
        self.name = None
        self.current_json = None
        self.cfg = None
        self.presets = None

    @classmethod
    def from_udp_multicast(cls, row):
        wled =  cls(ip=row[0].val)
        wled.udp_port = int(row[1].val)
        wled.name = row[2].val
        return wled

    @classmethod
    def from_omegaconf(self, additional_confs=[], additional_presets=[]):
        confs = DEFAULT_OMAEGACONFS
        confs += additional_confs
        confs = [omegaconf_universal_load(f) for f in confs]
        cfg = OmegaConf.merge(*confs)
        self.cfg = OmegaConf.to_container(cfg)
        self.udp_port = cfg["if"].sync.port0
        self.name = cfg.id.name
        self.presets = OmegaConf.merge(configs=DEFAULT_PRESETS + additional_presets)
        return self

    def to_omegaconf(self):
        confs = DEFAULT_OMAEGACONFS
        confs = [omegaconf_universal_load(f) for f in confs]
        cfg = OmegaConf.merge(*confs)
        new_cfg = create_patch_from_omegaconf(self.cfg, cfg)
        new_presets = create_patch_from_omegaconf(self.presets, {})

        return new_cfg, new_presets

        patch_dict = {}


    ## Endpoints 
    def http_endpoint(self):
        return f"http://{self.ip}/win"

    def json_endpoint(self):
        return f"http://{self.ip}/json"

    def edit_endpoint(self):
        return f"http://{self.ip}/edit"

    ## Request helpers
    def http_request_multi(self, params):
        req_str = self.http_endpoint()
        req_str += "".join([f"&{p[0]}={p[1]}" for p in params])
        # tdu.debug.debug(req_str)
        return requests.get(req_str)

    def http_request_one(self, param, value):
        return self.http_request_multi([(param, value)])

    def _send_udp(self, msg):
        # tdu.debug.debug(f"udp {self.udp_port}, msg: {msg}")
        sock.sendto(msg, (self.ip, self.udp_port))

    def send_udp_sync(self, brightness=255, col=[255,0,0], fx=0, fx_speed=10, fx_intensity=255, col_sec=[0, 255,0], transition_delay=0, palette=0):
        p = []
        # Byte Index	Var Name	Description	Notifier Version
        # 0	-	Packet Purpose Byte*	0
        p += [0]
        # 1	callMode	Packet Reason**	0
        p += [1]
        # 2	bri	Master Brightness	0
        p += [brightness]
        # 3	col[0]	Primary Red Value	0
        # 4	col[1]	Primary Green Value	0
        # 5	col[2]	Primary Blue Value	0
        p += col
        # 6	nightlightActive	Nightlight running?	0
        # 7	nightlightDelayMins	Nightlight Time	0
        p += [0, 0]
        # 8	effectCurrent	Effect Index	0
        # 9	effectSpeed	Effect Speed	0
        p += [fx, fx_speed]
        # 10	white	Primary White Value	1
        p += [255]
        # 11	-	Version Byte***	1
        p += [5]
        # 12	colSec[0]	Secondary Red Value	2
        # 13	colSec[1]	Secondary Green Value	2
        # 14	colSec[2]	Secondary Blue Value	2
        p += col_sec
        # 15	whiteSec	Secondary White Value	2
        p += [255]
        # 16	effectIntensity	Effect Intensity	3
        p += [fx_intensity]
        # 17	transitionDelay	Transition Duration Upper	4
        # 18	transitionDelay	Transition Duration Lower	4
        p += [transition_delay<<8, transition_delay%(1<<8)]
        # 19	effectPalette	FastLED palette	5
        p += [palette]
        # 20-23	-	Zeros	-
        p += [0]*4
        p = bytes(p)
        self._send_udp(p)

    # Json state requests
    def get_json(self):
        self.current_json = requests.get(self.json_endpoint()).json()
        return self.current_json
    
    def post_json_state(self, new_json={}):
        return requests.post(self.json_endpoint(), json=new_json)

    # FS helpers
    def get_fs_list(self):
        return requests.get(self.edit_endpoint() + "?list").json()

    def get_fs_file(self, filename):
        return requests.get(self.edit_endpoint() + "?edit=" + filename)

    def upload_fs_file(self, filename, contents):
        return requests.post(self.edit_endpoint(), files={filename:contents})

    def _attr_name_from_filename(self, filename):
        if not filename.endswith(".json"): raise ValueError(f"filename {filename} in the FS does not end in json, but attr name creation requested")
        return filename[:-5]

    def cache_fs(self):
        """Reads all the json files in the FS into the member dictionaries of this object with the name deduced from the filename"""
        for fp in self.get_fs_list():
            fn = fp["name"]
            if fn.endswith(".json"):
                self.__setattr__(self._attr_name_from_filename(fn), self.get_fs_file(fn).json())

    def get_cfg(self):
        self.cfg = self.get_fs_file("cfg.json").json()
        return self.cfg

    def get_presets(self):
        self.presets = self.get_fs_file("presets.json").json()
        return self.presets

    def upload_cfg(self):
        cfg_json = json.dumps(self.cfg, separators=(',', ':'))
        return self.upload_fs_file("cfg.json", cfg_json.encode("utf-8"))

    def upload_presets(self):
        cfg_json = json.dumps(self.presets, separators=(',', ':'))
        return self.upload_fs_file("presets.json", cfg_json.encode("utf-8"))
        
    
    # FS Dumps
    def get_fs_dump_dir(self, fs_dump_dir=FS_DUMP_DIR):
        """Populates the template for the local directory, where FS should be dumped. Creates it, if nececery, and returns a path to it"""
        fs_dump_dir = fs_dump_dir.format(ip=self.ip, name=self.name)
        os.makedirs(fs_dump_dir, exist_ok=True)
        return fs_dump_dir

    def dump_fs(self, fs_dump_dir=FS_DUMP_DIR):
        """Dumps all the files from the device to a local fs_dump_dir"""
        for fp in self.get_fs_list():
            fn = fp["name"]
            with open(f"{self.get_fs_dump_dir(fs_dump_dir)}/{fn}", "w") as fd:
                fd.write(self.get_fs_file(fn).text)

    def read_config_dump(self, fs_dump_dir=FS_DUMP_DIR):
        for f in os.listdir(self.get_fs_dump_dir(fs_dump_dir)):
            if f.endswith(".json"):
                with open(f"{self.get_fs_dump_dir(fs_dump_dir)}/{f}", "r") as fr:
                    self.__setattr__(self._attr_name_from_filename(f), json.load(fr))

    # Higher level functions
    def get_nodes(self):
       return requests.get(self.json_endpoint() + "/nodes").json()

    def set_solid_color(self, r, g, b, via_http=False):
        if via_http:
            new_state = {
                "FX": 0,
                "R": r,
                "G": g,
                "B": b,
            }
            self.http_request_multi(new_state.items())
        else:
            self.send_udp_sync(fx=0, col=[r, g, b])

    def update_time(self):
        self.http_request_one("ST", int(time.time()))

def omegaconf_universal_load(conf):
    if isinstance(conf, str):
        if conf.endswith(".yaml"):
            return OmegaConf.load(conf)
        else: return OmegaConf.create(conf)
    elif OmegaConf.is_config(conf):
        return conf
    else:
        return OmegaConf.create(conf)

def create_patch_from_omegaconf(custom_cfg, general_cfg):
    patch = list(dd.swap(dd.diff(custom_cfg, general_cfg, expand=True, dot_notation=False)))
    new_patch = []
    for p in patch:
        if p[0] == "remove":
            continue
        elif p[0] == "add":
            new_patch.append(p)
        elif p[0] == "change":
            new_patch.append(("add", p[1], p[2][1]))
        else:
            raise ValueError()
    new_cfg = OmegaConf.create()
    new_cfg = {}
    for p in new_patch:
        keys = list(p[1])
        v = p[2] 
        if isinstance(p[2], list):
            keys += [p[2][0][0]]
            v = p[2][0][1]

        if len(keys) == 1:
            new_cfg[keys[0]] = v
        else:
            curr = new_cfg
            orig = general_cfg
            prev = None
            for k, kn in zip(keys[:-1], keys[1:]): # key, key_next
                orig = orig[k]
                try:
                    curr = curr[k]
                except KeyError: # it is for dicts
                    if isinstance(kn, int):
                        curr[k] = orig # as far as we create list we need to copy it from the main config
                    elif isinstance(kn, str):
                        curr[k] = dict()
                    curr = curr[k]
                except IndexError: # for lists
                    if isinstance(kn, int):
                        curr.append(list())
                    elif isinstance(kn, str):
                        curr.append(dict())
                    curr = curr[-1]
            try:
                curr[kn] = v
            except IndexError:
                curr.append(v)
            

    new_cfg = OmegaConf.create(new_cfg)

    # dbg("="*20)
    # dbg(patch)
    # dbg("#"*20)
    # dbg(new_patch)
    # dbg("*"*20)
    # dbg(new_cfg)
    # dbg(">"*20  )
    # result = Wled.from_omegaconf(additional_confs=[OmegaConf.to_container(new_cfg)]).cfg
    # dbg(list(dd.diff(result, custom_cfg)))
    return new_cfg

if __name__ == "__main__":
    print("No action defined yet.")

    
