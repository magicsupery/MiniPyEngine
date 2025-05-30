# -*- coding: utf-8 -*-

import glfw
from graphics.window import Window

from collections import deque
from input.event_types import Key, KeyAction, MouseAction, MouseButton, ScrollDirection


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

    MOUSE_ACTION_TRANSFORM_MAP = {
        glfw.PRESS: MouseAction.PRESSED,
        glfw.RELEASE: MouseAction.RELEASED
    }

    MOUSE_BUTTON_TRANSFORM_MAP = {
        glfw.MOUSE_BUTTON_LEFT: MouseButton.LEFT,
        glfw.MOUSE_BUTTON_RIGHT: MouseButton.RIGHT,
        glfw.MOUSE_BUTTON_MIDDLE: MouseButton.MIDDLE
    }

    def __init__(self):
        super().__init__()
        self.last_cursor_pos = None
        self.window = None
        self.keyboard_events = deque()
        self.mouse_button_events = deque()
        self.mouse_move_events = deque()
        self.scroll_events = deque()

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
        glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)
        glfw.set_cursor_pos_callback(self.window, self.cursor_position_callback)
        glfw.set_scroll_callback(self.window, self.scroll_callback)
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

    def pop_mouse_button_event(self):
        if self.mouse_button_events:
            yield self.mouse_button_events.popleft()

    def pop_mouse_move_event(self):
        if self.mouse_move_events:
            yield self.mouse_move_events.popleft()

    def pop_scroll_event(self):
        if self.scroll_events:
            yield self.scroll_events.popleft()

    def key_callback(self, window, key, scancode, action, mods):
        if key not in self.KEY_TRANSFORM_MAP or action not in self.ACTION_TRANSFORM_MAP:
            return

        abstract_key = self.KEY_TRANSFORM_MAP[key]
        abstract_action = self.ACTION_TRANSFORM_MAP[action]

        self.keyboard_events.append((abstract_key, abstract_action))
        return

    def mouse_button_callback(self, window, button, action, mods):
        if button not in self.MOUSE_BUTTON_TRANSFORM_MAP or action not in self.MOUSE_ACTION_TRANSFORM_MAP:
            return

        abstract_button = self.MOUSE_BUTTON_TRANSFORM_MAP[button]
        abstract_action = self.MOUSE_ACTION_TRANSFORM_MAP[action]

        self.mouse_button_events.append((abstract_button, abstract_action))
        return

    # 鼠标移动回调函数
    def cursor_position_callback(self, window, xpos, ypos):
        if self.last_cursor_pos is None:
            self.last_cursor_pos = (xpos, ypos)
            return
        last_x, last_y = self.last_cursor_pos
        delta_x = xpos - last_x
        delta_y = ypos - last_y
        self.mouse_move_events.append((xpos, ypos, delta_x, delta_y))
        self.last_cursor_pos = (xpos, ypos)
        return

    def scroll_callback(self, window, xoffset, yoffset):
        self.scroll_events.append((xoffset, yoffset))
        return
