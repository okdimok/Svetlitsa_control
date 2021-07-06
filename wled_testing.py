# me - this DAT
# 
# channel - the Channel object which has changed
# sampleIndex - the index of the changed sample
# val - the numeric value of the changed sample
# prev - the previous sample value
# 
# Make sure the corresponding toggle is enabled in the CHOP Execute DAT.
import importlib
import tdutils as tdu
dbg = tdu.debug.debug
import os, sys
sys.path.insert(0, ".")
import wled_common_client
from dictdiffer import diff
from omegaconf import OmegaConf
import yaml
import json

def onOffToOn(channel, sampleIndex, val, prev):
	return

def whileOn(channel, sampleIndex, val, prev):
	return

def onOnToOff(channel, sampleIndex, val, prev):
	return

def whileOff(channel, sampleIndex, val, prev):
	return

def onValueChange(channel, sampleIndex, val, prev):
    if val != 1.0: return
    importlib.reload(wled_common_client)
    from wled_common_client import Wled, Wleds
    wleds = Wleds.from_udp_multicast_table(op("wled_nodes_table"))
    for wled in wleds:
        wled.cache_fs()
        if ("kitchen" in wled.name): continue
        # wled.dump_fs()
        # wled.dump_fs("config_dump/{ip}")
        tdu.debug.debug(wled.to_omegaconf()[1])
        # break
    # tdu.debug.debug(list(diff(wleds["WLED"].cfg, wleds["WLED-Dima-Office"].cfg)))
    # tdu.debug.debug(OmegaConf.create( wleds["WLED"].cfg).nw.ins[0].ip)
    # w0 = Wled.from_omegaconf()
    # tdu.debug.debug(list(diff(w0.cfg, wleds["WLED"].cfg)))
    # with open("dump_test.yaml", "w") as f:
    #     json.dump(wleds["WLED"].cfg, f, separators=(',', ':'))
    # wleds["WLED"].upload_cfg()
    # wleds["WLED"].upload_presets()
    return
	