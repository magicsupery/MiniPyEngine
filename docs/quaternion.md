# 四元数系统 (Quaternion System)

MiniPyEngine的四元数系统提供了专业级的3D旋转处理能力，避免万向锁问题并支持平滑的旋转插值。

## 核心优势

- **避免万向锁** - 解决欧拉角的万向锁问题
- **平滑插值** - 支持LERP和SLERP球面插值
- **精确计算** - 旋转组合更精确，无累积误差
- **高效存储** - 4个分量vs 9分量旋转矩阵

## 基础用法

### 创建四元数

```python
from util.quaternion import Quaternion

# 单位四元数（无旋转）
q1 = Quaternion.identity()

# 直接构造
q2 = Quaternion(x, y, z, w)

# 从欧拉角创建
q3 = Quaternion.from_euler_angles(pitch, yaw, roll)  # 角度制

# 从轴角创建  
q4 = Quaternion.from_axis_angle([0, 1, 0], 90)  # 绕Y轴90度

# 从数组创建
q5 = Quaternion.from_array([x, y, z, w])
```

### 四元数运算

```python
# 旋转组合（四元数乘法）
q_result = q1 * q2

# 归一化
q_normalized = q1.normalized()

# 逆四元数
q_inverse = q1.inverse()

# 共轭
q_conjugate = q1.conjugate()

# 模长
magnitude = q1.magnitude()

# 加法
q_sum = q1 + q2

# 标量乘法
q_scaled = q1 * 2.0
```

### 坐标转换

```python
# 转换为欧拉角
euler_angles = q.to_euler_angles()  # 返回 [pitch, yaw, roll]

# 转换为旋转矩阵
rotation_matrix = q.to_rotation_matrix()  # 4x4矩阵

# 旋转向量
rotated_vector = q.rotate_vector([1, 0, 0])

# 转换为数组
array = q.to_array()  # [x, y, z, w]
```

### 插值

```python
# 线性插值
q_lerp = Quaternion.lerp(q1, q2, 0.5)

# 球面插值（推荐用于动画）
q_slerp = Quaternion.slerp(q1, q2, 0.5)
```

## 高级用法

### 动画和平滑旋转

```python
# 相机平滑转向目标
current_rotation = camera.rotation_quaternion
target_rotation = Quaternion.from_euler_angles(0, target_yaw, 0)

# 使用SLERP实现平滑过渡
t = 0.1  # 插值速度
camera.rotation_quaternion = Quaternion.slerp(current_rotation, target_rotation, t)
```

### 复杂旋转组合

```python
# 多轴旋转组合
pitch_rotation = Quaternion.from_axis_angle([1, 0, 0], 30)  # 绕X轴
yaw_rotation = Quaternion.from_axis_angle([0, 1, 0], 45)    # 绕Y轴
roll_rotation = Quaternion.from_axis_angle([0, 0, 1], 60)   # 绕Z轴

# 组合旋转（顺序很重要）
final_rotation = yaw_rotation * pitch_rotation * roll_rotation
```

### 相对旋转

```python
# 在当前旋转基础上添加新旋转
additional_rotation = Quaternion.from_axis_angle([0, 1, 0], 15)
obj.transform.rotation_quaternion = obj.transform.rotation_quaternion * additional_rotation
```

## 数学原理

### 四元数表示
```
q = w + xi + yj + zk
其中 i² = j² = k² = ijk = -1
```

- **w**: 标量部分，cos(θ/2)
- **x, y, z**: 向量部分，sin(θ/2) * 轴向量

### 旋转公式
绕单位轴 **v** 旋转角度 **θ** 的四元数：
```
q = cos(θ/2) + sin(θ/2) * (vx*i + vy*j + vz*k)
```

### 向量旋转
使用四元数 q 旋转向量 v：
```
v' = q * v * q⁻¹
```

## 性能优化

### 归一化
四元数在连续运算后可能失去单位长度，定期归一化：
```python
q = q.normalized()  # 确保|q| = 1
```

### 插值优化
对于大量插值计算，考虑预计算或使用缓存：
```python
# 预计算插值表
interpolation_table = []
for i in range(101):  # 0% 到 100%
    t = i / 100.0
    interpolation_table.append(Quaternion.slerp(start_quat, end_quat, t))
```

## 常见问题

### Q: 为什么需要归一化？
A: 浮点运算误差会导致四元数失去单位长度，影响旋转准确性。

### Q: LERP vs SLERP 如何选择？
A: 
- **LERP**: 计算更快，适合小角度旋转或性能优先场景
- **SLERP**: 更平滑，适合动画和大角度旋转

### Q: 四元数乘法顺序重要吗？
A: 是的！四元数乘法不满足交换律，q1 * q2 ≠ q2 * q1

### Q: 如何避免翻转问题？
A: 选择最短路径旋转，检查四元数点积的符号：
```python
if q1.dot(q2) < 0:
    q2 = -q2  # 反转四元数选择最短路径
``` 