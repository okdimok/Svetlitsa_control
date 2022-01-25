from typing import Callable
import shows
from sound_controller import SoundController
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

    def __init__(self) -> None:
        self.current_show = shows.show_fast
        self.sound_controller = SoundController()
        self.button = Button(17)
        self.button.when_activated = self.on_button

    def on_button(self):
        print("Button pressed")
        self.sound_controller.sounds["squeak"].play()


    def run(self):
        self.current_show.run_infinetely()