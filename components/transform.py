# -*- coding:utf-8
import numpy as np
from core.ecs import Component


class Transform(Component):
    def __init__(self, position, rotation=None, scale=None):
        super(Transform, self).__init__()
        self.position = position
        self.rotation = rotation if rotation is not None else [0.0, 0.0, 0.0]
        self.scale = scale if scale is not None else [1.0, 1.0, 1.0]
        self.dirty = True
        self.model_matrix = None

    def __setattr__(self, key, value):
        if key in ['position', 'rotation', 'scale']:
            self.dirty = True
        super(Transform, self).__setattr__(key, value)

    def calculate_model_matrix(self):

        if not self.dirty:
            return self.model_matrix

        # Notice ！！！
        # 缩放矩阵
        scale = np.array([
            [self.scale[0], 0.0, 0.0, 0.0],
            [0.0, self.scale[1], 0.0, 0.0],
            [0.0, 0.0, self.scale[2], 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype=np.float32)

        # 平移矩阵
        translation = np.array([
            [1.0, 0.0, 0.0, self.position[0]],
            [0.0, 1.0, 0.0, self.position[1]],
            [0.0, 0.0, 1.0, self.position[2]],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype=np.float32)

        # 获取角度（degree 转换为 radian）
        pitch = np.radians(self.rotation[0])  # 绕 X 轴旋转
        yaw = np.radians(self.rotation[1])  # 绕 Y 轴旋转
        roll = np.radians(self.rotation[2])  # 绕 Z 轴旋转

        # 绕 X 轴的旋转矩阵（Pitch）
        rotation_x = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, np.cos(pitch), -np.sin(pitch), 0.0],
            [0.0, np.sin(pitch), np.cos(pitch), 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype=np.float32)

        # 绕 Y 轴的旋转矩阵（Yaw）
        rotation_y = np.array([
            [np.cos(yaw), 0.0, np.sin(yaw), 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [-np.sin(yaw), 0.0, np.cos(yaw), 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype=np.float32)

        # 绕 Z 轴的旋转矩阵（Roll）
        rotation_z = np.array([
            [np.cos(roll), -np.sin(roll), 0.0, 0.0],
            [np.sin(roll), np.cos(roll), 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype=np.float32)

        # 组合旋转矩阵（注意旋转顺序：Roll -> Pitch -> Yaw）
        rotation = np.matmul(np.matmul(rotation_y, rotation_x), rotation_z)

        # 最终模型矩阵：模型 = 平移 * 旋转 * 缩放
        self.model_matrix = (np.matmul(np.matmul(translation, rotation), scale)).flatten('F')
        self.dirty = False
        return self.model_matrix
