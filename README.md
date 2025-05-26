# MiniPyEngine

一个用于学习游戏引擎开发的轻量级Python游戏引擎。

## 🚀 主要特性

### 核心架构
- **ECS系统** - 实体-组件-系统架构
- **Transform系统** - 完整的3D变换支持，包含父子关系
- **四元数旋转** - 避免万向锁问题的旋转系统

### 3D资产加载 🆕
- **OBJ格式支持** - 标准3D模型文件格式
- **统一顶点格式** - `[x, y, z, nx, ny, nz, u, v]` 8个float
- **智能缓存** - 避免重复加载相同文件
- **自动优化** - 顶点去重、三角化、索引生成
- **格式兼容** - 支持多种OBJ格式变体

### 渲染系统
- **现代OpenGL** - 支持法线的光照渲染
- **基础光照** - 环境光 + 方向光漫反射
- **材质系统** - 支持纹理和shader属性
- **资源管理** - 统一的资源加载和缓存

### 输入系统
- **平滑相机控制** - SLERP四元数插值
- **WASD移动** - 第一人称相机控制
- **鼠标旋转** - 平滑的视角控制

## 📦 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行演示
```bash
python main.py
```

### 控制说明
- **WASD** - 移动相机
- **鼠标左键+拖拽** - 旋转相机视角

## 🎮 演示场景

当前演示包含：
- 🔷 **立方体模型** - 左侧，从OBJ文件加载，带光照效果
- 🔺 **金字塔模型** - 右侧，带旋转，展示法线光照
- 🔸 **小立方体** - 金字塔上方，展示父子关系

## 🔧 API使用

### 加载3D模型
```python
from resource_manager.file_resource_manager import FileResourceManager
from Context.context import global_data as GD

# 获取资源管理器
resource_manager = GD.resource_manager

# 加载3D模型 - 自动生成8个float格式顶点数据
mesh = resource_manager.load_mesh_from_file("resources/models/cube.obj")

# 添加到游戏对象
if mesh:
    ecs.add_component(game_object, mesh)
```

### 访问顶点数据
```python
# 获取顶点信息
vertex_count = mesh.get_vertex_count()
positions = mesh.get_positions()    # 位置数据
normals = mesh.get_normals()        # 法线数据  
uvs = mesh.get_uvs()               # 纹理坐标

# 顶点格式信息
vertex_info = mesh.get_vertex_info()
print(f"Stride: {vertex_info['stride']}")  # 8个float
```

### 创建游戏对象
```python
# 创建游戏对象
player = ecs.create_entity(GameObject, name="Player")

# 设置变换
player.transform.position = [0.0, 0.0, -5.0]
player.transform.rotation = [0.0, 45.0, 0.0]
player.transform.scale = [1.0, 1.0, 1.0]

# 添加组件
ecs.add_component(player, mesh)
ecs.add_component(player, material)
```

### 父子关系
```python
# 设置父子关系
child.set_parent(parent, world_position_stays=False)
```

## 📁 项目结构

```
MiniPyEngine/
├── components/          # 组件系统
│   ├── mesh.py         # 网格组件 (8个float格式)
│   ├── material.py     # 材质组件
│   └── transform.py    # 变换组件
├── resource_manager/    # 资源管理
│   └── file_resource_manager.py  # 文件资源管理器
├── resources/
│   ├── models/         # 3D模型文件
│   │   ├── cube.obj    # 立方体示例
│   │   └── pyramid.obj # 金字塔示例
│   ├── shaders/        # 着色器文件 (支持法线)
│   └── textures/       # 纹理文件
├── graphics/           # 渲染系统
├── systems/            # 系统
├── tests/              # 测试文件
├── util/               # 工具类
└── main.py            # 主程序
```

## 🧪 测试

### 运行3D模型加载测试
```bash
python tests/test_obj_loader.py
```

### 运行平滑旋转测试
```bash
python tests/test_smooth_rotation.py
```

## 🛠️ 支持的文件格式

### 3D模型
- **OBJ** (.obj) - ✅ 完全支持
  - 顶点坐标 (v)
  - 法线向量 (vn)
  - 纹理坐标 (vt)
  - 面定义 (f)
  - 自动三角化
  - 统一输出：8个float格式

### 纹理
- **PNG, JPG, BMP** - 通过OpenGL支持

### 着色器
- **GLSL** - 顶点和片段着色器，支持法线光照

## 🎯 顶点数据格式

MiniPyEngine使用统一的顶点数据格式：

```
每个顶点包含8个float值:
[x, y, z, nx, ny, nz, u, v]
 |  |  |   |   |   |  |  |
 位置坐标   法线向量   纹理坐标
```

### 特性
- **位置** (x, y, z) - 3D世界坐标
- **法线** (nx, ny, nz) - 用于光照计算
- **纹理坐标** (u, v) - 纹理映射

### 优势
- 统一格式，简化渲染管线
- 支持现代光照效果
- 高效的GPU渲染
- 便于数据处理和调试

## 🎯 设计目标

MiniPyEngine的设计目标是：

1. **教育友好** - 清晰的代码结构，便于学习游戏引擎原理
2. **现代化** - 使用现代的图形API和数学库
3. **实用性** - 支持真实的3D资产和工作流程
4. **简洁性** - 统一的数据格式，减少复杂性

## 🔮 未来计划

- [ ] **更多3D格式** - PLY, STL, glTF支持
- [ ] **高级光照** - 镜面反射、点光源、聚光灯
- [ ] **动画系统** - 骨骼动画和关键帧
- [ ] **物理系统** - 基础的碰撞检测
- [ ] **音频系统** - 3D空间音效
- [ ] **GUI系统** - 游戏内用户界面
- [ ] **场景编辑器** - 可视化场景编辑

## 📄 许可证

MIT License - 详见 LICENSE 文件

---

🎮 **Happy Coding!** 享受游戏引擎开发的乐趣！
