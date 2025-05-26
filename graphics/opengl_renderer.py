# -*- coding:utf-8 -*-

from ctypes import c_void_p
from OpenGL.GL import *
from graphics.renderer import Renderer, RenderObject
from graphics.factory import create_window
# TODO 目前感觉graphics不应该import上层的resource_manager，要么是texture的位置放置不对，要么是这里的依赖不应该出现
from resource_manager.opengl_texture import OpenGLTexture


class OpenGLRenderObject(RenderObject):
    def __init__(self, model_matrix, mesh, material):
        super().__init__(model_matrix, mesh, material)

    def render(self):
        shader = self.material.shader
        shader.use()

        texture_unit_index = 0  # 从 0 号纹理单元开始
        for prop_name, prop_value in self.material.properties.items():
            if prop_value is None:
                continue

            # 简单判断类型：如果是 Texture，我们假设 prop_value 为 Texture 实例
            # 如果是 float，我们用 glUniform1f 绑定
            if isinstance(prop_value, OpenGLTexture):  # 说明是 Texture (带 texture_id)
                tex_location = glGetUniformLocation(shader.shader_program, prop_name)
                if tex_location == -1:
                    # 如果 Shader 里没有对应 uniform，可能要报个警告或者跳过
                    print(f"Warning: uniform '{prop_name}' not found in Shader")
                    continue

                glActiveTexture(GL_TEXTURE0 + texture_unit_index)
                glBindTexture(GL_TEXTURE_2D, prop_value.id)
                glUniform1i(tex_location, texture_unit_index)
                texture_unit_index += 1

            elif isinstance(prop_value, float):
                # 假设这个 uniform 在 GLSL 中也是 float
                float_location = glGetUniformLocation(shader.shader_program, prop_name)
                if float_location != -1:
                    glUniform1f(float_location, prop_value)

        model_loc = glGetUniformLocation(shader.shader_program, "model")
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, self.model_matrix)

        VAO = glGenVertexArrays(1)
        VBO = glGenBuffers(1)
        EBO = glGenBuffers(1)

        glBindVertexArray(VAO)
        glBindBuffer(GL_ARRAY_BUFFER, VBO)
        glBufferData(GL_ARRAY_BUFFER, self.mesh.vertices.nbytes, self.mesh.vertices, GL_STATIC_DRAW)

        if len(self.mesh.indices) > 0:
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.mesh.indices.nbytes, self.mesh.indices, GL_STATIC_DRAW)

        # 固定的顶点属性设置 - 8个float格式 [x, y, z, nx, ny, nz, u, v]
        stride = 8 * self.mesh.vertices.itemsize
        
        # 位置属性 (location = 0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, c_void_p(0))
        glEnableVertexAttribArray(0)

        # 法线属性 (location = 1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, c_void_p(3 * self.mesh.vertices.itemsize))
        glEnableVertexAttribArray(1)

        # UV属性 (location = 2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, c_void_p(6 * self.mesh.vertices.itemsize))
        glEnableVertexAttribArray(2)

        if len(self.mesh.indices) > 0:
            glDrawElements(GL_TRIANGLES, len(self.mesh.indices), GL_UNSIGNED_INT, None)
        else:
            vertex_count = self.mesh.get_vertex_count()
            glDrawArrays(GL_TRIANGLES, 0, vertex_count)

        glDeleteVertexArrays(1, [VAO])
        glDeleteBuffers(1, [VBO])
        glDeleteBuffers(1, [EBO])


class OpenGLRenderer(Renderer):
    def __init__(self):
        self.title = None
        self.height = None
        self.width = None
        self.window = None
        self.render_objects = []
        self.shaders = []

    def initialize(self, width, height, title):
        self.width = width
        self.height = height
        self.title = title

        self.window = create_window()
        self.window.initialize(width, height, title)

        # init opengl
        self.init_opengl()

        # init shaders
        # self.shader_program = self.create_shader_program("graphics/shaders/vertex_shader.glsl",
        #                                                  "graphics/shaders/fragment_shader.glsl")

    def render(self, render_object_datas):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.render_objects = []
        for render_data in render_object_datas:
            render_object = OpenGLRenderObject(render_data[0], render_data[1], render_data[2])
            render_object.render()
            self.render_objects.append(render_object)

        self.window.swap_buffers()

    def cleanup(self):
        glDeleteVertexArrays(1, [self.VAO])
        glDeleteBuffers(1, [self.VBO])
        glDeleteProgram(self.shader_program)
        self.window.cleanup()

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
            print("compile vertext shader")
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

    def add_shader(self, shader):
        self.shaders.append(shader)

    def setup_camera(self, camera_setting):
        for shader in self.shaders:
            shader.use()
            camera_loc = glGetUniformLocation(shader.shader_program, "view")
            glUniformMatrix4fv(camera_loc, 1, GL_FALSE, camera_setting.view_matrix)
            projection_loc = glGetUniformLocation(shader.shader_program, "projection")
            glUniformMatrix4fv(projection_loc, 1, GL_FALSE, camera_setting.projection_matrix)

        glUseProgram(0)
        return
