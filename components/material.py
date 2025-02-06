# -*- coding: utf-8 -*-


import numpy as np
from core.ecs import Component


class Material(Component):
    def __init__(self, texture=None, shader=None):
        super().__init__()
        self.texture = texture
        self.shader = shader
