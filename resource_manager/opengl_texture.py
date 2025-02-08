from OpenGL.GL import *
from PIL import Image
from resource_manager.texture import BaseTexture


class OpenGLTexture(BaseTexture):
    """OpenGL 实现的 Texture"""

    def __init__(self, file_path):
        self.file_path = file_path
        self.id = self.create_opengl_texture(file_path)

    def bind(self, unit):
        glActiveTexture(GL_TEXTURE0 + unit)
        glBindTexture(GL_TEXTURE_2D, self.id)

    def unbind(self):
        glBindTexture(GL_TEXTURE_2D, 0)

    def cleanup(self):
        glDeleteTextures([self.id])

    def create_opengl_texture(self, file_path):
        # 使用 PIL 加载图片
        image = Image.open(file_path)
        image = image.convert("RGBA")  # 转换为 RGBA 格式

        # 创建 OpenGL 纹理对象
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        # 设置纹理参数
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        img_data = image.tobytes()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        glBindTexture(GL_TEXTURE_2D, 0)
        return texture_id
