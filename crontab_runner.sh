#!/usr/bin/env bash
export HOME=/home/pi

sudo amixer cset numid=1 95% # to avoid strange noises
cd /home/pi/Svetlitsa_control
source /home/pi/wled-env/bin/activate
python crontab_runner.py