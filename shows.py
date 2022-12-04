from threading import Event, Lock
import time
from typing import Callable
from show_elements import *
from sound_controller import Sound
from enum import Enum
from utils import dotdict, NamingEnum
from preset_manager import get_preset_id_by_name as ps
from fx_manager import fxs
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

class AudioOnlyShow:
    sound: Sound = None

    def __init__(self, sound=None) -> None:
        self.sound = sound

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.sound}"

    def __repr__(self) -> str:
        return self.__str__()

class DMXRaceShow(Show):
    def __init__(self, runner=None) -> None:
        self.dmxrace = DMXRace(5)
        self.dmxrace.sample_colors()
        self.dmxrace_intro = DMXRaceIntro(5.1)
        self.dmxrace_winner = DMXRaceWinner(5.1, self.dmxrace)
        elements = [self.dmxrace_intro, self.dmxrace, self.dmxrace_winner]
        super().__init__(elements, "DMXRaceShow")
        self.runner = runner

    def run_once(self):
        self.dmxrace.sample_colors()
        self.dmxrace_intro.colors = self.dmxrace.colors
        self.dmxrace_winner.colors = self.dmxrace.colors
        # self.sound_controller.play_overlay(soub)
        super().run_once()


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


tube = Show([SegmentOnDMX(10, lambda w: "tube-1" in w.name)], "tube")

colorloop = Show([Colorloop(10)], "colorloop_silent")

cubes = Show([
    RedImmediate(3, lambda w: "Cubes" in w.name),
    GreenImmediate(3, lambda w: "Cubes" in w.name),
    BlueImmediate(3, lambda w: "Cubes" in w.name),
], "cubes")

warm_white = Show([
    WarmWhite(5),
], "warm_white")

best_frames = Show([
    BestOnAllFrames1(15),
], "best_frames")

best_frames_long = Show([
    BestOnAllFrames1(1500),
], "best_frames")

## The audio guide shows for Holodok 2022

## Silent Shows

class SilentShows(NamingEnum):
    red_silent = Show([RedImmediate(2)])
    green_silent = Show([GreenImmediate(2)])
    blue_silent = Show([BlueImmediate(2)])
    # colorloop_silent = Show([
    #     Colorloop(10, 20),
    #     Colorloop(10, 50),
    #     Colorloop(10, 100),
    #     ])

    best_frames = Show([
            BestOnAllFrames1(20)
        ])

SilentShows.__init_names__()

## AudioOnlyShows

class AudioOnlyShows(NamingEnum):
    scandal = AudioOnlyShow(Sound.scandal)
    spring = AudioOnlyShow(Sound.spring)
    cozy = AudioOnlyShow(Sound.cozy)
    yes = AudioOnlyShow(Sound.yes)
    colorful = AudioOnlyShow(Sound.colorful)
    important = AudioOnlyShow(Sound.important)
    wait = AudioOnlyShow(Sound.wait)
    forwarded = AudioOnlyShow(Sound.forwarded)
    red_philosophy = AudioOnlyShow(Sound.red_philosophy)

## Show + Audio

class ShowAndAudio(NamingEnum):
    oops = Show([Off(3)], sound=Sound.oops)
    showers = Show([
        FXOnFiltered(0, 2, 255, 255, col=[255, 92, 119]),
        FXOnFiltered(0, 2, 255, 255, col=[66, 170, 255]),
        ]*2, sound=Sound.showers)
    blue = Show([BlueImmediate(10)], sound=Sound.blue)
    red = Show([RedImmediate(10)], sound=Sound.red)
    # kaleidoscope_mirrors
    color_change = Show([Colorloop(30, 50)], sound=Sound.color_change)
    walking = Show([
        FXOnFiltered(0, 5, 255, 255, col=[50, 255, 50], filter_lambda=lambda w: "Cubes" in w.name),
        FXOnFiltered(0, 5, 255, 255, col=[255, 255, 255], filter_lambda=lambda w: "Three-Colors" in w.name),
        Colorloop(10, filter_lambda=lambda w: "Stroop" in w.name),
        ], sound=Sound.walking)

ShowAndAudio.__init_names__()

## Frames Show + Audio

class FramesShowAndAudio(NamingEnum):
    # lenticular_triangles
    muller_lyer = Show([
        Colorloop(10, 10, filter_lambda=lambda w: "Muller-Lyer" in w.name),
        Red(3, filter_lambda=lambda w: "Muller-Lyer" in w.name),
        Green(3, filter_lambda=lambda w: "Muller-Lyer" in w.name),
        Blue(3, filter_lambda=lambda w: "Muller-Lyer" in w.name),
        Colorloop(10, 30, filter_lambda=lambda w: "Muller-Lyer" in w.name),
        Colorloop(20, 10, filter_lambda=lambda w: "Muller-Lyer" in w.name),
        ], sound=Sound.muller_lyer)
    convex_concave = Show([
        Colorloop(20, 20, filter_lambda=lambda w: "Cubes" in w.name),
        Red(3, filter_lambda=lambda w: "Cubes" in w.name),
        Green(3, filter_lambda=lambda w: "Cubes" in w.name),
        Blue(3, filter_lambda=lambda w: "Cubes" in w.name),
        Colorloop(20, 20, filter_lambda=lambda w: "Cubes" in w.name),
        ], sound=Sound.convex_concave)
    same_different_colors = Show([
        Colorloop(15, 40, filter_lambda=lambda w: "Three-Colors" in w.name),
        FXOnFiltered(fxs.STATIC, 50, 255, 255, brightness=200, col=[255, 255, 255], filter_lambda=lambda w: "Three-Colors" in w.name),
        ], sound=Sound.same_different_colors)
    rectangles_color = Show([
        Colorloop(30, 40, filter_lambda=lambda w: "Stroop" in w.name),
        FXOnFiltered(fxs.STATIC, 3, 255, 255, brightness=200, col=[255, 255, 255], filter_lambda=lambda w: "Stroop" in w.name),
        Red(3, filter_lambda=lambda w: "Stroop" in w.name),
        Green(3, filter_lambda=lambda w: "Stroop" in w.name),
        Blue(3, filter_lambda=lambda w: "Stroop" in w.name),
        ], sound=Sound.rectangles_color)
    rectangles_stroop = Show([
        FXOnFiltered(fxs.STATIC, 40, 255, 255, brightness=200, col=[255, 255, 255], filter_lambda=lambda w: "Stroop" in w.name),
        ], sound=Sound.rectangles_stroop)
    # lenticular_caleidoscope 
    # laser_light 

FramesShowAndAudio.__init_names__()

class AllShows(NamingEnum):
    pass
  
for a, v in list(SilentShows.items()) + list(AudioOnlyShows.items()) + list(ShowAndAudio.items()) + list(FramesShowAndAudio.items()):
    setattr(AllShows, a, v)

class ButtonShows(NamingEnum):
    objects = Show([
        FXOnFiltered(fxs.POLICE, 5 ,10, 1, col=[255, 92, 119], secondary_color=[0,0,0,0], tertiary_color=[0,0,0,0], filter_lambda=lambda w: "Objects" in w.name), # Police
        FXOnFiltered(fxs.TRICOLOR_CHASE, 5, 255, 255, col=[0, 255, 119], secondary_color=[0,0,0,0], tertiary_color=[0,0,0,0], filter_lambda=lambda w: "Objects" in w.name), # Green Running
        FXOnFiltered(fxs.TRICOLOR_CHASE, 5, 255, 255, col=[255, 0, 0], secondary_color=[0,0,0,0], tertiary_color=[0,0,0,0], filter_lambda=lambda w: "Objects" in w.name), # Red Running
        RBPills(5, filter_lambda=lambda w: "Objects" in w.name), # Red Running, 
        PresetOnFiltered(ps("Rainbow"), 5, 127, 64, filter_lambda=lambda w: "Objects" in w.name),
        PresetOnFiltered(ps("Gost Parade"), 5, filter_lambda=lambda w: "Objects" in w.name),
        PresetOnFiltered(ps("Rainbow"), 5, 127, 64, filter_lambda=lambda w: "Objects" in w.name),
        ])

for a, v in list(ShowAndAudio.items())*1 + list(FramesShowAndAudio.items())*2:
    setattr(ButtonShows, a, v)

class BackgroundShows(NamingEnum):
    pass

for a, v in list(SilentShows.items()):
    setattr(BackgroundShows, a, v)

class YerevanBackgroundShows(NamingEnum):
    main = Show([
        On(0.1),
        FXOnFiltered(fxs.RAINBOW, 60, 255, 1), 
        PresetOnFiltered(ps("Rainbow Slow"), 120),
        PresetOnFiltered(ps("RandomWipe"), 120),
        PresetOnFiltered(ps("Rainbow Plasma"), 60),
        ])

YerevanBackgroundShows.__init_names__()

class YerevanButtonShows(NamingEnum):
    main = YerevanBackgroundShows.main
    infinite_off = Show([Off(60*60*24*365*10)])

YerevanButtonShows.__init_names__()

# class DMXRaceShows(NamingEnum):
#     race = Show([], sound=)
#     pass

# DMXRaceShows.__init__names__()
