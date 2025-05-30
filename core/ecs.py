# -*- coding:utf-8

from bson import ObjectId
from collections import defaultdict


class Component(object):
    def __init__(self, component_id=None):
        if component_id is None:
            component_id = ObjectId()
        self.component_id = component_id
        self.owner = None

    def set_owner(self, owner):
        self.owner = owner


class Entity(object):
    def __init__(self, entity_id=None):
        if entity_id is None:
            entity_id = ObjectId()
        self.entity_id = entity_id
        self.components = {}

    def id(self):
        return self.entity_id

    def add_component(self, component):
        assert (isinstance(component, Component))
        assert (type(component) not in self.components)
        self.components[type(component)] = component
        component.set_owner(self)

    def get_component(self, component_type):
        return self.components.get(component_type, None)


class System(object):
    def __init__(self, system_id=None):
        if system_id is None:
            system_id = ObjectId()
        self.system_id = system_id

    def update(self, delta_time):
        raise NotImplementedError


class ECSManager(object):
    def __init__(self):
        # Scene管理
        from core.scene import SceneManager
        self.scene_manager = SceneManager()
        self.systems = []

    def create_entity(self, entity_type, entity_id=None, **kwargs):
        """
        创建实体并自动添加到活动场景
        所有Entity都必须在Scene中管理
        """
        assert (isinstance(entity_type, type))
        assert (issubclass(entity_type, Entity))
        entity = entity_type(entity_id, **kwargs)
        
        # 确保有活动场景
        active_scene = self.scene_manager.active_scene
        if active_scene is None:
            # 如果没有活动场景，创建默认场景
            active_scene = self.scene_manager.create_scene("MainScene")
        
        # 将所有Entity添加到场景中
        active_scene.add_entity(entity)
        
        return entity

    def add_component(self, entity, component):
        """为实体添加组件"""
        entity.add_component(component)
        
        # 通知Scene更新组件映射
        active_scene = self.scene_manager.active_scene
        if active_scene and entity.entity_id in active_scene._entities:
            active_scene.notify_component_added(entity, type(component))

    def get_entities_with_component(self, component_type):
        """
        获取具有指定组件的所有实体
        从活动场景中获取
        """
        active_scene = self.scene_manager.active_scene
        if active_scene:
            return active_scene.get_entities_with_component(component_type)
        return []

    def add_system(self, system):
        self.systems.append(system)

    def get_system(self, system_type):
        for system in self.systems:
            if isinstance(system, system_type):
                return system
        return None

    def get_systems(self):
        return self.systems
    
    # ============ Scene相关的便捷方法 ============
    
    def create_scene(self, name: str):
        """创建新场景"""
        return self.scene_manager.create_scene(name)
    
    def get_active_scene(self):
        """获取活动场景"""
        return self.scene_manager.active_scene
    
    def set_active_scene(self, scene):
        """设置活动场景"""
        return self.scene_manager.set_active_scene(scene)
    
    def find_entity(self, name: str):
        """在活动场景中查找Entity"""
        active_scene = self.scene_manager.active_scene
        if active_scene:
            return active_scene.find_entity(name)
        return None
    
    def get_all_entities(self):
        """获取活动场景中的所有Entity"""
        active_scene = self.scene_manager.active_scene
        if active_scene:
            return active_scene.all_entities
        return []
    
    def get_scene_info(self):
        """获取当前场景信息"""
        active_scene = self.scene_manager.active_scene
        if active_scene:
            return active_scene.get_scene_info()
        return {"error": "No active scene"}
