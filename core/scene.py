# -*- coding: utf-8 -*-
"""
Scene系统 - 场景管理
负责管理场景中所有Entity的生命周期和查询功能
"""

from bson import ObjectId
from typing import List, Optional, Dict
from core.ecs import Entity


class Scene:
    """
    Scene类 - 场景管理器
    管理场景中的所有Entity，提供场景级的操作和查询功能
    """
    
    def __init__(self, name: str = "Untitled"):
        self.scene_id = ObjectId()
        self.name = name
        self.is_loaded = False
        self.is_dirty = False  # 场景是否需要保存
        
        # Entity管理
        self._entities: Dict[ObjectId, Entity] = {}  # 所有Entity的字典映射
        self._name_to_entity: Dict[str, List[Entity]] = {}  # 名称到Entity的映射
        self._component_to_entities: Dict[type, List[Entity]] = {}  # 组件类型到Entity的映射
        
        # 场景统计信息
        self._entity_count = 0
    
    # ============ Entity 生命周期管理 ============
    
    def add_entity(self, entity: Entity) -> None:
        """
        向场景添加Entity
        Args:
            entity: 要添加的Entity
        """
        if entity.entity_id in self._entities:
            entity_name = getattr(entity, 'name', str(entity.entity_id))
            print(f"⚠️ Entity '{entity_name}' 已存在于场景中")
            return
        
        # 添加到全局管理
        self._entities[entity.entity_id] = entity
        self._entity_count += 1
        
        # 添加到名称映射（如果Entity有name属性）
        if hasattr(entity, 'name') and entity.name:
            if entity.name not in self._name_to_entity:
                self._name_to_entity[entity.name] = []
            self._name_to_entity[entity.name].append(entity)
        
        # 添加到组件映射
        self._update_component_mappings(entity, add=True)
        
        self._mark_dirty()
        entity_name = getattr(entity, 'name', str(entity.entity_id))
        print(f"✅ Entity '{entity_name}' 已添加到场景 '{self.name}'")
    
    def remove_entity(self, entity: Entity) -> bool:
        """
        从场景移除Entity
        Args:
            entity: 要移除的Entity
        Returns:
            移除是否成功
        """
        if entity.entity_id not in self._entities:
            entity_name = getattr(entity, 'name', str(entity.entity_id))
            print(f"⚠️ Entity '{entity_name}' 不在当前场景中")
            return False
        
        # 从组件映射中移除
        self._update_component_mappings(entity, add=False)
        
        # 从字典映射中移除
        del self._entities[entity.entity_id]
        self._entity_count -= 1
        
        # 从名称映射中移除
        if hasattr(entity, 'name') and entity.name and entity.name in self._name_to_entity:
            self._name_to_entity[entity.name].remove(entity)
            if not self._name_to_entity[entity.name]:
                del self._name_to_entity[entity.name]
        
        # 如果是GameObject，处理父子关系
        from Entity.gameobject import GameObject
        if isinstance(entity, GameObject):
            # 移除子对象
            children_to_remove = []
            for i in range(entity.child_count):
                children_to_remove.append(entity.get_child(i))
            
            for child in children_to_remove:
                self.remove_entity(child)
            
            # 从父对象中移除
            if entity.parent is not None:
                entity.set_parent(None)
        
        self._mark_dirty()
        entity_name = getattr(entity, 'name', str(entity.entity_id))
        print(f"✅ Entity '{entity_name}' 已从场景 '{self.name}' 移除")
        return True
    
    # ============ Entity 查询功能 ============
    
    def find_entity(self, name: str) -> Optional[Entity]:
        """
        按名称查找Entity（返回第一个匹配的）
        Args:
            name: Entity名称
        Returns:
            找到的Entity或None
        """
        entities = self._name_to_entity.get(name, [])
        return entities[0] if entities else None
    
    def find_entities_with_name(self, name: str) -> List[Entity]:
        """
        按名称查找所有匹配的Entity
        Args:
            name: Entity名称
        Returns:
            匹配的Entity列表
        """
        return self._name_to_entity.get(name, []).copy()
    
    def get_entities_with_component(self, component_type) -> List[Entity]:
        """
        按组件类型查找所有匹配的Entity (优化版本)
        Args:
            component_type: 组件类型
        Returns:
            匹配的Entity列表
        """
        return self._component_to_entities.get(component_type, []).copy()
    
    def find_entity_with_component(self, component_type) -> Optional[Entity]:
        """
        查找包含指定组件类型的第一个Entity (优化版本)
        Args:
            component_type: 组件类型
        Returns:
            找到的Entity或None
        """
        entities = self._component_to_entities.get(component_type, [])
        return entities[0] if entities else None
    
    # ============ 场景属性和状态 ============
    
    @property
    def all_entities(self) -> List[Entity]:
        """获取场景中所有Entity"""
        return list(self._entities.values())
    
    @property
    def entity_count(self) -> int:
        """场景中Entity总数"""
        return self._entity_count
    
    @property
    def game_objects(self) -> List['GameObject']:
        """获取场景中所有GameObject"""
        from Entity.gameobject import GameObject
        return [entity for entity in self._entities.values() if isinstance(entity, GameObject)]
    
    @property
    def root_game_objects(self) -> List['GameObject']:
        """获取所有根级GameObject"""
        from Entity.gameobject import GameObject
        result = []
        for entity in self._entities.values():
            if isinstance(entity, GameObject) and entity.parent is None:
                result.append(entity)
        return result
    
    # ============ 场景操作 ============
    
    def is_valid(self) -> bool:
        """检查场景是否有效"""
        return self.is_loaded and self.name is not None
    
    def _mark_dirty(self):
        """标记场景为脏状态（需要保存）"""
        self.is_dirty = True
    
    def get_scene_info(self) -> Dict:
        """获取场景信息摘要"""
        gameobject_count = len(self.game_objects)
        root_gameobject_count = len(self.root_game_objects)
        
        return {
            'name': self.name,
            'scene_id': str(self.scene_id),
            'is_loaded': self.is_loaded,
            'is_dirty': self.is_dirty,
            'total_entities': self.entity_count,
            'game_objects': gameobject_count,
            'root_game_objects': root_gameobject_count
        }
    
    def _update_component_mappings(self, entity: Entity, add: bool = True):
        """
        更新组件映射
        Args:
            entity: 要更新的Entity
            add: True为添加，False为移除
        """
        # 遍历Entity的所有组件
        for component_type, component in entity.components.items():
            if add:
                # 添加到映射
                if component_type not in self._component_to_entities:
                    self._component_to_entities[component_type] = []
                if entity not in self._component_to_entities[component_type]:
                    self._component_to_entities[component_type].append(entity)
            else:
                # 从映射中移除
                if component_type in self._component_to_entities:
                    if entity in self._component_to_entities[component_type]:
                        self._component_to_entities[component_type].remove(entity)
                    # 如果列表为空，删除这个映射
                    if not self._component_to_entities[component_type]:
                        del self._component_to_entities[component_type]
    
    def notify_component_added(self, entity: Entity, component_type: type):
        """
        通知Scene某个Entity添加了组件
        Args:
            entity: 添加组件的Entity
            component_type: 组件类型
        """
        if entity.entity_id not in self._entities:
            return  # Entity不在这个Scene中
        
        if component_type not in self._component_to_entities:
            self._component_to_entities[component_type] = []
        if entity not in self._component_to_entities[component_type]:
            self._component_to_entities[component_type].append(entity)
    
    def notify_component_removed(self, entity: Entity, component_type: type):
        """
        通知Scene某个Entity移除了组件
        Args:
            entity: 移除组件的Entity
            component_type: 组件类型
        """
        if entity.entity_id not in self._entities:
            return  # Entity不在这个Scene中
        
        if component_type in self._component_to_entities:
            if entity in self._component_to_entities[component_type]:
                self._component_to_entities[component_type].remove(entity)
            if not self._component_to_entities[component_type]:
                del self._component_to_entities[component_type]


class SceneManager:
    """
    场景管理器
    负责场景的加载、卸载、切换等全局操作
    """
    
    def __init__(self):
        self._scenes: Dict[str, Scene] = {}
        self._active_scene: Optional[Scene] = None
        self._loaded_scenes: List[Scene] = []
    
    # ============ 场景管理 ============
    
    def create_scene(self, name: str) -> Scene:
        """
        创建新场景
        Args:
            name: 场景名称
        Returns:
            创建的Scene对象
        """
        if name in self._scenes:
            print(f"⚠️ 场景 '{name}' 已存在")
            return self._scenes[name]
        
        scene = Scene(name)
        scene.is_loaded = True
        self._scenes[name] = scene
        self._loaded_scenes.append(scene)
        
        # 如果这是第一个场景，设为活动场景
        if self._active_scene is None:
            self._active_scene = scene
            print(f"✅ 场景 '{name}' 已创建并设为活动场景")
        else:
            print(f"✅ 场景 '{name}' 已创建")
        
        return scene
    
    def load_scene(self, name: str) -> Optional[Scene]:
        """
        加载场景（如果存在）
        Args:
            name: 场景名称
        Returns:
            加载的Scene对象或None
        """
        if name not in self._scenes:
            print(f"❌ 场景 '{name}' 不存在")
            return None
        
        scene = self._scenes[name]
        if not scene.is_loaded:
            scene.is_loaded = True
            if scene not in self._loaded_scenes:
                self._loaded_scenes.append(scene)
            print(f"✅ 场景 '{name}' 已加载")
        
        return scene
    
    def unload_scene(self, name: str) -> bool:
        """
        卸载场景
        Args:
            name: 场景名称
        Returns:
            卸载是否成功
        """
        if name not in self._scenes:
            print(f"❌ 场景 '{name}' 不存在")
            return False
        
        scene = self._scenes[name]
        
        # 不能卸载活动场景
        if scene == self._active_scene:
            print(f"❌ 不能卸载活动场景 '{name}'")
            return False
        
        scene.is_loaded = False
        if scene in self._loaded_scenes:
            self._loaded_scenes.remove(scene)
        
        print(f"✅ 场景 '{name}' 已卸载")
        return True
    
    def set_active_scene(self, scene: Scene) -> bool:
        """
        设置活动场景
        Args:
            scene: 要设为活动的场景
        Returns:
            设置是否成功
        """
        if not scene.is_loaded:
            print(f"❌ 场景 '{scene.name}' 未加载，无法设为活动场景")
            return False
        
        old_scene = self._active_scene
        self._active_scene = scene
        
        if old_scene:
            print(f"🔄 活动场景从 '{old_scene.name}' 切换到 '{scene.name}'")
        else:
            print(f"✅ 场景 '{scene.name}' 设为活动场景")
        
        return True
    
    # ============ 属性访问 ============
    
    @property
    def active_scene(self) -> Optional[Scene]:
        """获取当前活动场景"""
        return self._active_scene
    
    @property
    def loaded_scene_count(self) -> int:
        """已加载场景数量"""
        return len(self._loaded_scenes)
    
    @property
    def scene_count(self) -> int:
        """总场景数量"""
        return len(self._scenes)
    
    def get_scene_by_name(self, name: str) -> Optional[Scene]:
        """按名称获取场景"""
        return self._scenes.get(name)
    
    def get_loaded_scenes(self) -> List[Scene]:
        """获取所有已加载的场景"""
        return self._loaded_scenes.copy() 