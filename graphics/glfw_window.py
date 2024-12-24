# -*- coding: utf-8 -*-

import glfw
from graphics.window import Window


class GlfwWindow(Window):
    def __init__(self):
        super().__init__()
        self.window = None

    def initialize(self, width, height, title):
        if not glfw.init():
            raise Exception("GLFW initialization failed")

        if not glfw.init():
            raise Exception("GLFW initialization failed")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
        # glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        # glfw.window_hint(glfw.CLIENT_API, glfw.OPENGL_ES_API)

        self.window = glfw.create_window(width, height, title, None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("GLFW window creation failed")

        glfw.make_context_current(self.window)
        return

    def poll_events(self):
        glfw.poll_events()
        return

    def should_close(self):
        return glfw.window_should_close(self.window)

    def swap_buffers(self):
        glfw.swap_buffers(self.window)

    def get_key(self, key):
        pass

    def cleanup(self):
        glfw.destroy_window(self.window)
        glfw.terminate()
        return
