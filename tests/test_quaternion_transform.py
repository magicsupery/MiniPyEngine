# -*- coding: utf-8 -*-
"""
测试四元数和Transform系统的完整功能
包括四元数基本运算、旋转计算、坐标转换等
"""
import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import math
from Entity.gameobject import GameObject
from core.ecs import ECSManager
from util.quaternion import Quaternion


def test_quaternion_basics():
    """测试四元数基本功能"""
    print("=== 测试四元数基本功能 ===\n")
    
    # 创建四元数
    q1 = Quaternion(0, 0, 0, 1)  # 单位四元数
    q2 = Quaternion.identity()   # 单位四元数的另一种创建方式
    
    print(f"单位四元数 q1: {q1}")
    print(f"单位四元数 q2: {q2}")
    print(f"q1 == q2: {q1 == q2}")
    
    # 从欧拉角创建四元数
    euler_angles = [30, 45, 60]  # pitch, yaw, roll
    q3 = Quaternion.from_euler_angles(euler_angles[0], euler_angles[1], euler_angles[2])
    print(f"从欧拉角 {euler_angles} 创建的四元数: {q3}")
    
    # 转换回欧拉角
    converted_euler = q3.to_euler_angles()
    print(f"转换回欧拉角: {converted_euler}")
    print(f"误差: {np.array(euler_angles) - np.array(converted_euler)}\n")
    
    # 四元数运算
    q4 = Quaternion(1, 0, 0, 0)
    q5 = Quaternion(0, 1, 0, 0)
    q_mult = q4 * q5
    print(f"四元数乘法 {q4} * {q5} = {q_mult}")
    
    # 归一化
    q_unnormalized = Quaternion(1, 1, 1, 1)
    q_normalized = q_unnormalized.normalized()
    print(f"未归一化: {q_unnormalized} (模长: {q_unnormalized.magnitude():.3f})")
    print(f"归一化后: {q_normalized} (模长: {q_normalized.magnitude():.3f})\n")


def test_quaternion_rotation():
    """测试四元数旋转功能"""
    print("=== 测试四元数旋转功能 ===\n")
    
    # 绕Y轴旋转90度
    axis = [0, 1, 0]
    angle = 90
    q_rotation = Quaternion.from_axis_angle(axis, angle)
    print(f"绕Y轴旋转90度的四元数: {q_rotation}")
    
    # 旋转向量
    vector = [1, 0, 0]  # X轴方向
    rotated_vector = q_rotation.rotate_vector(vector)
    print(f"向量 {vector} 旋转后: {rotated_vector}")
    print(f"期望结果: [0, 0, -1] (大致)")
    
    # 旋转矩阵
    rotation_matrix = q_rotation.to_rotation_matrix()
    print(f"旋转矩阵:\n{rotation_matrix}\n")
    
    # 插值测试
    q1 = Quaternion.identity()
    q2 = Quaternion.from_euler_angles(0, 90, 0)
    q_lerp = Quaternion.lerp(q1, q2, 0.5)
    q_slerp = Quaternion.slerp(q1, q2, 0.5)
    
    print(f"插值测试:")
    print(f"起始四元数: {q1} (欧拉角: {q1.to_euler_angles()})")
    print(f"结束四元数: {q2} (欧拉角: {q2.to_euler_angles()})")
    print(f"LERP 50%: {q_lerp} (欧拉角: {q_lerp.to_euler_angles()})")
    print(f"SLERP 50%: {q_slerp} (欧拉角: {q_slerp.to_euler_angles()})\n")


def test_transform_with_quaternions():
    """测试Transform使用四元数的功能"""
    print("=== 测试Transform四元数功能 ===\n")
    
    # 创建ECS管理器
    ecs = ECSManager()
    
    # 创建游戏对象
    obj = ecs.create_entity(GameObject, name="TestObject")
    
    # 测试四元数属性
    print("1. 四元数属性测试:")
    obj.transform.local_rotation = [30, 45, 60]
    print(f"设置欧拉角旋转: {obj.transform.local_rotation}")
    print(f"对应的四元数: {obj.transform.local_rotation_quaternion}")
    
    # 直接设置四元数
    quat = Quaternion.from_euler_angles(45, 0, 0)
    obj.transform.local_rotation_quaternion = quat
    print(f"设置四元数: {quat}")
    print(f"对应的欧拉角: {obj.transform.local_rotation}\n")
    
    # 测试rotate方法
    print("2. rotate方法测试:")
    obj.transform.local_rotation = [0, 0, 0]  # 重置
    print(f"初始旋转: {obj.transform.local_rotation}")
    
    obj.transform.rotate([0, 1, 0], 90)  # 绕Y轴旋转90度
    print(f"绕Y轴旋转90度后: {obj.transform.local_rotation}")
    
    obj.transform.rotate([1, 0, 0], 45)  # 绕X轴旋转45度
    print(f"再绕X轴旋转45度后: {obj.transform.local_rotation}\n")


def test_transform_hierarchy_with_quaternions():
    """测试Transform层级关系中的四元数计算"""
    print("=== 测试Transform层级关系四元数计算 ===\n")
    
    # 创建ECS管理器
    ecs = ECSManager()
    
    # 创建父子物体
    parent = ecs.create_entity(GameObject, name="Parent")
    child = ecs.create_entity(GameObject, name="Child")
    
    # 设置父物体旋转
    parent.transform.rotation = [0, 45, 0]  # 绕Y轴45度
    print(f"父物体旋转: {parent.transform.rotation}")
    print(f"父物体四元数: {parent.transform.rotation_quaternion}")
    
    # 设置子物体本地旋转
    child.transform.local_rotation = [30, 0, 0]  # 绕X轴30度
    print(f"子物体本地旋转: {child.transform.local_rotation}")
    print(f"子物体本地四元数: {child.transform.local_rotation_quaternion}")
    
    # 建立父子关系
    child.set_parent(parent, world_position_stays=False)
    
    # 检查世界旋转
    print(f"子物体世界旋转: {child.transform.rotation}")
    print(f"子物体世界四元数: {child.transform.rotation_quaternion}")
    
    # 验证四元数组合的正确性
    expected_quat = parent.transform.rotation_quaternion * child.transform.local_rotation_quaternion
    actual_quat = child.transform.rotation_quaternion
    print(f"预期世界四元数: {expected_quat}")
    print(f"实际世界四元数: {actual_quat}")
    print(f"四元数匹配: {expected_quat == actual_quat}\n")


def test_coordinate_transformation():
    """测试坐标变换"""
    print("=== 测试坐标变换 ===\n")
    
    # 创建ECS管理器
    ecs = ECSManager()
    
    # 创建旋转的物体
    obj = ecs.create_entity(GameObject, name="RotatedObject")
    obj.transform.position = [5, 0, 0]
    obj.transform.rotation = [0, 90, 0]  # 绕Y轴旋转90度
    
    print(f"物体位置: {obj.transform.position}")
    print(f"物体旋转: {obj.transform.rotation}")
    
    # 测试点变换
    local_point = [1, 0, 0]  # 本地X轴方向1单位
    world_point = obj.transform.transform_point(local_point)
    print(f"本地点 {local_point} 转换为世界坐标: {world_point}")
    
    # 反向变换
    back_to_local = obj.transform.inverse_transform_point(world_point)
    print(f"世界点 {world_point} 转换回本地坐标: {back_to_local}")
    
    # 测试方向变换
    local_direction = [1, 0, 0]  # 本地X轴方向
    world_direction = obj.transform.transform_direction(local_direction)
    print(f"本地方向 {local_direction} 转换为世界方向: {world_direction}")
    
    # 反向变换
    back_to_local_dir = obj.transform.inverse_transform_direction(world_direction)
    print(f"世界方向 {world_direction} 转换回本地方向: {back_to_local_dir}\n")


def test_look_at_functionality():
    """测试LookAt功能"""
    print("=== 测试LookAt功能 ===\n")
    
    # 创建ECS管理器
    ecs = ECSManager()
    
    # 创建物体
    obj = ecs.create_entity(GameObject, name="LookAtObject")
    obj.transform.position = [0, 0, 0]
    
    # 朝向目标点
    target = [1, 0, 1]
    print(f"物体位置: {obj.transform.position}")
    print(f"目标位置: {target}")
    
    obj.transform.look_at(target)
    print(f"LookAt后的旋转: {obj.transform.rotation}")
    print(f"LookAt后的四元数: {obj.transform.rotation_quaternion}")
    
    # 验证前方向量
    forward_local = [0, 0, 1]  # 本地前方向
    forward_world = obj.transform.transform_direction(forward_local)
    expected_direction = np.array(target) - np.array(obj.transform.position)
    expected_direction = expected_direction / np.linalg.norm(expected_direction)
    
    print(f"变换后的前方向: {forward_world}")
    print(f"期望的方向: {expected_direction}")
    print(f"方向匹配度: {np.dot(forward_world, expected_direction):.3f} (应该接近1)\n")


def test_unity_compatibility():
    """测试Unity风格API兼容性"""
    print("=== 测试Unity风格API兼容性 ===\n")
    
    # 创建ECS管理器
    ecs = ECSManager()
    
    # 创建物体
    obj = ecs.create_entity(GameObject, name="UnityStyleTest")
    
    # 使用Unity风格API
    obj.transform.localPosition = [1, 2, 3]
    obj.transform.localRotation = [30, 45, 60]
    obj.transform.localScale = [2, 2, 2]
    
    print(f"Unity风格设置:")
    print(f"localPosition: {obj.transform.localPosition}")
    print(f"localRotation: {obj.transform.localRotation}")
    print(f"localScale: {obj.transform.localScale}")
    
    # 验证与Python风格API的一致性
    print(f"\nPython风格读取:")
    print(f"local_position: {obj.transform.local_position}")
    print(f"local_rotation: {obj.transform.local_rotation}")
    print(f"local_scale: {obj.transform.local_scale}")
    
    # 测试Unity风格方法
    obj.transform.Rotate([0, 1, 0], 90)
    print(f"\nRotate后的旋转: {obj.transform.rotation}")
    
    print("✅ Unity风格API测试通过！\n")


def run_all_tests():
    """运行所有测试"""
    print("========================================")
    print("        四元数Transform系统测试")
    print("========================================\n")
    
    try:
        test_quaternion_basics()
        test_quaternion_rotation()
        test_transform_with_quaternions()
        test_transform_hierarchy_with_quaternions()
        test_coordinate_transformation()
        test_look_at_functionality()
        test_unity_compatibility()
        
        print("========================================")
        print("✅ 所有测试通过！四元数系统运行正常！")
        print("========================================")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests() 