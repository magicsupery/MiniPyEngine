# -*- coding: utf-8 -*-
import numpy as np

from Entity.camera import Camera
from Entity.gameobject import GameObject
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
    """
    相机移动逻辑模块
    
    包含两种控制模式：
    1. 键盘控制 (WASD) - 平滑移动
    2. 鼠标控制 - 平滑旋转 (使用SLERP四元数插值)
    """
    
    def __init__(self):
        self.move_speed = 5.0  # 移动速度
        self.sensitivity = 0.1  # 鼠标灵敏度
        self.zoom_speed = 2.0  # 滚轮缩放速度
        self.min_fov = 10.0    # 最小视场角
        self.max_fov = 120.0   # 最大视场角
        
        # 移动状态
        self.move_directions = {
            CameraMoveDirection.FORWARD: False,
            CameraMoveDirection.BACKWARD: False,
            CameraMoveDirection.LEFT: False,
            CameraMoveDirection.RIGHT: False,
        }
        
        # 鼠标控制
        self.mouse_pressed = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        
        # 目标旋转 (用于平滑插值) - 从相机当前角度初始化
        self.target_yaw = -90.0  # 初始yaw值，与Camera默认值一致
        self.target_pitch = 0.0  # 初始pitch值
        self.rotation_smoothing = 10.0  # 旋转平滑度
        
        # 注册输入监听
        self._register_input_listeners()
        
        print("🎮 相机控制系统已启动")
        print("   WASD - 移动相机")
        print("   鼠标左键+拖拽 - 旋转相机视角")
        print("   鼠标滚轮 - 缩放视野 (FOV)")
    
    def _register_input_listeners(self):
        """注册输入事件监听器"""
        input_system = GD.ecs_manager.get_system(InputSystem)
        if not input_system:
            print("❌ 未找到InputSystem")
            return
        
        # 键盘按下事件
        input_system.register_keyboard_listener(Key.W, KeyAction.PRESSED, 
                                               lambda: self._set_move_direction(CameraMoveDirection.FORWARD, True))
        input_system.register_keyboard_listener(Key.S, KeyAction.PRESSED, 
                                               lambda: self._set_move_direction(CameraMoveDirection.BACKWARD, True))
        input_system.register_keyboard_listener(Key.A, KeyAction.PRESSED, 
                                               lambda: self._set_move_direction(CameraMoveDirection.LEFT, True))
        input_system.register_keyboard_listener(Key.D, KeyAction.PRESSED, 
                                               lambda: self._set_move_direction(CameraMoveDirection.RIGHT, True))
        
        # 键盘释放事件
        input_system.register_keyboard_listener(Key.W, KeyAction.RELEASED, 
                                               lambda: self._set_move_direction(CameraMoveDirection.FORWARD, False))
        input_system.register_keyboard_listener(Key.S, KeyAction.RELEASED, 
                                               lambda: self._set_move_direction(CameraMoveDirection.BACKWARD, False))
        input_system.register_keyboard_listener(Key.A, KeyAction.RELEASED, 
                                               lambda: self._set_move_direction(CameraMoveDirection.LEFT, False))
        input_system.register_keyboard_listener(Key.D, KeyAction.RELEASED, 
                                               lambda: self._set_move_direction(CameraMoveDirection.RIGHT, False))
        
        # 鼠标按钮事件
        input_system.register_mouse_button_listener(MouseButton.LEFT, MouseAction.PRESSED, self._on_mouse_press)
        input_system.register_mouse_button_listener(MouseButton.LEFT, MouseAction.RELEASED, self._on_mouse_release)
        
        # 鼠标移动事件
        input_system.register_mouse_move_listener(self._on_mouse_move)
        
        # 鼠标滚轮事件
        input_system.register_scroll_listener(self._on_scroll)
    
    def _set_move_direction(self, direction, pressed):
        """设置移动方向状态"""
        self.move_directions[direction] = pressed
    
    def _on_mouse_press(self):
        """鼠标按下事件"""
        self.mouse_pressed = True
    
    def _on_mouse_release(self):
        """鼠标释放事件"""
        self.mouse_pressed = False
    
    def _on_mouse_move(self, x, y, delta_x, delta_y):
        """鼠标移动事件"""
        if self.mouse_pressed:
            # 更新目标旋转
            self.target_yaw -= delta_x * self.sensitivity
            self.target_pitch -= delta_y * self.sensitivity
            
            # 限制俯仰角
            self.target_pitch = max(-89.0, min(89.0, self.target_pitch))
    
    def _on_scroll(self, xoffset, yoffset):
        """鼠标滚轮事件"""
        camera = GD.main_camera
        if not camera:
            return
        
        # 使用Y轴偏移调整FOV实现缩放
        zoom_delta = yoffset * self.zoom_speed
        new_fov = camera.fov - zoom_delta  # 向上滚动减小FOV（放大），向下滚动增大FOV（缩小）
        
        # 限制FOV范围
        new_fov = max(self.min_fov, min(self.max_fov, new_fov))
        
        # 应用新的FOV
        camera.set_fov(new_fov)
        
        print(f"🔍 相机FOV: {new_fov:.1f}° ({'放大' if zoom_delta > 0 else '缩小'})")
    
    def update(self, delta_time):
        """更新相机状态"""
        camera = GD.main_camera
        if not camera:
            return
        
        # 处理移动 
        self._update_movement(camera, delta_time)
        
        # 处理旋转 (平滑插值)
        self._update_rotation(camera, delta_time)
    
    def _update_movement(self, camera, delta_time):
        """更新相机移动"""
        # 计算移动向量
        movement = np.array([0.0, 0.0, 0.0])
        
        if self.move_directions[CameraMoveDirection.FORWARD]:
            movement += camera.front
        if self.move_directions[CameraMoveDirection.BACKWARD]:
            movement -= camera.front
        if self.move_directions[CameraMoveDirection.LEFT]:
            movement -= camera.right
        if self.move_directions[CameraMoveDirection.RIGHT]:
            movement += camera.right
        
        # 归一化并应用速度
        if np.linalg.norm(movement) > 0:
            movement = movement / np.linalg.norm(movement)
            movement *= self.move_speed * delta_time
            
            # 更新相机位置
            camera.position += movement
            camera.is_dirty = True
    
    def _update_rotation(self, camera, delta_time):
        """更新相机旋转 (使用直接角度更新)"""
        if not self.mouse_pressed:
            return
        
        # 直接更新相机的角度
        camera.yaw = self.target_yaw
        camera.pitch = self.target_pitch
        
        # 触发相机更新方向向量
        camera.update_direction_vectors()
        camera.is_dirty = True


def main():
    # 初始化资源管理器
    resource_manager = FileResourceManager()
    GD.resource_manager = resource_manager
    
    # 初始化ECS管理器 (这会自动创建SceneManager)
    ecs = ECSManager()
    GD.ecs_manager = ecs
    GD.scene_manager = ecs.scene_manager  # 同时设置全局引用

    # 创建默认场景 (MainScene会在第一个Entity创建时自动创建)
    print("🎬 场景系统初始化完成")
    
    # 创建相机 (也是Entity，需要在Scene中管理)
    camera = ecs.create_entity(Camera)
    GD.main_camera = camera
    
    # 添加系统
    ecs.add_system(RenderSystem())
    
    input_system = InputSystem()
    ecs.add_system(input_system)

    logic_system = LogicSystem()
    ecs.add_system(logic_system)

    camera_move_module = CameraMovementModule()
    logic_system.add_logic_module(camera_move_module)

    print("🚀 开始创建3D场景...")
    
    # 加载材质组件
    material_component = GD.resource_manager.load_material_from_config("resources/shaders/my_first_shader.json")
    
    # 创建第一个游戏对象 - 使用立方体模型 (会自动添加到MainScene)
    print("🔷 创建立方体对象...")
    cube_player = ecs.create_entity(GameObject, name="CubePlayer")
    cube_player.transform.position = [-2.0, 0.0, -8.0]
    cube_player.transform.rotation = [0.0, 0.0, 0.0]
    cube_player.transform.scale = [1.0, 1.0, 1.0]
    
    # 使用资源管理器加载立方体模型
    cube_mesh = GD.resource_manager.load_mesh_from_file("resources/models/cube.obj")
    if cube_mesh:
        ecs.add_component(cube_player, cube_mesh)
        print("   ✅ 立方体模型加载成功!")
    else:
        # 回退到原始三角形
        print("   ❌ 立方体模型加载失败，使用原始三角形")
        vertices = np.array([
            -0.5, -0.5, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
            0.5, -0.5, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0,
            0.5, 0.5, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0
        ], dtype=np.float32)
        ecs.add_component(cube_player, Mesh(vertices))
    
    ecs.add_component(cube_player, material_component)

    # 创建第二个游戏对象 - 使用金字塔模型
    print("🔺 创建金字塔对象...")
    pyramid_player = ecs.create_entity(GameObject, name="PyramidPlayer")
    pyramid_player.transform.position = [2.0, 0.0, -8.0]
    pyramid_player.transform.rotation = [0.0, 45.0, 0.0]
    pyramid_player.transform.scale = [1.5, 1.5, 1.5]  # 稍微放大
    
    # 使用资源管理器加载金字塔模型
    pyramid_mesh = GD.resource_manager.load_mesh_from_file("resources/models/pyramid.obj")
    if pyramid_mesh:
        ecs.add_component(pyramid_player, pyramid_mesh)
        print("   ✅ 金字塔模型加载成功!")
        
        # 显示模型信息
        if hasattr(pyramid_mesh, 'obj_data'):
            obj_data = pyramid_mesh.obj_data
            print(f"   📊 金字塔信息: {len(obj_data['vertices'])}顶点, {len(obj_data['faces'])}面")
    else:
        print("   ❌ 金字塔模型加载失败")

    ecs.add_component(pyramid_player, material_component)

    # 创建第三个游戏对象 - 子对象（小立方体）
    print("🔸 创建子立方体对象...")
    child_cube = ecs.create_entity(GameObject, name="ChildCube")
    child_cube.transform.local_position = [0.0, 2.0, 0.0]  # 在金字塔上方
    child_cube.transform.local_rotation = [0.0, 0.0, 45.0]  # 倾斜45度
    child_cube.transform.local_scale = [0.3, 0.3, 0.3]  # 小尺寸
    
    # 使用立方体模型（从缓存中获取）
    small_cube_mesh = GD.resource_manager.load_mesh_from_file("resources/models/cube.obj")
    if small_cube_mesh:
        ecs.add_component(child_cube, small_cube_mesh)
        print("   ✅ 子立方体模型加载成功!")
    
    ecs.add_component(child_cube, material_component)

    # 设置父子关系 - 小立方体是金字塔的子对象
    child_cube.set_parent(pyramid_player, world_position_stays=False)
    print("   🔗 父子关系设置完成: 小立方体 -> 金字塔")

    # 显示场景信息
    scene_info = ecs.get_scene_info()
    print(f"\n🎬 场景信息:")
    print(f"   场景名称: {scene_info['name']}")
    print(f"   总Entity数: {scene_info['total_entities']}")
    print(f"   GameObject数: {scene_info['game_objects']}")
    print(f"   根GameObject数: {scene_info['root_game_objects']}")
    print(f"   场景已加载: {scene_info['is_loaded']}")

    print("✅ 3D场景创建完成!")
    print("\n🎮 控制说明:")
    print("   WASD - 移动相机")
    print("   鼠标左键+拖拽 - 旋转相机视角")
    print("   立方体在左侧，金字塔在右侧，小立方体在金字塔上方")
    
    main_loop = MainLoop()
    main_loop.run()


if __name__ == "__main__":
    main()
