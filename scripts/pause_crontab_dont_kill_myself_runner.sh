#!/usr/bin/env bash
# The name helps not to kill itself during the pkill
pkill -f crontab_runner ; bash -c "echo \$\$ > /tmp/crontab_runner_pid; sleep infinity" &