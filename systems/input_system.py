# -*- coding: utf-8 -*-

from bson import ObjectId
from core.ecs import System
from Context.context import global_data as GD
from collections import defaultdict


class InputSystem(System):
    def __init__(self):
        super(InputSystem, self).__init__()
        self.mouse_move_listener = []
        self.mouse_button_listener = defaultdict(list)
        self.keyboard_listener = defaultdict(list)
        self.scroll_listener = []
        self.id_2_callback = {}

    def update(self, dt):
        self.handle_keyboard_input()
        self.handle_mouse_button_input()
        self.handle_mouse_move_input()
        self.handle_scroll_input()
        return

    def handle_keyboard_input(self):
        window = GD.renderer.window

        for key, action in window.pop_keyboard_event():
            for callback in self.keyboard_listener[(key, action)]:
                callback()

    def handle_mouse_button_input(self):
        window = GD.renderer.window

        for button, action in window.pop_mouse_button_event():
            for callback in self.mouse_button_listener[(button, action)]:
                callback()

    def handle_mouse_move_input(self):
        window = GD.renderer.window
        for xpos, ypos, delta_x, delta_y in window.pop_mouse_move_event():
            for callback in self.mouse_move_listener:
                callback(xpos, ypos, delta_x, delta_y)

    def handle_scroll_input(self):
        window = GD.renderer.window
        for xoffset, yoffset in window.pop_scroll_event():
            for callback in self.scroll_listener:
                callback(xoffset, yoffset)

    def register_keyboard_listener(self, key, action, callback):
        listener_id = ObjectId()
        self.keyboard_listener[(key, action)].append(callback)
        self.id_2_callback[listener_id] = (key, action, callback)
        return listener_id

    def unregister_keyboard_listener(self, listener_id):
        key, action, callback = self.id_2_callback[listener_id]
        self.keyboard_listener[(key, action)].remove(callback)
        return

    def register_mouse_button_listener(self, button, action, callback):
        listener_id = ObjectId()
        self.mouse_button_listener[(button, action)].append(callback)
        self.id_2_callback[listener_id] = (button, action, callback)
        return listener_id

    def unregister_mouse_button_listener(self, listener_id):
        button, action, callback = self.id_2_callback[listener_id]
        self.mouse_button_listener[(button, action)].remove(callback)
        return

    def register_mouse_move_listener(self, callback):
        listener_id = ObjectId()
        self.mouse_move_listener.append(callback)
        self.id_2_callback[listener_id] = callback
        return listener_id

    def unregister_mouse_move_listener(self, listener_id):
        callback = self.id_2_callback[listener_id]
        self.mouse_move_listener.remove(callback)
        return

    def register_scroll_listener(self, callback):
        listener_id = ObjectId()
        self.scroll_listener.append(callback)
        self.id_2_callback[listener_id] = callback
        return listener_id

    def unregister_scroll_listener(self, listener_id):
        callback = self.id_2_callback[listener_id]
        self.scroll_listener.remove(callback)
        return
