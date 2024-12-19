# -*- coding:utf-8 -*-
import numpy as np
from components.mesh import Mesh
from components.transform import Transform
from core.ecs import System
from components.texture import Texture
from graphics.opengl_reanderer import OpenGLRenderer, OpenGLRenderObject


class WindowConfig(object):
    Width = 800
    Height = 600
    Title = "OpenGL Renderer"


class RenderSystem(System):
    def __init__(self, ecs_manager):
        super().__init__(ecs_manager)
        # 之后需要重构，应该由工厂类返回对应的Renderer
        self.renderer = OpenGLRenderer()
        self.renderer.initialize(WindowConfig.Width, WindowConfig.Height, WindowConfig.Title)

    def update(self, delta_time):
        # entities = self.manager.get_entities_with_component(Texture)
        # for entity in entities:
        #     texture = entity.components[Texture]

        render_objects = []
        mesh_entities = self.manager.get_entities_with_component(Mesh)
        for entity in mesh_entities:
            transform = entity.components[Transform]
            assert (transform is not None)

            mesh = entity.components[Mesh]
            # 之后重构，应该由工厂类返回对应的RenderObject
            render_object = OpenGLRenderObject(transform.calculate_model_matrix(), mesh)
            render_objects.append(render_object)

        self.renderer.render(render_objects)
