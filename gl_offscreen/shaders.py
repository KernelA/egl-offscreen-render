VERTEX_SHADER = """
#version 150

in vec3 vertex_pos;
in vec4 a_color;

out vec4 v_color;

uniform mat4 projection;

void main()
{
   gl_Position = projection * vec4(vertex_pos, 1.0f);
   gl_Position.y *= -1; // invert texture for saving
   v_color = a_color;
}
"""

FRAGMENT_SHADER = """
#version 150

in vec4 v_color;

void main()
{
   gl_FragColor = v_color;
}
"""
