if __name__ == "__main__":
    print("Starting the firmware update")

# import os, sys, time
from local_env import *
# from run_once import should_this_continue_running
from wled_common_client import Wled, Wleds
from time import sleep
# from multiprocessing.pool import ThreadPool
from concurrent.futures import ThreadPoolExecutor
import logging
logging.basicConfig(level=logging.DEBUG)
try:
    import coloredlogs
    coloredlogs.install(logging.getLogger().getEffectiveLevel())
except:
    pass

logger = logging.getLogger(__name__)

firmware_filename = default_firmware_file()


if __name__ == "__main__":
    logger.info("Getting the list of nodes")
    wleds = Wleds.from_one_ip(default_wled_ip(), cache_fs=False)
    default_wled = wleds.get_by_ip(default_wled_ip())
    state = default_wled.get_json_state()
    pl, ps =state["pl"], state["ps"]
    logger.debug(f"pl {pl} ps {ps}")
    wleds.print("Updating ")
    for wled in wleds:
        try:
            wled.update_firmware(firmware_filename)
        except Exception as e:
            logger.error(f"Failed to update for {wled} with {e}")
    logger.info("Updated all the firmwares")
    sleep_show(10)
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

    print("Done updating firmwares")