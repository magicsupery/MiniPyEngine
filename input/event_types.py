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


class MouseButton(Enum):
    LEFT = auto()
    RIGHT = auto()
    MIDDLE = auto()


class MouseAction(Enum):
    PRESSED = auto()
    RELEASED = auto()


class ScrollDirection(Enum):
    """鼠标滚轮方向"""
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
