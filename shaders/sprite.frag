#version 330 core

// Textura a muestrear (la generada por el compute shader)
uniform sampler2D u_texture;

// Coordenadas UV recibidas desde el vertex shader
in vec2 v_uv;

// Color final del fragmento
out vec4 f_color;

void main() {
    // Tomar el color desde la textura
    f_color = texture(u_texture, v_uv);
}
