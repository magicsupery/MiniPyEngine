# -*- coding:utf-8 -*-

from core.ecs import System
from components.texture import Texture
from graphics.vulkan_renderer import VulkanRenderer


class WindowConfig(object):
	Width = 800
	Height = 600
	Title = "Vulkan Renderer"


class RenderSystem(System):
	def __init__(self, ecs_manager):
		super().__init__(ecs_manager)
		self.renderer = VulkanRenderer()
		self.renderer.initialize(WindowConfig.Width, WindowConfig.Height, WindowConfig.Title)

	def update(self, delta_time):
		entities = self.manager.get_entities_with_component(Texture)
		for entity in entities:
			texture = entity.components[Texture]

		self.renderer.render()
