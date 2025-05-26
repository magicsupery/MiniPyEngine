# MiniPyEngine 变更日志

本文档记录 MiniPyEngine 项目的所有重要变更和版本更新。

---

## [2024-12-19] - v0.2.0 - 3D资产加载系统

### 🚀 新增功能
- **3D模型加载系统**: 在FileResourceManager中添加`load_mesh_from_file()`方法支持OBJ文件加载
- **完整OBJ解析**: 实现顶点、法线、纹理坐标、面数据的完整解析
- **智能缓存机制**: 添加双层缓存系统 - 原始模型数据缓存(`mesh_cache`) + Mesh组件缓存(`mesh_map`)
- **自动优化处理**: 支持自动顶点去重、三角化和索引生成
- **基础光照系统**: 更新着色器支持法线输入，实现环境光+方向光漫反射

### 🔧 改进优化
- **统一顶点格式**: 简化Mesh组件，统一使用8个float顶点格式 `[x,y,z,nx,ny,nz,u,v]`
- **渲染器增强**: 更新OpenGL渲染器支持法线属性和动态顶点格式处理
- **架构优化**: 移除VertexFormat枚举，不再兼容旧数据格式，简化代码复杂度
- **测试重组**: 移动测试文件从`tools/`到`tests/`目录，更新API调用方式

### 🐛 问题修复
- 修复顶点数据格式不一致导致的渲染问题
- 完善OBJ文件解析的错误处理机制
- 修正多种OBJ格式变体的兼容性问题

### 📁 文件变更

#### 新增文件:
- `docs/changelog.md` - 项目变更日志
- `.cursorrules` - Cursor AI开发规则文件
- `tests/test_obj_loader.py` - OBJ加载器综合测试

#### 主要修改:
- `resource_manager/file_resource_manager.py` - 添加完整的3D模型加载功能
- `components/mesh.py` - 简化为统一8float格式，添加数据提取方法
- `graphics/opengl_renderer.py` - 支持法线渲染和基础光照
- `graphics/shaders/vertex_shader.glsl` - 添加法线输入
- `graphics/shaders/fragment_shader.glsl` - 实现基础光照计算
- `main.py` - 更新为使用资源管理器加载模型
- `README.md` - 完善3D资产加载功能文档

#### 删除文件:
- `components/model_loader.py` - 替换为资源管理器方案
- `tools/obj_loader_test.py` - 移至tests目录
- `docs/3D_ASSET_LOADING.md` - 整合到主文档
- `docs/3D_DEMO_GUIDE.md` - 不再需要
- `3D_ASSET_UPGRADE_SUMMARY.md` - 临时文档
- `tests/test_mesh_compatibility.py` - 不再需要兼容性测试

### 🎯 技术亮点
- **Unity风格API**: 参考Unity的资源管理模式设计文件加载接口
- **教育友好**: 清晰的代码结构和丰富的注释，便于学习3D图形编程
- **现代化渲染**: 支持法线的光照计算，提升视觉效果
- **缓存优化**: 避免重复加载相同文件，提升性能

### 🧪 测试覆盖
- OBJ文件解析和加载功能
- 缓存机制验证
- 多种OBJ格式兼容性
- 数据提取和格式转换
- 错误处理和边界情况

---

## [历史版本] - v0.1.0 - 基础引擎框架

### 🚀 初始功能
- **ECS架构**: 实体-组件-系统基础框架
- **Transform系统**: 3D变换支持，包含父子关系和四元数旋转
- **基础渲染**: OpenGL渲染管线和着色器系统
- **输入系统**: 键盘鼠标输入处理和相机控制
- **资源管理**: 纹理和着色器的基础加载管理

### 📁 核心文件
- 核心ECS系统 (`core/`, `Entity/`, `components/`, `systems/`)
- 渲染系统 (`graphics/`)
- 输入处理 (`input/`)
- 资源管理 (`resource_manager/`)
- 数学工具 (`util/`)

---

## 📋 开发规范

### 变更日志格式说明
- **🚀 新增功能**: 全新的功能特性
- **🔧 改进优化**: 对现有功能的改进和优化
- **🐛 问题修复**: Bug修复和错误处理
- **📁 文件变更**: 文件的新增、修改、删除
- **🎯 技术亮点**: 重要的技术实现和设计决策
- **🧪 测试覆盖**: 测试相关的更新和验证

### Unity参考标准
本项目在架构设计和API设计上尽可能参考Unity引擎的实现模式，以提供熟悉的开发体验和学习价值。 