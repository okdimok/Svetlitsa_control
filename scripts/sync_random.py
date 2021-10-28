if __name__ == "__main__":
    print("Starting the sync")

# import os, sys, time
from local_env import *
# from run_once import should_this_continue_running
# from shows import *
from wled_common_client import Wled, Wleds
from time import sleep


if __name__ == "__main__":
    print("Getting the list of nodes")
    wleds = Wleds.from_one_ip(default_wled_ip(), cache_fs=False)
    default_wled = wleds.get_by_ip(default_wled_ip())
    pl, ps = default_wled.get_json_state()["pl"], default_wled.get_json_state()["ps"]
    print(f"pl {pl} ps {ps}")
    for wled in wleds:
        print (f"Syncing {wled.name} at {wled.ip}")
        wled.set_effect(0)
        wled.set_random_seed(42)
        wled.update_time()
    default_wled.set_fake_NTP(130)
    default_wled.set_effect(0)
    sleep(1)
    if pl > 0:
        default_wled.set_playlist(pl)
    elif ps > 0:
        default_wled.set_preset(ps)




print("Done updating times")