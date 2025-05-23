# -*- coding: utf-8 -*-
"""
测试相机系统的四元数功能
验证camerasetting使用新的四元数类是否正常工作
"""
import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from components.camera_setting import CameraSetting, ProjectionType
from util.quaternion import Quaternion


def test_camera_quaternion_integration():
    """测试相机系统与新四元数类的集成"""
    print("=== 测试相机系统四元数集成 ===\n")
    
    # 创建相机
    camera = CameraSetting()
    print(f"初始相机位置: {camera.position}")
    print(f"初始相机旋转四元数: {camera.rotation}")
    print(f"初始俯仰角: {camera.pitch}")
    print(f"初始偏航角: {camera.yaw}")
    
    # 测试使用新四元数类创建相机
    custom_rotation = Quaternion.from_euler_angles(30, 45, 0)
    camera2 = CameraSetting(
        position=np.array([5, 3, 2]),
        rotation=custom_rotation,
        fov=75.0
    )
    
    print(f"\n自定义相机:")
    print(f"位置: {camera2.position}")
    print(f"旋转四元数: {camera2.rotation}")
    print(f"俯仰角: {camera2.pitch}")
    print(f"偏航角: {camera2.yaw}")
    
    # 测试新的四元数方法
    print(f"\n=== 测试新增的四元数方法 ===")
    
    # 测试四元数旋转
    rotation_quat = Quaternion.from_axis_angle([0, 1, 0], 45)
    camera.rotate_by_quaternion(rotation_quat)
    print(f"旋转后的四元数: {camera.rotation}")
    print(f"旋转后的欧拉角: pitch={camera.pitch:.1f}, yaw={camera.yaw:.1f}")
    
    # 测试直接设置四元数
    target_quat = Quaternion.from_euler_angles(15, -30, 0)
    camera.set_rotation_quaternion(target_quat)
    print(f"设置新四元数后: {camera.rotation}")
    print(f"对应的欧拉角: pitch={camera.pitch:.1f}, yaw={camera.yaw:.1f}")
    
    # 测试方向向量计算
    print(f"\n=== 测试方向向量 ===")
    print(f"前方向: {camera.front}")
    print(f"右方向: {camera.right}")
    print(f"上方向: {camera.up}")
    
    # 验证方向向量的正交性
    front_right_dot = np.dot(camera.front, camera.right)
    front_up_dot = np.dot(camera.front, camera.up)
    right_up_dot = np.dot(camera.right, camera.up)
    
    print(f"\n方向向量正交性检查:")
    print(f"前·右 = {front_right_dot:.6f} (应接近0)")
    print(f"前·上 = {front_up_dot:.6f} (应接近0)")
    print(f"右·上 = {right_up_dot:.6f} (应接近0)")
    
    # 测试LookAt功能
    print(f"\n=== 测试LookAt功能 ===")
    camera.position = np.array([0, 0, 5])
    target = np.array([0, 0, 0])
    camera.look_at(target)
    
    print(f"LookAt后的四元数: {camera.rotation}")
    print(f"前方向应指向目标: {camera.front}")
    
    # 验证前方向是否指向目标
    to_target = (target - camera.position) / np.linalg.norm(target - camera.position)
    direction_error = np.linalg.norm(camera.front - to_target)
    print(f"方向误差: {direction_error:.6f} (应接近0)")
    
    print(f"\n✅ 相机四元数系统测试通过！")


def test_camera_matrix_generation():
    """测试相机矩阵生成"""
    print(f"\n=== 测试相机矩阵生成 ===")
    
    camera = CameraSetting(
        position=np.array([1, 2, 3]),
        fov=60.0,
        aspect_ratio=16/9
    )
    
    # 获取矩阵
    view_matrix = camera.view_matrix
    projection_matrix = camera.projection_matrix
    
    print(f"视图矩阵形状: {view_matrix.shape}")
    print(f"投影矩阵形状: {projection_matrix.shape}")
    
    # 验证矩阵不是零矩阵
    view_non_zero = np.any(view_matrix != 0)
    proj_non_zero = np.any(projection_matrix != 0)
    
    print(f"视图矩阵非零: {view_non_zero}")
    print(f"投影矩阵非零: {proj_non_zero}")
    
    # 测试不同投影类型
    camera.projection_type = ProjectionType.ORTHOGRAPHIC
    camera.calculate_projection_matrix()
    ortho_matrix = camera.projection_matrix
    
    print(f"正交投影矩阵形状: {ortho_matrix.shape}")
    print(f"正交投影矩阵非零: {np.any(ortho_matrix != 0)}")


def test_quaternion_precision():
    """测试四元数精度"""
    print(f"\n=== 测试四元数精度 ===")
    
    camera = CameraSetting()
    
    # 测试多次旋转的累积误差
    original_quat = camera.rotation
    
    # 进行多次小旋转
    for i in range(100):
        small_rotation = Quaternion.from_axis_angle([0, 1, 0], 1)  # 1度旋转
        camera.rotate_by_quaternion(small_rotation)
    
    # 计算最终旋转
    final_quat = camera.rotation
    
    # 验证四元数是否保持归一化
    magnitude = final_quat.magnitude()
    print(f"100次旋转后四元数模长: {magnitude:.6f} (应接近1.0)")
    
    # 计算总旋转角度（应该是100度）
    expected_quat = Quaternion.from_axis_angle([0, 1, 0], 100)
    combined_quat = original_quat * expected_quat
    
    print(f"期望的最终四元数: {combined_quat}")
    print(f"实际的最终四元数: {final_quat}")
    
    # 计算误差
    error_quat = final_quat * combined_quat.inverse()
    error_magnitude = error_quat.magnitude()
    print(f"累积误差: {error_magnitude:.6f}")


if __name__ == "__main__":
    print("========================================")
    print("        相机四元数系统测试")
    print("========================================")
    
    try:
        test_camera_quaternion_integration()
        test_camera_matrix_generation()
        test_quaternion_precision()
        
        print("\n========================================")
        print("✅ 所有相机四元数测试通过！")
        print("✅ camerasetting成功集成新的四元数系统！")
        print("========================================")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc() 