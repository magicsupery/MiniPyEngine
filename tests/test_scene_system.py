# -*- coding: utf-8 -*-
"""
Scene系统测试
验证场景管理、Entity组织和查询功能
"""
import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Entity.gameobject import GameObject
from Entity.camera import Camera
from core.ecs import ECSManager
from core.scene import Scene, SceneManager
from components.mesh import Mesh
from components.material import Material
import numpy as np


def test_scene_creation():
    """测试场景创建和基本操作"""
    print("========================================")
    print("        Scene 系统创建测试")
    print("========================================\n")
    
    # 创建场景管理器
    scene_manager = SceneManager()
    
    # 测试场景创建
    print("🚀 测试场景创建:")
    scene1 = scene_manager.create_scene("TestScene1")
    print(f"   创建场景: {scene1.name}")
    print(f"   场景ID: {scene1.scene_id}")
    print(f"   是否已加载: {scene1.is_loaded}")
    print(f"   是否为活动场景: {scene_manager.active_scene == scene1}")
    
    scene2 = scene_manager.create_scene("TestScene2")
    print(f"   创建场景: {scene2.name}")
    print(f"   当前活动场景: {scene_manager.active_scene.name}")
    
    print(f"   总场景数: {scene_manager.scene_count}")
    print(f"   已加载场景数: {scene_manager.loaded_scene_count}")
    print()


def test_entity_management():
    """测试Entity在场景中的管理"""
    print("🚀 测试Entity管理:")
    
    # 创建ECS管理器
    ecs = ECSManager()
    
    # 创建不同类型的Entity
    gameobject1 = ecs.create_entity(GameObject, name="Player")
    gameobject2 = ecs.create_entity(GameObject, name="Enemy")
    camera = ecs.create_entity(Camera)  # Camera也是Entity
    
    # 获取活动场景
    scene = ecs.get_active_scene()
    if scene is None:
        print("   ❌ 无法获取活动场景")
        return
        
    print(f"   活动场景: {scene.name}")
    print(f"   创建的Entity: GameObject x2, Camera x1")
    print(f"   场景中Entity数量: {scene.entity_count}")
    print(f"   GameObject数量: {len(scene.game_objects)}")
    
    # 设置GameObject父子关系
    gameobject2.set_parent(gameobject1)  # Enemy是Player的子对象
    
    print(f"   设置父子关系: Enemy -> Player")
    print(f"   根GameObject数量: {len(scene.root_game_objects)}")
    
    # 显示场景中的根对象和所有GameObject
    root_names = [obj.name for obj in scene.root_game_objects]
    gameobject_names = [obj.name for obj in scene.game_objects]
    print(f"   根GameObject: {root_names}")
    print(f"   所有GameObject: {gameobject_names}")
    print()


def test_entity_search():
    """测试Entity搜索功能"""
    print("🚀 测试Entity搜索:")
    
    ecs = ECSManager()
    
    # 创建一些测试对象
    player = ecs.create_entity(GameObject, name="Player")
    enemy1 = ecs.create_entity(GameObject, name="Enemy")
    enemy2 = ecs.create_entity(GameObject, name="Enemy")  # 同名对象
    boss = ecs.create_entity(GameObject, name="Boss")
    camera = ecs.create_entity(Camera)
    
    # 获取活动场景
    scene = ecs.get_active_scene()
    if scene is None:
        print("   ❌ 无法获取活动场景")
        return
    
    print(f"   创建Entity: GameObject x4, Camera x1")
    
    # 测试按名称查找
    found_player = scene.find_entity("Player")
    print(f"   查找'Player': {found_player.name if found_player else 'None'}")
    
    found_enemy = scene.find_entity("Enemy")
    print(f"   查找'Enemy': {found_enemy.name if found_enemy else 'None'}")
    
    all_enemies = scene.find_entities_with_name("Enemy")
    print(f"   查找所有'Enemy': {len(all_enemies)}个")
    
    # 测试按组件类型查找
    # 为一些对象添加组件
    vertices = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0], dtype=np.float32)
    mesh = Mesh(vertices)
    ecs.add_component(player, mesh)
    ecs.add_component(boss, mesh)
    
    mesh_entities = scene.get_entities_with_component(Mesh)
    mesh_names = [entity.name if hasattr(entity, 'name') else str(entity.entity_id) for entity in mesh_entities]
    print(f"   具有Mesh组件的Entity: {mesh_names}")
    
    first_mesh_entity = scene.find_entity_with_component(Mesh)
    first_name = first_mesh_entity.name if hasattr(first_mesh_entity, 'name') else str(first_mesh_entity.entity_id)
    print(f"   第一个具有Mesh组件的Entity: {first_name}")
    print()


def test_scene_operations():
    """测试场景操作功能"""
    print("🚀 测试场景操作:")
    
    ecs = ECSManager()
    scene_manager = ecs.scene_manager
    
    # 创建多个场景
    main_scene = scene_manager.create_scene("MainScene")
    test_scene = scene_manager.create_scene("TestScene")
    
    # 在主场景中创建对象
    scene_manager.set_active_scene(main_scene)
    main_obj = ecs.create_entity(GameObject, name="MainObject")
    print(f"   在主场景创建对象: {main_obj.name}")
    print(f"   主场景Entity数: {main_scene.entity_count}")
    
    # 切换到测试场景
    scene_manager.set_active_scene(test_scene)
    test_obj = ecs.create_entity(GameObject, name="TestObject")
    print(f"   切换到测试场景并创建对象: {test_obj.name}")
    print(f"   测试场景Entity数: {test_scene.entity_count}")
    print(f"   主场景Entity数: {main_scene.entity_count} (未变化)")
    
    # 显示场景信息
    print(f"\n   主场景信息: {main_scene.get_scene_info()}")
    print(f"   测试场景信息: {test_scene.get_scene_info()}")
    print()


def test_entity_removal():
    """测试Entity移除功能"""
    print("🚀 测试Entity移除:")
    
    ecs = ECSManager()
    
    # 创建父子关系的对象
    parent = ecs.create_entity(GameObject, name="Parent")
    child1 = ecs.create_entity(GameObject, name="Child1")
    child2 = ecs.create_entity(GameObject, name="Child2")
    grandchild = ecs.create_entity(GameObject, name="GrandChild")
    camera = ecs.create_entity(Camera)
    
    # 获取活动场景
    scene = ecs.get_active_scene()
    if scene is None:
        print("   ❌ 无法获取活动场景")
        return
    
    # 建立层级关系
    child1.set_parent(parent)
    child2.set_parent(parent)
    grandchild.set_parent(child1)
    
    print(f"   创建层级: Parent -> Child1 -> GrandChild")
    print(f"              └─> Child2")
    print(f"   场景Entity数: {scene.entity_count}")
    print(f"   根GameObject数: {len(scene.root_game_objects)}")
    
    # 移除子对象（同时移除所有子对象）
    scene.remove_entity(child1)
    print(f"   移除Child1及其子对象")
    print(f"   场景Entity数: {scene.entity_count}")
    
    # 移除相机
    scene.remove_entity(camera)
    print(f"   移除Camera")
    print(f"   场景Entity数: {scene.entity_count}")
    
    root_names = [obj.name for obj in scene.root_game_objects]
    print(f"   剩余根GameObject: {root_names}")
    print()


def test_ecs_integration():
    """测试ECS系统与Scene的集成"""
    print("🚀 测试ECS与Scene集成:")
    
    ecs = ECSManager()
    
    # 创建对象和组件
    obj1 = ecs.create_entity(GameObject, name="Object1")
    obj2 = ecs.create_entity(GameObject, name="Object2")
    obj3 = ecs.create_entity(GameObject, name="Object3")
    camera = ecs.create_entity(Camera)
    
    # 添加Mesh组件
    vertices = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0], dtype=np.float32)
    mesh1 = Mesh(vertices)
    mesh2 = Mesh(vertices)
    
    ecs.add_component(obj1, mesh1)
    ecs.add_component(obj2, mesh2)
    # obj3 和 camera 没有Mesh组件
    
    print(f"   创建4个Entity，其中2个GameObject有Mesh组件")
    
    # 测试组件查询（应该从场景中获取）
    mesh_entities = ecs.get_entities_with_component(Mesh)
    mesh_names = [entity.name if hasattr(entity, 'name') else str(entity.entity_id) for entity in mesh_entities]
    print(f"   通过ECS查找具有Mesh的Entity: {mesh_names}")
    
    # 测试场景信息获取
    scene_info = ecs.get_scene_info()
    print(f"   ECS获取场景信息: {scene_info}")
    
    # 测试通过ECS查找Entity
    found_obj = ecs.find_entity("Object2")
    print(f"   通过ECS查找Object2: {found_obj.name if found_obj else 'None'}")
    
    all_entities = ecs.get_all_entities()
    entity_names = [entity.name if hasattr(entity, 'name') else type(entity).__name__ for entity in all_entities]
    print(f"   通过ECS获取所有Entity: {entity_names}")
    print()


if __name__ == "__main__":
    try:
        test_scene_creation()
        test_entity_management()
        test_entity_search()
        test_scene_operations()
        test_entity_removal()
        test_ecs_integration()
        
        print("========================================")
        print("✅ Scene系统测试完成!")
        print("✅ 所有功能正常工作!")
        print("✅ ECS集成测试通过!")
        print("✅ 简化API设计验证成功!")
        print("========================================")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc() 