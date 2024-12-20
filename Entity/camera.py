# -*- coding: utf-8 -*-

from core.ecs import Entity
from Context.context import global_data as GD
from components.camera_setting import CameraSetting


class Camera(Entity):
    def __init__(self, entity_id=None, **kwargs):
        super().__init__(entity_id)
        GD.ecs_manager.add_component(self, CameraSetting(**kwargs))
