# -*- coding: utf-8 -*-
import os
from PIL import Image
from OpenGL.GL import *
from abc import ABC, abstractmethod


class BaseTexture(ABC):
    """Texture的抽象基类，定义所有渲染器共有的接口"""

    @abstractmethod
    def bind(self, unit):
        """
        绑定纹理到指定的纹理单元
        """
        pass

    @abstractmethod
    def unbind(self):
        """
        解绑当前纹理
        """
        pass

    @abstractmethod
    def cleanup(self):
        """
        清理纹理资源
        """
        pass
