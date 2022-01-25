import pygame
from typing import Dict

class SoundController:
    sounds: Dict[str, pygame.mixer.Sound]
    
    def __init__(self) -> None:
        pygame.mixer.init()  # Initialize the mixer module.
        self.sounds = dict()
        self.load_sounds()

    def load_sounds(self):
        print("Loading sounds...")
        self.sounds["ambient_blues"] = pygame.mixer.Sound('sounds/Ambient_Blues_1.mp3')  # Load a sound.
        self.sounds["squeak"] = pygame.mixer.Sound('sounds/mixkit-tropical-bird-squeak-27.wav')  # Load a sound.
        print("Loading sounds completed!")

    