import time
from threading import Thread

class PomodoroTimer:
    def __init__(self, default_duration=25, on_tick=None, on_finish=None, on_focus=None, on_distract=None):
        self.default_duration = default_duration * 60  # in seconds
        self.duration = self.default_duration
        self.remaining = self.duration
        self.running = False
        self.paused = False

        self.task = None
        self.difficulty = None

        self.on_tick = on_tick
        self.on_finish = on_finish
        self.on_focus = on_focus
        self.on_distract = on_distract

        self._timer_thread = None

    def start(self, task=None, difficulty=None, duration=None):
        if not self.running:
            # store task info
            self.task = task
            self.difficulty = difficulty
            self.duration = (duration * 60) if duration else self.default_duration
            self.remaining = self.duration

            self.running = True
            self.paused = False
            self._timer_thread = Thread(target=self._run, daemon=True)
            self._timer_thread.start()

            if self.on_focus:
                self.on_focus()

    def _run(self):
        while self.running and self.remaining > 0:
            if self.paused:
                time.sleep(0.5)
                continue
            time.sleep(1)
            self.remaining -= 1
            if self.on_tick:
                self.on_tick(self.remaining)

        if self.remaining <= 0:
            self.running = False
            if self.on_finish:
                self.on_finish()

    def pause(self):
        if self.running:
            self.paused = True
            if self.on_distract:
                self.on_distract()

    def resume(self):
        if self.paused:
            self.paused = False
            if self.on_focus:
                self.on_focus()

    def reset(self):
        self.running = False
        self.paused = False
        self.remaining = self.duration
        self.task = None
        self.difficulty = None

    def is_running(self):
        return self.running and not self.paused

    def is_paused(self):
        return self.paused
