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
from util.quaternion import Quaternion

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
        
        # 平滑旋转相关属性
        self.rotation_smoothing = 8.0  # 旋转平滑程度，值越大越平滑
        self.target_yaw = None  # 目标偏航角
        self.target_pitch = None  # 目标俯仰角
        self.target_rotation = None  # 目标四元数旋转

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
            self.horizontal_directions.append(CameraMoveDirection.LEFT)

        def camera_left_released():
            self.horizontal_directions.remove(CameraMoveDirection.LEFT)

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
                
                # 初始化目标旋转值（如果还没有初始化）
                if self.target_yaw is None:
                    self.target_yaw = camera_setting.yaw
                    self.target_pitch = camera_setting.pitch
                    self.target_rotation = camera_setting.rotation
                
                # 更新目标旋转角度
                self.target_yaw += delta_x * self.rotation_sensitive
                self.target_pitch += delta_y * self.rotation_sensitive

                # 约束俯仰角
                if self.constrain_pitch:
                    self.target_pitch = max(-89.0, min(89.0, self.target_pitch))

                # 计算目标四元数旋转
                self.target_rotation = Quaternion.from_euler_angles(self.target_pitch, self.target_yaw, 0.0)

        input_system.register_mouse_move_listener(camera_mouse_move)

        def camera_mouse_left_button_pressed():
            self.need_rotate = True
            # 初始化目标旋转为当前旋转
            camera_setting = GD.main_camera.get_component(CameraSetting)
            self.target_yaw = camera_setting.yaw
            self.target_pitch = camera_setting.pitch
            self.target_rotation = camera_setting.rotation

        def camera_mouse_left_button_released():
            self.need_rotate = False

        input_system.register_mouse_button_listener(MouseButton.LEFT, MouseAction.PRESSED,
                                                    camera_mouse_left_button_pressed)
        input_system.register_mouse_button_listener(MouseButton.LEFT, MouseAction.RELEASED,
                                                    camera_mouse_left_button_released)

    def update(self, dt):
        camera_setting = GD.main_camera.get_component(CameraSetting)
        
        # 平滑旋转处理
        if self.target_rotation is not None:
            current_rotation = camera_setting.rotation
            
            # 计算插值系数（基于帧率的平滑过渡）
            # 使用指数衰减来实现平滑过渡
            smoothing_factor = 1.0 - pow(0.5, self.rotation_smoothing * dt)
            
            # 检查四元数方向，选择最短路径
            if current_rotation.dot(self.target_rotation) < 0:
                # 如果点积为负，说明需要反转其中一个四元数以选择最短路径
                target_for_slerp = Quaternion(-self.target_rotation.x, -self.target_rotation.y, 
                                             -self.target_rotation.z, -self.target_rotation.w)
            else:
                target_for_slerp = self.target_rotation
            
            # 使用SLERP进行平滑插值
            smoothed_rotation = Quaternion.slerp(current_rotation, target_for_slerp, smoothing_factor)
            
            # 应用平滑后的旋转
            camera_setting.set_rotation_quaternion(smoothed_rotation)
            
            # 如果已经足够接近目标旋转，停止插值
            rotation_difference = abs(1.0 - abs(current_rotation.dot(target_for_slerp)))
            if rotation_difference < 0.001:  # 非常小的阈值
                camera_setting.set_rotation_quaternion(self.target_rotation)
                if not self.need_rotate:
                    self.target_rotation = None  # 清除目标旋转
        
        # 相机移动逻辑保持不变
        if len(self.horizontal_directions) > 0 or len(self.vertical_directions) > 0:
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

    # 创建第一个游戏对象
    player = ecs.create_entity(GameObject, name="Player")
    player.transform.position = [0.0, 0.0, -10.0]
    player.transform.rotation = [0.0, 0.0, 0.0]
    player.transform.scale = [1.0, 1.0, 1.0]
    vertices = np.array([
        -0.5, -0.5, 0.0, 0.0, 0.0,
        0.5, -0.5, 0.0, 1.0, 0.0,
        0.5, 0.5, 0.0, 1.0, 1.0
    ], dtype=np.float32)
    ecs.add_component(player, Mesh(vertices))

    material_component = GD.resource_manager.load_material_from_config("resources/shaders/my_first_shader.json")

    ecs.add_component(player, material_component)

    # 创建第二个游戏对象作为子物体
    player1 = ecs.create_entity(GameObject, name="Child")
    player1.transform.local_position = [1.0, 0.0, 0.0]  # 使用本地坐标
    player1.transform.local_rotation = [0.0, 0.0, 0.0]
    player1.transform.local_scale = [0.5, 0.5, 0.5]  # 子物体缩放为一半
    ecs.add_component(player1, Mesh(vertices))

    ecs.add_component(player1, material_component)

    # 使用Python风格的父子关系设置
    player1.set_parent(player, world_position_stays=False)  # 不保持世界位置，使用本地坐标

    main_loop = MainLoop()
    main_loop.run()


if __name__ == "__main__":
    main()
