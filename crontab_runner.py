import os, sys, time
sys.path.insert(0, ".")
from run_once import should_this_continue_running
from shows import *
import datetime


if __name__ == "__main__":
    if not should_this_continue_running("/tmp/crontab_runner_pid"):
        print("Another instance is already running, exiting")
        sys.exit(1)
    print(f"Running from crontab {os.getpid()} at {datetime.datetime.now()}")
    print(show)
    show.run_infinetely()
    print(f"Stopping from crontab {os.getpid()} at {datetime.datetime.now()}")