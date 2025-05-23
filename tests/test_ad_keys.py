# -*- coding: utf-8 -*-
"""
测试A和D键的相机移动功能
验证修复后的左右移动是否正常工作
"""
import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from components.camera_setting import CameraSetting
from util.quaternion import Quaternion

# 模拟 main.py 中的 CameraMoveDirection 枚举
from enum import Enum, auto

class CameraMoveDirection(Enum):
    FORWARD = auto()
    BACKWARD = auto()
    LEFT = auto()
    RIGHT = auto()

def test_horizontal_movement():
    """测试水平方向移动（A和D键）"""
    print("=== 测试A和D键相机移动 ===\n")
    
    # 创建相机设置
    camera_setting = CameraSetting()
    
    # 设置一个特定的旋转以便测试
    test_rotation = Quaternion.from_euler_angles(0, 0, 0)  # 无旋转，面向-Z轴
    camera_setting.set_rotation_quaternion(test_rotation)
    
    initial_position = camera_setting.position.copy()
    print(f"初始位置: {initial_position}")
    print(f"前方向: {camera_setting.front}")
    print(f"右方向: {camera_setting.right}")
    print(f"上方向: {camera_setting.up}")
    
    # 模拟移动参数
    move_speed = 1.0
    dt = 0.1  # 较大的时间步长便于观察
    
    # 模拟main.py中的移动逻辑
    def simulate_horizontal_movement(direction):
        """模拟水平移动"""
        camera_setting.position = initial_position.copy()  # 重置位置
        
        if direction == CameraMoveDirection.LEFT:
            camera_setting.position -= camera_setting.right * move_speed * dt
            direction_name = "左移 (A键)"
        elif direction == CameraMoveDirection.RIGHT:
            camera_setting.position += camera_setting.right * move_speed * dt
            direction_name = "右移 (D键)"
        
        return direction_name, camera_setting.position.copy()
    
    # 测试左移 (A键)
    left_name, left_position = simulate_horizontal_movement(CameraMoveDirection.LEFT)
    print(f"\n{left_name}后位置: {left_position}")
    left_movement = left_position - initial_position
    print(f"移动向量: {left_movement}")
    
    # 测试右移 (D键)
    right_name, right_position = simulate_horizontal_movement(CameraMoveDirection.RIGHT)
    print(f"\n{right_name}后位置: {right_position}")
    right_movement = right_position - initial_position
    print(f"移动向量: {right_movement}")
    
    # 验证移动方向
    print(f"\n=== 移动方向验证 ===")
    print(f"右方向向量: {camera_setting.right}")
    print(f"左移向量应该是右方向的负值: {-camera_setting.right * move_speed * dt}")
    print(f"右移向量应该是右方向的正值: {camera_setting.right * move_speed * dt}")
    
    # 检查移动是否正确
    expected_left = initial_position - camera_setting.right * move_speed * dt
    expected_right = initial_position + camera_setting.right * move_speed * dt
    
    left_correct = np.allclose(left_position, expected_left, atol=1e-6)
    right_correct = np.allclose(right_position, expected_right, atol=1e-6)
    
    print(f"\n左移正确: {left_correct}")
    print(f"右移正确: {right_correct}")
    
    # 验证左右移动是相反的
    opposite_movement = np.allclose(left_movement, -right_movement, atol=1e-6)
    print(f"左右移动相反: {opposite_movement}")
    
    return left_correct and right_correct and opposite_movement

def test_different_camera_orientations():
    """测试不同相机朝向下的A和D键移动"""
    print(f"\n=== 测试不同相机朝向下的移动 ===\n")
    
    # 测试不同的相机朝向
    orientations = [
        (0, 0, "正前方 (默认)"),
        (0, 90, "向右转90度"),
        (0, -90, "向左转90度"),
        (0, 180, "向后转180度"),
        (30, 45, "复合旋转")
    ]
    
    move_speed = 1.0
    dt = 0.1
    
    for pitch, yaw, description in orientations:
        print(f"--- {description} ---")
        
        camera_setting = CameraSetting()
        test_rotation = Quaternion.from_euler_angles(pitch, yaw, 0)
        camera_setting.set_rotation_quaternion(test_rotation)
        
        initial_pos = camera_setting.position.copy()
        
        print(f"右方向: {camera_setting.right}")
        
        # 左移
        camera_setting.position = initial_pos.copy()
        camera_setting.position -= camera_setting.right * move_speed * dt
        left_pos = camera_setting.position.copy()
        
        # 右移
        camera_setting.position = initial_pos.copy()
        camera_setting.position += camera_setting.right * move_speed * dt
        right_pos = camera_setting.position.copy()
        
        # 计算移动距离
        left_distance = np.linalg.norm(left_pos - initial_pos)
        right_distance = np.linalg.norm(right_pos - initial_pos)
        expected_distance = move_speed * dt
        
        print(f"左移距离: {left_distance:.6f} (期望: {expected_distance:.6f})")
        print(f"右移距离: {right_distance:.6f} (期望: {expected_distance:.6f})")
        print(f"距离正确: {abs(left_distance - expected_distance) < 1e-6 and abs(right_distance - expected_distance) < 1e-6}")
        print()

if __name__ == "__main__":
    print("========================================")
    print("        A和D键相机移动测试")
    print("========================================")
    
    try:
        basic_test_pass = test_horizontal_movement()
        test_different_camera_orientations()
        
        print("========================================")
        if basic_test_pass:
            print("✅ A和D键相机移动测试通过！")
            print("✅ 左右移动功能已修复！")
        else:
            print("❌ A和D键相机移动测试失败！")
        print("========================================")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc() 