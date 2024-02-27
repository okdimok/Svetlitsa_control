#!/usr/bin/env bash
kill -9 $(cat /tmp/crontab_runner_pid); sleep 0.2 && sudo nice -n -10 su pi ~/Svetlitsa_control/crontab_runner.sh