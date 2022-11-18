#!/usr/bin/env bash
export HOME=/home/pi

sudo amixer cset numid=1 100%
cd /home/pi/Svetlitsa_control
source /home/pi/wled-env/bin/activate
python crontab_runner.py