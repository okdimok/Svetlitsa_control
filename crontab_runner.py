import os, sys, time
sys.path.insert(0, ".")
from run_once import should_this_continue_running
from importlib import reload
import shows
from shows import *


if __name__ == "__main__":
    if not should_this_continue_running("/tmp/crontab_runner_pid"):
        sys.exit(1)
    print(f"Running from crontab {os.getpid()}")
    show_1()
    print(f"Stopping from crontab {os.getpid()}")