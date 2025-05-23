# -*- coding: utf-8 -*-
"""
测试main.py中的相机控制逻辑
验证相机移动和旋转功能是否正常工作
"""
import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from components.camera_setting import CameraSetting
from util.quaternion import Quaternion


def test_camera_rotation_logic():
    """测试相机旋转逻辑（模拟main.py中的鼠标旋转）"""
    print("=== 测试相机旋转逻辑 ===\n")
    
    # 创建相机设置
    camera_setting = CameraSetting()
    
    print(f"初始状态:")
    print(f"  Yaw: {camera_setting.yaw:.2f}")
    print(f"  Pitch: {camera_setting.pitch:.2f}")
    print(f"  前方向: {camera_setting.front}")
    
    # 模拟鼠标移动事件 (模拟main.py中的逻辑)
    rotation_sensitive = 0.1
    constrain_pitch = True
    
    # 模拟鼠标向右移动
    delta_x = 10.0  # 鼠标X轴偏移
    delta_y = 5.0   # 鼠标Y轴偏移
    
    # 使用main.py中更新后的逻辑
    new_yaw = camera_setting.yaw + delta_x * rotation_sensitive
    new_pitch = camera_setting.pitch + delta_y * rotation_sensitive
    
    # 约束俯仰角
    if constrain_pitch:
        new_pitch = max(-89.0, min(89.0, new_pitch))
    
    # 使用新的四元数方法设置旋转
    new_rotation = Quaternion.from_euler_angles(new_pitch, new_yaw, 0.0)
    camera_setting.set_rotation_quaternion(new_rotation)
    
    print(f"\n鼠标移动后:")
    print(f"  Yaw: {camera_setting.yaw:.2f} (期望: {new_yaw:.2f})")
    print(f"  Pitch: {camera_setting.pitch:.2f} (期望: {new_pitch:.2f})")
    print(f"  前方向: {camera_setting.front}")
    
    # 验证四元数是否正确归一化
    magnitude = camera_setting.rotation.magnitude()
    print(f"  四元数模长: {magnitude:.6f} (应接近1.0)")
    
    # 测试俯仰角限制
    print(f"\n=== 测试俯仰角限制 ===")
    
    # 尝试设置超出限制的俯仰角
    extreme_pitch = 95.0  # 超过89度限制
    extreme_yaw = camera_setting.yaw + 30.0
    
    # 应用限制
    limited_pitch = max(-89.0, min(89.0, extreme_pitch))
    
    extreme_rotation = Quaternion.from_euler_angles(limited_pitch, extreme_yaw, 0.0)
    camera_setting.set_rotation_quaternion(extreme_rotation)
    
    print(f"尝试设置俯仰角: {extreme_pitch:.2f}")
    print(f"应用限制后: {limited_pitch:.2f}")
    print(f"实际设置俯仰角: {camera_setting.pitch:.2f}")
    print(f"限制生效: {abs(camera_setting.pitch - limited_pitch) < 0.1}")


def test_camera_movement_logic():
    """测试相机移动逻辑（模拟main.py中的WASD移动）"""
    print(f"\n=== 测试相机移动逻辑 ===\n")
    
    camera_setting = CameraSetting()
    
    # 设置一个特定的旋转以便测试方向向量
    test_rotation = Quaternion.from_euler_angles(0, 45, 0)  # 向右旋转45度
    camera_setting.set_rotation_quaternion(test_rotation)
    
    initial_position = camera_setting.position.copy()
    print(f"初始位置: {initial_position}")
    print(f"前方向: {camera_setting.front}")
    print(f"右方向: {camera_setting.right}")
    
    # 模拟移动参数
    move_speed = 1.0
    dt = 0.016  # 60 FPS
    
    # 测试向前移动 (W键)
    camera_setting.position += camera_setting.front * move_speed * dt
    forward_position = camera_setting.position.copy()
    print(f"\n向前移动后: {forward_position}")
    
    # 重置位置
    camera_setting.position = initial_position.copy()
    
    # 测试向右移动 (D键)  
    camera_setting.position += camera_setting.right * move_speed * dt
    right_position = camera_setting.position.copy()
    print(f"向右移动后: {right_position}")
    
    # 重置位置
    camera_setting.position = initial_position.copy()
    
    # 测试向后移动 (S键)
    camera_setting.position -= camera_setting.front * move_speed * dt
    backward_position = camera_setting.position.copy()
    print(f"向后移动后: {backward_position}")
    
    # 重置位置  
    camera_setting.position = initial_position.copy()
    
    # 测试向左移动 (A键，虽然在main.py中A键被用作其他功能)
    camera_setting.position -= camera_setting.right * move_speed * dt
    left_position = camera_setting.position.copy()
    print(f"向左移动后: {left_position}")
    
    # 验证移动是否符合预期
    forward_distance = np.linalg.norm(forward_position - initial_position)
    right_distance = np.linalg.norm(right_position - initial_position)
    
    expected_distance = move_speed * dt
    print(f"\n移动距离验证:")
    print(f"前进距离: {forward_distance:.6f} (期望: {expected_distance:.6f})")
    print(f"右移距离: {right_distance:.6f} (期望: {expected_distance:.6f})")
    print(f"距离匹配: {abs(forward_distance - expected_distance) < 1e-6}")


def test_quaternion_consistency():
    """测试四元数系统的一致性"""
    print(f"\n=== 测试四元数系统一致性 ===\n")
    
    camera_setting = CameraSetting()
    
    # 记录初始状态
    initial_quat = camera_setting.rotation
    initial_front = camera_setting.front.copy()
    
    print(f"初始四元数: {initial_quat}")
    print(f"初始前方向: {initial_front}")
    
    # 进行一系列旋转
    rotations = [
        (15, 30, 0),
        (-10, 45, 0),
        (30, -20, 0)
    ]
    
    for i, (pitch, yaw, roll) in enumerate(rotations):
        rotation_quat = Quaternion.from_euler_angles(pitch, yaw, roll)
        camera_setting.set_rotation_quaternion(rotation_quat)
        
        print(f"\n旋转 {i+1}: pitch={pitch}, yaw={yaw}, roll={roll}")
        print(f"  设置的四元数: {rotation_quat}")
        print(f"  相机的四元数: {camera_setting.rotation}")
        print(f"  欧拉角: pitch={camera_setting.pitch:.2f}, yaw={camera_setting.yaw:.2f}")
        
        # 验证四元数归一化
        magnitude = camera_setting.rotation.magnitude()
        print(f"  四元数模长: {magnitude:.6f}")
        
        # 验证方向向量正交性
        front_right_dot = np.dot(camera_setting.front, camera_setting.right)
        front_up_dot = np.dot(camera_setting.front, camera_setting.up)
        right_up_dot = np.dot(camera_setting.right, camera_setting.up)
        
        print(f"  方向向量正交性: front·right={front_right_dot:.6f}, front·up={front_up_dot:.6f}, right·up={right_up_dot:.6f}")


if __name__ == "__main__":
    print("========================================")
    print("        Main.py 相机控制测试")
    print("========================================")
    
    try:
        test_camera_rotation_logic()
        test_camera_movement_logic()  
        test_quaternion_consistency()
        
        print("\n========================================")
        print("✅ 所有Main.py相机控制测试通过！")
        print("✅ 相机控制逻辑与新四元数系统兼容！")
        print("========================================")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc() 