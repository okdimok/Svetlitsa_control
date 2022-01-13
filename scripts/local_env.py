import os, sys
from time import sleep
file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, file_path)
sys.path.insert(0, file_path + "/..")
sys.path.insert(0, file_path + "/../svetlitsa_virtualenv/Lib/site-packages")

# print(sys.path)

def default_wled_ip(): return "192.168.0.122" # defined as a function for the sake of further changes

def default_firmware_file(): return file_path + "/../../../Arduino/WLED/build_output/firmware/d1_mini.bin"

def scripts_path(): return file_path

def sleep_show(secs):
    print(f"Waiting for {secs} seconds")
    for _ in range(secs):
        sleep(1)
        print(".", end="", flush=True)
    print("", flush=True)
