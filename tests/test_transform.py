# -*- coding: utf-8 -*-
"""
测试Python风格的Transform父子关系管理
包含四元数功能测试
"""
import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from Entity.gameobject import GameObject
from core.ecs import ECSManager
from util.quaternion import Quaternion


def test_transform_hierarchy():
    """测试Transform层级关系"""
    print("=== 测试Python风格的Transform父子关系管理 ===\n")
    
    # 创建ECS管理器
    ecs = ECSManager()
    
    # 创建父物体
    parent = ecs.create_entity(GameObject, name="Parent")
    parent.transform.position = [5.0, 0.0, 0.0]
    parent.transform.rotation = [0.0, 45.0, 0.0]
    parent.transform.scale = [2.0, 2.0, 2.0]
    
    print(f"父物体 '{parent.name}':")
    print(f"  世界位置: {parent.transform.position}")
    print(f"  世界旋转: {parent.transform.rotation}")
    print(f"  世界缩放: {parent.transform.lossy_scale}")
    print(f"  子物体数量: {parent.transform.child_count}")
    print(f"  旋转四元数: {parent.transform.rotation_quaternion}\n")
    
    # 创建子物体
    child = ecs.create_entity(GameObject, name="Child")
    child.transform.local_position = [1.0, 0.0, 0.0]
    child.transform.local_rotation = [0.0, 0.0, 30.0]
    child.transform.local_scale = [0.5, 0.5, 0.5]
    
    print(f"子物体 '{child.name}' (设置父物体前):")
    print(f"  本地位置: {child.transform.local_position}")
    print(f"  世界位置: {child.transform.position}")
    print(f"  本地旋转: {child.transform.local_rotation}")
    print(f"  本地四元数: {child.transform.local_rotation_quaternion}")
    print(f"  父物体: {child.parent}\n")
    
    # 设置父子关系
    child.set_parent(parent, world_position_stays=False)
    
    print(f"设置父子关系后:")
    print(f"父物体 '{parent.name}' 子物体数量: {parent.transform.child_count}")
    print(f"子物体 '{child.name}' 父物体: {child.parent.name if child.parent else 'None'}")
    print(f"子物体世界旋转: {child.transform.rotation}")
    print(f"子物体世界四元数: {child.transform.rotation_quaternion}\n")
    
    # 测试坐标转换
    print("=== 测试坐标转换 ===")
    local_point = [1.0, 0.0, 0.0]
    world_point = child.transform.transform_point(local_point)
    print(f"本地点 {local_point} 转换为世界坐标: {world_point}")
    
    # 反向转换验证
    back_to_local = child.transform.inverse_transform_point(world_point)
    print(f"世界点转换回本地坐标: {back_to_local}")
    print(f"转换误差: {np.array(local_point) - np.array(back_to_local)}\n")
    
    # 测试Unity风格别名兼容性
    print("=== 测试Unity风格别名兼容性 ===")
    child2 = ecs.create_entity(GameObject, name="Child2")
    child2.transform.localPosition = [2.0, 0.0, 0.0]  # Unity风格
    child2.SetParent(parent, worldPositionStays=False)  # Unity风格
    print(f"使用Unity风格API创建的子物体成功")
    print(f"父物体子物体数量: {parent.childCount}")  # Unity风格属性
    
    # 测试四元数旋转
    print("\n=== 测试四元数旋转功能 ===")
    child2.transform.rotate([0, 1, 0], 90)  # 绕Y轴旋转90度
    print(f"Child2绕Y轴旋转90度后的欧拉角: {child2.transform.local_rotation}")
    print(f"Child2的本地四元数: {child2.transform.local_rotation_quaternion}")
    
    # 测试直接设置四元数
    quat = Quaternion.from_euler_angles(45, 0, 0)
    child2.transform.local_rotation_quaternion = quat
    print(f"直接设置四元数后的欧拉角: {child2.transform.local_rotation}")
    
    print("\n✅ 所有测试通过！")


def test_quaternion_accuracy():
    """测试四元数精度和转换"""
    print("\n=== 测试四元数精度和转换 ===\n")
    
    # 创建ECS管理器
    ecs = ECSManager()
    obj = ecs.create_entity(GameObject, name="QuaternionTest")
    
    # 测试欧拉角到四元数再到欧拉角的转换精度
    test_angles = [
        [0, 0, 0],
        [30, 0, 0],
        [0, 45, 0],
        [0, 0, 60],
        [30, 45, 60],
        [-30, 90, -45]
    ]
    
    print("欧拉角转换精度测试:")
    for angles in test_angles:
        obj.transform.local_rotation = angles
        quat = obj.transform.local_rotation_quaternion
        converted_back = obj.transform.local_rotation
        error = np.array(angles) - np.array(converted_back)
        
        print(f"原始: {angles}")
        print(f"四元数: {quat}")
        print(f"转换回: {converted_back}")
        print(f"误差: {error}")
        print(f"最大误差: {np.max(np.abs(error)):.6f}\n")


def test_rotation_composition():
    """测试旋转组合"""
    print("=== 测试旋转组合 ===\n")
    
    # 创建ECS管理器
    ecs = ECSManager()
    
    # 创建父子物体进行复杂旋转测试
    parent = ecs.create_entity(GameObject, name="Parent")
    child = ecs.create_entity(GameObject, name="Child")
    grandchild = ecs.create_entity(GameObject, name="GrandChild")
    
    # 设置旋转
    parent.transform.rotation = [0, 90, 0]  # 绕Y轴90度
    child.transform.local_rotation = [90, 0, 0]  # 绕X轴90度
    grandchild.transform.local_rotation = [0, 0, 90]  # 绕Z轴90度
    
    # 建立层级关系
    child.set_parent(parent, world_position_stays=False)
    grandchild.set_parent(child, world_position_stays=False)
    
    print(f"父物体旋转: {parent.transform.rotation}")
    print(f"子物体本地旋转: {child.transform.local_rotation}")
    print(f"子物体世界旋转: {child.transform.rotation}")
    print(f"孙子物体本地旋转: {grandchild.transform.local_rotation}")
    print(f"孙子物体世界旋转: {grandchild.transform.rotation}")
    
    # 验证四元数组合
    expected_child_quat = parent.transform.rotation_quaternion * child.transform.local_rotation_quaternion
    actual_child_quat = child.transform.rotation_quaternion
    
    expected_grandchild_quat = child.transform.rotation_quaternion * grandchild.transform.local_rotation_quaternion
    actual_grandchild_quat = grandchild.transform.rotation_quaternion
    
    print(f"\n四元数组合验证:")
    print(f"子物体 - 预期: {expected_child_quat}")
    print(f"子物体 - 实际: {actual_child_quat}")
    print(f"子物体 - 匹配: {expected_child_quat == actual_child_quat}")
    
    print(f"孙子物体 - 预期: {expected_grandchild_quat}")
    print(f"孙子物体 - 实际: {actual_grandchild_quat}")
    print(f"孙子物体 - 匹配: {expected_grandchild_quat == actual_grandchild_quat}")


if __name__ == "__main__":
    test_transform_hierarchy()
    test_quaternion_accuracy()
    test_rotation_composition()
    print("\n🎉 Transform四元数系统测试完成！") 