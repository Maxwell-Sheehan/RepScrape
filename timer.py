import time

class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end = time.perf_counter()
        self.duration = self.end - self.start

    def ms(self):
        """Return elapsed time in milliseconds."""
        return round(self.duration * 1000, 2)

    def sec(self):
        """Return elapsed time in seconds."""
        return round(self.duration, 3)
