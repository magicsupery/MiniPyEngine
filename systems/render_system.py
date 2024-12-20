# -*- coding:utf-8 -*-
import numpy as np

from components.camera_setting import CameraSetting
from components.mesh import Mesh
from components.transform import Transform
from core.ecs import System
from graphics.opengl_reanderer import OpenGLRenderer, OpenGLRenderObject
from config.renderer import RendererConfig
from Context.context import global_data as GD


class RenderSystem(System):
    def __init__(self):
        super().__init__()
        # 之后需要重构，应该由工厂类返回对应的Renderer
        self.renderer = OpenGLRenderer()
        GD.renderer = self.renderer
        self.renderer.initialize(RendererConfig.Width, RendererConfig.Height, RendererConfig.Title)

        # setting camera
        camera_entities = GD.ecs_manager.get_entities_with_component(CameraSetting)
        if len(camera_entities) != 1:
            raise Exception("There should be exactly one camera in the scene")

        self.main_camera = camera_entities[0]
        self.renderer.setup_camera(self.main_camera.components[CameraSetting])

    def update(self, delta_time):
        # entities = self.manager.get_entities_with_component(Texture)
        # for entity in entities:
        #     texture = entity.components[Texture]

        render_objects = []
        mesh_entities = GD.ecs_manager.get_entities_with_component(Mesh)
        for entity in mesh_entities:
            transform = entity.components[Transform]
            assert (transform is not None)

            mesh = entity.components[Mesh]
            # 之后重构，应该由工厂类返回对应的RenderObject
            render_object = OpenGLRenderObject(transform.calculate_model_matrix(), mesh)
            render_objects.append(render_object)

        self.renderer.render(render_objects)
