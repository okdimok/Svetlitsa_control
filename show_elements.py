import time
from wled_common_client import Wled, Wleds

wleds = Wleds.from_one_ip("192.168.0.22")

class ShowElement:
    def __init__(self, duration, eff_intensity=256, eff_speed=20):
        self.duration = duration
        self.eff_intensity = eff_intensity
        self.eff_speed = eff_speed

    def sleep(self):
        time.sleep(self.duration)

    def activate(self):
        for wled in wleds:
            print(wled.name)

    def run(self):
        self.activate()
        self.sleep()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(pow {self.eff_intensity}, spd {self.eff_speed}) for {self.duration} s"

class TotalPreset(ShowElement):
    def __init__(self, ps, duration):
        super().__init__(duration)
        self.ps = ps

    def activate(self):
        for wled in wleds:
            for i in range(3):
                wled.set_preset(self.ps, self.eff_intensity, self.eff_speed)

class RYAndroid(TotalPreset):
    def __init__(self, duration):
        super().__init__(3, duration)

class Red(TotalPreset):
    def __init__(self, duration):
        super().__init__(14, duration)

class Green(TotalPreset):
    def __init__(self, duration):
        super().__init__(17, duration)

class Blue(TotalPreset):
    def __init__(self, duration):
        super().__init__(11, duration)

class WarmWhite(TotalPreset):
    def __init__(self, duration):
        super().__init__(20, duration)

class Colorloop(TotalPreset):
    def __init__(self, duration):
        super().__init__(22, duration)

class TotalEffect(ShowElement):
    def __init__(self, duration,  eff_intensity, eff_speed):
        super().__init__(duration, eff_intensity=eff_intensity, eff_speed=eff_speed)





