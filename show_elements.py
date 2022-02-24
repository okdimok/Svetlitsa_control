from threading import Event, Timer, Lock
import time
from wled_common_client import Wled, Wleds, WledDMX
from scripts.local_env import default_wled_ip
import wled_listener as wl
from preset_manager import get_preset_id_by_name as ps
from fx_manager import fxs
import logging
logger = logging.getLogger(__name__)


_sleep_quant = 0.1

class ShowElement:
    _sleep_timer: Timer
    _is_activating_lock: Lock = Lock()

    def __init__(self, duration, eff_intensity=255, eff_speed=20, filter_lambda=lambda w: True):
        self.duration = duration
        self.eff_intensity = eff_intensity
        self.eff_speed = eff_speed
        self.filter_lambda = filter_lambda

    def sleep(self):
        self._sleep_timer = Timer(self.duration, lambda: True) # No name for timers:(  name=f"{self.__class__.__name__}_sleep_timer")
        self._sleep_timer.start()
        self._sleep_timer.join()

    def activate(self):
        logger.debug(wl.wleds)

    def deactivate(self):
        pass

    def run(self):
        with self._is_activating_lock:
            self.activate()
        self.sleep()
        self.deactivate()

    def stop(self):
        with self._is_activating_lock:
            try:
                self._sleep_timer.cancel() # it is OK to cancel Timer twice
            except Exception as e:
                logger.exception(f"Was unable to stop {self}: {e}")


    def __str__(self) -> str:
        return f"{self.__class__.__name__}(pow {self.eff_intensity}, spd {self.eff_speed}) for {self.duration} s"

class TotalPreset(ShowElement):
    def __init__(self, ps_id, duration, transition_delay=None):
        super().__init__(duration)
        self.ps = ps_id
        self.transition_delay = transition_delay

    def activate(self):
        for i in range(3):
            try:
                wl.wleds.set_preset_udp(self.ps, self.eff_intensity, self.eff_speed, follow_up = (i != 0), transition_delay=self.transition_delay)
            except Exception as e:
                logger.warning(f"{e} while setting {self}")

class PresetOnFiltered(ShowElement):
    def __init__(self, ps_id, duration, eff_intensity=None, eff_speed=None, filter_lambda=lambda w: True, transition_delay=None, black_transition_delay=1000):
        super().__init__(duration, eff_intensity=eff_intensity, eff_speed=eff_speed, filter_lambda=filter_lambda)
        self.ps = ps_id
        self.transition_delay = transition_delay
        self.black_transition_delay = black_transition_delay

    def activate(self):
        for i in range(3):
            wl.wleds.filter(lambda w: not self.filter_lambda(w)).send_udp_sync(brightness=255, col=[0,0,0,0], transition_delay=self.black_transition_delay, follow_up = (i != 0))
        for i in range(3):
            try:
                wl.wleds.filter(self.filter_lambda).set_preset_udp(self.ps, self.eff_intensity, self.eff_speed, transition_delay=self.transition_delay, follow_up = (i != 0))
            except Exception as e:
                logger.warning(f"{e} while setting {self} with {self.filter_lambda}")


class TotalFX(ShowElement):
    def __init__(self, fx_id, duration, eff_intensity, eff_speed, filter_lambda=lambda w: True):
        super().__init__(duration, eff_intensity, eff_speed, filter_lambda=filter_lambda)
        self.fx_id = fx_id

    def activate(self):
        for i in range(3):
            wl.wleds.filter(self.filter_lambda).send_udp_sync(fx=self.fx_id, fx_intensity = self.eff_intensity, fx_speed = self.eff_speed)

class FXOnFiltered(ShowElement):
    def __init__(self, fx_id, duration, eff_intensity, eff_speed, filter_lambda=lambda w: True, transition_delay=1000, black_transition_delay=1000, col=None, secondary_color=None, tertiary_color=None, brightness=None):
        super().__init__(duration, eff_intensity, eff_speed, filter_lambda=filter_lambda)
        self.fx_id = fx_id
        self.transition_delay = transition_delay
        self.black_transition_delay = black_transition_delay
        self.col = col
        self.secondary_color = secondary_color
        self.tertiary_color = tertiary_color
        self.brightness = brightness

    def activate(self):
        for i in range(3):
            wl.wleds.filter(lambda w: not self.filter_lambda(w)).send_udp_sync(brightness=255, col=[0,0,0,0], transition_delay=self.black_transition_delay, follow_up = (i != 0))
        for i in range(3):
            try:
                kwargs = dict()
                if self.col is not None: kwargs["col"] = self.col
                if self.secondary_color is not None: kwargs["secondary_color"] = self.secondary_color
                if self.tertiary_color is not None: kwargs["tertiary_color"] = self.tertiary_color
                if self.brightness is not None: kwargs["brightness"] = self.brightness
                wl.wleds.filter(self.filter_lambda).send_udp_sync(fx=self.fx_id, 
                    fx_intensity = self.eff_intensity, fx_speed = self.eff_speed, 
                    transition_delay=self.transition_delay, follow_up = (i != 0),
                    **kwargs)
            except Exception as e:
                logger.warning(f"{e} while setting {self} with {self.filter_lambda}")

class RYAndroid(PresetOnFiltered):
    def __init__(self, duration, filter_lambda=lambda w: True):
        super().__init__(3, duration, filter_lambda=filter_lambda)

class Red(PresetOnFiltered):
    def __init__(self, duration, filter_lambda=lambda w: True):
        super().__init__(14, duration, filter_lambda=filter_lambda)

class Green(PresetOnFiltered):
    def __init__(self, duration, filter_lambda=lambda w: True):
        super().__init__(17, duration, filter_lambda=filter_lambda)

class Blue(PresetOnFiltered):
    def __init__(self, duration, filter_lambda=lambda w: True):
        super().__init__(11, duration, filter_lambda=filter_lambda)

class RedImmediate(PresetOnFiltered):
    def __init__(self, duration, filter_lambda=lambda w: True):
        super().__init__(14, duration, transition_delay=0, black_transition_delay=0, filter_lambda=filter_lambda)

class GreenImmediate(PresetOnFiltered):
    def __init__(self, duration, filter_lambda=lambda w: True):
        super().__init__(17, duration, transition_delay=0, black_transition_delay=0, filter_lambda=filter_lambda)

class BlueImmediate(PresetOnFiltered):
    def __init__(self, duration, filter_lambda=lambda w: True):
        super().__init__(11, duration, transition_delay=0, black_transition_delay=0, filter_lambda=filter_lambda)

class ColorImmediate(FXOnFiltered):
    def __init__(self, col, duration, eff_intensity, eff_speed, filter_lambda=lambda w: True):
        super().__init__(0, duration, eff_intensity, eff_speed, filter_lambda=filter_lambda, transition_delay=0, black_transition_delay=0, col=col)

class WarmWhite(FXOnFiltered):
    def __init__(self, duration):
        super().__init__(fxs.STATIC, duration, 100, 100, brightness=150, col=[255, 200, 200])

class RBPills(PresetOnFiltered):
    def __init__(self, duration, filter_lambda=lambda w: True):
        super().__init__(29, duration, transition_delay=0, black_transition_delay=0, filter_lambda=filter_lambda)



# This one is deprecated: the UDP one is much more reliable in terms of synchronously setting the same mode
# class Colorloop(TotalPreset):
#     def __init__(self, duration):
#         super().__init__(22, duration)

class Colorloop(FXOnFiltered):
    def __init__(self, duration, eff_speed = 20, filter_lambda=lambda w: True):
        super().__init__(8, duration, 255, eff_speed, filter_lambda=filter_lambda)
        
class Off(ShowElement):
    def __init__(self, duration):
        super().__init__(duration)

    def activate(self):
        for i in range(3):
            wl.wleds.send_udp_sync(fx=0, brightness=0)

class TotalEffect(ShowElement):
    def __init__(self, duration,  eff_intensity, eff_speed):
        super().__init__(duration, eff_intensity=eff_intensity, eff_speed=eff_speed)

class SegmentOnDMX(ShowElement):
    def __init__(self, duration, filter_lambda=lambda w: True):
        super().__init__(duration, filter_lambda=filter_lambda)

    def activate(self):
        for i in range(3):
            wl.wleds.send_udp_sync(brightness=255, col=[0,0,0,0], follow_up = (i != 0))
        for wled in wl.wleds.filter(self.filter_lambda):
            try:
                wled.dmx.start() # this sets the n_leds
                n_leds = self.tube.dmx.n_leds
                data = []
                data += [0, 0, 0] * (n_leds//3 )
                data += [255, 255, 255] * (n_leds//3 )
                data += [255, 255, 0] * (n_leds-len(data)//3 )
                wled.dmx.set_data(data)
            except Exception as e:
                logger.warning(f"{e} while setting {self}")

    def deactivate(self):
        logging.debug("Deactivating sACN senders.")
        for wled in wl.wleds.filter(self.filter_lambda):
            try:
                wled.dmx.stop() # this sets the n_leds
            except Exception as e:
                logger.warning(f"{e} while stopping {self}")
        time.sleep(WledDMX.SEND_OUT_INTERVAL + 0.2 ) # remember to set the timeout in WLED to + 0.1