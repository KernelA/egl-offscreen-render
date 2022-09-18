from OpenGL.GL import *
import numpy as np
import pyrr

VertextAttribType = np.float32
IndexType = np.uint32
OpenglVertexAttrType = GL_FLOAT
OpenglTriangleIndexType = GL_UNSIGNED_INT


def generate_vao(vertex_positions: np.ndarray, vertex_colors: np.ndarray, face_indices: np.ndarray):
    assert vertex_positions.ndim == 2
    assert vertex_positions.shape[1] == 3
    assert vertex_positions.shape == vertex_colors.shape
    assert face_indices.ndim == 1

    face_indices = face_indices.astype(IndexType)

    vertex_attributes = np.hstack(
        (vertex_positions, vertex_colors)).astype(VertextAttribType)

    num_pos_per_vertex = vertex_positions.shape[1]
    num_colors_per_vertex = vertex_colors.shape[1]

    triangle_vao = glGenVertexArrays(1)

    glBindVertexArray(triangle_vao)

    num_properties_per_vertex = vertex_attributes.shape[1]

    triangle_vertex_properties = glGenBuffers(1)

    glBindBuffer(GL_ARRAY_BUFFER, triangle_vertex_properties)
    glBufferData(GL_ARRAY_BUFFER, vertex_attributes.nbytes,
                 vertex_attributes, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, num_pos_per_vertex, OpenglVertexAttrType, GL_FALSE, vertex_attributes.itemsize *
                          num_properties_per_vertex, ctypes.c_void_p(0))

    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, num_colors_per_vertex, OpenglVertexAttrType, GL_FALSE, vertex_attributes.itemsize *
                          num_properties_per_vertex, ctypes.c_void_p(vertex_attributes.itemsize * num_pos_per_vertex))

    triangle_indices = glGenBuffers(1)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, triangle_indices)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, face_indices.nbytes,
                 face_indices, GL_STATIC_DRAW)

    glBindVertexArray(0)

    return triangle_vao


def set_shader_params(shader):
    matrix_proj_loc = glGetUniformLocation(shader, "projection")
    matrix_proj = pyrr.matrix44.create_orthogonal_projection(
        0, 1, 0, 1, -1, 1, dtype=np.float32)
    glUniformMatrix4fv(matrix_proj_loc, 1, GL_FALSE, matrix_proj)


def render(gl_primitive_type, num_elements: int):
    glDrawElements(gl_primitive_type, num_elements, OpenglTriangleIndexType, ctypes.c_void_p(0))
