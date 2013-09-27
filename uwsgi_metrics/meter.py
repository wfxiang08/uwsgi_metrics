import time

from ewma import EWMA

class Meter(object):
    """A meter metric which measures mean throughput and one-, five-, and
    fifteen-minute exponentially-weighted moving average throughputs.

    Translated from https://github.com/codahale/metrics/blob/master/metrics-core/src/main/java/com/codahale/metrics/Meter.java
    """

    def __init__(self):
        self.m1_rate = EWMA.one_minute_EWMA()
        self.m5_rate = EWMA.five_minute_EWMA()
        self.m15_rate = EWMA.fifteen_minute_EWMA()
        self.count = 0
        self.start_time = time.time()
        self.last_tick = self.start_time

    def mark(self, n=1):
        """Mark the occurrence of a given number of events."""
        self.tick_if_necessary()
        self.count += n
        self.m1_rate.update(n)
        self.m5_rate.update(n)
        self.m15_rate.update(n)

    def tick_if_necessary(self):
        old_tick, new_tick = self.last_tick, time.time()
        age = new_tick - old_tick
        if age > EWMA.TICK_INTERVAL_S:
            self.last_tick = new_tick - age % EWMA.TICK_INTERVAL_S
            required_ticks = int(age / EWMA.TICK_INTERVAL_S)
            for _ in xrange(required_ticks):
                self.m1_rate.tick()
                self.m5_rate.tick()
                self.m15_rate.tick()

    def get_count(self):
        return self.count

    def get_one_minute_rate(self):
        self.tick_if_necessary()
        return self.m1_rate.get_rate()

    def get_five_minute_rate(self):
        self.tick_if_necessary()
        return self.m5_rate.get_rate()

    def get_fifteen_minute_rate(self):
        self.tick_if_necessary()
        return self.m15_rate.get_rate()

    def get_mean_rate(self):
        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return 0.0
        return self.count / elapsed