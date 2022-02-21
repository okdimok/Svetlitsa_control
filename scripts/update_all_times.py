import os, sys, time
from local_env import *
from run_once import should_this_continue_running
import datetime
import wled_common_client, importlib    
importlib.reload(wled_common_client)
from wled_common_client import Wled, Wleds


if __name__ == "__main__":
    wleds = Wleds.from_one_ip(default_wled_ip())
    # wleds.cache_fs()
    wleds.print()
    wleds.update_time()
    # for wled in wleds:
    #     print (f"Updating {wled.name} at {wled.ip}")


print("Done updating times")