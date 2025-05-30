# -*- coding: utf-8 -*-
"""
Camera实体 - 参考Unity Camera设计
自包含相机逻辑，不依赖外部组件
"""

import numpy as np
from math import radians, cos, sin, sqrt
from enum import Enum
from core.ecs import Entity
from util.quaternion import Quaternion


class ProjectionType(Enum):
    PERSPECTIVE = 0
    ORTHOGRAPHIC = 1


class Camera(Entity):
    """
    Camera实体 - 自包含相机功能
    参考Unity Camera的设计，直接在Entity中实现相机逻辑
    """
    
    def __init__(self, entity_id=None, 
                 position=np.array([0.0, 0.0, 3.0]),
                 rotation=None,
                 fov=45.0,
                 aspect_ratio=800/600,
                 near_clip=0.1,
                 far_clip=100.0,
                 projection_type=ProjectionType.PERSPECTIVE):
        super().__init__(entity_id)
        
        # 相机基本属性
        self.position = position
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.near_clip = near_clip
        self.far_clip = far_clip
        self.projection_type = projection_type
        
        # 相机旋转
        self.pitch = 0.0  # 俯仰角
        self.yaw = -90.0  # 偏航角，初始化指向负Z轴
        
        # 四元数旋转
        if rotation is None:
            self.rotation = Quaternion.from_euler_angles(self.pitch, self.yaw, 0.0)
        else:
            self.rotation = rotation.normalized()
        
        # 方向向量
        self.front = np.array([0.0, 0.0, -1.0])
        self.right = np.array([1.0, 0.0, 0.0])
        self.up = np.array([0.0, 1.0, 0.0])
        
        # 矩阵
        self.view_matrix = None
        self.projection_matrix = None
        
        # 脏标记
        self.is_dirty = True
        
        # 初始化
        self.update_direction_vectors()
        self.calculate_projection_matrix()
        self.calculate_view_matrix()
    
    def __setattr__(self, key, value):
        """当相机属性变化时标记为脏"""
        if hasattr(self, 'is_dirty') and key in ['position', 'rotation', 'fov', 'aspect_ratio', 
                                                 'near_clip', 'far_clip', 'projection_type', 'pitch', 'yaw']:
            self.is_dirty = True
        super(Camera, self).__setattr__(key, value)
    
    # ============ 方向向量更新 ============
    
    def update_direction_vectors(self):
        """根据当前的偏航和俯仰角度更新前、上、右向量"""
        # 计算前向量
        front = np.array([
            cos(radians(self.yaw)) * cos(radians(self.pitch)),
            sin(radians(self.pitch)),
            sin(radians(self.yaw)) * cos(radians(self.pitch))
        ])
        self.front = self.normalize(front)
        
        # 计算右向量
        self.right = self.normalize(np.cross(self.front, np.array([0.0, 1.0, 0.0])))
        
        # 计算上向量
        self.up = self.normalize(np.cross(self.right, self.front))
        
        # 同步更新旋转四元数
        self.rotation = Quaternion.from_euler_angles(self.pitch, self.yaw, 0.0)
    
    # ============ 矩阵计算 ============
    
    def calculate_view_matrix(self):
        """计算视图矩阵"""
        if self.is_dirty:
            self.update_direction_vectors()
        
        # 使用 LookAt 矩阵的计算方式
        target = self.position + self.front
        z_axis = self.normalize(self.position - target)  # forward
        x_axis = self.normalize(np.cross(self.up, z_axis))  # right
        y_axis = np.cross(z_axis, x_axis)  # up
        
        self.view_matrix = np.array([
            [x_axis[0], y_axis[0], z_axis[0], 0],
            [x_axis[1], y_axis[1], z_axis[1], 0],
            [x_axis[2], y_axis[2], z_axis[2], 0],
            [-np.dot(x_axis, self.position), -np.dot(y_axis, self.position), -np.dot(z_axis, self.position), 1]
        ])
        
        self.is_dirty = False
    
    def calculate_projection_matrix(self):
        """计算投影矩阵"""
        tan_half_fov = np.tan(np.radians(self.fov) / 2)
        
        if self.projection_type == ProjectionType.PERSPECTIVE:
            self.projection_matrix = np.array([
                [1 / (tan_half_fov * self.aspect_ratio), 0, 0, 0],
                [0, 1 / tan_half_fov, 0, 0],
                [0, 0, -(self.far_clip + self.near_clip) / (self.far_clip - self.near_clip), -1],
                [0, 0, -2 * self.far_clip * self.near_clip / (self.far_clip - self.near_clip), 0]
            ])
        elif self.projection_type == ProjectionType.ORTHOGRAPHIC:
            # 正交投影
            left, right = -10.0, 10.0
            bottom, top = -10.0, 10.0
            near, far = self.near_clip, self.far_clip
            self.projection_matrix = np.array([
                [2.0 / (right - left), 0, 0, -(right + left) / (right - left)],
                [0, 2.0 / (top - bottom), 0, -(top + bottom) / (top - bottom)],
                [0, 0, -2.0 / (far - near), -(far + near) / (far - near)],
                [0, 0, 0, 1.0]
            ])
        else:
            raise ValueError(f"Unknown projection type: {self.projection_type}")
    
    # ============ 相机控制方法 ============
    
    def look_at(self, target, up=np.array([0.0, 1.0, 0.0])):
        """看向指定目标点"""
        direction = self.normalize(target - self.position)
        forward = direction
        right = self.normalize(np.cross(up, forward))
        recalculated_up = np.cross(forward, right)
        
        # 构造旋转矩阵
        rotation_matrix = np.array([
            [right[0], recalculated_up[0], -forward[0]],
            [right[1], recalculated_up[1], -forward[1]],
            [right[2], recalculated_up[2], -forward[2]],
        ])
        
        # 转换为四元数
        self.rotation = self._matrix_to_quaternion(rotation_matrix).normalized()
        self.is_dirty = True
        self.calculate_view_matrix()
    
    def rotate_by_quaternion(self, quat):
        """使用四元数旋转相机"""
        self.rotation = (self.rotation * quat).normalized()
        self._update_from_quaternion()
    
    def set_rotation_quaternion(self, quat):
        """直接设置相机的旋转四元数"""
        self.rotation = quat.normalized()
        self._update_from_quaternion()
    
    def _update_from_quaternion(self):
        """从四元数更新欧拉角和方向向量"""
        # 从四元数转换为欧拉角
        euler_angles = self.rotation.to_euler_angles()
        self.pitch = euler_angles[0]
        self.yaw = euler_angles[1]
        
        # 使用四元数直接计算方向向量
        self.front = np.array(self.rotation.rotate_vector([0, 0, -1]), dtype=np.float32)
        self.right = np.array(self.rotation.rotate_vector([1, 0, 0]), dtype=np.float32)
        self.up = np.array(self.rotation.rotate_vector([0, 1, 0]), dtype=np.float32)
        
        self.is_dirty = True
    
    # ============ 工具方法 ============
    
    def normalize(self, vec):
        """归一化向量"""
        norm = np.linalg.norm(vec)
        if norm == 0:
            return vec
        return vec / norm
    
    def _matrix_to_quaternion(self, matrix):
        """将旋转矩阵转换为四元数"""
        m = matrix
        trace = np.trace(m)
        
        if trace > 0:
            s = 0.5 / sqrt(trace + 1.0)
            w = 0.25 / s
            x = (m[2, 1] - m[1, 2]) * s
            y = (m[0, 2] - m[2, 0]) * s
            z = (m[1, 0] - m[0, 1]) * s
        elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
            s = 2.0 * sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2])
            w = (m[2, 1] - m[1, 2]) / s
            x = 0.25 * s
            y = (m[0, 1] + m[1, 0]) / s
            z = (m[0, 2] + m[2, 0]) / s
        elif m[1, 1] > m[2, 2]:
            s = 2.0 * sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2])
            w = (m[0, 2] - m[2, 0]) / s
            x = (m[0, 1] + m[1, 0]) / s
            y = 0.25 * s
            z = (m[1, 2] + m[2, 1]) / s
        else:
            s = 2.0 * sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1])
            w = (m[1, 0] - m[0, 1]) / s
            x = (m[0, 2] + m[2, 0]) / s
            y = (m[1, 2] + m[2, 1]) / s
            z = 0.25 * s
        
        return Quaternion(x, y, z, w)
    
    # ============ 便捷属性 ============
    
    def get_view_matrix(self):
        """获取视图矩阵（自动更新）"""
        if self.is_dirty:
            self.calculate_view_matrix()
        return self.view_matrix
    
    def get_projection_matrix(self):
        """获取投影矩阵"""
        return self.projection_matrix
    
    def set_aspect_ratio(self, width, height):
        """设置宽高比"""
        self.aspect_ratio = width / height
        self.calculate_projection_matrix()
    
    def set_fov(self, fov):
        """设置视场角"""
        self.fov = fov
        self.calculate_projection_matrix()
    
    def move(self, direction, distance):
        """沿指定方向移动"""
        self.position += direction * distance
        self.is_dirty = True
