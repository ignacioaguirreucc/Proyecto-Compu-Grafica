#version 330 core

// Entrada: posición y coordenadas UV del quad
in vec2 in_pos;
in vec2 in_uv;

// Salida hacia el fragment shader
out vec2 v_uv;

void main() {
    // Posición en pantalla (ya no se aplica matriz MVP)
    gl_Position = vec4(in_pos, 0.0, 1.0);
    v_uv = in_uv;
}
