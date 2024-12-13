﻿# -*- coding:utf-8
import time
import glfw
from core.time_core import TimeManager


class MainLoop(object):
	def __init__(self, ecs_manager, renderer, target_fps=60):
		self.target_fps = target_fps
		self.ecs_manager = ecs_manager
		self.renderer = renderer
		self.running = True

	def run(self):
		time_manager = TimeManager()

		try:
			while self.running:
				delta_time = time_manager.get_delta_time()

				systems = self.ecs_manager.get_systems()
				for system in systems:
					system.update(delta_time)

				self.handle_events()
				# control the frame rate
				time.sleep(max(1 / self.target_fps - (time_manager.get_delta_time()), 0))
		except KeyboardInterrupt:
			self.running = False

	def handle_events(self):
		glfw.poll_events()
		self.running = not glfw.window_should_close(self.renderer.window)