# -*- coding:utf-8 -*-

from abc import ABC, abstractmethod


class Renderer(ABC):

	@abstractmethod
	def initialize(self, width, height, title):
		pass

	@abstractmethod
	def render(self):
		pass

	@abstractmethod
	def cleanup(self):
		pass
