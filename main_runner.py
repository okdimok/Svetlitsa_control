import logging
logging.basicConfig(level=logging.DEBUG)
try:
    import coloredlogs
    coloredlogs.install(logging.getLogger().getEffectiveLevel())
except:
    pass

logger = logging.getLogger(__name__)

import threading
from threading import Thread, Lock, Event, Timer
from typing import Callable, Iterable
from wled_listener import WledListener
import shows
from sound_controller import SoundController, Sounds
from time import sleep
from itertools import cycle
try:
    from gpiozero import Button
except ModuleNotFoundError:
    class Button:
        when_activated: Callable
        def __init__(self, pin) -> None:
            pass


class MainRunner:
    current_show: shows.Show = None
    button: Button
    sound_controller: SoundController
    _show_thread: Thread = None
    _show_lock: Lock = Lock()
    shows_on_button: Iterable[shows.Show] = cycle([shows.show_red, shows.show_green, shows.show_blue])
    background_shows: Iterable[shows.Show] = cycle([shows.show_fast, shows.show_short])
    # _button_show_not_running: Event = Event()

    def __init__(self) -> None:
        self.sound_controller = SoundController()
        self.button = Button(17)
        self.button.when_activated = self.on_button
        self.wled_listener = WledListener()

    def on_button(self):
        self.sound_controller.play_overlay(Sounds.squeak)
        next_show = next(self.shows_on_button)
        logger.info(f"Button pressed, starting {next_show}")
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
        next_show = next(self.background_shows)
        self.start_show(next_show)
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

    