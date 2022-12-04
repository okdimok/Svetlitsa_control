from threading import Event, Timer, Lock, Thread
import time
from math import floor
import random as rnd
from wled_common_client import Wled, Wleds, WledDMX
from scripts.local_env import default_wled_ip
import wled_listener as wl
from preset_manager import get_preset_id_by_name as ps
from fx_manager import fxs
from sound_controller import Sound
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

class On(ShowElement):
    def __init__(self, duration):
        super().__init__(duration)

    def activate(self):
        for i in range(1):
            try:
                wl.wleds.set_on_off(on=True)
            except Exception as e:
                logger.warning(f"{e} while turning on: {self}")

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
                n_leds = wled.dmx.n_leds
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

class DMXRace(ShowElement):
    color_map = {
        "красный": [255, 0, 0],
        "жёлтый": [255, 176, 0], # #ffb000
        "зелёный": [0, 255, 0],
        "синий": [0, 0, 255],
        "розовый": [255, 110, 149], # #ff6e95
        "голубой": [120, 176, 255], # #78b0ff
        "оранжевый": [255, 102, 0], # #ff6600
        # "": [], # 
        # "": [], # 
        # "": [], # 
        # "": [], # 
        # "": [], # 
    }

    def __init__(self, duration, runner = None):
        self.substripes_map = {
            "WLED-Light-Bet-1": [50, 50, 50]
        }
        filter_lambda = lambda w: w.name in self.substripes_map.keys()
        super().__init__(duration, filter_lambda=filter_lambda)
        self.n_leds=50
        self.set_lines()
        self.last_winner = None
        self.last_color = None
        self.last_substrip_winner = None
        self.runner = runner

    def play_sound(self):
        if self.runner:
            self.runner.sound_controller.play_overlay(Sound.старт)

    def set_lines(self):
        self.wled_lines = wl.wleds.filter(self.filter_lambda)
        self.n_lines = sum(len(self.substripes_map[w.name]) for w in self.wled_lines)

    def activate(self):
        rnd.seed(time.time())
        for i in range(3):
            wl.wleds.send_udp_sync(brightness=255, col=[0,0,0,0], follow_up = (i != 0))
        self.set_lines()
        self.current_progress = []
        if not len(self.wled_lines):
            logger.warning(f"{self}: no matching wleds connected.")
            return
        self.play_sound()
        logger.debug(f"{self} {self.wled_lines}")
        for wled in self.wled_lines:
            try:
                substripes = self.substripes_map[wled.name]
                wled.dmx.start() # this sets the n_leds
                total_n_leds = wled.dmx.n_leds
                if (sum(substripes) != total_n_leds):
                    logger.warning(f"Length inequality: sum({substripes}) != {total_n_leds} for {wled}") 
                data = []
                data += [0, 0, 0] * (total_n_leds)
                wled.dmx.set_data(data)
                self.current_progress += [5] * len(substripes)
            except Exception as e:
                logger.warning(f"{e} while  setting {self} for {wled}")
        

    def celebrate_winner(self, wled, color, champion_substrip):
        print(f"{wled.name} substrip {champion_substrip} won! Winning color: {color}")
        self.last_winner = wled
        self.last_color = color
        self.last_substrip_winner = champion_substrip

    def step_progress(self):
        step_every = self.duration/self.n_leds/len(self.current_progress)
        need_steps = floor((time.time() - self.last_step)/step_every)
        for i in range(need_steps):
            self.current_progress[rnd.randint(0, len(self.current_progress) - 1)] += 1
            self.last_step = time.time()
        # self.current_progress = [49, 0, 1]
        # logger.debug(f"{self.current_progress}")
    
    def sample_colors(self):
        self.set_lines()
        self.colors = list(rnd.sample(list(DMXRace.color_map.items()) , k=self.n_lines))

    def iterate(self):
        if not len(self.wled_lines):
            logger.warning(f"{self}: no matching wleds connected.")
            return
        self.last_step = time.time()
        champion_found = False
        champion_substrip = None
        champion_color = None
        if not self.colors: self.sample_colors()
        while not champion_found:
            self.step_progress()
            cur_line = 0
            for wled in self.wled_lines:
                substripes = self.substripes_map[wled.name]
                data = []
                for i, n_leds in enumerate(substripes):
                    progress = self.current_progress[cur_line]
                    color = self.colors[cur_line]
                    data += self.get_data_from_progress(progress, col1=color[1])
                    cur_line += 1
                    if (progress >= self.n_leds):
                        champion_found = True
                        champion_substrip = i
                        champion_color = color
                wled.dmx.set_data(data)
                if champion_found:
                    self.celebrate_winner(wled, champion_color, champion_substrip)
                    break
            time.sleep(1/60)

    def get_data_from_progress(self, progress, col1 = [255, 0, 0], col2=[0,0,0]):
        data = []
        data += col1 * (progress)
        data += col2 * (self.n_leds - progress)
        return data

    def sleep(self):
        self._sleep_timer = Thread(target=self.iterate, args=[]) # No name for timers:(  name=f"{self.__class__.__name__}_sleep_timer")
        self._sleep_timer.start()
        self._sleep_timer.join()

    def deactivate(self):
        logging.debug("Deactivating sACN senders.")
        for wled in wl.wleds.filter(self.filter_lambda):
            try:
                wled.dmx.stop() # this sets the n_leds
            except Exception as e:
                logger.warning(f"{e} while stopping {self}")
        time.sleep(WledDMX.SEND_OUT_INTERVAL + 0.2 ) # remember to set the timeout in WLED to + 0.1

class DMXRaceIntro(DMXRace):
    def __init__(self, duration, dmxrace, runner):
        super().__init__(duration, runner)
        self.dmxrace = dmxrace

    def step_progress(self):
        period = 0.5
        cutoff = 0.8
        is_on = (((time.time() - self.last_step) % period ) / period) < cutoff
        self.current_progress = [5 if is_on else 0] * self.n_lines

    def play_sound(self):
        if self.runner:
            sounds = [Sound.добро_пожаловать]
            for c in self.colors:
                sounds += [Sound[c[0]]]
            sounds += [Sound.старт]
            sound_duration = self.runner.sound_controller.play_overlays(sounds)
            if sound_duration > 0:
                self.duration = sound_duration

    def iterate(self):
        if not len(self.wled_lines):
            logger.warning(f"{self}: no matching wleds connected.")
            return
        self.last_step = time.time()
        if not self.colors:
            if not self.dmxrace.colors:
                self.dmxrace.sample_colors()
            self.colors = self.dmxrace.colors.copy()
            logger.warning(f"{self} had to sample {self.colors}")
        while time.time() - self.last_step < self.duration:
            self.step_progress()
            cur_line = 0
            for wled in self.wled_lines:
                substripes = self.substripes_map[wled.name]
                data = []
                for i, n_leds in enumerate(substripes):
                    progress = self.current_progress[cur_line]
                    color = self.colors[cur_line]
                    data += self.get_data_from_progress(progress, col1=color[1])
                    cur_line += 1
                wled.dmx.set_data(data)
            time.sleep(1/60)

class DMXRaceWinner(DMXRaceIntro):
    def play_sound(self):
        if self.runner:
            sounds = []
            if self.dmxrace.last_color is not None:
                sounds += [Sound.победитель]
                sounds += [Sound[self.dmxrace.last_color[0]]]
            sounds += [Sound.финиш]
            sound_duration = self.runner.sound_controller.play_overlays(sounds)
            if sound_duration > 0:
                self.duration = sound_duration


    def step_progress(self):
        try:
            self.current_progress = self.dmxrace.current_progress.copy()
        except AttributeError:
            return
        period = 0.5
        cutoff = 0.8
        is_on = (((time.time() - self.last_step) % period ) / period) < cutoff
        from operator import itemgetter
        try:
            winner_index, _ = max(enumerate(self.dmxrace.current_progress), key=itemgetter(1))
            self.current_progress[winner_index] = self.dmxrace.n_leds if is_on else 0
        except ValueError:
            pass
        



class BestOnAllFrames1(ShowElement):
    def activate(self):
        for i in range(3):
            pass
            # wl.wleds.filter(lambda w: "frame" not in w.name).send_udp_sync(brightness=150, col=[255,200,200,0], follow_up = (i != 0))
        for i in range(3):
            try:
                wl.wleds.filter(lambda w: "Cubes" in w.name
                    or "Stroop" in w.name
                    or "mirror" in w.name
                    or "Muller-Lyer" in w.name
                    ).send_udp_sync(fx=fxs.RAINBOW, fx_intensity = 255, fx_speed = 40, follow_up = (i != 0))
                wl.wleds.filter(lambda w: "Paste" in w.name).send_udp_sync(fx=fxs.RAINBOW_CYCLE, fx_intensity = 127, fx_speed = 65, follow_up = (i != 0))
                wl.wleds.filter(lambda w: "Objects" in w.name).send_udp_sync(fx=fxs.POLICE, fx_intensity = 10, fx_speed = 1, col=[255, 92, 119], secondary_color=[0,0,0,0], tertiary_color=[0,0,0,0])
                wl.wleds.filter(lambda w: "Three-Colors" in w.name).send_udp_sync(fx=fxs.STATIC, fx_intensity = 10, fx_speed = 1, brightness=150, col=[255, 255, 255], secondary_color=[0,0,0,0], tertiary_color=[0,0,0,0])
                wl.wleds.filter(lambda w: "tube" in w.name).send_udp_sync(fx=fxs.RAINBOW_CYCLE, fx_intensity = 255, fx_speed = 255, follow_up = (i != 0))
            except Exception as e:
                logger.warning(f"{e} while setting {self} with {self.filter_lambda}")