import os, sys, time
sys.path.insert(0, ".")
from run_once import should_this_continue_running
from shows import *
import datetime
import wled_common_client, importlib    
importlib.reload(wled_common_client)
from wled_common_client import Wled, Wleds


if __name__ == "__main__":
    wleds = Wleds.from_one_ip("192.168.0.23")
    wleds.cache_fs()
    for wled in wleds:
        wled.update_time()
        wled.presets = OmegaConf.to_container(OmegaConf.load("default_presets.yaml"))
        wled.upload_presets()
        oc_dir = wled.get_fs_dump_dir("omegaconf_source/{name}")
        cfg_yaml = f"{oc_dir}/cfg.yaml"
        ww = Wled.from_omegaconf(additional_confs=[cfg_yaml])
        ww.ip = wled.ip
        ww.upload_cfg()