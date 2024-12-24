# -*- coding: utf-8 -*-

from core.ecs import System
from Context.context import global_data as GD

from enum import Enum, auto


class EventType(Enum):
    KEY_PRESSED = auto()
    KEY_RELEASED = auto()


class Key(Enum):
    W = auto()
    A = auto()
    S = auto()
    D = auto()


class InputSystem(System):
    def __init__(self):
        super(InputSystem, self).__init__()
        self.keyboard_listener = defaultdict(defaultdict(list))

    def update(self, dt):
        self.handle_keyboard_input()
        return

    def handle_keyboard_input(self):
        cur_window = GD.renderer.window

    def register_keyboard_listener(self, event, key, callback):
        self.keyboard_events[key].append(event)
