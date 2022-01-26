from threading import Event, Lock
import time
from show_elements import *

class Show:
    _current_show_element: ShowElement = None
    _needs_stop: Event = Event()
    _is_not_running: Event = Event()

    def __init__(self, elements=[], name="") -> None:
        self.elements = list(elements)
        self._is_not_running.set()
        self.name = name

    def __repr__(self) -> str:
        s = ""
        s += self.__str__()
        s += f"\nTotal {len(self.elements)} effects for {sum(e.duration for e in self.elements)} s\n"
        s += ",\n".join(str(se) for se in self.elements)
        return s

    def run_once(self):
        self._is_not_running.clear()
        print(f"Running {self}.")
        for se in self.elements:
            if self._needs_stop.is_set():
                break
            print(f"# launching {se}")
            self._current_show_element = se
            se.run()
        self._is_not_running.set()

    def stop(self):
        self._needs_stop.set()
        if self._current_show_element is not None: self._current_show_element.stop()
        self._is_not_running.wait()
        self._needs_stop.clear()

    def is_running(self) -> bool:
        return not self._is_not_running.is_set()
        
    def run_infinetely(self):
        while True:
            self.run_once()
            if self._needs_stop.is_set():
                break

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.name}"


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

show_short = Show([
    ShowElement(0),
    Colorloop(5),
    Red(5),
], "short")

dt = 1.0 # minimal reasonable time has to be larger, than transition
show_fast = [
    ShowElement(0),
    Colorloop(5),
] + [Red(dt), Green(dt), Off(dt)] * 3
show_fast = Show(show_fast, "fast")

show = show_fast