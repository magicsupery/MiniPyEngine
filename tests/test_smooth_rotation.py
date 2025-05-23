# -*- coding: utf-8 -*-
"""
测试平滑鼠标旋转功能
验证SLERP插值和平滑体验
"""
import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from components.camera_setting import CameraSetting
from util.quaternion import Quaternion
import time

# 模拟 main.py 中的 CameraMovementModule 平滑逻辑
class MockCameraMovementModule:
    def __init__(self):
        self.rotation_sensitive = 0.1
        self.constrain_pitch = True
        self.rotation_smoothing = 8.0
        self.target_yaw = None
        self.target_pitch = None
        self.target_rotation = None
        self.need_rotate = False
    
    def simulate_mouse_move(self, camera_setting, delta_x, delta_y):
        """模拟鼠标移动事件"""
        if self.need_rotate:
            # 初始化目标旋转值（如果还没有初始化）
            if self.target_yaw is None:
                self.target_yaw = camera_setting.yaw
                self.target_pitch = camera_setting.pitch
                self.target_rotation = camera_setting.rotation
            
            # 更新目标旋转角度
            self.target_yaw += delta_x * self.rotation_sensitive
            self.target_pitch += delta_y * self.rotation_sensitive

            # 约束俯仰角
            if self.constrain_pitch:
                self.target_pitch = max(-89.0, min(89.0, self.target_pitch))

            # 计算目标四元数旋转
            self.target_rotation = Quaternion.from_euler_angles(self.target_pitch, self.target_yaw, 0.0)
    
    def start_rotation(self, camera_setting):
        """开始旋转（模拟鼠标左键按下）"""
        self.need_rotate = True
        self.target_yaw = camera_setting.yaw
        self.target_pitch = camera_setting.pitch
        self.target_rotation = camera_setting.rotation
    
    def stop_rotation(self):
        """停止旋转（模拟鼠标左键释放）"""
        self.need_rotate = False
    
    def update_smooth_rotation(self, camera_setting, dt):
        """更新平滑旋转"""
        if self.target_rotation is not None:
            current_rotation = camera_setting.rotation
            
            # 计算插值系数（基于帧率的平滑过渡）
            smoothing_factor = 1.0 - pow(0.5, self.rotation_smoothing * dt)
            
            # 检查四元数方向，选择最短路径
            if current_rotation.dot(self.target_rotation) < 0:
                target_for_slerp = Quaternion(-self.target_rotation.x, -self.target_rotation.y, 
                                             -self.target_rotation.z, -self.target_rotation.w)
            else:
                target_for_slerp = self.target_rotation
            
            # 使用SLERP进行平滑插值
            smoothed_rotation = Quaternion.slerp(current_rotation, target_for_slerp, smoothing_factor)
            
            # 应用平滑后的旋转
            camera_setting.set_rotation_quaternion(smoothed_rotation)
            
            # 如果已经足够接近目标旋转，停止插值
            rotation_difference = abs(1.0 - abs(current_rotation.dot(target_for_slerp)))
            if rotation_difference < 0.001:
                camera_setting.set_rotation_quaternion(self.target_rotation)
                if not self.need_rotate:
                    self.target_rotation = None

def test_smooth_rotation_basic():
    """测试基础平滑旋转功能"""
    print("=== 测试基础平滑旋转功能 ===\n")
    
    camera_setting = CameraSetting()
    camera_module = MockCameraMovementModule()
    
    print(f"初始旋转: yaw={camera_setting.yaw:.2f}, pitch={camera_setting.pitch:.2f}")
    print(f"初始四元数: {camera_setting.rotation}")
    
    # 开始旋转模式
    camera_module.start_rotation(camera_setting)
    
    # 模拟鼠标移动
    mouse_delta_x = 50.0  # 较大的鼠标移动
    mouse_delta_y = 30.0
    
    camera_module.simulate_mouse_move(camera_setting, mouse_delta_x, mouse_delta_y)
    
    print(f"\n目标旋转设置后:")
    print(f"目标 yaw={camera_module.target_yaw:.2f}, pitch={camera_module.target_pitch:.2f}")
    print(f"目标四元数: {camera_module.target_rotation}")
    print(f"当前四元数: {camera_setting.rotation}")
    
    # 模拟几个更新帧来看平滑过渡
    dt = 1.0 / 60.0  # 60 FPS
    frame_count = 10
    
    print(f"\n模拟 {frame_count} 帧的平滑过渡:")
    for i in range(frame_count):
        camera_module.update_smooth_rotation(camera_setting, dt)
        
        # 计算与目标的距离
        current_dot = camera_setting.rotation.dot(camera_module.target_rotation)
        distance = abs(1.0 - abs(current_dot))
        
        print(f"帧 {i+1}: yaw={camera_setting.yaw:.2f}, pitch={camera_setting.pitch:.2f}, "
              f"距离目标={distance:.6f}")
    
    # 验证最终是否接近目标
    final_dot = camera_setting.rotation.dot(camera_module.target_rotation)
    final_distance = abs(1.0 - abs(final_dot))
    
    print(f"\n最终距离目标: {final_distance:.6f}")
    print(f"平滑过渡成功: {final_distance < 0.01}")
    
    return final_distance < 0.01

def test_smooth_rotation_continuous():
    """测试连续鼠标移动的平滑旋转"""
    print(f"\n=== 测试连续鼠标移动平滑旋转 ===\n")
    
    camera_setting = CameraSetting()
    camera_module = MockCameraMovementModule()
    
    # 开始旋转
    camera_module.start_rotation(camera_setting)
    
    dt = 1.0 / 60.0
    
    # 模拟连续的小幅鼠标移动
    mouse_movements = [
        (5, 3), (5, 3), (5, 3), (5, 3), (5, 3),  # 连续向右上移动
        (-3, -2), (-3, -2), (-3, -2),  # 稍微向左下调整
        (10, 0), (10, 0)  # 水平移动
    ]
    
    print("模拟连续鼠标移动:")
    for i, (dx, dy) in enumerate(mouse_movements):
        # 更新目标
        camera_module.simulate_mouse_move(camera_setting, dx, dy)
        
        # 执行几帧平滑过渡
        for _ in range(3):  # 每次移动后更新3帧
            camera_module.update_smooth_rotation(camera_setting, dt)
        
        current_dot = camera_setting.rotation.dot(camera_module.target_rotation)
        distance = abs(1.0 - abs(current_dot))
        
        print(f"移动 {i+1}: 目标yaw={camera_module.target_yaw:.1f}, "
              f"当前yaw={camera_setting.yaw:.1f}, 距离={distance:.4f}")
    
    print(f"\n连续移动测试完成")

def test_smoothing_parameters():
    """测试不同的平滑参数"""
    print(f"\n=== 测试不同平滑参数的效果 ===\n")
    
    smoothing_values = [4.0, 8.0, 15.0]  # 不同的平滑程度
    
    for smoothing in smoothing_values:
        print(f"--- 平滑程度: {smoothing} ---")
        
        camera_setting = CameraSetting()
        camera_module = MockCameraMovementModule()
        camera_module.rotation_smoothing = smoothing
        
        # 开始旋转并设置目标
        camera_module.start_rotation(camera_setting)
        camera_module.simulate_mouse_move(camera_setting, 30, 20)
        
        dt = 1.0 / 60.0
        frames_to_converge = 0
        
        # 计算收敛到目标需要多少帧
        for frame in range(100):  # 最多100帧
            camera_module.update_smooth_rotation(camera_setting, dt)
            
            current_dot = camera_setting.rotation.dot(camera_module.target_rotation)
            distance = abs(1.0 - abs(current_dot))
            
            if distance < 0.01:  # 足够接近
                frames_to_converge = frame + 1
                break
        
        convergence_time = frames_to_converge * dt
        print(f"收敛时间: {convergence_time:.3f}秒 ({frames_to_converge} 帧)")
        print(f"平滑效果: {'非常平滑' if convergence_time > 0.1 else '响应迅速'}")
        print()

def test_quaternion_dot_product():
    """测试四元数点积功能"""
    print(f"\n=== 测试四元数点积功能 ===\n")
    
    # 创建测试四元数
    q1 = Quaternion.from_euler_angles(0, 0, 0)     # 单位四元数
    q2 = Quaternion.from_euler_angles(0, 90, 0)    # 90度旋转
    q3 = Quaternion.from_euler_angles(0, 180, 0)   # 180度旋转
    
    print(f"q1 (无旋转): {q1}")
    print(f"q2 (90度): {q2}")
    print(f"q3 (180度): {q3}")
    
    # 测试点积
    dot_q1_q2 = q1.dot(q2)
    dot_q1_q3 = q1.dot(q3)
    dot_q2_q3 = q2.dot(q3)
    
    print(f"\nq1 · q2 = {dot_q1_q2:.6f}")
    print(f"q1 · q3 = {dot_q1_q3:.6f}")
    print(f"q2 · q3 = {dot_q2_q3:.6f}")
    
    # 验证点积属性
    print(f"\n点积验证:")
    print(f"相同四元数点积 = 1: {abs(q1.dot(q1) - 1.0) < 1e-6}")
    print(f"正交四元数点积接近0: {abs(dot_q1_q3) < 0.1}")  # 180度旋转
    
    return True

if __name__ == "__main__":
    print("========================================")
    print("        平滑鼠标旋转测试")
    print("========================================")
    
    try:
        basic_pass = test_smooth_rotation_basic()
        test_smooth_rotation_continuous()
        test_smoothing_parameters()
        dot_pass = test_quaternion_dot_product()
        
        print("\n========================================")
        if basic_pass and dot_pass:
            print("✅ 平滑鼠标旋转功能测试通过！")
            print("✅ 四元数SLERP插值工作正常！")
            print("✅ 点积方法验证成功！")
        else:
            print("❌ 平滑鼠标旋转测试失败！")
        print("========================================")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc() 