# -*- coding: utf-8 -*-
from util.singleton import SingletonMeta
from resource_manager.texture import Texture
from resource_manager.shader import Shader
from components.material import Material
from Context.context import global_data as GD


class FileResourceManager(object, metaclass=SingletonMeta):
    def __init__(self):
        self.texture_map = {}
        self.shader_map = {}
        self.material_map = {}

    def load_texture(self, file_path):
        if file_path in self.texture_map:
            return self.texture_map[file_path]
        self.texture_map[file_path] = Texture(file_path)
        return self.texture_map[file_path]

    def load_shader(self, vertex_path, fragment_path):
        key = (vertex_path, fragment_path)
        if key in self.shader_map:
            return self.shader_map[key]
        self.shader_map[key] = Shader(vertex_path, fragment_path)
        GD.renderer.add_shader(self.shader_map[key])
        return self.shader_map[key]

    def load_material(self, texture_path, vertex_shader_path, fragment_shader_path):
        key = (texture_path, vertex_shader_path, fragment_shader_path)
        if key in self.material_map:
            return self.material_map[key]

        texture = self.load_texture(texture_path)
        shader = self.load_shader(vertex_shader_path, fragment_shader_path)
        self.material_map[key] = Material(texture, shader)
        return self.material_map[key]
