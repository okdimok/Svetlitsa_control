import os, sys, time
from run_once import should_this_continue_running

if __name__ == "__main__":
    if not should_this_continue_running("/tmp/crontab_runner_pid"):
        sys.exit(1)
    print(f"Running from crontab {os.getpid()}")
    time.sleep(300)
    print(f"Stopping from crontab {os.getpid()}")