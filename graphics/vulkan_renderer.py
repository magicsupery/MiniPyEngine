# -*- coding:utf-8 -*-
from abc import ABC

import vulkan as vk
import glfw
from graphics.renderer import Renderer


class VulkanRenderer(Renderer, ABC):
	def __init__(self):
		self.instance = None
		self.window = None
		self.title = None
		self.height = None
		self.width = None

	def initialize(self, width, height, title):
		self.width = width
		self.height = height
		self.title = title

		if not glfw.init():
			raise Exception("GLFW initialization failed")

		glfw.window_hint(glfw.CLIENT_API, glfw.NO_API)
		self.window = glfw.create_window(width, height, title, None, None)
		self.init_vulkan()

	def init_vulkan(self):
		app_info = vk.VkApplicationInfo(
			sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
			pApplicationName="Hello Triangle",
			applicationVersion=vk.VK_MAKE_VERSION(1, 0, 0),
			pEngineName="No Engine",
			engineVersion=vk.VK_MAKE_VERSION(1, 0, 0),
			apiVersion=vk.VK_API_VERSION_1_0
		)

		create_info = vk.VkInstanceCreateInfo(
			sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
			pApplicationInfo=app_info
		)

		self.instance = vk.vkCreateInstance(create_info, None)

	def render(self):
		pass

	def cleanup(self):
		vk.vkDestroyInstance(self.instance, None)
		glfw.destroy_window(self.window)
		glfw.terminate()
