import time
from show_elements import *

class Show:
    def __init__(self, elements=[]) -> None:
        self.elements = list(elements)

    def __str__(self) -> str:
        s = ""
        s += f"Total {len(self.elements)} effects for {sum(e.duration for e in self.elements)} s\n"
        s += ",\n".join(str(se) for se in self.elements)
        return s

    def run_once(self):
        for se in self.elements:
            print(f"# launching {se}")
            se.run()

    def run_infinetely(self):
        while True:
            self.run_once()

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
])