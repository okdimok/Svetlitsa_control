import logging
logging.basicConfig(level=logging.DEBUG)
try:
    import coloredlogs
    coloredlogs.install(logging.getLogger().getEffectiveLevel())
except:
    pass

logger = logging.getLogger(__name__)

from threading import Thread, Lock
from typing import Callable, Iterable
from wled_listener import WledListener
import shows
from sound_controller import SoundController
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
    current_show: shows.Show
    button: Button
    sound_controller: SoundController
    _show_thread: Thread = None
    _show_lock: Lock = Lock()
    shows_on_button: Iterable = cycle([shows.show_red, shows.show_green, shows.show_blue])

    def __init__(self) -> None:
        self.current_show = shows.show_fast
        self.sound_controller = SoundController()
        self.button = Button(17)
        self.button.when_activated = self.on_button
        self.wled_listener = WledListener()

    def on_button(self):
        logger.info("Button pressed")
        self.sound_controller.play_overlay("squeak")
        self.start_show(next(self.shows_on_button))

    def start_show(self, show):
        with self._show_lock:
            if self.current_show is not None:
                self.current_show.stop()
            self.current_show = show
            if self._show_thread is None:
                self._show_thread = Thread(target=self._show_loop)
                self._show_thread.start()

    def run(self):
        while True:
            self.start_show(shows.show_fast)
            sleep(20)
            self.start_show(shows.show_short)
            sleep(20)

    def _show_loop(self):
        while True:
            self.current_show.run_once()
            with self._show_lock:
                pass

    