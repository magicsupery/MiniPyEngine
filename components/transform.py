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
        self.local_matrix = None  # parent-child
        self.world_matrix = None

    def __setattr__(self, key, value):
        if key in ['position', 'rotation', 'scale']:
            self.mark_dirty()
        super(Transform, self).__setattr__(key, value)

    def mark_dirty(self):
        self.dirty = True
        if self.owner:
            for child in self.owner.children:
                child.get_component(Transform).mark_dirty()

    def clear_dirty(self):
        self.dirty = False

    def calculate_local_matrix(self):
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
        return (np.matmul(np.matmul(translation, rotation), scale))

    def calculate_world_matrix(self):
        if not self.dirty:
            return self.world_matrix

        self.local_matrix = self.calculate_local_matrix()
        self.world_matrix = self.local_matrix
        if self.owner.parent is not None:
            parent_world_matrix = self.owner.parent.get_component(Transform).calculate_world_matrix()
            self.world_matrix = np.matmul(parent_world_matrix, self.local_matrix)

        self.clear_dirty()

        return self.world_matrix

    def update_local_transform(self):
        """
        This method is called when a child object is added to a parent object.
        It updates the position, rotation, and scale of the child object relative to its parent.
        """
        if self.owner.parent is not None:
            # If there is a parent, update the position, rotation, and scale relative to the parent.
            parent_transform = self.owner.parent.get_component(Transform)

            self.position = np.subtract(self.position, parent_transform.position)

            self.rotation = np.subtract(self.rotation, parent_transform.rotation)

            self.scale = np.divide(self.scale, parent_transform.scale)

            # Mark as dirty to recompute world matrix later
            self.mark_dirty()
