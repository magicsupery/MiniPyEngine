# -*- coding:utf-8 -*-


from abc import ABC, abstractmethod
from enum import Enum, auto


class KeyboardEventType(Enum):
    KEY_PRESSED = auto()
    KEY_RELEASED = auto()


class Key(Enum):
    W = auto()
    A = auto()
    S = auto()
    D = auto()


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
    def pop_keyboard_event(self):
        pass

    @abstractmethod
    def pop_mouse_button_event(self):
        pass

    @abstractmethod
    def pop_mouse_move_event(self):
        pass
   
    @abstractmethod
    def cleanup(self):
        pass
