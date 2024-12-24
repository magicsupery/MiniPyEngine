# -*- coding: utf-8 -*-


from enum import Enum, auto


class Key(Enum):
    W = auto()
    A = auto()
    S = auto()
    D = auto()


class KeyAction(Enum):
    PRESSED = auto()
    REPEAT = auto()
    RELEASED = auto()
