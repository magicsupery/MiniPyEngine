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
        self.right = np.cross(self.front, self.up)
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.near_clip = near_clip
        self.far_clip = far_clip
        assert self.near_clip > 0, "near_clip must be greater than 0"
        assert self.far_clip > self.near_clip, "far_clip must be greater than near_clip"
        self.projection_type = projection_type
        self.view_matrix = None
        self.calculate_view_matrix()
        self.projection_matrix = None
        self.calculate_projection_matrix()

    def calculate_view_matrix(self):
        z_axis = self.normalize(self.position - self.front)
        x_axis = self.normalize(np.cross(self.up, z_axis))
        y_axis = self.normalize(np.cross(z_axis, x_axis))
        self.view_matrix = np.array([
            [x_axis[0], y_axis[0], z_axis[0], 0],
            [x_axis[1], y_axis[1], z_axis[1], 0],
            [x_axis[2], y_axis[2], z_axis[2], 0],
            [-np.dot(x_axis, self.position), -np.dot(y_axis, self.position), -np.dot(z_axis, self.position), 1]
        ])

    def normalize(self, vec):
        return vec / np.linalg.norm(vec)

    def calculate_projection_matrix(self):
        tan_half_fov = np.tan(np.radians(self.fov) / 2)
        self.projection_matrix = np.array([
            [1 / (tan_half_fov * self.aspect_ratio), 0, 0, 0],
            [0, 1 / tan_half_fov, 0, 0],
            [0, 0, -(self.far_clip + self.near_clip) / (self.far_clip - self.near_clip), -1],
            [0, 0, -2 * self.far_clip * self.near_clip / (self.far_clip - self.near_clip), 0]
        ])
