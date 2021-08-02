from Svetlitsa_control import run_once
import time

class ShowElement:
    def __init__(self, duration, eff_power=256, eff_speed=20):
        self.duration = duration
        self.eff_power = eff_power
        self.eff_speed = eff_speed

    def sleep():
        time.sleep(self.duration)

    def activate(self):
        pass

    def run(self):
        self.activate()
        self.sleep()

    def __str__(self) -> str:
        return f"{self.__class__}(pow {self.eff_power}, spd {self.eff_speed}) for {self.duration} s"


class ColorCycle(ShowElement):
    def activate(self):


