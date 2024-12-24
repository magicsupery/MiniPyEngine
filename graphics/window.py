# -*- coding:utf-8 -*-


from abc import ABC, abstractmethod


class Window(ABC):
    @abstractmethod
    def initialize(self, width, height, title):
        pass

    @abstractmethod
    def poll_events(self):
        pass

    @abstractmethod
    def should_close(self):
        pass

    @abstractmethod
    def swap_buffers(self):
        pass

    @abstractmethod
    def get_key(self, key):
        pass

    @abstractmethod
    def cleanup(self):
        pass
