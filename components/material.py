# -*- coding: utf-8 -*-


import numpy as np
from core.ecs import Component


class Material(Component):
    def __init__(self, color=None, diffuse=None):
        super().__init__()
        if color is None:
            color = [1.0, 1.0, 1.0]
        self.color = np.array(color, dtype=np.float32)
        self.diffuse = diffuse

    def set_diffuse(self, diffuse):
        self.diffuse = diffuse
