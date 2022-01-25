from time import sleep
from xml.dom.pulldom import parseString
import pygame
from typing import Dict
from threading import Thread

MUSIC_END = pygame.USEREVENT+1

class SoundController:
    sounds: Dict[str, pygame.mixer.Sound]
    sounds_ready: bool = False
    ambient_channel: pygame.mixer.Channel
    overlay_channel: pygame.mixer.Channel
    _default_ambient_volume: float = 0.8
    _ambient_volume_thread: Thread
    
    def __init__(self) -> None:
        pygame.mixer.init()  # Initialize the mixer module.
        self.sounds = dict()
        Thread(target=self.load_sounds).start()
        self.ambient_channel = pygame.mixer.Channel(0)
        self.overlay_channel = pygame.mixer.Channel(1)

    def load_sounds(self):
        print("Loading sounds...")
        self.sounds["ambient_blues"] = pygame.mixer.Sound('sounds/Ambient_Blues_1.mp3')  # Load a sound.
        self.sounds["squeak"] = pygame.mixer.Sound('sounds/mixkit-tropical-bird-squeak-27.wav')  # Load a sound.
        print("Loading sounds completed!")
        self.sounds_ready = True
        self.start_ambient()

    def start_ambient(self):
        self.ambient_channel.set_volume(self._default_ambient_volume)
        self.ambient_channel.play(self.get_sound("ambient_blues"), loops=-1) # see https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Sound.play
        self._ambient_volume_thread_start()
        

    def _on_overlay_end(self):
        self.ambient_channel.set_volume(self._default_ambient_volume)

    def _ambient_volume_loop(self):
        while True:
            if not self.overlay_channel.get_busy():
                self.ambient_channel.set_volume(self._default_ambient_volume)
            sleep(0.1)

    def _ambient_volume_thread_start(self):
        self._ambient_volume_thread = Thread(target=self._ambient_volume_loop)
        self._ambient_volume_thread.start()

    def play_overlay(self, sound_name):
        sound = self.get_sound(sound_name)
        if sound is not None:
            self.ambient_channel.set_volume(0.3)
            self.overlay_channel.play(sound, fade_ms=200)
        else:
            print(f"WARNING: Trying to play sound {sound_name} before it is loaded")

    def get_sound(self, sound_name):
        if not self.sounds_ready:
            return None
        if sound_name in self.sounds.keys():
            return self.sounds[sound_name]
        return None


    