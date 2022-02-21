#!/usr/bin/env python3
import os, sys, time
from local_env import *
from run_once import should_this_continue_running
import datetime
import wled_common_client, importlib    
importlib.reload(wled_common_client)
from wled_common_client import Wled, Wleds
from omegaconf import OmegaConf


if __name__ == "__main__":
    wleds = Wleds.from_one_ip(default_wled_ip())
    wleds.cache_fs()
    for wled in wleds:
        # if ("kitchen" in wled.name):
        #     print(f"Skipping {wled.name} at {wled.ip} — filtered by name")
        #     continue
        print (f"Updating {wled.name} at {wled.ip}")
        # wled.update_time() # useless, because a reset is required
        ww = Wled.reconfig_from_omegaconf(wled, keep_presets=True)

t_sleep = 15
print(f"Sleeping for {t_sleep} seconds before the time update cycle")
for i in range(t_sleep):
    print(".", end="", flush=True)
    time.sleep(1)
print()

for wled in wleds:
    print (f"Updating time for {wled.name} at {wled.ip}")
    wled.update_time()