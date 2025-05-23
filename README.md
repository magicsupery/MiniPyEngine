# MiniPyEngine

一个用Python开发的迷你游戏引擎，用于学习游戏引擎架构的基础模块。

## 特性概览

- **ECS架构** - Entity-Component-System 游戏引擎架构
- **Python风格API** - 遵循PEP 8命名约定，提供Unity风格兼容API
- **四元数旋转系统** - 专业级旋转计算，避免万向锁问题
- **Transform系统** - 完整的3D变换和父子关系管理
- **相机系统** - 多投影模式，基于四元数的精确控制
- **输入系统** - 键盘和鼠标输入处理
- **渲染系统** - 基于OpenGL的3D渲染
- **资源管理** - 统一的资源加载和管理

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行示例
```bash
python main.py
```

### 运行测试
```bash
# 基础Transform测试
python tests/test_transform.py

# 完整四元数系统测试
python tests/test_quaternion_transform.py
```

## 基础用法

### 创建游戏对象
```python
from Entity.gameobject import GameObject
from core.ecs import ECSManager

ecs = ECSManager()
obj = ecs.create_entity(GameObject, name="MyObject")

# Transform操作
obj.transform.position = [1, 2, 3]
obj.transform.rotation = [0, 45, 0]
obj.transform.scale = [2, 2, 2]
```

### 四元数旋转
```python
from util.quaternion import Quaternion

# 创建四元数
quat = Quaternion.from_euler_angles(30, 45, 60)
obj.transform.rotation_quaternion = quat

# 平滑插值
target_quat = Quaternion.from_axis_angle([0, 1, 0], 90)
interpolated = Quaternion.slerp(quat, target_quat, 0.5)
```

## 系统文档

详细的API文档和使用指南：

- **[四元数系统](docs/quaternion.md)** - 四元数数学原理、API使用和高级技巧
- **[Transform系统](docs/transform.md)** - 3D变换、父子关系和坐标转换
- **[相机系统](docs/camera.md)** - 相机控制、投影设置和高级相机类型

## 项目结构

```
MiniPyEngine/
├── components/          # 组件系统
│   ├── transform.py    # Transform组件
│   └── camera_setting.py # 相机组件
├── core/               # 核心模块
├── Entity/             # 实体定义
├── systems/            # 系统模块
├── input/              # 输入处理
├── graphics/           # 图形渲染
├── util/               # 工具模块
│   └── quaternion.py   # 四元数实现
├── tests/              # 测试文件
├── docs/               # 详细文档
│   ├── quaternion.md   # 四元数文档
│   ├── transform.md    # Transform文档
│   └── camera.md       # 相机文档
├── main.py             # 主程序入口
└── requirements.txt    # 依赖列表
```

## 学习目标

这个项目旨在帮助开发者了解和学习：

1. **游戏引擎架构** - ECS模式的实现和应用
2. **3D数学** - 四元数、变换矩阵、坐标系统
3. **旋转数学** - 避免万向锁的四元数旋转系统
4. **图形编程** - OpenGL渲染管线基础
5. **系统设计** - 模块化和组件化设计模式
6. **Python最佳实践** - 代码风格和项目结构

## 核心优势

### 四元数旋转系统
- 避免万向锁问题
- 支持LERP和SLERP球面插值  
- 旋转组合更精确，无累积误差
- 高效存储（4个分量 vs 9个分量的旋转矩阵）

### 双重API设计
```python
# Python风格 (推荐)
obj.transform.local_position = [1, 2, 3]
child.set_parent(parent)

# Unity风格 (兼容)  
obj.transform.localPosition = [1, 2, 3]
child.SetParent(parent)
```

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

[MIT License](LICENSE)
