# -*- coding: utf-8 -*-


from core.ecs import System

from abc import ABC, abstractmethod


class LogicModule(ABC):
    @abstractmethod
    def update(self, dt):
        pass


class LogicSystem(System):
    def __init__(self):
        super(LogicSystem, self).__init__()
        self.logic_modules = []

    def add_logic_module(self, logic_module):
        self.logic_modules.append(logic_module)
        return
    
    def update(self, dt):
        for module in self.logic_modules:
            module.update(dt)
        return
