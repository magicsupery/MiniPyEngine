# -*- coding: utf-8 -*-
from components.transform import Transform
from core.ecs import Entity


class GameObject(Entity):
    def __init__(self, entity_id=None):
        super().__init__(entity_id)
        self.components = {}
        self.add_component(Transform([0.0, 0.0, 0.0]))
