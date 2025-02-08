from OpenGL.GL import *
from resource_manager.shader import BaseShader


class OpenGLShader(BaseShader):
    def __init__(self):
        self.shader_program = None
        self.vertex_shader = None
        self.fragment_shader = None

    def load(self, vertex_path, fragment_path):
        # 加载着色器源代码
        with open(vertex_path, 'r', encoding="utf-8") as file:
            vertex_src = file.read()
        with open(fragment_path, 'r', encoding="utf-8") as file:
            fragment_src = file.read()

        self.vertex_shader = self.compile_shader(vertex_src, GL_VERTEX_SHADER)
        self.fragment_shader = self.compile_shader(fragment_src, GL_FRAGMENT_SHADER)

    def compile(self):
        # 编译着色器
        self.shader_program = glCreateProgram()
        glAttachShader(self.shader_program, self.vertex_shader)
        glAttachShader(self.shader_program, self.fragment_shader)
        glLinkProgram(self.shader_program)
        if not glGetProgramiv(self.shader_program, GL_LINK_STATUS):
            raise Exception(f"Error linking shader program: {glGetProgramInfoLog(self.shader_program).decode()}")

        glDeleteShader(self.vertex_shader)
        glDeleteShader(self.fragment_shader)

    def use(self):
        glUseProgram(self.shader_program)

    def compile_shader(self, source, shader_type):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            raise Exception(f"Error compiling shader: {glGetShaderInfoLog(shader).decode()}")
        return shader

    def cleanup(self):
        glDeleteProgram(self.shader_program)
