# 相机系统 (Camera System)

MiniPyEngine的相机系统提供了完整的3D相机功能，支持透视投影和正交投影，以及基于四元数的精确旋转控制。

## 功能特性

- **多种投影模式** - 透视投影和正交投影
- **四元数旋转** - 精确的相机旋转控制，避免万向锁
- **视图矩阵** - 自动计算视图变换矩阵
- **LookAt功能** - 相机朝向控制
- **可配置参数** - FOV、宽高比、裁剪面等

## 基础用法

### 创建相机

```python
from components.camera_setting import CameraSetting, ProjectionType
from util.quaternion import Quaternion
import numpy as np

# 创建基础相机
camera = CameraSetting()

# 创建自定义相机
camera = CameraSetting(
    position=np.array([0.0, 5.0, 10.0]),
    rotation=Quaternion.from_euler_angles(0, 0, 0),
    fov=60.0,
    aspect_ratio=16/9,
    near_clip=0.1,
    far_clip=1000.0,
    projection_type=ProjectionType.PERSPECTIVE
)
```

### 相机参数

```python
# 位置和旋转
camera.position = np.array([10.0, 5.0, 0.0])
camera.pitch = -15.0  # 俯仰角（度）
camera.yaw = 90.0     # 偏航角（度）

# 投影参数
camera.fov = 75.0              # 视场角（度）
camera.aspect_ratio = 1920/1080  # 宽高比
camera.near_clip = 0.1         # 近裁剪面
camera.far_clip = 500.0        # 远裁剪面

# 投影类型
camera.projection_type = ProjectionType.PERSPECTIVE
# 或
camera.projection_type = ProjectionType.ORTHOGRAPHIC
```

## 相机控制

### 基础移动

```python
# 直接设置位置
camera.position = np.array([x, y, z])

# 相对移动
camera.position += camera.front * speed  # 向前
camera.position += camera.right * speed  # 向右
camera.position += camera.up * speed     # 向上
```

### 旋转控制

```python
# 使用欧拉角（简单）
camera.pitch += mouse_y_delta * sensitivity
camera.yaw += mouse_x_delta * sensitivity

# 使用四元数（更精确）
rotation_quat = Quaternion.from_axis_angle([0, 1, 0], yaw_delta)
camera.rotate_by_quaternion(rotation_quat)

# 直接设置四元数
target_rotation = Quaternion.from_euler_angles(pitch, yaw, 0)
camera.set_rotation_quaternion(target_rotation)
```

### LookAt功能

```python
# 朝向特定点
target_position = np.array([0, 0, 0])
camera.look_at(target_position)

# 指定上方向
camera.look_at(target_position, up=np.array([0, 1, 0]))

# 朝向移动的物体
def update_camera(target_object):
    camera.look_at(target_object.transform.position)
```

## 高级相机控制

### 第一人称相机

```python
class FirstPersonCamera:
    def __init__(self, camera_setting):
        self.camera = camera_setting
        self.sensitivity = 0.1
        self.speed = 5.0
    
    def update(self, delta_time, input_handler):
        # 鼠标旋转
        mouse_delta = input_handler.get_mouse_delta()
        self.camera.yaw += mouse_delta[0] * self.sensitivity
        self.camera.pitch -= mouse_delta[1] * self.sensitivity
        
        # 限制俯仰角
        self.camera.pitch = max(-89.0, min(89.0, self.camera.pitch))
        
        # 键盘移动
        move_vector = np.array([0.0, 0.0, 0.0])
        
        if input_handler.is_key_pressed('W'):
            move_vector += self.camera.front
        if input_handler.is_key_pressed('S'):
            move_vector -= self.camera.front
        if input_handler.is_key_pressed('A'):
            move_vector -= self.camera.right
        if input_handler.is_key_pressed('D'):
            move_vector += self.camera.right
        
        # 归一化并应用速度
        if np.linalg.norm(move_vector) > 0:
            move_vector = move_vector / np.linalg.norm(move_vector)
            self.camera.position += move_vector * self.speed * delta_time
```

### 第三人称相机

```python
class ThirdPersonCamera:
    def __init__(self, camera_setting, target):
        self.camera = camera_setting
        self.target = target
        self.distance = 10.0
        self.height = 2.0
        self.angle = 0.0
    
    def update(self, delta_time, input_handler):
        # 鼠标控制角度
        mouse_delta = input_handler.get_mouse_delta()
        self.angle += mouse_delta[0] * 0.01
        
        # 计算相机位置
        offset_x = self.distance * np.cos(self.angle)
        offset_z = self.distance * np.sin(self.angle)
        
        camera_pos = self.target.transform.position + np.array([offset_x, self.height, offset_z])
        self.camera.position = camera_pos
        
        # 朝向目标
        self.camera.look_at(self.target.transform.position)
```

### 轨道相机

```python
class OrbitCamera:
    def __init__(self, camera_setting, target_position):
        self.camera = camera_setting
        self.target = target_position
        self.radius = 10.0
        self.theta = 0.0  # 水平角度
        self.phi = 0.0    # 垂直角度
    
    def orbit(self, delta_theta, delta_phi):
        self.theta += delta_theta
        self.phi = max(-89.0, min(89.0, self.phi + delta_phi))
        
        # 球坐标转笛卡尔坐标
        x = self.radius * np.cos(np.radians(self.phi)) * np.cos(np.radians(self.theta))
        y = self.radius * np.sin(np.radians(self.phi))
        z = self.radius * np.cos(np.radians(self.phi)) * np.sin(np.radians(self.theta))
        
        self.camera.position = self.target + np.array([x, y, z])
        self.camera.look_at(self.target)
    
    def zoom(self, delta):
        self.radius = max(1.0, self.radius + delta)
        self.orbit(0, 0)  # 更新位置
```

## 矩阵获取

### 视图矩阵和投影矩阵

```python
# 获取变换矩阵
view_matrix = camera.view_matrix
projection_matrix = camera.projection_matrix

# 在渲染管线中使用
def render_object(obj, shader):
    # 设置矩阵到着色器
    shader.set_matrix4("view", view_matrix)
    shader.set_matrix4("projection", projection_matrix)
    shader.set_matrix4("model", obj.transform.local_to_world_matrix)
    
    # 渲染物体
    obj.render()
```

### 手动更新

```python
# 通常相机会自动更新，但也可以手动触发
camera.calculate_view_matrix()
camera.calculate_projection_matrix()

# 检查是否需要更新
if camera.is_dirty:
    camera.calculate_view_matrix()
```

## 相机切换

```python
class CameraManager:
    def __init__(self):
        self.cameras = {}
        self.active_camera = None
    
    def add_camera(self, name, camera):
        self.cameras[name] = camera
    
    def set_active_camera(self, name):
        if name in self.cameras:
            self.active_camera = self.cameras[name]
    
    def get_active_camera(self):
        return self.active_camera
    
    def update(self, delta_time):
        if self.active_camera:
            self.active_camera.calculate_view_matrix()

# 使用示例
camera_mgr = CameraManager()
camera_mgr.add_camera("main", main_camera)
camera_mgr.add_camera("debug", debug_camera)
camera_mgr.set_active_camera("main")
```

## 性能优化

### 矩阵缓存

相机系统使用脏标记避免不必要的矩阵计算：

```python
# 只有当相机参数改变时才重新计算
camera.position = new_position  # 标记为脏
matrix = camera.view_matrix      # 重新计算
matrix2 = camera.view_matrix     # 使用缓存
```

### 视锥体裁剪

```python
def is_in_view_frustum(camera, object_position, object_radius):
    """简单的球体视锥体裁剪检测"""
    # 将物体位置转换到相机空间
    relative_pos = object_position - camera.position
    
    # 检查距离
    distance = np.linalg.norm(relative_pos)
    if distance < camera.near_clip or distance > camera.far_clip:
        return False
    
    # 检查FOV（简化版本）
    forward_dot = np.dot(relative_pos, camera.front)
    if forward_dot < 0:  # 在相机后面
        return False
    
    return True
```

## 调试工具

### 相机信息显示

```python
def debug_camera_info(camera):
    print(f"Camera Position: {camera.position}")
    print(f"Camera Rotation: pitch={camera.pitch:.1f}, yaw={camera.yaw:.1f}")
    print(f"Camera Front: {camera.front}")
    print(f"Camera FOV: {camera.fov}")
    print(f"Camera Aspect: {camera.aspect_ratio}")
```

### 相机方向可视化

```python
def draw_camera_debug(camera, length=2.0):
    """绘制相机的方向向量（需要调试渲染支持）"""
    origin = camera.position
    
    # 前方向（蓝色）
    front_end = origin + camera.front * length
    draw_line(origin, front_end, color=[0, 0, 1])
    
    # 右方向（红色）
    right_end = origin + camera.right * length
    draw_line(origin, right_end, color=[1, 0, 0])
    
    # 上方向（绿色）
    up_end = origin + camera.up * length
    draw_line(origin, up_end, color=[0, 1, 0])
``` 