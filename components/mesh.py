# -*- coding:utf-8 -*-
from core.ecs import Component


class MeshComponent(Component):
    def __init__(self, vertices, indices):
        super().__init__()
        self.vertices = vertices
        self.indices = indices
