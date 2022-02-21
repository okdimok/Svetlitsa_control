from threading import Event, Lock
import time
from typing import Callable
from show_elements import *
from sound_controller import Sound
import logging
logger = logging.getLogger(__name__)

class Show:
    _current_show_element: ShowElement = None
    _needs_stop: Event = Event()
    _is_not_running: Event = Event()
    sound: Sound = None

    def __init__(self, elements=[], name="", sound=None) -> None:
        self.elements = list(elements)
        self._is_not_running.set()
        self.name = name
        self.sound = sound

    def __repr__(self) -> str:
        s = ""
        s += self.__str__()
        s += f"\nTotal {len(self.elements)} effects for {self.get_duration()} s\n"
        s += ",\n".join(str(se) for se in self.elements)
        return s

    def run_once(self):
        self._is_not_running.clear()
        logger.info(f"#"*6 + f" Running {self}.")
        for se in self.elements:
            if self._needs_stop.is_set():
                break
            logger.info(f"#"*3 + f" launching {se}")
            self._current_show_element = se
            se.run()
        self._is_not_running.set()
        cancelled = self._needs_stop.is_set()
        reason = "Canceled" if cancelled else "Finished"
        logger.debug(f"#"*6 + f" {reason} {self}.")
        return cancelled # returns, whether it has been cancelled (error 1), or everything is fine (0)

    def stop(self):
        logger.debug(f"#"*6 + f" Stopping {self}.")
        self._needs_stop.set()
        if self._current_show_element is not None: self._current_show_element.stop()
        self._is_not_running.wait()
        self._needs_stop.clear()
        logger.debug(f"#"*6 + f" Stopped {self}.")
    
    def wait(self):
        logger.debug(f"#"*6 + f" {self.wait.__name__} Waiting: {self}.")
        self._is_not_running.wait()
        logger.debug(f"#"*6 + f" {self.wait.__name__} Completed: {self}.")

    def is_running(self) -> bool:
        return not self._is_not_running.is_set()
        
    def run_infinetely(self):
        while True:
            self.run_once()
            if self._needs_stop.is_set():
                break

    def get_duration(self):
        return sum(e.duration for e in self.elements)

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.name}"


show_1 = Show([
    ShowElement(0),
    Colorloop(30),
    RYAndroid(5),
    Green(5),
    Red(5),
    Blue(5),
    Red(5),
    Blue(5), # 30
    Green(5),
    Red(5),
    Blue(5),
    Red(5),
    Colorloop(30),
    WarmWhite(5)
], "show_1")

short = Show([
    ShowElement(0),
    Colorloop(5),
    Red(5),
], "short")

dt = 1.0 # minimal reasonable time has to be larger, than transition
fast = [
    ShowElement(0),
    Colorloop(5),
] + [Red(dt), Green(dt), Blue(dt)] * 2
fast = Show(fast, "fast")

red_silent = Show([RedImmediate(5)], "red_silent", Sound.squeak)
green = Show([GreenImmediate(5)], "green")
blue_silent = Show([BlueImmediate(5)], "blue_silent")
tube = Show([SegmentOnDMX(10, lambda w: "tube-1" in w.name)], "tube")

colorloop = Show([Colorloop(10)], "colorloop_silent")

cubes = Show([
    RedImmediate(3, lambda w: "Cubes" in w.name),
    GreenImmediate(3, lambda w: "Cubes" in w.name),
    BlueImmediate(3, lambda w: "Cubes" in w.name),
], "cubes")

## The audio guide shows for Holodok 2022

oops = Show([Off(3)], "oops", Sound.oops)
showers = Show([
    FXOnFiltered(0, 2, 255, 255, col=[255, 92, 119]),
    FXOnFiltered(0, 2, 255, 255, col=[66, 170, 255]),
]*2, "showers", Sound.showers)
blue = Show([BlueImmediate(10)], "blue", Sound.blue)
red = Show([RedImmediate(10)], "red", Sound.red)
# kaleidoscope_mirrors
color_change = Show([Colorloop(30, 50)], "color_change", Sound.color_change)
walking = Show([
    FXOnFiltered(0, 5, 255, 255, col=[50, 255, 50], filter_lambda=lambda w: "Cubes" in w.name),
    FXOnFiltered(0, 5, 255, 255, col=[255, 255, 255], filter_lambda=lambda w: "Three-Colors" in w.name),
    Colorloop(10, filter_lambda=lambda w: "Stroop" in w.name),
], "walking", Sound.walking)

