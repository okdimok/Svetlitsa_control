import logging
logging.basicConfig(level=logging.DEBUG)
try:
    import coloredlogs
    coloredlogs.install(logging.getLogger().getEffectiveLevel())
    pass
except:
    pass

logger = logging.getLogger(__name__)

import threading
from threading import Thread, Lock, Event, Timer
from typing import Callable, Iterable
from wled_listener import WledListener
import shows
import show_elements
from sound_controller import SoundController, Sound
from time import sleep
from itertools import cycle
from scripts.local_env import parent_path
import datetime
import random
random.seed(42)
try:
    from gpiozero import Button
except ModuleNotFoundError:
    class Button:
        when_activated: Callable
        def __init__(self, pin) -> None:
            pass

class ActivateOneShowOnButton:
    current_show: shows.Show = None
    button: Button
    sound_controller: SoundController
    _show_thread: Thread = None
    _show_lock: Lock = Lock()
    shows_on_button: Iterable[shows.Show] = cycle(shows.ButtonShows.values())
    # background_shows: Iterable[shows.Show] = cycle([shows.warm_white])
    background_shows: Iterable[shows.Show] = cycle([shows.best_frames])
    background_shows: Iterable[shows.Show] = cycle(shows.BackgroundShows.values())
    sounds: Iterable[Sound] = cycle(Sound)
    # _button_show_not_running: Event = Event()

    def __init__(self) -> None:
        self.sound_controller = SoundController()
        self.button = Button(17)
        shows_on_button = list(shows.YerevanButtonShows.values())
        random.shuffle(shows_on_button)
        self.shows_on_button = cycle(shows_on_button)
        background_shows = list(shows.YerevanBackgroundShows.values())
        random.shuffle(background_shows)
        self.background_shows = cycle(background_shows)
        self.init_show = shows.YerevanButtonShows.infinite_off
        self.button.when_activated = self.on_button
        self.wled_listener = WledListener()

    def on_button(self):
        next_show = next(self.shows_on_button)
        next_sound = next_show.sound
        if next_sound is not None:
            self.sound_controller.stop_overlay()
            self.sound_controller.play_overlay(next_sound)
        logger.info(f"Button pressed, starting {next_show}, and sound {next_sound}")
        with open(parent_path + "/button_pushed.log", "a") as f:
            f.write(f"{str(datetime.datetime.now())}\n")
        if isinstance(next_show, shows.Show):
            self.start_show(next_show)

    def start_show(self, show):
        with self._show_lock:
            logger.debug(f"In MainRunner.start_show: starting {show} in place of {self.current_show}")
            if self.current_show is not None:
                self.current_show.stop()
            self.current_show = show
            if self._show_thread is None:
                self._show_thread = Thread(target=self._show_loop, name=f"{self.__class__.__name__}_show_thread")
                self._show_thread.start()
        logger.debug(f"In MainRunner.start_show: started {show}")

    def run(self):
        self.start_show(self.init_show)
        main_thread = threading.main_thread()
        while True:
            L = threading.enumerate()
            L.remove(main_thread)  # or avoid it in the for loop
            for t in L:
                t.join()

    def _show_loop(self):
        while True:
            logger.debug(f"In MainRunner._show_loop: running once {self.current_show}")
            has_been_cancelled = self.current_show.run_once()
            reason = "canceled" if has_been_cancelled else "finished"
            logger.debug(f"In MainRunner._show_loop: ran once ({reason}) {self.current_show}")
            with self._show_lock:
                if (not has_been_cancelled): self.current_show = next(self.background_shows)

class LightBetRunner(ActivateOneShowOnButton):
    def __init__(self) -> None:
        super().__init__()
        dmxrace_show = shows.DMXRaceShow(self)
        shows_on_button = [dmxrace_show]
        random.shuffle(shows_on_button)
        self.shows_on_button = cycle(shows_on_button)
        background_shows = list(shows.YerevanBackgroundShows.values())
        random.shuffle(background_shows)
        self.background_shows = cycle(background_shows)
        self.init_show = shows.Show([show_elements.Red(5)], "red")

class MainRunner(LightBetRunner):
    def __init__(self) -> None:
        super().__init__()