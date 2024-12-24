# -*- coding: utf-8 -*-

from bson import ObjectId
from core.ecs import System
from Context.context import global_data as GD
from collections import defaultdict


class InputSystem(System):
    def __init__(self):
        super(InputSystem, self).__init__()
        self.keyboard_listener = defaultdict(list)
        self.id_2_callback = {}

    def update(self, dt):
        self.handle_keyboard_input()
        return

    def handle_keyboard_input(self):
        window = GD.renderer.window

        for key, action in window.pop_keyboard_event():
            for callback in self.keyboard_listener[(key, action)]:
                callback()

    def register_keyboard_listener(self, key, action, callback):
        listener_id = ObjectId()
        self.keyboard_listener[(key, action)].append(callback)
        self.id_2_callback[listener_id] = (key, action, callback)
        return listener_id

    def unregister_keyboard_listener(self, listener_id):
        key, action, callback = self.id_2_callback[listener_id]
        self.keyboard_listener[(key, action)].remove(callback)
        return
