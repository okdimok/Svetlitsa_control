from math import log
from time import sleep
from xml.dom.pulldom import parseString
import pygame
from typing import Dict, List
from threading import Thread, Timer
import logging
logger = logging.getLogger(__name__)
from enum import Enum, auto

class Sound(Enum):
    ambient_blues = auto()
    squeak = auto()
    blue = auto()
    color_change = auto()
    colorful = auto()
    convex_concave = auto()
    cozy = auto()
    forwarded = auto()
    important = auto()
    kaleidoscope_mirrors = auto()
    laser_light = auto()
    lenticular_caleidoscope = auto()
    lenticular_triangles = auto()
    muller_lyer = auto()
    oops = auto()
    rectangles_color = auto()
    rectangles_stroop = auto()
    red = auto()
    red_philosophy = auto()
    same_different_colors = auto()
    scandal = auto()
    showers = auto()
    spring = auto()
    wait = auto()
    walking = auto()
    yes = auto()
    
    красный = auto()
    жёлтый = auto()
    зелёный = auto()
    синий = auto()
    розовый = auto()
    голубой = auto()
    оранжевый = auto()

    добро_пожаловать = auto()
    старт = auto()
    гонка_фон = auto()
    победитель = auto()
    финиш = auto()

    lb_red = auto()
    lb_yellow = auto()
    lb_green = auto()
    lb_blue = auto()
    lb_pink = auto()
    lb_light_blue = auto()
    lb_orange = auto()

    lb_welcome = auto()
    lb_start = auto()
    # гонка_фон = auto()
    lb_winner = auto()
    lb_finish = auto()

class SoundController:
    sounds: Dict[str, pygame.mixer.Sound]
    sounds_ready: bool = False
    ambient_channel: pygame.mixer.Channel
    overlay_channel: pygame.mixer.Channel
    _default_ambient_volume: float = 0.35
    _ambient_volume_thread: Thread
    _overlays_timer: Timer = Timer(0, lambda: True)
    
    def __init__(self) -> None:
        pygame.mixer.init(buffer=2**12)  # Initialize the mixer module.
        self.sounds = dict()
        Thread(target=self.load_sounds, name=f"{self.__class__.__name__}_load_sounds").start()
        self.ambient_channel = pygame.mixer.Channel(0)
        self.overlay_channel = pygame.mixer.Channel(1)
        self.overlay_channel.set_volume(1.0)
        self._overlays_timer.start()

    def load_sounds(self):
        logger.info("Loading sounds...")
        self.sounds[Sound.ambient_blues] = pygame.mixer.Sound('sounds/Ambient_Blues_1.mp3')  # Load a sound.
        self.sounds[Sound.squeak] = pygame.mixer.Sound('sounds/mixkit-tropical-bird-squeak-27.wav')  # Load a sound.
        self.sounds[Sound.гонка_фон] = pygame.mixer.Sound('sounds/Elvis Herod - Danny Glover.mp3')
        for sound in Sound:
            if sound in self.sounds.keys():
                continue
            try:
                self.sounds[sound] = pygame.mixer.Sound(f'sounds/{sound.name}.mp3')  # Load a sound.
            except:
                logging.warning(f"No mp3 for {sound}")
        logger.info("Loading sounds completed!")
        self.sounds_ready = True
        self.start_ambient()

    def start_ambient(self):
        self.ambient_channel.set_volume(self._default_ambient_volume)
        self.ambient_channel.play(self.get_sound(Sound.ambient_blues), loops=-1) # see https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Sound.play
        self._ambient_volume_thread_start()
        

    def _on_overlay_end(self):
        self.ambient_channel.set_volume(self._default_ambient_volume)

    def _ambient_volume_loop(self):
        while True:
            if not self.overlay_channel.get_busy():
                self.ambient_channel.set_volume(self._default_ambient_volume)
            sleep(0.1)

    def _ambient_volume_thread_start(self):
        self._ambient_volume_thread = Thread(target=self._ambient_volume_loop, name=f"{self.__class__.__name__}_ambient_volume")
        self._ambient_volume_thread.start()

    def play_overlay(self, sound: Sound, force=True):
        if force:
            self._overlays_timer.cancel()
        loaded_sound = self.get_sound(sound)
        if loaded_sound is not None:
            self.ambient_channel.set_volume(0.1)
            self.overlay_channel.play(loaded_sound, fade_ms=200)
        else:
            logging.warning(f"Trying to play sound {sound} before it is loaded")

    def play_overlays(self, sounds: List[Sound]) -> float:
        self._overlays_timer.cancel()
        sounds_iter = iter(sounds)
        def play_next():
            try:
                sound = next(sounds_iter)
            except StopIteration:
                return
            try:
                l = self.get_sound(sound).get_length()
            except:
                return
            self.play_overlay(sound, force=False)
            logger.debug(f"{self.__class__} {sound}")
            self._overlays_timer = Timer(l, play_next)
            self._overlays_timer.start()
        play_next()
        return self._get_cumulative_duration(sounds)

    def _get_cumulative_duration(self, sounds: List[Sound]):
        l = 0
        for sound in sounds:
            try:
                l += self.get_sound(sound).get_length()
            except:
                pass
        return l

    def stop_overlay(self):
        self.overlay_channel.stop()

    def get_sound(self, sound: Sound):
        if not self.sounds_ready:
            return None
        if sound in self.sounds.keys():
            return self.sounds[sound]
        return None


    