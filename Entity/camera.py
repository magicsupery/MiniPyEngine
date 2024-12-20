# -*- coding: utf-8 -*-

from core.ecs import Entity
from components.camera_setting import CameraSetting
from config.renderer import RendererConfig
from Context.context import global_data as GD


class Camera(Entity):
    def __init__(self, entity_id=None):
        super().__init__(entity_id)
        GD.ecs_manager.add_component(self, CameraSetting(aspect_ratio=RendererConfig.Width / RendererConfig.Height))
