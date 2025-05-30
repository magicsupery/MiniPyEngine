# -*- coding:utf-8 -*-

class GlobalData(object):
    def __init__(self):
        self.ecs_manager = None
        self.renderer = None
        self.main_camera = None
        self.resource_manager = None
        self.scene_manager = None


global_data = GlobalData()
