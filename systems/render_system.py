# -*- coding:utf-8 -*-
import numpy as np

from components.camera_setting import CameraSetting
from components.mesh import Mesh
from components.transform import Transform
from core.ecs import System
from config.renderer import RendererConfig
from graphics.factory import create_renderer
from Context.context import global_data as GD


class RenderSystem(System):
    def __init__(self):
        super().__init__()
        # 之后需要重构，应该由工厂类返回对应的Renderer
        self.renderer = create_renderer()
        GD.renderer = self.renderer
        self.renderer.initialize(RendererConfig.Width, RendererConfig.Height, RendererConfig.Title)

        # setting camera
        camera_entities = GD.ecs_manager.get_entities_with_component(CameraSetting)
        if len(camera_entities) != 1:
            raise Exception("There should be exactly one camera in the scene")

        self.main_camera = camera_entities[0]
        GD.main_camera = self.main_camera
        self.renderer.setup_camera(self.main_camera.components[CameraSetting])

    def update(self, delta_time):
        main_camera_setting = self.main_camera.CameraSetting
        if main_camera_setting.is_dirty:
            main_camera_setting.calculate_view_matrix()
            self.renderer.setup_camera(main_camera_setting)

        render_objects = []
        mesh_entities = GD.ecs_manager.get_entities_with_component(Mesh)
        for entity in mesh_entities:
            transform = entity.components[Transform]
            assert (transform is not None)

            mesh = entity.components[Mesh]
            # 之后重构，应该由工厂类返回对应的RenderObject
            # render_object = OpenGLRenderObject(transform.calculate_model_matrix(), mesh)
            render_objects.append((transform.calculate_model_matrix(), mesh))

        self.renderer.render(render_objects)
