# -*- coding: utf-8 -*-

from config.renderer import RendererConfig, WindowType, RendererType
from graphics.window import Window
from graphics.renderer import Renderer


def create_window(**kwargs) -> Window:
    if RendererConfig.WindowType == WindowType.GLFW:
        from graphics.glfw_window import GlfwWindow
        return GlfwWindow(**kwargs)

    raise ValueError("Invalid window type")


def create_renderer(**kwargs) -> Renderer:
    if RendererConfig.RendererType == RendererType.OPENGL:
        from graphics.opengl_renderer import OpenGLRenderer
        return OpenGLRenderer(**kwargs)

    raise ValueError("Invalid renderer type")
