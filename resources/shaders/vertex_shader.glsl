#version 300 es
precision mediump float;

layout(location = 0) in vec3 inPosition;
layout(location = 1) in vec3 inNormal;    // 新增：法线输入
layout(location = 2) in vec2 inTexCoord;  // 调整：纹理坐标改为location 2

// 传递给 Fragment Shader
out vec2 TexCoord;
out vec3 Normal;        // 新增：传递法线到片段着色器
out vec3 FragPos;       // 新增：传递世界坐标位置

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    // 计算世界坐标位置
    FragPos = vec3(model * vec4(inPosition, 1.0));
    
    // 计算世界坐标下的法线（需要使用法线矩阵）
    Normal = mat3(transpose(inverse(model))) * inNormal;
    
    // 传递纹理坐标
    TexCoord = inTexCoord;
    
    gl_Position = projection * view * model * vec4(inPosition, 1.0);
}
