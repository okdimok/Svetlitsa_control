if __name__ == "__main__":
    print("Starting the sync")

# import os, sys, time
from local_env import *
# from run_once import should_this_continue_running
# from shows import *
from wled_common_client import Wled, Wleds
from time import sleep
# from multiprocessing.pool import ThreadPool
from concurrent.futures import ThreadPoolExecutor

if __name__ == "__main__":
    print("Getting the list of nodes")
    wleds = Wleds.from_one_ip(default_wled_ip(), cache_fs=False)
    default_wled = wleds.get_by_ip(default_wled_ip())
    state = default_wled.get_json_state()
    pl, ps = state["pl"], state["ps"]
    print(f"pl {pl} ps {ps}")
    wleds.print("Updating ")
    wleds.set_effect(0)
    wleds.set_random_seed(42)
    wleds.update_time()
    default_wled.set_fake_NTP(130)
    default_wled.set_effect(0)
    sleep(1)
    if pl > 0:
        default_wled.set_playlist(pl)
    elif ps > 0:
        default_wled.set_preset(ps)

    print("Done updating times")