from OpenGL.GL import *
from ctypes import c_void_p


class Shader:
    def __init__(self, vertex_path, fragment_path):
        self.vertex_shader = self.compile_shader(vertex_path, GL_VERTEX_SHADER)
        self.fragment_shader = self.compile_shader(fragment_path, GL_FRAGMENT_SHADER)
        self.shader_program = self.create_program()

    def compile_shader(self, shader_path, shader_type):
        with open(shader_path, 'r', encoding='utf-8') as file:
            shader_src = file.read()
            shader = glCreateShader(shader_type)
            glShaderSource(shader, shader_src)
            glCompileShader(shader)
            if not glGetShaderiv(shader, GL_COMPILE_STATUS):
                raise Exception(f"Error compiling shader at {shader_path}: {glGetShaderInfoLog(shader).decode()}")
            return shader

    def create_program(self):
        shader_program = glCreateProgram()
        glAttachShader(shader_program, self.vertex_shader)
        glAttachShader(shader_program, self.fragment_shader)
        glLinkProgram(shader_program)
        if not glGetProgramiv(shader_program, GL_LINK_STATUS):
            raise Exception(f"Error linking shader program: {glGetProgramInfoLog(shader_program).decode()}")
        return shader_program

    def use(self):
        glUseProgram(self.shader_program)
