# -*- coding: utf-8 -*-
import json
import os

from util.singleton import SingletonMeta
from config.renderer import RendererConfig
from resource_manager.opengl_texture import OpenGLTexture
from resource_manager.opengl_shader import OpenGLShader
from components.material import Material
from Context.context import global_data as GD


class FileResourceManager(object, metaclass=SingletonMeta):
    def __init__(self):
        self.texture_map = {}
        self.shader_map = {}
        self.material_map = {}

    def load_texture(self, file_path):
        if file_path in self.texture_map:
            return self.texture_map[file_path]
        if RendererConfig.RendererType == RendererConfig.RendererType.OPENGL:
            self.texture_map[file_path] = OpenGLTexture(file_path)
        else:
            raise NotImplementedError(f"Renderer type {RendererConfig.RendererType} not supported yet.")
        return self.texture_map[file_path]

    def load_shader(self, vertex_path, fragment_path):
        key = (vertex_path, fragment_path)
        if key in self.shader_map:
            return self.shader_map[key]
        if RendererConfig.RendererType == RendererConfig.RendererType.OPENGL:
            shader = OpenGLShader()
            # TODO 以后再考虑加载策略
            shader.load(vertex_path, fragment_path)
            shader.compile()
            self.shader_map[key] = shader
        else:
            raise NotImplementedError(f"Renderer type {RendererConfig.RendererType} not supported yet.")
        GD.renderer.add_shader(self.shader_map[key])
        return self.shader_map[key]

    def load_material_from_config(self, config_path: str) -> Material:
        """
        读取形如 myshader.json 的文件，自动解析 Shader 路径及属性信息，
        并构造出一个带有“属性表”的 Material。
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Shader config file not found: {config_path}")

        # 如果已经解析过该 config，就直接返回对应 Material
        if config_path in self.material_map:
            return self.material_map[config_path]

        # 1. 读取 json
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # 2. 提取顶点/片段着色器路径，创建 Shader
        vertex_path = config_data["vertex"]
        fragment_path = config_data["fragment"]
        shader = self.load_shader(vertex_path, fragment_path)

        # 3. 创建一个 Material，里面除了 `shader` 外，还要根据 properties 初始化属性
        material = Material()
        material.shader = shader
        material.properties = {}  # 用于存储各类可编辑属性（texture2D、float等）

        # 4. 遍历 properties 列表，为每个属性设置默认值（如果有）
        for prop in config_data.get("properties", []):
            prop_type = prop.get("type")
            prop_name = prop.get("name")
            default_val = prop.get("default")

            if prop_type == "texture2D":
                # 自动加载 default 提供的纹理
                if default_val and os.path.exists(default_val):
                    tex = self.load_texture(default_val)
                    material.properties[prop_name] = tex
                else:
                    material.properties[prop_name] = None
            elif prop_type == "float":
                material.properties[prop_name] = float(default_val) if default_val is not None else 0.0
            else:
                # 其他类型可以继续扩展
                material.properties[prop_name] = default_val

        # 将该 Material 缓存起来，避免重复解析
        self.material_map[config_path] = material
        return material
