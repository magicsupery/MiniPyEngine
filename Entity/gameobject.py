# -*- coding: utf-8 -*-
from components.transform import Transform
from core.ecs import Entity


class GameObject(Entity):
    def __init__(self, entity_id=None, name=None):
        super().__init__(entity_id)
        self.name = name if name is not None else f"GameObject_{self.entity_id}"
        
        # 添加Transform组件
        trans = Transform()
        self.add_component(trans)

    # ============ Python风格的Transform访问 ============
    
    @property
    def transform(self):
        """获取Transform组件"""
        return self.get_component(Transform)
    
    # ============ Python风格的父子关系管理 ============
    
    @property
    def parent(self):
        """父GameObject (通过Transform管理)"""
        parent_transform = self.transform.parent
        return parent_transform.owner if parent_transform else None
    
    @parent.setter
    def parent(self, value):
        """设置父GameObject"""
        if value is None:
            self.transform.set_parent(None)
        else:
            self.transform.set_parent(value.transform)
    
    def set_parent(self, parent, world_position_stays=True):
        """设置父物体"""
        if parent is None:
            self.transform.set_parent(None, world_position_stays)
        else:
            self.transform.set_parent(parent.transform, world_position_stays)
    
    @property
    def child_count(self):
        """子物体数量"""
        return self.transform.child_count
    
    def get_child(self, index):
        """获取指定索引的子GameObject"""
        child_transform = self.transform.get_child(index)
        return child_transform.owner
    
    def find(self, name):
        """按名称查找子GameObject"""
        child_transform = self.transform.find(name)
        return child_transform.owner if child_transform else None
    
    def detach_children(self):
        """分离所有子物体"""
        self.transform.detach_children()

    # ============ Unity风格别名 (兼容性接口) ============
    
    def SetParent(self, parent, worldPositionStays=True):
        """Unity风格别名"""
        return self.set_parent(parent, worldPositionStays)
    
    @property
    def childCount(self):
        """Unity风格别名"""
        return self.child_count
    
    def GetChild(self, index):
        """Unity风格别名"""
        return self.get_child(index)
    
    def Find(self, name):
        """Unity风格别名"""
        return self.find(name)
    
    def DetachChildren(self):
        """Unity风格别名"""
        return self.detach_children()

    # ============ 兼容性方法 (保持与旧代码的兼容) ============
    
    def add_child(self, child):
        """兼容旧版本的add_child方法"""
        child.set_parent(self, world_position_stays=True)

    def remove_child(self, child):
        """兼容旧版本的remove_child方法"""
        if child.parent == self:
            child.set_parent(None)
