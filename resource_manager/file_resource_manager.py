# -*- coding: utf-8 -*-
import json
import os
import numpy as np
from typing import Optional

from util.singleton import SingletonMeta
from config.renderer import RendererConfig
from resource_manager.opengl_texture import OpenGLTexture
from resource_manager.opengl_shader import OpenGLShader
from components.material import Material
from components.mesh import Mesh
from Context.context import global_data as GD


class FileResourceManager(object, metaclass=SingletonMeta):
    def __init__(self):
        self.texture_map = {}
        self.shader_map = {}
        self.material_map = {}
        self.mesh_cache = {}  # 新增：缓存已解析的原始模型数据
        self.mesh_map = {}    # 新增：缓存生成的Mesh组件

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
        并构造出一个带有"属性表"的 Material。
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

    def load_mesh_from_file(self, file_path: str) -> Optional[Mesh]:
        """
        根据文件后缀加载3D模型文件，生成Mesh组件
        Args:
            file_path: 模型文件路径
        Returns:
            Mesh组件或None
        """
        if not os.path.exists(file_path):
            print(f"❌ 模型文件不存在: {file_path}")
            return None

        # 检查缓存
        if file_path in self.mesh_map:
            return self.mesh_map[file_path]

        # 根据文件扩展名选择加载器
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.obj':
            mesh = self._load_obj_mesh(file_path)
        else:
            print(f"❌ 不支持的文件格式: {file_extension}")
            return None

        # 缓存生成的Mesh
        if mesh:
            self.mesh_map[file_path] = mesh
            
        return mesh

    def _load_obj_mesh(self, file_path: str) -> Optional[Mesh]:
        """
        加载OBJ格式文件并生成Mesh
        Args:
            file_path: OBJ文件路径
        Returns:
            Mesh组件或None
        """
        # 检查原始数据缓存
        if file_path in self.mesh_cache:
            obj_data = self.mesh_cache[file_path]
        else:
            obj_data = self._parse_obj_file(file_path)
            if obj_data is None:
                return None
            self.mesh_cache[file_path] = obj_data

        # 从缓存的数据生成Mesh
        return self._generate_mesh_from_obj_data(obj_data)

    def _parse_obj_file(self, file_path: str) -> Optional[dict]:
        """
        解析OBJ文件，提取顶点、法线、纹理坐标、面数据
        Returns:
            包含解析数据的字典或None
        """
        try:
            vertices = []
            normals = []
            texture_coords = []
            faces = []
            
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split()
                    if not parts:
                        continue
                    
                    # 解析顶点坐标 (v x y z)
                    if parts[0] == 'v':
                        if len(parts) >= 4:
                            vertex = [float(parts[1]), float(parts[2]), float(parts[3])]
                            vertices.append(vertex)
                    
                    # 解析法线 (vn x y z)
                    elif parts[0] == 'vn':
                        if len(parts) >= 4:
                            normal = [float(parts[1]), float(parts[2]), float(parts[3])]
                            normals.append(normal)
                    
                    # 解析纹理坐标 (vt u v)
                    elif parts[0] == 'vt':
                        if len(parts) >= 3:
                            tex_coord = [float(parts[1]), float(parts[2])]
                            texture_coords.append(tex_coord)
                    
                    # 解析面 (f v1/vt1/vn1 v2/vt2/vn2 v3/vt3/vn3)
                    elif parts[0] == 'f':
                        if len(parts) >= 4:
                            face = []
                            for i in range(1, len(parts)):
                                face_vertex = self._parse_face_vertex(parts[i])
                                if face_vertex:
                                    face.append(face_vertex)
                            
                            if len(face) >= 3:
                                faces.append(face)
            
            print(f"✅ OBJ文件解析成功: {file_path}")
            print(f"   顶点数: {len(vertices)}, 法线数: {len(normals)}, 纹理坐标数: {len(texture_coords)}, 面数: {len(faces)}")
            
            return {
                'vertices': vertices,
                'normals': normals,
                'texture_coords': texture_coords,
                'faces': faces,
                'file_path': file_path
            }
            
        except Exception as e:
            print(f"❌ 解析OBJ文件失败: {e}")
            return None

    def _parse_face_vertex(self, face_str: str) -> Optional[tuple]:
        """
        解析面顶点字符串 (格式: v/vt/vn 或 v//vn 或 v/vt 或 v)
        """
        try:
            parts = face_str.split('/')
            
            # 顶点索引 (必须存在)
            vertex_idx = int(parts[0]) - 1 if parts[0] else -1
            
            # 纹理坐标索引 (可选)
            texture_idx = -1
            if len(parts) > 1 and parts[1]:
                texture_idx = int(parts[1]) - 1
            
            # 法线索引 (可选)
            normal_idx = -1
            if len(parts) > 2 and parts[2]:
                normal_idx = int(parts[2]) - 1
            
            return (vertex_idx, texture_idx, normal_idx)
            
        except (ValueError, IndexError):
            return None

    def _generate_mesh_from_obj_data(self, obj_data: dict) -> Optional[Mesh]:
        """
        从解析的OBJ数据生成Mesh组件
        """
        vertices = obj_data['vertices']
        normals = obj_data['normals']
        texture_coords = obj_data['texture_coords']
        faces = obj_data['faces']
        
        if not vertices or not faces:
            print("❌ 无法生成Mesh: 缺少顶点或面数据")
            return None
        
        # 构建顶点数据数组 - 使用新的8个float格式，包含法线
        # 格式: [x, y, z, nx, ny, nz, u, v] 每个顶点8个值
        vertex_data = []
        indices = []
        
        vertex_map = {}  # 用于去重相同的顶点
        current_index = 0
        
        for face in faces:
            face_indices = []
            
            for vertex_idx, texture_idx, normal_idx in face:
                # 验证索引有效性
                if vertex_idx < 0 or vertex_idx >= len(vertices):
                    continue
                
                # 获取顶点数据
                vertex = vertices[vertex_idx]
                
                # 获取法线 (如果有)
                if normal_idx >= 0 and normal_idx < len(normals):
                    normal = normals[normal_idx]
                else:
                    # 如果没有法线，计算面法线或使用默认法线
                    normal = [0.0, 0.0, 1.0]  # 默认朝向Z轴正方向
                
                # 获取纹理坐标 (如果有)
                if texture_idx >= 0 and texture_idx < len(texture_coords):
                    tex_coord = texture_coords[texture_idx]
                else:
                    tex_coord = [0.0, 0.0]  # 默认纹理坐标
                
                # 创建完整的顶点数据（新的8个float格式）
                full_vertex = (
                    vertex[0], vertex[1], vertex[2],      # 位置
                    normal[0], normal[1], normal[2],      # 法线
                    tex_coord[0], tex_coord[1]            # 纹理坐标
                )
                
                # 检查是否已存在相同顶点
                vertex_key = (vertex_idx, texture_idx, normal_idx)
                if vertex_key in vertex_map:
                    face_indices.append(vertex_map[vertex_key])
                else:
                    vertex_data.extend(full_vertex)
                    vertex_map[vertex_key] = current_index
                    face_indices.append(current_index)
                    current_index += 1
            
            # 三角化面 (如果是四边形或多边形)
            if len(face_indices) >= 3:
                # 简单的扇形三角化
                for i in range(1, len(face_indices) - 1):
                    indices.extend([face_indices[0], face_indices[i], face_indices[i + 1]])
        
        # 转换为numpy数组
        vertices_array = np.array(vertex_data, dtype=np.float32)
        indices_array = np.array(indices, dtype=np.uint32) if indices else None
        
        print(f"✅ Mesh生成成功:")
        print(f"   最终顶点数: {len(vertices_array) // 8}")
        print(f"   三角形数: {len(indices) // 3 if indices else len(vertices_array) // 24}")
        print(f"   顶点格式: 位置+法线+UV (8个float)")
        
        # 创建新格式的Mesh组件
        mesh = Mesh(vertices_array, indices_array)
        
        # 附加原始OBJ数据供后续使用
        mesh.obj_data = obj_data
        
        return mesh
