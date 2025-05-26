#version 300 es
precision mediump float;

// 从 Vertex Shader 传递过来的数据
in vec2 TexCoord;
in vec3 Normal;
in vec3 FragPos;

// Fragment Shader 输出的颜色
out vec4 outColor;

// 纹理采样器
uniform sampler2D MainTex;

void main()
{
    // 基本的环境光和方向光照明
    vec3 lightDir = normalize(vec3(0.5, 1.0, 0.3));  // 方向光方向
    vec3 lightColor = vec3(1.0, 1.0, 1.0);           // 白色光
    vec3 ambient = vec3(0.3, 0.3, 0.3);              // 环境光
    
    // 归一化法线
    vec3 norm = normalize(Normal);
    
    // 计算漫反射
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;
    
    // 采样纹理颜色
    vec4 texColor = texture(MainTex, TexCoord);
    
    // 最终颜色 = (环境光 + 漫反射) * 纹理颜色
    vec3 lighting = ambient + diffuse;
    outColor = vec4(lighting * texColor.rgb, texColor.a);
}
