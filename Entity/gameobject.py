# -*- coding: utf-8 -*-
from components.transform import Transform
from core.ecs import Entity


class GameObject(Entity):
    def __init__(self, entity_id=None):
        super().__init__(entity_id)
        self.parent = None
        self.children = []

        trans = Transform([0.0, 0.0, 0.0])
        self.add_component(trans)
        trans.mark_dirty()

    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)
            child.parent = self
            child.get_component(Transform).update_local_transform()

    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
            child.parent = None
