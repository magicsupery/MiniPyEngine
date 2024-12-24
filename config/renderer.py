# -*- coding:utf-8 -*-

from enum import Enum, auto


class WindowType(Enum):
    GLFW = auto()


class RendererType(Enum):
    OPENGL = auto()


class RendererConfig(object):
    Width = 800
    Height = 600
    Title = "OpenGL Renderer"
    WindowType = WindowType.GLFW
    RendererType = RendererType.OPENGL
