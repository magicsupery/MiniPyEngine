# -*- coding:utf-8 -*-

import glfw
from ctypes import c_void_p
from OpenGL.GL import *
from graphics.renderer import Renderer, RenderObject


class OpenGLRenderObject(RenderObject):
    def __init__(self, model_matrix, mesh):
        super().__init__(model_matrix, mesh)

    def render(self, shader_program):
        VAO = glGenVertexArrays(1)
        VBO = glGenBuffers(1)
        EBO = glGenBuffers(1)

        glBindVertexArray(VAO)
        glBindBuffer(GL_ARRAY_BUFFER, VBO)
        glBufferData(GL_ARRAY_BUFFER, self.mesh.vertices.nbytes, self.mesh.vertices, GL_STATIC_DRAW)

        if len(self.mesh.indices) > 0:
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.mesh.indices.nbytes, self.mesh.indices, GL_STATIC_DRAW)

        # position attribute
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * self.mesh.vertices.itemsize, c_void_p(0))
        glEnableVertexAttribArray(0)

        model_loc = glGetUniformLocation(shader_program, "model")
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, self.model_matrix)

        if len(self.mesh.indices) > 0:
            glDrawElements(GL_TRIANGLES, len(self.mesh.indices), GL_UNSIGNED_INT, None)
        else:
            glDrawArrays(GL_TRIANGLES, 0, len(self.mesh.vertices) // 3)

        glDeleteVertexArrays(1, [VAO])
        glDeleteBuffers(1, [VBO])
        glDeleteBuffers(1, [EBO])


class OpenGLRenderer(Renderer):
    def __init__(self):
        self.shader_program = None
        self.title = None
        self.height = None
        self.width = None
        self.window = None
        self.render_objects = []

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

        self.setup_camera()

    def render(self, render_objects):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader_program)

        self.render_objects = render_objects
        for render_object in render_objects:
            render_object.render(self.shader_program)

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
        glEnable(GL_DEPTH_TEST)

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

    def setup_camera(self):
        pass
