# -*- coding: utf-8 -*-
import os
from PIL import Image
from OpenGL.GL import *


def load_texture_image(file_path):
    """使用 PIL 加载图像并转换为 RGBA 格式。"""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Texture file not found: {file_path}")

    image = Image.open(file_path)
    # 转换为 RGBA 格式，方便上传到 GPU
    image = image.convert("RGBA")
    return image


class Texture:
    """纹理类，负责加载图像并创建 OpenGL 纹理对象。"""

    def __init__(self, file_path):
        self.file_path = file_path
        self.image = load_texture_image(file_path)
        self.width, self.height = self.image.size

        # 创建 OpenGL 纹理 ID
        self.id = self.create_opengl_texture(self.image)

    def create_opengl_texture(self, image: Image.Image):
        """将 PIL Image 数据上传到 GPU，创建可用的 OpenGL 纹理。"""
        # 生成纹理 ID
        texture_id = glGenTextures(1)

        # 绑定纹理对象，并设置纹理参数
        glBindTexture(GL_TEXTURE_2D, texture_id)

        # 纹理环绕方式
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        # 纹理过滤方式（放大/缩小）
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # 获取图像的原始数据（byte 数据）
        img_data = image.tobytes()

        # 将图像数据传递给 GPU
        glTexImage2D(
            GL_TEXTURE_2D,
            0,  # 纹理等级，0 为基本图像等级
            GL_RGBA,  # 纹理存储格式（GPU端）
            self.width,
            self.height,
            0,  # 边框大小，一般为0
            GL_RGBA,  # 数据格式（CPU端）
            GL_UNSIGNED_BYTE,  # 数据类型
            img_data
        )

        # 自动生成多级纹理
        glGenerateMipmap(GL_TEXTURE_2D)

        # 解绑定纹理，防止后续误使用
        glBindTexture(GL_TEXTURE_2D, 0)

        return texture_id

    def __del__(self):
        """析构时，删除 OpenGL 纹理对象（可选）。"""
        try:
            glDeleteTextures([self.texture_id])
        except Exception:
            # 如果 OpenGL 上下文已经销毁，不必删除
            pass
