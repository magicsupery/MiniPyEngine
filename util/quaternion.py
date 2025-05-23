# -*- coding: utf-8 -*-
"""
四元数(Quaternion)实现
用于3D旋转计算，避免万向锁问题
"""
import numpy as np
import math


class Quaternion:
    """四元数类，用于表示3D旋转"""
    
    def __init__(self, x=0.0, y=0.0, z=0.0, w=1.0):
        """
        初始化四元数
        Args:
            x, y, z: 向量部分
            w: 标量部分
        """
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(w)
    
    def __repr__(self):
        return f"Quaternion(x={self.x:.3f}, y={self.y:.3f}, z={self.z:.3f}, w={self.w:.3f})"
    
    def __eq__(self, other):
        if not isinstance(other, Quaternion):
            return False
        epsilon = 1e-6
        return (abs(self.x - other.x) < epsilon and 
                abs(self.y - other.y) < epsilon and
                abs(self.z - other.z) < epsilon and
                abs(self.w - other.w) < epsilon)
    
    def __mul__(self, other):
        """四元数乘法"""
        if isinstance(other, Quaternion):
            # 四元数乘法公式
            w = self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z
            x = self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y
            y = self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x
            z = self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w
            return Quaternion(x, y, z, w)
        elif isinstance(other, (int, float)):
            # 标量乘法
            return Quaternion(self.x * other, self.y * other, self.z * other, self.w * other)
        else:
            raise TypeError(f"Cannot multiply Quaternion with {type(other)}")
    
    def __rmul__(self, other):
        """右乘法"""
        return self.__mul__(other)
    
    def __add__(self, other):
        """四元数加法"""
        if isinstance(other, Quaternion):
            return Quaternion(self.x + other.x, self.y + other.y, 
                            self.z + other.z, self.w + other.w)
        else:
            raise TypeError(f"Cannot add Quaternion with {type(other)}")
    
    def conjugate(self):
        """四元数共轭"""
        return Quaternion(-self.x, -self.y, -self.z, self.w)
    
    def magnitude(self):
        """四元数模长"""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2 + self.w**2)
    
    def normalize(self):
        """归一化四元数"""
        mag = self.magnitude()
        if mag > 1e-8:
            return Quaternion(self.x / mag, self.y / mag, self.z / mag, self.w / mag)
        else:
            return Quaternion(0, 0, 0, 1)  # 单位四元数
    
    def normalized(self):
        """返回归一化的副本"""
        return self.normalize()
    
    def inverse(self):
        """四元数逆"""
        conj = self.conjugate()
        mag_sq = self.x**2 + self.y**2 + self.z**2 + self.w**2
        if mag_sq > 1e-8:
            return Quaternion(conj.x / mag_sq, conj.y / mag_sq, 
                            conj.z / mag_sq, conj.w / mag_sq)
        else:
            return Quaternion(0, 0, 0, 1)
    
    def to_euler_angles(self):
        """
        转换为欧拉角 (degrees)
        返回: [pitch, yaw, roll] (绕X, Y, Z轴的旋转角度)
        使用ZYX顺序 (Roll-Pitch-Yaw)
        """
        # 归一化
        q = self.normalized()
        
        x, y, z, w = q.x, q.y, q.z, q.w
        
        # 计算欧拉角 (ZYX顺序)
        # Roll (X轴旋转)
        sin_r_cos_p = 2 * (w * x + y * z)
        cos_r_cos_p = 1 - 2 * (x * x + y * y)
        roll = math.atan2(sin_r_cos_p, cos_r_cos_p)
        
        # Pitch (Y轴旋转) 
        sin_p = 2 * (w * y - z * x)
        sin_p = max(-1.0, min(1.0, sin_p))  # 限制在[-1, 1]范围内
        pitch = math.asin(sin_p)
        
        # Yaw (Z轴旋转)
        sin_y_cos_p = 2 * (w * z + x * y)
        cos_y_cos_p = 1 - 2 * (y * y + z * z)
        yaw = math.atan2(sin_y_cos_p, cos_y_cos_p)
        
        # 转换为角度并返回 [pitch, yaw, roll] 顺序
        return [math.degrees(pitch), math.degrees(yaw), math.degrees(roll)]
    
    def to_rotation_matrix(self):
        """
        转换为旋转矩阵 (4x4)
        返回: numpy数组
        """
        # 归一化
        q = self.normalized()
        
        x, y, z, w = q.x, q.y, q.z, q.w
        
        # 计算旋转矩阵元素
        xx, yy, zz = x*x, y*y, z*z
        xy, xz, yz = x*y, x*z, y*z
        wx, wy, wz = w*x, w*y, w*z
        
        matrix = np.array([
            [1 - 2*(yy + zz), 2*(xy - wz), 2*(xz + wy), 0],
            [2*(xy + wz), 1 - 2*(xx + zz), 2*(yz - wx), 0],
            [2*(xz - wy), 2*(yz + wx), 1 - 2*(xx + yy), 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        return matrix
    
    def rotate_vector(self, vector):
        """
        使用四元数旋转向量
        Args:
            vector: [x, y, z] 三维向量
        Returns:
            旋转后的向量
        """
        # 将向量转换为纯四元数
        v_quat = Quaternion(vector[0], vector[1], vector[2], 0)
        
        # q * v * q^-1
        result = self * v_quat * self.inverse()
        
        return [result.x, result.y, result.z]
    
    @staticmethod
    def from_euler_angles(pitch, yaw, roll):
        """
        从欧拉角创建四元数
        Args:
            pitch: 绕X轴旋转角度 (degrees)
            yaw: 绕Y轴旋转角度 (degrees)  
            roll: 绕Z轴旋转角度 (degrees)
        Returns:
            Quaternion对象
        使用ZYX旋转顺序 (Roll-Pitch-Yaw)
        """
        # 转换为弧度
        roll_rad = math.radians(roll) / 2    # Z轴
        pitch_rad = math.radians(pitch) / 2  # X轴  
        yaw_rad = math.radians(yaw) / 2      # Y轴
        
        # 计算sin和cos值
        cr = math.cos(roll_rad)   # cos(roll/2)
        sr = math.sin(roll_rad)   # sin(roll/2)
        cp = math.cos(pitch_rad)  # cos(pitch/2)
        sp = math.sin(pitch_rad)  # sin(pitch/2)
        cy = math.cos(yaw_rad)    # cos(yaw/2)
        sy = math.sin(yaw_rad)    # sin(yaw/2)
        
        # ZYX旋转顺序的四元数计算
        w = cr * cp * cy + sr * sp * sy
        x = sr * cp * cy - cr * sp * sy
        y = cr * sp * cy + sr * cp * sy
        z = cr * cp * sy - sr * sp * cy
        
        return Quaternion(x, y, z, w)
    
    @staticmethod
    def from_axis_angle(axis, angle):
        """
        从轴角创建四元数
        Args:
            axis: [x, y, z] 旋转轴(单位向量)
            angle: 旋转角度 (degrees)
        Returns:
            Quaternion对象
        """
        # 归一化轴
        axis = np.array(axis, dtype=np.float32)
        axis_length = np.linalg.norm(axis)
        if axis_length < 1e-8:
            return Quaternion(0, 0, 0, 1)  # 单位四元数
        
        axis = axis / axis_length
        
        # 转换为弧度
        half_angle = math.radians(angle) / 2
        sin_half = math.sin(half_angle)
        cos_half = math.cos(half_angle)
        
        return Quaternion(
            axis[0] * sin_half,
            axis[1] * sin_half,
            axis[2] * sin_half,
            cos_half
        )
    
    @staticmethod
    def identity():
        """单位四元数"""
        return Quaternion(0, 0, 0, 1)
    
    @staticmethod
    def lerp(q1, q2, t):
        """
        线性插值 (Linear Interpolation)
        Args:
            q1, q2: 两个四元数
            t: 插值参数 [0, 1]
        Returns:
            插值结果四元数
        """
        t = max(0.0, min(1.0, t))  # 限制t在[0,1]范围内
        
        # 选择较短路径
        dot = q1.x * q2.x + q1.y * q2.y + q1.z * q2.z + q1.w * q2.w
        if dot < 0:
            q2 = Quaternion(-q2.x, -q2.y, -q2.z, -q2.w)
        
        # 线性插值
        result = Quaternion(
            q1.x * (1 - t) + q2.x * t,
            q1.y * (1 - t) + q2.y * t,
            q1.z * (1 - t) + q2.z * t,
            q1.w * (1 - t) + q2.w * t
        )
        
        return result.normalized()
    
    @staticmethod
    def slerp(q1, q2, t):
        """
        球面线性插值 (Spherical Linear Interpolation)
        Args:
            q1, q2: 两个四元数
            t: 插值参数 [0, 1]
        Returns:
            插值结果四元数
        """
        t = max(0.0, min(1.0, t))  # 限制t在[0,1]范围内
        
        # 计算夹角余弦值
        dot = q1.x * q2.x + q1.y * q2.y + q1.z * q2.z + q1.w * q2.w
        
        # 选择较短路径
        if dot < 0:
            q2 = Quaternion(-q2.x, -q2.y, -q2.z, -q2.w)
            dot = -dot
        
        # 如果夹角很小，使用线性插值
        if dot > 0.9995:
            return Quaternion.lerp(q1, q2, t)
        
        # 球面插值
        theta = math.acos(abs(dot))
        sin_theta = math.sin(theta)
        
        if sin_theta < 1e-8:
            return q1
        
        t1 = math.sin((1 - t) * theta) / sin_theta
        t2 = math.sin(t * theta) / sin_theta
        
        result = Quaternion(
            q1.x * t1 + q2.x * t2,
            q1.y * t1 + q2.y * t2,
            q1.z * t1 + q2.z * t2,
            q1.w * t1 + q2.w * t2
        )
        
        return result.normalized()
    
    def to_array(self):
        """转换为numpy数组 [x, y, z, w]"""
        return np.array([self.x, self.y, self.z, self.w], dtype=np.float32)
    
    @staticmethod
    def from_array(array):
        """从numpy数组创建四元数 [x, y, z, w]"""
        return Quaternion(array[0], array[1], array[2], array[3]) 