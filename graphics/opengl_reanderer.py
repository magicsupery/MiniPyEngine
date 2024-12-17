# -*- coding:utf-8 -*-

import glfw
import numpy as np
from ctypes import c_void_p
from OpenGL.GL import *
from graphics.renderer import Renderer


class OpenGLRenderer(Renderer):
    def __init__(self):
        self.vertices = None
        self.VBO = None
        self.VAO = None
        self.shader_program = None
        self.title = None
        self.height = None
        self.width = None
        self.window = None

    def initialize(self, width, height, title):
        self.width = width
        self.height = height
        self.title = title
        if not glfw.init():
            raise Exception("GLFW initialization failed")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
        # glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        # glfw.window_hint(glfw.CLIENT_API, glfw.OPENGL_ES_API)

        self.window = glfw.create_window(width, height, title, None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("GLFW window creation failed")

        glfw.make_context_current(self.window)

        # init opengl
        self.init_opengl()

        # init shaders
        self.shader_program = self.create_shader_program("graphics/shaders/vertex_shader.glsl",
                                                         "graphics/shaders/fragment_shader.glsl")

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(self.shader_program)
        glBindVertexArray(self.VAO)
        glDrawArrays(GL_TRIANGLES, 0, 3)
        glBindVertexArray(0)
        glfw.swap_buffers(self.window)

    def cleanup(self):
        glDeleteVertexArrays(1, [self.VAO])
        glDeleteBuffers(1, [self.VBO])
        glDeleteProgram(self.shader_program)
        glfw.destroy_window(self.window)
        glfw.terminate()

    def init_opengl(self):
        glViewport(0, 0, self.width, self.height)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        self.setup_mesh()

    def setup_mesh(self):
        # 定义一个简单的三角形
        self.vertices = np.array([
            0.0, -0.5, 0.0,  # 左下
            0.5, 0.5, 0.0,  # 右上
            -0.5, 0.5, 0.0  # 左上
        ], dtype=np.float32)

        # 创建 VAO 和 VBO
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)

        glBindVertexArray(self.VAO)

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # 设置顶点属性指针
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * self.vertices.itemsize, c_void_p(0))

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def create_shader_program(self, vertex_path, fragment_path):
        with open(vertex_path, 'r', encoding='utf-8') as file:
            vertex_src = file.read()
            vertex_shader = glCreateShader(GL_VERTEX_SHADER)
            glShaderSource(vertex_shader, vertex_src)
            glCompileShader(vertex_shader)
            if not glGetShaderiv(vertex_shader, GL_COMPILE_STATUS):
                raise Exception("Error compiling vertex shader: " + glGetShaderInfoLog(vertex_shader).decode())

        with open(fragment_path, 'r', encoding='utf-8') as file:
            fragment_src = file.read()
            fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
            glShaderSource(fragment_shader, fragment_src)
            glCompileShader(fragment_shader)
            if not glGetShaderiv(fragment_shader, GL_COMPILE_STATUS):
                raise Exception("Error compiling fragment shader: " + glGetShaderInfoLog(fragment_shader).decode())

        shader_program = glCreateProgram()
        glAttachShader(shader_program, vertex_shader)
        glAttachShader(shader_program, fragment_shader)
        glLinkProgram(shader_program)
        if not glGetProgramiv(shader_program, GL_LINK_STATUS):
            raise Exception("Error linking shader program: " + glGetProgramInfoLog(shader_program).decode())

        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

        return shader_program
