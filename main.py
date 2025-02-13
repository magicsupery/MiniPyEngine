# -*- coding: utf-8 -*-
import numpy as np

from Entity.camera import Camera
from Entity.gameobject import GameObject
from components.camera_setting import CameraSetting
from components.mesh import Mesh
from components.transform import Transform
from core.main_loop import MainLoop
from core.ecs import ECSManager
from systems.input_system import InputSystem
from systems.logic_system import LogicSystem, LogicModule
from systems.render_system import RenderSystem
from Context.context import global_data as GD
from input.event_types import Key, KeyAction, MouseButton, MouseAction
from resource_manager.file_resource_manager import FileResourceManager

from enum import Enum, auto


class CameraMoveDirection(Enum):
    FORWARD = auto()
    BACKWARD = auto()
    LEFT = auto()
    RIGHT = auto()


class CameraMovementModule(LogicModule):
    def __init__(self):
        super(CameraMovementModule, self).__init__()
        self.move_speed = 1.0

        self.rotation_sensitive = 0.1
        self.constrain_pitch = True
        self.need_rotate = False
        self.horizontal_directions = []
        self.vertical_directions = []

        self.register_events()

    def register_events(self):

        # keyboard events
        def camera_forward_pressed():
            self.vertical_directions.append(CameraMoveDirection.FORWARD)

        def camera_forward_released():
            self.vertical_directions.remove(CameraMoveDirection.FORWARD)

        def camera_backward_pressed():
            self.vertical_directions.append(CameraMoveDirection.BACKWARD)

        def camera_backward_released():
            self.vertical_directions.remove(CameraMoveDirection.BACKWARD)

        def camera_left_pressed():
            # self.horizontal_directions.append(CameraMoveDirection.LEFT)
            result = GD.ecs_manager.entities[1].get_component(Transform).position[0] - 0.5
            GD.ecs_manager.entities[1].get_component(Transform).position = [result, 0.0, -10.0]
            print(GD.ecs_manager.entities[1])
            print(GD.ecs_manager.entities[1].get_component(Transform).position)
            pass

        def camera_left_released():
            # self.horizontal_directions.remove(CameraMoveDirection.LEFT)
            pass

        def camera_right_pressed():
            self.horizontal_directions.append(CameraMoveDirection.RIGHT)

        def camera_right_released():
            self.horizontal_directions.remove(CameraMoveDirection.RIGHT)

        input_system = GD.ecs_manager.get_system(InputSystem)
        input_system.register_keyboard_listener(Key.S, KeyAction.PRESSED, camera_backward_pressed)
        input_system.register_keyboard_listener(Key.S, KeyAction.RELEASED, camera_backward_released)
        input_system.register_keyboard_listener(Key.A, KeyAction.PRESSED, camera_left_pressed)
        input_system.register_keyboard_listener(Key.A, KeyAction.RELEASED, camera_left_released)
        input_system.register_keyboard_listener(Key.D, KeyAction.PRESSED, camera_right_pressed)
        input_system.register_keyboard_listener(Key.D, KeyAction.RELEASED, camera_right_released)
        input_system.register_keyboard_listener(Key.W, KeyAction.PRESSED, camera_forward_pressed)
        input_system.register_keyboard_listener(Key.W, KeyAction.RELEASED, camera_forward_released)

        # mouse events
        def camera_mouse_move(xpos, ypos, delta_x, delta_y):
            if self.need_rotate:
                camera_setting = GD.main_camera.get_component(CameraSetting)
                camera_setting.yaw += delta_x * self.rotation_sensitive
                camera_setting.pitch += delta_y * self.rotation_sensitive

                if self.constrain_pitch:
                    if camera_setting.pitch > 89.0:
                        camera_setting.pitch = 89.0
                    if camera_setting.pitch < -89.0:
                        camera_setting.pitch = -89.0

        input_system.register_mouse_move_listener(camera_mouse_move)

        def camera_mouse_left_button_pressed():
            self.need_rotate = True

        def camera_mouse_left_button_released():
            self.need_rotate = False

        input_system.register_mouse_button_listener(MouseButton.LEFT, MouseAction.PRESSED,
                                                    camera_mouse_left_button_pressed)
        input_system.register_mouse_button_listener(MouseButton.LEFT, MouseAction.RELEASED,
                                                    camera_mouse_left_button_released)

    def update(self, dt):
        if len(self.horizontal_directions) == 0 and len(self.vertical_directions) == 0:
            return

        camera_setting = GD.main_camera.get_component(CameraSetting)
        if len(self.horizontal_directions) > 0:
            last_horizontal_direction = self.horizontal_directions[-1]
            if last_horizontal_direction == CameraMoveDirection.LEFT:
                camera_setting.position -= camera_setting.right * self.move_speed * dt
            elif last_horizontal_direction == CameraMoveDirection.RIGHT:
                camera_setting.position += camera_setting.right * self.move_speed * dt

        if len(self.vertical_directions) > 0:
            last_vertical_direction = self.vertical_directions[-1]
            if last_vertical_direction == CameraMoveDirection.FORWARD:
                camera_setting.position += camera_setting.front * self.move_speed * dt
            elif last_vertical_direction == CameraMoveDirection.BACKWARD:
                camera_setting.position -= camera_setting.front * self.move_speed * dt


def main():
    resource_manager = FileResourceManager()
    GD.resource_manager = resource_manager
    ecs = ECSManager()
    GD.ecs_manager = ecs

    GD.ecs_manager.create_entity(Camera)

    ecs.add_system(RenderSystem())

    input_system = InputSystem()
    ecs.add_system(input_system)

    logic_system = LogicSystem()
    ecs.add_system(logic_system)

    camera_move_module = CameraMovementModule()
    logic_system.add_logic_module(camera_move_module)

    player = ecs.create_entity(GameObject)
    player_trans = player.get_component(Transform)
    player_trans.position = [0.0, 0.0, -10.0]
    player_trans.rotation = [0.0, 0.0, 0.0]
    player_trans.scale = [1.0, 1.0, 1.0]
    vertices = np.array([
        -0.5, -0.5, 0.0, 0.0, 0.0,
        0.5, -0.5, 0.0, 1.0, 0.0,
        0.5, 0.5, 0.0, 1.0, 1.0
    ], dtype=np.float32)
    ecs.add_component(player, Mesh(vertices))

    material_component = GD.resource_manager.load_material_from_config("resources/shaders/my_first_shader.json")

    ecs.add_component(player, material_component)

    player1 = ecs.create_entity(GameObject)
    player_trans = player1.get_component(Transform)
    player_trans.position = [1.0, 0.0, -10.0]
    player_trans.rotation = [0.0, 0.0, 0.0]
    player_trans.scale = [1.0, 1.0, 1.0]
    ecs.add_component(player1, Mesh(vertices))

    ecs.add_component(player1, material_component)

    player.add_child(player1)

    main_loop = MainLoop()
    main_loop.run()


if __name__ == "__main__":
    main()
