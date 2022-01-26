from threading import Event, Timer
import time
from wled_common_client import Wled, Wleds
from scripts.local_env import default_wled_ip

wleds = Wleds.from_one_ip(default_wled_ip())

_sleep_quant = 0.1

class ShowElement:
    _sleep_timer: Timer

    def __init__(self, duration, eff_intensity=256, eff_speed=20):
        self.duration = duration
        self.eff_intensity = eff_intensity
        self.eff_speed = eff_speed

    def sleep(self):
        self._sleep_timer = Timer(self.duration, lambda: True)
        self._sleep_timer.start()
        self._sleep_timer.join()

    def activate(self):
        wleds.print()

    def run(self):
        self.activate()
        self.sleep()

    def stop(self):
        self._sleep_timer.cancel() # it is OK to cancel Timer twice


    def __str__(self) -> str:
        return f"{self.__class__.__name__}(pow {self.eff_intensity}, spd {self.eff_speed}) for {self.duration} s"

class TotalPreset(ShowElement):
    def __init__(self, ps, duration):
        super().__init__(duration)
        self.ps = ps

    def activate(self):
        for i in range(3):
            wleds.set_preset(self.ps, self.eff_intensity, self.eff_speed)

class TotalFX(ShowElement):
    def __init__(self, fx, duration, eff_intensity, eff_speed):
        super().__init__(duration, eff_intensity, eff_speed)
        self.fx = fx

    def activate(self):
        for i in range(3):
            wleds.send_udp_sync(fx=self.fx, fx_intensity = self.eff_intensity, fx_speed = self.eff_speed)

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

# This one is deprecated: the UDP one is much more reliable in terms of synchronously setting the same mode
# class Colorloop(TotalPreset):
#     def __init__(self, duration):
#         super().__init__(22, duration)

class Colorloop(TotalFX):
    def __init__(self, duration, eff_speed = 20):
        super().__init__(8, duration, 255, eff_speed)
        
class Off(ShowElement):
    def __init__(self, duration):
        super().__init__(duration)

    def activate(self):
        for i in range(3):
            wleds.send_udp_sync(fx=0, brightness=0)

class TotalEffect(ShowElement):
    def __init__(self, duration,  eff_intensity, eff_speed):
        super().__init__(duration, eff_intensity=eff_intensity, eff_speed=eff_speed)





