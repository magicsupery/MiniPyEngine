#version 300 es
precision mediump float;

layout(location = 0) in vec3 inPosition;
// 假设纹理坐标使用 location = 1
layout(location = 1) in vec2 inTexCoord;

// 传递给 Fragment Shader
out vec2 TexCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    TexCoord = inTexCoord;  // 将顶点的纹理坐标传给片段着色器
    gl_Position = projection * view * model * vec4(inPosition, 1.0);
}
