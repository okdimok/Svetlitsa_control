import os, sys
file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, file_path)
sys.path.insert(0, file_path + "/..")
sys.path.insert(0, file_path + "/../svetlitsa_virtualenv/Lib/site-packages")

# print(sys.path)

def default_wled_ip(): return "192.168.0.122" # defined as a function for the sake of further changes