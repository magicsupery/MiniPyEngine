# Transform系统

MiniPyEngine的Transform系统提供了完整的3D变换功能，支持位置、旋转、缩放的管理，以及父子关系的层级管理。

## 功能特性

- **完整的3D变换** - 位置、旋转、缩放的统一管理
- **四元数旋转** - 内部使用四元数避免万向锁
- **父子关系** - 支持Unity风格的层级管理
- **坐标转换** - 本地坐标与世界坐标的相互转换
- **双重API** - Python风格和Unity风格的API

## Python风格API (推荐)

### 基础变换

```python
from Entity.gameobject import GameObject
from core.ecs import ECSManager

ecs = ECSManager()
obj = ecs.create_entity(GameObject, name="MyObject")

# 位置
obj.transform.local_position = [1.0, 0.0, 0.0]
obj.transform.position = [5.0, 2.0, -3.0]

# 旋转 (欧拉角)
obj.transform.local_rotation = [30.0, 45.0, 60.0]
obj.transform.rotation = [0.0, 90.0, 0.0]

# 旋转 (四元数) - 更精确
from util.quaternion import Quaternion
quat = Quaternion.from_euler_angles(45, 0, 0)
obj.transform.local_rotation_quaternion = quat
obj.transform.rotation_quaternion = quat

# 缩放
obj.transform.local_scale = [2.0, 2.0, 2.0]
print(obj.transform.lossy_scale)  # 世界缩放（只读）
```

### 旋转方法

```python
# 绕指定轴旋转
obj.transform.rotate([0, 1, 0], 90)  # 绕Y轴旋转90度

# 朝向目标点
obj.transform.look_at([5, 0, 5])
obj.transform.look_at([5, 0, 5], up=[0, 1, 0])  # 指定上方向
```

### 父子关系管理

```python
# 设置父子关系
child.set_parent(parent, world_position_stays=True)

# 获取信息
parent_count = parent.child_count
first_child = parent.get_child(0)
found_child = parent.find("ChildName")

# 分离子物体
parent.detach_children()

# 移除父关系
child.set_parent(None)
```

### 坐标转换

```python
# 点的坐标转换
local_point = [1, 0, 0]
world_point = obj.transform.transform_point(local_point)
back_to_local = obj.transform.inverse_transform_point(world_point)

# 方向的转换（不受位移影响）
local_direction = [1, 0, 0]
world_direction = obj.transform.transform_direction(local_direction)
back_to_local_dir = obj.transform.inverse_transform_direction(world_direction)

# 获取变换矩阵
local_to_world = obj.transform.local_to_world_matrix
world_to_local = obj.transform.world_to_local_matrix
```

## Unity风格API (兼容性)

```python
# 属性访问
obj.transform.localPosition = [1, 2, 3]
obj.transform.localRotation = [30, 45, 60]
obj.transform.localScale = [2, 2, 2]

# 只读属性
print(obj.transform.lossyScale)
print(obj.transform.childCount)

# 方法调用
child.SetParent(parent, worldPositionStays=True)
first_child = parent.GetChild(0)
found_child = parent.Find("ChildName")
parent.DetachChildren()

# 坐标转换
world_point = obj.transform.TransformPoint(local_point)
local_point = obj.transform.InverseTransformPoint(world_point)
world_dir = obj.transform.TransformDirection(local_direction)
local_dir = obj.transform.InverseTransformDirection(world_direction)

# 旋转方法
obj.transform.Rotate([0, 1, 0], 90)
obj.transform.LookAt([5, 0, 5])

# 矩阵访问
matrix = obj.transform.localToWorldMatrix
inverse_matrix = obj.transform.worldToLocalMatrix
```

## 高级用法

### 复杂层级结构

```python
# 创建多层级结构
root = ecs.create_entity(GameObject, name="Root")
branch = ecs.create_entity(GameObject, name="Branch")
leaf1 = ecs.create_entity(GameObject, name="Leaf1")
leaf2 = ecs.create_entity(GameObject, name="Leaf2")

# 建立层级关系
branch.set_parent(root)
leaf1.set_parent(branch)
leaf2.set_parent(branch)

# 根物体变换影响所有子物体
root.transform.rotation = [0, 45, 0]  # 整个树都会旋转
```

### 动画和插值

```python
from util.quaternion import Quaternion

# 平滑旋转动画
start_rotation = obj.transform.rotation_quaternion
target_rotation = Quaternion.from_euler_angles(0, 180, 0)

# 在游戏循环中
def update(delta_time):
    t = min(1.0, animation_time / duration)
    current_rotation = Quaternion.slerp(start_rotation, target_rotation, t)
    obj.transform.rotation_quaternion = current_rotation
```

### 相对变换

```python
# 在当前基础上添加变换
obj.transform.position += [1, 0, 0]  # 向右移动1单位

# 相对旋转
relative_rotation = Quaternion.from_axis_angle([0, 1, 0], 15)
obj.transform.rotation_quaternion *= relative_rotation
```

### 坐标系变换应用

```python
# 武器在角色手中的相对位置
weapon.set_parent(character)
weapon.transform.local_position = [0.5, 0, 0]  # 相对于角色的位置
weapon.transform.local_rotation = [0, 45, 0]    # 相对于角色的旋转

# 角色移动时，武器自动跟随
character.transform.position = new_position
# weapon的世界位置自动更新
```

## 性能优化

### 矩阵缓存

Transform系统使用脏标记机制缓存变换矩阵：

```python
# 矩阵只在需要时重新计算
obj.transform.position = [1, 2, 3]  # 标记为脏
matrix = obj.transform.local_to_world_matrix  # 重新计算并缓存
matrix2 = obj.transform.local_to_world_matrix  # 使用缓存，无需重算
```

### 批量操作

```python
# 避免频繁的单独设置
# 不推荐
obj.transform.position = [x, y, z]
obj.transform.rotation = [rx, ry, rz]
obj.transform.scale = [sx, sy, sz]

# 推荐
obj.transform.local_position = [x, y, z]
obj.transform.local_rotation = [rx, ry, rz]  
obj.transform.local_scale = [sx, sy, sz]
```

## 注意事项

### 本地坐标 vs 世界坐标

- **本地坐标**: 相对于父物体的坐标
- **世界坐标**: 相对于世界原点的绝对坐标

```python
# 设置本地位置
child.transform.local_position = [1, 0, 0]

# 如果父物体位置是[5, 0, 0]，则子物体世界位置是[6, 0, 0]
print(child.transform.position)  # [6, 0, 0]
```

### 旋转顺序

四元数避免了欧拉角的万向锁问题，但转换时仍需注意旋转顺序：

```python
# 使用四元数进行复杂旋转
q1 = Quaternion.from_axis_angle([1, 0, 0], 30)  # 绕X轴
q2 = Quaternion.from_axis_angle([0, 1, 0], 45)  # 绕Y轴

# 顺序很重要
result1 = q2 * q1  # 先X轴再Y轴
result2 = q1 * q2  # 先Y轴再X轴
# result1 != result2
```

### 性能考虑

- 避免每帧都访问世界坐标属性
- 使用local属性进行相对变换
- 合理设计物体层级结构，避免过深的嵌套 