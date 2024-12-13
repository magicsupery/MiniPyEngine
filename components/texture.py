# -*- coding: utf-8 -*-

from core.ecs import Component


class Texture(Component):
	def __init__(self, texture):
		super().__init__()
		self.texture = texture
