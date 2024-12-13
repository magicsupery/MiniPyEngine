# -*- coding:utf-8

import time


class TimeManager(object):
    def __init__(self):
        self.last_time = time.time()

    def get_delta_time(self):
        now = time.time()
        delta = now - self.last_time
        self.last_time = now
        return delta
