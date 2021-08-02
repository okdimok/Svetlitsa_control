import time
from show_elements import *

class Show:
    def __init__(self, elements=[]) -> None:
        self.elements = list(elements)

    def __str__(self) -> str:
        return ",\n".join(str(se) for se in self.elements)

    def run_once(self):
        for se in self.elements:
            se.run()

    def run_infinetely(self):
        while True:
            self.run_once()

def show_1()
    return