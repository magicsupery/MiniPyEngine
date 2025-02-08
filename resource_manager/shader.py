from OpenGL.GL import *

from abc import ABC, abstractmethod


class BaseShader(ABC):
    @abstractmethod
    def load(self, vertex_path, fragment_path):
        pass

    @abstractmethod
    def compile(self):
        pass

    @abstractmethod
    def use(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass
