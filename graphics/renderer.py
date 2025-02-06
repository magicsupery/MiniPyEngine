# -*- coding:utf-8 -*-

from abc import ABC, abstractmethod


class RenderObject:
    def __init__(self, model_matrix, mesh, material):
        self.model_matrix = model_matrix
        self.mesh = mesh
        self.material = material


class Renderer(ABC):

    @abstractmethod
    def initialize(self, width, height, title):
        pass

    @abstractmethod
    def add_shader(self, shader):
        pass
   
    @abstractmethod
    def setup_camera(self, camera_setting):
        pass

    @abstractmethod
    def render(self, render_objects):
        pass

    @abstractmethod
    def cleanup(self):
        pass
