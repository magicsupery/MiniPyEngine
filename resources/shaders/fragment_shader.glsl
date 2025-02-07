#version 300 es
precision mediump float;

// 从 Vertex Shader 传递过来的纹理坐标
in vec2 TexCoord;

// Fragment Shader 输出的颜色
out vec4 outColor;

// 纹理采样器（对应 OpenGL 中的 GL_TEXTURE_2D）
uniform sampler2D MainTex;

void main()
{
    // 使用传递过来的纹理坐标来采样纹理的颜色
    outColor = texture(MainTex, TexCoord);
}
