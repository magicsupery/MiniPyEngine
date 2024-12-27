# -*- coding: utf-8 -*-
import os.path

from util.singleton import SingletonMeta
from resource_manager.texture import Texture


class FileResourceManager(object, metaclass=SingletonMeta):
    def __init__(self):
        self.texture_map = {}
        return

    def load_texture(self, file_path):
        if file_path in self.texture_map:
            return self.texture_map[file_path]

        self.texture_map[file_path] = Texture(file_path)
        return self.texture_map[file_path]

    def load_mesh(self, file_path):
        pass
