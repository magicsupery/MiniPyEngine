# -*- coding:utf-8
import numpy as np
from core.ecs import Component
from util.quaternion import Quaternion


class Transform(Component):
    def __init__(self, position=None, rotation=None, scale=None):
        super(Transform, self).__init__()
        # 本地坐标系属性 (相对于父物体)
        self._local_position = position if position is not None else [0.0, 0.0, 0.0]
        self._local_scale = scale if scale is not None else [1.0, 1.0, 1.0]
        
        # 内部使用四元数存储旋转
        if rotation is not None:
            self._local_rotation_quat = Quaternion.from_euler_angles(rotation[0], rotation[1], rotation[2])
        else:
            self._local_rotation_quat = Quaternion.identity()
        
        # 父子关系管理
        self._parent = None
        self._children = []
        
        # 缓存的矩阵
        self._dirty = True
        self._local_to_world_matrix = None
        self._world_to_local_matrix = None

    # ============ Python风格的属性接口 ============
    
    @property
    def local_position(self):
        """本地位置 (相对于父物体)"""
        return np.array(self._local_position, dtype=np.float32)
    
    @local_position.setter
    def local_position(self, value):
        self._local_position = np.array(value, dtype=np.float32).tolist()
        self._mark_dirty()
    
    @property
    def position(self):
        """世界位置"""
        if self._parent is None:
            return self.local_position
        else:
            # 将本地坐标转换为世界坐标
            local_pos_4d = np.array([*self._local_position, 1.0], dtype=np.float32)
            world_pos_4d = np.dot(self._parent.local_to_world_matrix, local_pos_4d)
            return world_pos_4d[:3]
    
    @position.setter
    def position(self, value):
        """设置世界位置"""
        if self._parent is None:
            self.local_position = value
        else:
            # 将世界坐标转换为本地坐标
            world_pos_4d = np.array([*value, 1.0], dtype=np.float32)
            local_pos_4d = np.dot(self._parent.world_to_local_matrix, world_pos_4d)
            self.local_position = local_pos_4d[:3]
    
    @property
    def local_rotation(self):
        """本地旋转 (相对于父物体) - 欧拉角表示"""
        return np.array(self._local_rotation_quat.to_euler_angles(), dtype=np.float32)
    
    @local_rotation.setter
    def local_rotation(self, value):
        self._local_rotation_quat = Quaternion.from_euler_angles(value[0], value[1], value[2])
        self._mark_dirty()
    
    @property
    def local_rotation_quaternion(self):
        """本地旋转四元数"""
        return self._local_rotation_quat
    
    @local_rotation_quaternion.setter
    def local_rotation_quaternion(self, value):
        if isinstance(value, Quaternion):
            self._local_rotation_quat = value.normalized()
        else:
            raise TypeError("Expected Quaternion object")
        self._mark_dirty()
    
    @property
    def rotation(self):
        """世界旋转 - 欧拉角表示"""
        if self._parent is None:
            return self.local_rotation
        else:
            # 四元数乘法组合旋转
            world_quat = self._parent.rotation_quaternion * self._local_rotation_quat
            return np.array(world_quat.to_euler_angles(), dtype=np.float32)
    
    @rotation.setter
    def rotation(self, value):
        """设置世界旋转"""
        if self._parent is None:
            self.local_rotation = value
        else:
            # 计算相对旋转四元数
            target_quat = Quaternion.from_euler_angles(value[0], value[1], value[2])
            parent_quat_inv = self._parent.rotation_quaternion.inverse()
            self._local_rotation_quat = (parent_quat_inv * target_quat).normalized()
            self._mark_dirty()
    
    @property
    def rotation_quaternion(self):
        """世界旋转四元数"""
        if self._parent is None:
            return self._local_rotation_quat
        else:
            return self._parent.rotation_quaternion * self._local_rotation_quat
    
    @rotation_quaternion.setter
    def rotation_quaternion(self, value):
        """设置世界旋转四元数"""
        if not isinstance(value, Quaternion):
            raise TypeError("Expected Quaternion object")
        
        if self._parent is None:
            self._local_rotation_quat = value.normalized()
        else:
            parent_quat_inv = self._parent.rotation_quaternion.inverse()
            self._local_rotation_quat = (parent_quat_inv * value).normalized()
        self._mark_dirty()
    
    @property
    def local_scale(self):
        """本地缩放 (相对于父物体)"""
        return np.array(self._local_scale, dtype=np.float32)
    
    @local_scale.setter
    def local_scale(self, value):
        self._local_scale = np.array(value, dtype=np.float32).tolist()
        self._mark_dirty()
    
    @property
    def lossy_scale(self):
        """世界缩放 (只读)"""
        if self._parent is None:
            return self.local_scale
        else:
            return self._parent.lossy_scale * self.local_scale

    # ============ 父子关系管理 ============
    
    @property
    def parent(self):
        """父Transform"""
        return self._parent
    
    @parent.setter
    def parent(self, value):
        """设置父Transform"""
        self.set_parent(value)
    
    @property
    def child_count(self):
        """子物体数量"""
        return len(self._children)
    
    def get_child(self, index):
        """获取指定索引的子Transform"""
        if 0 <= index < len(self._children):
            return self._children[index]
        raise IndexError(f"Child index {index} out of range")
    
    def set_parent(self, parent, world_position_stays=True):
        """设置父物体"""
        if parent == self._parent:
            return
            
        # 如果需要保持世界位置
        old_world_pos = None
        old_world_rot_quat = None
        if world_position_stays:
            old_world_pos = self.position.copy()
            old_world_rot_quat = self.rotation_quaternion
        
        # 从旧父物体移除
        if self._parent is not None:
            self._parent._children.remove(self)
        
        # 设置新父物体
        self._parent = parent
        if parent is not None:
            parent._children.append(self)
        
        # 如果需要保持世界位置，则调整本地坐标
        if world_position_stays:
            if old_world_pos is not None:
                self.position = old_world_pos
            if old_world_rot_quat is not None:
                self.rotation_quaternion = old_world_rot_quat
        
        self._mark_dirty()
    
    def detach_children(self):
        """分离所有子物体"""
        for child in self._children[:]:  # 复制列表避免修改时出错
            child.set_parent(None)
    
    def find(self, name):
        """按名称查找子Transform (需要GameObject支持name属性)"""
        for child in self._children:
            if hasattr(child.owner, 'name') and child.owner.name == name:
                return child
        return None

    # ============ 矩阵计算 ============
    
    @property
    def local_to_world_matrix(self):
        """本地到世界的变换矩阵"""
        if self._dirty or self._local_to_world_matrix is None:
            self._update_matrices()
        return self._local_to_world_matrix
    
    @property
    def world_to_local_matrix(self):
        """世界到本地的变换矩阵"""
        if self._dirty or self._world_to_local_matrix is None:
            self._update_matrices()
        return self._world_to_local_matrix
    
    def _update_matrices(self):
        """更新变换矩阵"""
        # 计算本地变换矩阵
        local_matrix = self._calculate_local_matrix()
        
        # 计算世界变换矩阵
        if self._parent is None:
            self._local_to_world_matrix = local_matrix
        else:
            parent_world_matrix = self._parent.local_to_world_matrix
            self._local_to_world_matrix = np.dot(parent_world_matrix, local_matrix)
        
        # 计算逆矩阵
        self._world_to_local_matrix = np.linalg.inv(self._local_to_world_matrix)
        
        self._dirty = False
    
    def _calculate_local_matrix(self):
        """计算本地变换矩阵 TRS (Translation * Rotation * Scale)"""
        # 缩放矩阵
        scale_matrix = np.array([
            [self._local_scale[0], 0.0, 0.0, 0.0],
            [0.0, self._local_scale[1], 0.0, 0.0],
            [0.0, 0.0, self._local_scale[2], 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype=np.float32)

        # 使用四元数生成旋转矩阵
        rotation_matrix = self._local_rotation_quat.to_rotation_matrix()

        # 平移矩阵
        translation_matrix = np.array([
            [1.0, 0.0, 0.0, self._local_position[0]],
            [0.0, 1.0, 0.0, self._local_position[1]],
            [0.0, 0.0, 1.0, self._local_position[2]],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype=np.float32)

        # 最终矩阵: T * R * S
        return np.dot(np.dot(translation_matrix, rotation_matrix), scale_matrix)
    
    def _mark_dirty(self):
        """标记为需要更新，并递归标记所有子物体"""
        self._dirty = True
        for child in self._children:
            child._mark_dirty()

    # ============ 坐标系转换方法 ============
    
    def transform_point(self, point):
        """将点从本地坐标系转换到世界坐标系"""
        point_4d = np.array([*point, 1.0], dtype=np.float32)
        world_point_4d = np.dot(self.local_to_world_matrix, point_4d)
        return world_point_4d[:3]
    
    def inverse_transform_point(self, point):
        """将点从世界坐标系转换到本地坐标系"""
        point_4d = np.array([*point, 1.0], dtype=np.float32)
        local_point_4d = np.dot(self.world_to_local_matrix, point_4d)
        return local_point_4d[:3]
    
    def transform_direction(self, direction):
        """将方向从本地坐标系转换到世界坐标系 (不受位移影响)"""
        direction_4d = np.array([*direction, 0.0], dtype=np.float32)
        world_direction_4d = np.dot(self.local_to_world_matrix, direction_4d)
        return world_direction_4d[:3]
    
    def inverse_transform_direction(self, direction):
        """将方向从世界坐标系转换到本地坐标系 (不受位移影响)"""
        direction_4d = np.array([*direction, 0.0], dtype=np.float32)
        local_direction_4d = np.dot(self.world_to_local_matrix, direction_4d)
        return local_direction_4d[:3]
    
    def rotate(self, axis, angle):
        """绕指定轴旋转指定角度"""
        rotation_quat = Quaternion.from_axis_angle(axis, angle)
        self._local_rotation_quat = (self._local_rotation_quat * rotation_quat).normalized()
        self._mark_dirty()
    
    def look_at(self, target, up=None):
        """朝向目标点"""
        if up is None:
            up = [0, 1, 0]  # 默认向上方向
        
        forward = np.array(target) - np.array(self.position)
        forward = forward / np.linalg.norm(forward)
        
        right = np.cross(forward, up)
        right = right / np.linalg.norm(right)
        
        up = np.cross(right, forward)
        
        # 构建旋转矩阵
        rotation_matrix = np.array([
            [right[0], up[0], -forward[0], 0],
            [right[1], up[1], -forward[1], 0],
            [right[2], up[2], -forward[2], 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        # 从旋转矩阵转换为四元数 (简化实现)
        # 这里可以使用更精确的矩阵到四元数转换算法
        trace = rotation_matrix[0, 0] + rotation_matrix[1, 1] + rotation_matrix[2, 2]
        if trace > 0:
            s = np.sqrt(trace + 1.0) * 2
            w = 0.25 * s
            x = (rotation_matrix[2, 1] - rotation_matrix[1, 2]) / s
            y = (rotation_matrix[0, 2] - rotation_matrix[2, 0]) / s
            z = (rotation_matrix[1, 0] - rotation_matrix[0, 1]) / s
        else:
            if rotation_matrix[0, 0] > rotation_matrix[1, 1] and rotation_matrix[0, 0] > rotation_matrix[2, 2]:
                s = np.sqrt(1.0 + rotation_matrix[0, 0] - rotation_matrix[1, 1] - rotation_matrix[2, 2]) * 2
                w = (rotation_matrix[2, 1] - rotation_matrix[1, 2]) / s
                x = 0.25 * s
                y = (rotation_matrix[0, 1] + rotation_matrix[1, 0]) / s
                z = (rotation_matrix[0, 2] + rotation_matrix[2, 0]) / s
            elif rotation_matrix[1, 1] > rotation_matrix[2, 2]:
                s = np.sqrt(1.0 + rotation_matrix[1, 1] - rotation_matrix[0, 0] - rotation_matrix[2, 2]) * 2
                w = (rotation_matrix[0, 2] - rotation_matrix[2, 0]) / s
                x = (rotation_matrix[0, 1] + rotation_matrix[1, 0]) / s
                y = 0.25 * s
                z = (rotation_matrix[1, 2] + rotation_matrix[2, 1]) / s
            else:
                s = np.sqrt(1.0 + rotation_matrix[2, 2] - rotation_matrix[0, 0] - rotation_matrix[1, 1]) * 2
                w = (rotation_matrix[1, 0] - rotation_matrix[0, 1]) / s
                x = (rotation_matrix[0, 2] + rotation_matrix[2, 0]) / s
                y = (rotation_matrix[1, 2] + rotation_matrix[2, 1]) / s
                z = 0.25 * s
        
        self.rotation_quaternion = Quaternion(x, y, z, w)

    # ============ Unity风格别名 (兼容性接口) ============
    
    # 属性别名
    @property
    def localPosition(self):
        """Unity风格别名"""
        return self.local_position
    
    @localPosition.setter
    def localPosition(self, value):
        self.local_position = value
    
    @property
    def localRotation(self):
        """Unity风格别名"""
        return self.local_rotation
    
    @localRotation.setter
    def localRotation(self, value):
        self.local_rotation = value
    
    @property
    def localScale(self):
        """Unity风格别名"""
        return self.local_scale
    
    @localScale.setter
    def localScale(self, value):
        self.local_scale = value
    
    @property
    def lossyScale(self):
        """Unity风格别名"""
        return self.lossy_scale
    
    @property
    def childCount(self):
        """Unity风格别名"""
        return self.child_count
    
    @property
    def localToWorldMatrix(self):
        """Unity风格别名"""
        return self.local_to_world_matrix
    
    @property
    def worldToLocalMatrix(self):
        """Unity风格别名"""
        return self.world_to_local_matrix
    
    # 方法别名
    def SetParent(self, parent, worldPositionStays=True):
        """Unity风格别名"""
        return self.set_parent(parent, worldPositionStays)
    
    def GetChild(self, index):
        """Unity风格别名"""
        return self.get_child(index)
    
    def DetachChildren(self):
        """Unity风格别名"""
        return self.detach_children()
    
    def Find(self, name):
        """Unity风格别名"""
        return self.find(name)
    
    def TransformPoint(self, point):
        """Unity风格别名"""
        return self.transform_point(point)
    
    def InverseTransformPoint(self, point):
        """Unity风格别名"""
        return self.inverse_transform_point(point)
    
    def TransformDirection(self, direction):
        """Unity风格别名"""
        return self.transform_direction(direction)
    
    def InverseTransformDirection(self, direction):
        """Unity风格别名"""
        return self.inverse_transform_direction(direction)
    
    def Rotate(self, axis, angle):
        """Unity风格别名"""
        return self.rotate(axis, angle)
    
    def LookAt(self, target, up=None):
        """Unity风格别名"""
        return self.look_at(target, up)

    # ============ 兼容性属性 (保持与旧代码的兼容) ============
    
    @property
    def scale(self):
        """兼容旧版本的scale属性"""
        return self.local_scale
    
    @scale.setter
    def scale(self, value):
        self.local_scale = value

    def mark_dirty(self):
        """兼容旧版本的mark_dirty方法"""
        self._mark_dirty()

    def calculate_world_matrix(self):
        """兼容旧版本的calculate_world_matrix方法"""
        return self.local_to_world_matrix

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
