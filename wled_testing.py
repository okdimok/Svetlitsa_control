# me - this DAT
# 
# channel - the Channel object which has changed
# sampleIndex - the index of the changed sample
# val - the numeric value of the changed sample
# prev - the previous sample value
# 
# Make sure the corresponding toggle is enabled in the CHOP Execute DAT.
import importlib
import wled_common_client

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
        wled.dump_fs()
    return
	