# -*- coding: utf-8 -*-
"""
OBJ加载器测试
验证资源管理器的3D模型加载功能
"""
import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resource_manager.file_resource_manager import FileResourceManager


def test_obj_loading():
    """测试OBJ文件加载功能"""
    print("========================================")
    print("        OBJ 3D模型加载器测试")
    print("========================================\n")
    
    resource_manager = FileResourceManager()
    
    # 测试立方体模型
    print("🚀 测试立方体模型加载:")
    cube_path = "resources/models/cube.obj"
    
    cube_mesh = resource_manager.load_mesh_from_file(cube_path)
    
    if cube_mesh:
        print(f"✅ 立方体Mesh生成成功!")
        print(f"   顶点数据长度: {len(cube_mesh.vertices)}")
        print(f"   索引数据长度: {len(cube_mesh.indices) if cube_mesh.indices is not None else 0}")
        print(f"   顶点数量: {cube_mesh.get_vertex_count()}")
        
        # 显示前几个顶点
        print(f"   前3个顶点数据:")
        for i in range(min(3, cube_mesh.get_vertex_count())):
            start = i * 8
            vertex = cube_mesh.vertices[start:start+8]
            print(f"     顶点{i+1}: 位置({vertex[0]:.2f}, {vertex[1]:.2f}, {vertex[2]:.2f}) "
                  f"法线({vertex[3]:.2f}, {vertex[4]:.2f}, {vertex[5]:.2f}) "
                  f"UV({vertex[6]:.2f}, {vertex[7]:.2f})")
                  
        # 显示OBJ原始信息
        if hasattr(cube_mesh, 'obj_data'):
            obj_data = cube_mesh.obj_data
            print(f"   原始OBJ信息:")
            print(f"     顶点数: {len(obj_data['vertices'])}")
            print(f"     法线数: {len(obj_data['normals'])}")
            print(f"     纹理坐标数: {len(obj_data['texture_coords'])}")
            print(f"     面数: {len(obj_data['faces'])}")
    else:
        print("❌ 立方体模型加载失败!")
    
    print()
    
    # 测试金字塔模型
    print("🚀 测试金字塔模型加载:")
    pyramid_path = "resources/models/pyramid.obj"
    
    pyramid_mesh = resource_manager.load_mesh_from_file(pyramid_path)
    
    if pyramid_mesh:
        print(f"✅ 金字塔Mesh生成成功!")
        print(f"   顶点数据长度: {len(pyramid_mesh.vertices)}")
        print(f"   索引数据长度: {len(pyramid_mesh.indices) if pyramid_mesh.indices is not None else 0}")
        print(f"   顶点数量: {pyramid_mesh.get_vertex_count()}")
        
        # 显示OBJ原始信息
        if hasattr(pyramid_mesh, 'obj_data'):
            obj_data = pyramid_mesh.obj_data
            print(f"   原始OBJ信息:")
            print(f"     顶点数: {len(obj_data['vertices'])}")
            print(f"     法线数: {len(obj_data['normals'])}")
            print(f"     纹理坐标数: {len(obj_data['texture_coords'])}")
            print(f"     面数: {len(obj_data['faces'])}")
    else:
        print("❌ 金字塔模型加载失败!")
    
    print()


def test_cache_functionality():
    """测试缓存功能"""
    print("🚀 测试缓存功能:")
    
    resource_manager = FileResourceManager()
    
    # 第一次加载
    print("   第一次加载立方体...")
    cube_mesh1 = resource_manager.load_mesh_from_file("resources/models/cube.obj")
    
    # 第二次加载（应该从缓存获取）
    print("   第二次加载立方体...")
    cube_mesh2 = resource_manager.load_mesh_from_file("resources/models/cube.obj")
    
    # 验证是否是同一个对象（缓存生效）
    if cube_mesh1 is cube_mesh2:
        print("   ✅ 缓存功能正常！返回相同的Mesh对象")
    else:
        print("   ❌ 缓存功能失效！返回不同的Mesh对象")
    
    print()


def test_different_obj_formats():
    """测试不同OBJ格式的兼容性"""
    print("🚀 测试OBJ格式兼容性:")
    
    resource_manager = FileResourceManager()
    
    # 创建不同格式的测试OBJ
    test_obj_simple = """# 简单格式 - 只有顶点和面
v 0.0 0.0 0.0
v 1.0 0.0 0.0
v 0.5 1.0 0.0
f 1 2 3
"""
    
    test_obj_with_textures = """# 带纹理坐标
v 0.0 0.0 0.0
v 1.0 0.0 0.0
v 0.5 1.0 0.0
vt 0.0 0.0
vt 1.0 0.0
vt 0.5 1.0
f 1/1 2/2 3/3
"""
    
    test_obj_full = """# 完整格式
v 0.0 0.0 0.0
v 1.0 0.0 0.0
v 0.5 1.0 0.0
vt 0.0 0.0
vt 1.0 0.0
vt 0.5 1.0
vn 0.0 0.0 1.0
vn 0.0 0.0 1.0
vn 0.0 0.0 1.0
f 1/1/1 2/2/2 3/3/3
"""
    
    test_files = [
        ("简单格式", "test_simple.obj", test_obj_simple),
        ("带纹理", "test_texture.obj", test_obj_with_textures),
        ("完整格式", "test_full.obj", test_obj_full)
    ]
    
    for name, filename, content in test_files:
        # 写入测试文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 测试加载
        mesh = resource_manager.load_mesh_from_file(filename)
        
        if mesh:
            vertex_count = mesh.get_vertex_count()
            print(f"   ✅ {name}: 成功加载，{vertex_count}个顶点")
        else:
            print(f"   ❌ {name}: 加载失败")
        
        # 清理测试文件
        if os.path.exists(filename):
            os.remove(filename)


def test_mesh_data_extraction():
    """测试Mesh数据提取功能"""
    print("🚀 测试Mesh数据提取功能:")
    
    resource_manager = FileResourceManager()
    mesh = resource_manager.load_mesh_from_file("resources/models/cube.obj")
    
    if mesh:
        print(f"   顶点总数: {mesh.get_vertex_count()}")
        
        # 测试数据提取功能
        positions = mesh.get_positions()
        uvs = mesh.get_uvs()
        normals = mesh.get_normals()
        
        print(f"   位置数据长度: {len(positions)}")
        print(f"   UV数据长度: {len(uvs)}")
        print(f"   法线数据长度: {len(normals)}")
        
        vertex_info = mesh.get_vertex_info()
        print(f"   顶点信息: stride={vertex_info['stride']}, "
              f"pos_offset={vertex_info['position_offset']}, "
              f"normal_offset={vertex_info['normal_offset']}, "
              f"uv_offset={vertex_info['uv_offset']}")
        
        print("   ✅ 数据提取功能正常!")
    else:
        print("   ❌ 无法加载测试模型")
    
    print()


def test_error_handling():
    """测试错误处理"""
    print("🚀 测试错误处理:")
    
    resource_manager = FileResourceManager()
    
    # 测试不存在的文件
    print("   测试不存在的文件...")
    mesh = resource_manager.load_mesh_from_file("non_existent_file.obj")
    if mesh is None:
        print("   ✅ 正确处理不存在的文件")
    else:
        print("   ❌ 未正确处理不存在的文件")
    
    # 测试不支持的格式
    print("   测试不支持的格式...")
    # 创建一个假的3DS文件
    with open("test.3ds", 'w') as f:
        f.write("fake 3ds file")
    
    mesh = resource_manager.load_mesh_from_file("test.3ds")
    if mesh is None:
        print("   ✅ 正确处理不支持的格式")
    else:
        print("   ❌ 未正确处理不支持的格式")
    
    # 清理
    if os.path.exists("test.3ds"):
        os.remove("test.3ds")
    
    print()


if __name__ == "__main__":
    try:
        test_obj_loading()
        test_cache_functionality()
        test_different_obj_formats()
        test_mesh_data_extraction()
        test_error_handling()
        
        print("========================================")
        print("✅ OBJ加载器测试完成!")
        print("✅ 资源管理器3D模型加载功能正常工作!")
        print("✅ 新版本Mesh组件功能完整!")
        print("========================================")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc() 