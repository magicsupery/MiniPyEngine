# -*- coding:utf-8

from bson import ObjectId
from collections import defaultdict


class Component(object):
	def __init__(self, component_id=None):
		if component_id is None:
			component_id = ObjectId()
		self.component_id = component_id


class Entity(object):
	def __init__(self, entity_id=None):
		if entity_id is None:
			entity_id = ObjectId()
		self.entity_id = entity_id
		self.components = {}

	def id(self):
		return self.entity_id

	def add_component(self, component):
		self.components[type(component)] = component


class System(object):
	def __init__(self, ecs_manager, system_id=None):
		if system_id is None:
			system_id = ObjectId()
		self.system_id = system_id
		self.manager = ecs_manager

	def update(self, delta_time):
		raise NotImplementedError


class ECSManager(object):
	def __init__(self):
		self.entities = []
		self.component_to_entity = defaultdict(list)
		self.systems = []

	def create_entity(self):
		entity = Entity()
		self.entities.append(entity)
		return entity

	def add_component(self, entity, component):
		entity.add_component(component)
		self.component_to_entity[type(component)].append(entity)

	def get_entities_with_component(self, component_type):
		return self.component_to_entity[component_type]

	def add_system(self, system):
		self.systems.append(system)

	def get_systems(self):
		return self.systems
