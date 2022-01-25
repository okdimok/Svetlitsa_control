#!/usr/bin/env bash
export HOME=/home/pi

cd /home/pi/Svetlitsa_control
source /home/pi/wled-env/bin/activate
python crontab_runner.py