# -*- coding:utf-8 -*-
import numpy as np

from components.material import Material
from components.mesh import Mesh
from components.transform import Transform
from core.ecs import System
from config.renderer import RendererConfig
from graphics.factory import create_renderer
from Context.context import global_data as GD
from Entity.camera import Camera


class RenderSystem(System):
    def __init__(self):
        super().__init__()
        # 之后需要重构，应该由工厂类返回对应的Renderer
        self.renderer = create_renderer()
        GD.renderer = self.renderer
        self.renderer.initialize(RendererConfig.Width, RendererConfig.Height, RendererConfig.Title)

    def update(self, delta_time):
        """
        渲染系统更新
        """
        # 确保有可用的相机
        self._ensure_camera_available()
        
        # 渲染所有网格对象
        if GD.main_camera:
            # 确保相机矩阵被正确设置
            if GD.main_camera.is_dirty or not hasattr(self, '_camera_setup_done'):
                GD.main_camera.calculate_view_matrix()
                self.renderer.setup_camera(GD.main_camera)
                self._camera_setup_done = True

            # 收集渲染对象
            render_objects = []
            mesh_entities = GD.ecs_manager.get_entities_with_component(Mesh)
            for entity in mesh_entities:
                transform = entity.get_component(Transform)
                assert (transform is not None)
                mesh = entity.get_component(Mesh)
                assert (mesh is not None)
                material = entity.get_component(Material)
                assert (material is not None)
                render_objects.append((transform.calculate_world_matrix().flatten("F"), mesh, material))

            # 执行渲染
            self.renderer.render(render_objects)

    def _ensure_camera_available(self):
        """确保有可用的相机"""
        if GD.main_camera is None:
            # 从场景中查找Camera类型的实体
            scene = GD.ecs_manager.get_active_scene()
            if scene:
                for entity in scene.all_entities:
                    if isinstance(entity, Camera):
                        GD.main_camera = entity
                        self.renderer.setup_camera(GD.main_camera)
                        break
