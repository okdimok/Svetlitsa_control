```log
2022-12-05 00:17:10 raspberrypi sacn[7897] INFO Started sACN sending/sender thread
Exception in thread Thread-14:
Traceback (most recent call last):
  File "/usr/lib/python3.7/threading.py", line 917, in _bootstrap_inner
    self.run()
  File "/usr/lib/python3.7/threading.py", line 865, in run
    self._target(*self._args, **self._kwargs)
  File "/home/pi/Svetlitsa_control/scripts/../show_elements.py", line 382, in iterate
    color = self.colors[cur_line]
IndexError: list index out of range
```
```log
Exception in thread Thread-17:
Traceback (most recent call last):
  File "/usr/lib/python3.7/threading.py", line 917, in _bootstrap_inner
    self.run()
  File "/usr/lib/python3.7/threading.py", line 865, in run
    self._target(*self._args, **self._kwargs)
  File "/home/pi/Svetlitsa_control/scripts/../show_elements.py", line 375, in iterate
    self.step_progress()
  File "/home/pi/Svetlitsa_control/scripts/../show_elements.py", line 418, in step_progress
    self.current_progress[winner_index] = self.dmxrace.n_leds if is_on else 0
TypeError: list indices must be integers or slices, not NoneType
```

```log
Traceback (most recent call last):
  File "/usr/lib/python3.7/threading.py", line 917, in _bootstrap_inner
    self.run()
  File "/usr/lib/python3.7/threading.py", line 865, in run
    self._target(*self._args, **self._kwargs)
  File "/home/pi/Svetlitsa_control/scripts/../show_elements.py", line 380, in iterate
    self.step_progress()
  File "/home/pi/Svetlitsa_control/scripts/../show_elements.py", line 415, in step_progress
    self.current_progress = self.dmxrace.current_progress.copy()
AttributeError: 'DMXRace' object has no attribute 'current_progress'```

```log
ALSA lib pcm.c:8424:(snd_pcm_recover) underrun occurred
```
