# -*- coding:utf-8 -*-


'''
1. position
类型：np.array([0.0, 0.0, 3.0])
含义：相机的位置，表示相机在三维世界中的坐标。
作用：确定相机的观察点。它决定了相机从哪里观察场景。例如，position=np.array([0.0, 0.0, 3.0]) 表示相机位于 (0.0, 0.0, 3.0) 的位置。

2. front
类型：np.array([0.0, 0.0, -1.0])
含义：相机前方的方向向量，表示相机的朝向。
作用：定义相机的视线方向。例如，front=np.array([0.0, 0.0, -1.0]) 表示相机的前方是指向负 Z 轴的方向。这个向量通常是从相机的位置指向它正在观察的场景。

3. up
类型：np.array([0.0, 1.0, 0.0])
含义：相机的上方向向量，通常是 Y 轴方向。
作用：决定相机的“上”方向，用来避免相机出现倾斜或旋转。在常规的相机设置中，up=np.array([0.0, 1.0, 0.0]) 表示相机的“上”方向是沿着 Y 轴。

4. right
类型：np.cross(up, front)
含义：相机的右方向向量，通常是 X 轴方向。
作用：这个向量是通过相机的 up 向量与 front 向量进行叉乘得到的，表示相机的右方。叉乘运算确保这个向量是垂直于 up 和 front 的，代表相机的右侧方向。

5. fov (Field of View)
类型：45.0
含义：视场角，表示相机能够看到的视野的角度（通常是垂直方向的角度）。
作用：fov 控制相机的可视范围。较大的 fov 会使得相机能看到更宽广的场景，但也会产生一定的透视失真。通常 fov 的范围为 30 到 120 度，fov=45.0 表示相机的视场角为 45 度。

6. aspect_ratio
类型：1.0
含义：屏幕的宽高比，通常为 width / height，表示显示屏幕的比例。
作用：aspect_ratio 控制相机的投影矩阵，确保显示效果符合屏幕的长宽比例。例如，若屏幕分辨率为 1920x1080，则 aspect_ratio 为 1920/1080 = 1.777...。aspect_ratio=1.0 表示屏幕的宽高比为正方形。

7. near_clip
类型：0.1
含义：近裁剪面，定义了离相机最近的可见距离。
作用：该参数控制视锥体的前面，任何在此距离内的物体都会被裁剪掉，不可见。它的值通常大于 0。设置得太小可能会导致近处物体的深度冲突，设置得太大则可能会让一些本应看到的物体被忽略。

8. far_clip
类型：100.0
含义：远裁剪面，定义了离相机最远的可见距离。
作用：该参数控制视锥体的后面，任何在此距离外的物体都会被裁剪掉，不可见。它的值决定了相机能够看到的最远距离。设置得过小可能会导致远处物体无法显示，设置得过大会降低渲染精度。

9. view_matrix
类型：np.identity(4)
含义：视图矩阵（View Matrix），是从相机的角度将场景从世界空间转换到相机空间的矩阵。
作用：视图矩阵表示的是相机如何观察场景，它通过将世界坐标系中的物体坐标转换到相机坐标系来确定物体的位置。默认情况下，它被初始化为单位矩阵，表示没有进行任何视图变换。

10. projection_matrix
类型：self.perspective_projection(fov, aspect_ratio, near_clip, far_clip)
含义：投影矩阵（Projection Matrix），用于将三维场景投影到二维平面上（例如屏幕）。
作用：投影矩阵决定了物体如何根据视场角（fov）、宽高比（aspect_ratio）、近裁剪面和远裁剪面进行投影。self.perspective_projection() 是一个自定义的函数，生成透视投影矩阵，用来模拟相机镜头的透视效果。
'''

import numpy as np
from core.ecs import Component
from enum import Enum
from math import radians, cos, sin, sqrt


class ProjectionType(Enum):
    PERSPECTIVE = 0
    ORTHOGRAPHIC = 1


class CameraSetting(Component):
    def __init__(self, position=np.array([0.0, 0.0, 3.0]),
                 front=np.array([0.0, 0.0, -1.0]),
                 up=np.array([0.0, 1.0, 0.0]),
                 fov=45.0,
                 aspect_ratio=800 / 600,
                 near_clip=0.1,
                 far_clip=100.0,
                 projection_type=ProjectionType.PERSPECTIVE):
        super(CameraSetting, self).__init__()
        self.position = position
        self.front = self.normalize(front)
        self.up = self.normalize(up)
        self.right = self.normalize(np.cross(self.up, self.front))
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.near_clip = near_clip
        self.far_clip = far_clip
        assert self.near_clip > 0, "near_clip must be greater than 0"
        assert self.far_clip > self.near_clip, "far_clip must be greater than near_clip"
        self.projection_type = projection_type

        # 初始化视图矩阵和投影矩阵
        self.view_matrix = None
        self.projection_matrix = None
        self.calculate_projection_matrix()

        self.is_dirty = True
        # 初始化旋转四元数
        self.rotation = None
        self.adjust_view_matrix()

    def __setattr__(self, key, value):
        if key in ['position']:
            self.is_dirty = True
        super(CameraSetting, self).__setattr__(key, value)
       
    def calculate_view_matrix(self):
        """根据四元数和位置计算视图矩阵"""
        forward = self.get_forward()  # 从四元数中计算 forward
        print("forward: ", forward)
        right = self.normalize(np.cross(self.up, forward))
        up = self.normalize(np.cross(forward, right))

        # 构造视图矩阵
        self.view_matrix = np.array([
            [right[0], up[0], forward[0], 0],
            [right[1], up[1], forward[1], 0],
            [right[2], up[2], forward[2], 0],
            [-np.dot(right, self.position), -np.dot(up, self.position), -np.dot(forward, self.position), 1]
        ])

        print("rotation like view_matrix: ", self.view_matrix)
        z_axis = self.normalize(self.position - self.front)
        print("z_axis: ", z_axis)
        x_axis = self.normalize(np.cross(self.up, z_axis))
        y_axis = self.normalize(np.cross(z_axis, x_axis))
        tmp_matrix = np.array([
            [x_axis[0], y_axis[0], z_axis[0], 0],
            [x_axis[1], y_axis[1], z_axis[1], 0],
            [x_axis[2], y_axis[2], z_axis[2], 0],
            [-np.dot(x_axis, self.position), -np.dot(y_axis, self.position), -np.dot(z_axis, self.position), 1]
        ])

        print("no rotation like view_matrix: ", tmp_matrix)
        # self.view_matrix = tmp_matrix
        self.is_dirty = False

    def adjust_view_matrix(self):
        self.rotation = self.look_at_rotation(self.position, self.position + self.front, self.up)
        self.calculate_view_matrix()

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
            left, right = -10.0, 10.0
            bottom, top = -10.0, 10.0
            near, far = 0.1, 100.0
            self.projection_matrix = np.array([
                [2.0 / (right - left), 0, 0, -(right + left) / (right - left)],
                [0, 2.0 / (top - bottom), 0, -(top + bottom) / (top - bottom)],
                [0, 0, -2.0 / (far - near), -(far + near) / (far - near)],
                [0, 0, 0, 1.0]
            ])
        else:
            raise ValueError(f"Unknown projection type: {self.projection_type}")

    def look_at(self, target):
        """类似 Unity 的 LookAt 方法，更新相机朝向"""
        self.front = self.normalize(target - self.position)
        self.rotation = self.look_at_rotation(self.position, target, self.up)
        self.calculate_view_matrix()

    def look_at_rotation(self, position, target, up):
        """生成一个从 position 指向 target 的四元数旋转"""
        forward = self.normalize(target - position)
        right = self.normalize(np.cross(up, forward))
        up = np.cross(forward, right)

        # 构造旋转矩阵
        rotation_matrix = np.array([
            [right[0], up[0], -forward[0]],
            [right[1], up[1], -forward[1]],
            [right[2], up[2], -forward[2]],
        ])

        # 将旋转矩阵转换为四元数
        return self.matrix_to_quaternion(rotation_matrix)

    def matrix_to_quaternion(self, matrix):
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

        return np.array([w, x, y, z])

    def get_forward(self):
        """通过四元数获取前方向"""
        w, x, y, z = self.rotation
        return np.array([
            2 * (x * z + w * y),
            2 * (y * z - w * x),
            1 - 2 * (x * x + y * y)
        ])

    def normalize(self, vec):
        """归一化向量"""
        norm = np.linalg.norm(vec)
        if norm == 0:
            return vec
        return vec / norm
