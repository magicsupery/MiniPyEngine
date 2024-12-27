# -*- coding:utf-8 -*-
from core.ecs import Component


class Mesh(Component):
    def __init__(self, vertices, indices=None):
        super().__init__()
        self.vertices = vertices
        # self.uvs = uvs
        self.indices = indices if indices is not None else []
