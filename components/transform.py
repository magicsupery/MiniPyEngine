# -*- coding:utf-8
from core.ecs import Component


class Transform(Component):
	def __init__(self, x=0, y=0, z=0, yaw=0, pitch=0, roll=0):
		super(Transform, self).__init__()
		self.x = x
		self.y = y
		self.z = z
		self.yaw = yaw
		self.pitch = pitch
		self.roll = roll
