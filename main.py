import argparse
import os

os.environ["PYOPENGL_PLATFORM"] = "egl"

import numpy as np
import OpenGL.EGL as egl
from OpenGL.GL import *
from OpenGL.GL import shaders
from PIL import Image

from gl_offscreen.gl_utils import create_opengl_context, init_frame_buffer
from gl_offscreen.shaders import VERTEX_SHADER, FRAGMENT_SHADER
from gl_offscreen.off_screen_render import VertextAttribType, IndexType, generate_vao, set_shader_params, render


def main(args):
    display, egl_surf, opengl_context = create_opengl_context(
        (args.width, args.height))

    vertex_positions = np.array([
        [0, 0, 0],
        [1, 0, 0],
        [0, 1, 0]
    ], dtype=VertextAttribType)

    vertex_colors = np.array([
        [1, 0, 0, 1],
        [0, 1, 0, 1],
        [0, 0, 1, 1]
    ], dtype=VertextAttribType)

    face_indices = np.array([0, 1, 2], dtype=IndexType)

    num_channels = 3 if args.image_mode == "rgb" else 4
    rendered_image = np.zeros((args.height, args.width, num_channels), dtype=np.uint8)

    mode = "RGB"
    texture_type = GL_RGB

    if num_channels == 4:
        mode = "RGBA"
        texture_type = GL_RGBA

    try:
        glClearColor(0, 0, 0.0, 1.0)
        glEnable(GL_MULTISAMPLE)

        shader = shaders.compileProgram(
            shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
            shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER),)

        vao = generate_vao(vertex_positions, vertex_colors, face_indices)

        glUseProgram(shader)
        # Orto projection in range [0; 1]
        set_shader_params(shader)

        render_frame_object, render_frame_ms_object = init_frame_buffer(rendered_image)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glBindFramebuffer(GL_FRAMEBUFFER, render_frame_ms_object)
        glBindVertexArray(vao)
        render(GL_TRIANGLES, len(face_indices))
        glBindVertexArray(0)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glBindFramebuffer(GL_READ_FRAMEBUFFER, render_frame_ms_object)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, render_frame_object)

        glBlitFramebuffer(0, 0, args.width, args.height, 0, 0, args.width,
                          args.height, GL_COLOR_BUFFER_BIT, GL_NEAREST)

        glBindFramebuffer(GL_READ_FRAMEBUFFER, 0)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
        glBindFramebuffer(GL_FRAMEBUFFER, render_frame_object)
        glReadBuffer(GL_COLOR_ATTACHMENT0)

        data = glReadPixels(0, 0, args.width, args.height, texture_type, GL_UNSIGNED_BYTE)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glUseProgram(shader)

        image = Image.frombuffer(mode, (args.width, args.height), data)
        image.save(args.out_image, optimize=True)
    finally:
        egl.eglDestroySurface(display, egl_surf)
        egl.eglDestroyContext(display, opengl_context)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", dest="width", type=int, default=256)
    parser.add_argument("--height", dest="height", type=int, default=256)
    parser.add_argument("-o", "--out_image", dest="out_image", type=str, default="out.png",
                        help="A path to the output image with render")
    parser.add_argument("--image_mode", choices=["rgb", "rgba"], default="rgb")

    args = parser.parse_args()
    main(args)
