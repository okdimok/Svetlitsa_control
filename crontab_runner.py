import os, sys, time
sys.path.insert(0, ".")
from run_once import should_this_continue_running
from main_runner import MainRunner
import datetime


if __name__ == "__main__":
    if not should_this_continue_running("/tmp/crontab_runner_pid"):
        print("Another instance is already running, exiting")
        sys.exit(1)
    print(f"Running from crontab {os.getpid()} at {datetime.datetime.now()}")
    runner = MainRunner()
    runner.run()
    print(f"Stopping from crontab {os.getpid()} at {datetime.datetime.now()}")