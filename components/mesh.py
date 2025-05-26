# -*- coding:utf-8 -*-
import numpy as np
from core.ecs import Component


class Mesh(Component):
    def __init__(self, vertices, indices=None):
        super().__init__()
        self.vertices = vertices
        self.indices = indices if indices is not None else []
        
        # 用于存储原始OBJ数据（如果从OBJ加载）
        self.obj_data = None
        
        # 固定的顶点格式：[x, y, z, nx, ny, nz, u, v] - 8个float
        self._stride = 8
    
    def get_vertex_count(self):
        """获取顶点数量"""
        return len(self.vertices) // self._stride if len(self.vertices) > 0 else 0
    
    def get_positions(self):
        """提取位置数据"""
        positions = []
        for i in range(0, len(self.vertices), self._stride):
            pos = self.vertices[i:i+3]  # 位置：前3个float
            positions.extend(pos)
        return np.array(positions, dtype=np.float32)
    
    def get_normals(self):
        """提取法线数据"""
        normals = []
        for i in range(0, len(self.vertices), self._stride):
            normal = self.vertices[i+3:i+6]  # 法线：第4-6个float
            normals.extend(normal)
        return np.array(normals, dtype=np.float32)
    
    def get_uvs(self):
        """提取UV数据"""
        uvs = []
        for i in range(0, len(self.vertices), self._stride):
            uv = self.vertices[i+6:i+8]  # UV：最后2个float
            uvs.extend(uv)
        return np.array(uvs, dtype=np.float32)
    
    def get_vertex_info(self):
        """获取顶点格式信息"""
        return {
            'stride': 8,           # 每个顶点8个float
            'position_offset': 0,  # 位置在偏移0
            'position_size': 3,    # 位置3个分量
            'normal_offset': 3,    # 法线在偏移3
            'normal_size': 3,      # 法线3个分量
            'uv_offset': 6,        # UV在偏移6
            'uv_size': 2           # UV 2个分量
        }
