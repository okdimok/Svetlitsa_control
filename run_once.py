import os, sys


def should_this_continue_running(control_file):
    def dump():
        with open(control_file, "w") as cf:
            cf.write(f"{os.getpid()}")        
    if not os.path.exists(control_file):
        dump()
        return True
    with open(control_file, "r") as cf:
        other_pid = int(cf.read())
        if other_pid == os.getpid():
            return True
        if os.path.exists(f"/proc/{other_pid}"):
            return False
        else:
            dump()
            return True


        