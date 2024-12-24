# -*- coding: utf-8 -*-

import glfw
from graphics.window import Window

from collections import deque
from input.event_types import Key, KeyAction


class GlfwWindow(Window):
    ACTION_TRANSFORM_MAP = {
        glfw.PRESS: KeyAction.PRESSED,
        glfw.REPEAT: KeyAction.REPEAT,
        glfw.RELEASE: KeyAction.RELEASED
    }

    KEY_TRANSFORM_MAP = {
        glfw.KEY_W: Key.W,
        glfw.KEY_A: Key.A,
        glfw.KEY_S: Key.S,
        glfw.KEY_D: Key.D
    }

    def __init__(self):
        super().__init__()
        self.window = None
        self.keyboard_events = deque()

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

        glfw.set_key_callback(self.window, self.key_callback)
        return

    def poll_events(self):
        glfw.poll_events()
        return

    def should_close(self):
        return glfw.window_should_close(self.window)

    def swap_buffers(self):
        glfw.swap_buffers(self.window)

    def cleanup(self):
        glfw.destroy_window(self.window)
        glfw.terminate()
        return

    def pop_keyboard_event(self):
        if self.keyboard_events:
            yield self.keyboard_events.popleft()

    def key_callback(self, window, key, scancode, action, mods):
        if key not in self.KEY_TRANSFORM_MAP or action not in self.ACTION_TRANSFORM_MAP:
            return

        abstract_key = self.KEY_TRANSFORM_MAP[key]
        abstract_action = self.ACTION_TRANSFORM_MAP[action]

        self.keyboard_events.append((abstract_key, abstract_action))
        return
