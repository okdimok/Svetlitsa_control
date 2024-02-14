import os, sys, time
sys.path.insert(0, ".")
from run_once import should_this_continue_running
import datetime
import logging
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    if not should_this_continue_running("/tmp/crontab_runner_pid"):
        logger.critical("Another instance is already running, exiting")
        sys.exit(1)
    logger.info(f"Running from crontab {os.getpid()} at {datetime.datetime.now()}")
    from main_runner import MainRunner
    runner = MainRunner()
    runner.run()
    logger.critical(f"Stopping from crontab {os.getpid()} at {datetime.datetime.now()}")