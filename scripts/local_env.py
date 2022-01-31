import os, sys
from time import sleep
file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, file_path)
sys.path.insert(0, file_path + "/..")
sys.path.insert(0, file_path + "/../svetlitsa_virtualenv/Lib/site-packages")
parent_path = os.path.dirname(file_path)

# print(sys.path)

def default_wled_ip(): return "192.168.0.122" # defined as a function for the sake of further changes

def default_firmware_file(): return file_path + "/../../../Arduino/WLED/build_output/firmware/d1_mini.bin"

def scripts_path(): return file_path

def DEFAULT_PRESETS():
    return (parent_path + "/default_presets.yaml",)

def FS_DUMP_DIR():
    return parent_path + "/config_dump/{name}"

def OMEGACONF_DUMP_DIR():
    return parent_path + "/omegaconf_dump/{name}"

def DEFAULT_OMAEGACONFS():
    return (parent_path + "/default_cfg.yaml", parent_path + "/important_default_cfg.yaml")

def sleep_show(secs):
    print(f"Waiting for {secs} seconds")
    for _ in range(secs):
        sleep(1)
        print(".", end="", flush=True)
    print("", flush=True)
