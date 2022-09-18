from typing import Tuple
import ctypes

import numpy as np
import OpenGL.EGL as egl
from OpenGL.raw.EGL.EXT.platform_device import EGL_PLATFORM_DEVICE_EXT
from OpenGL.EGL.EXT.device_base import egl_get_devices
from OpenGL import error
from OpenGL.GL import *


def create_initialized_headless_egl_display():
    """Creates an initialized EGL display directly on a device.
    """
    for device in egl_get_devices():
        display = egl.eglGetPlatformDisplayEXT(
            EGL_PLATFORM_DEVICE_EXT, device, None)

        if display != egl.EGL_NO_DISPLAY and egl.eglGetError() == egl.EGL_SUCCESS:
            # `eglInitialize` may or may not raise an exception on failure depending
            # on how PyOpenGL is configured. We therefore catch a `GLError` and also
            # manually check the output of `eglGetError()` here.
            try:
                initialized = egl.eglInitialize(display, None, None)
            except error.GLError:
                pass
            else:
                if initialized == egl.EGL_TRUE and egl.eglGetError() == egl.EGL_SUCCESS:
                    return display
    return egl.EGL_NO_DISPLAY


def create_opengl_context(surface_size: Tuple[int, int]):
    """Create offscreen OpenGL context and make it current.

    Users are expected to directly use EGL API in case more advanced

    context management is required.

    Args:
        surface_size: (width, height), size of the offscreen rendering surface.

    """
    egl_display = create_initialized_headless_egl_display()

    if egl_display == egl.EGL_NO_DISPLAY:
        raise RuntimeError('Cannot initialize a headless EGL display.')

    major, minor = egl.EGLint(), egl.EGLint()

    egl.eglInitialize(egl_display, ctypes.pointer(
        major), ctypes.pointer(minor))

    config_attribs = [
        egl.EGL_SURFACE_TYPE, egl.EGL_PBUFFER_BIT, egl.EGL_BLUE_SIZE, 8,
        egl.EGL_GREEN_SIZE, 8, egl.EGL_RED_SIZE, 8, egl.EGL_DEPTH_SIZE, 24,
        egl.EGL_RENDERABLE_TYPE, egl.EGL_OPENGL_BIT, egl.EGL_NONE
    ]
    config_attribs = (egl.EGLint * len(config_attribs))(*config_attribs)

    num_configs = egl.EGLint()
    egl_cfg = egl.EGLConfig()

    egl.eglChooseConfig(egl_display, config_attribs, ctypes.pointer(egl_cfg), 1,
                        ctypes.pointer(num_configs))

    width, height = surface_size

    pbuffer_attribs = [
        egl.EGL_WIDTH,
        width,
        egl.EGL_HEIGHT,
        height,
        egl.EGL_NONE,
    ]
    pbuffer_attribs = (egl.EGLint * len(pbuffer_attribs))(*pbuffer_attribs)
    egl_surf = egl.eglCreatePbufferSurface(
        egl_display, egl_cfg, pbuffer_attribs)

    egl.eglBindAPI(egl.EGL_OPENGL_API)

    egl_context = egl.eglCreateContext(
        egl_display, egl_cfg, egl.EGL_NO_CONTEXT, None)

    egl.eglMakeCurrent(egl_display, egl_surf, egl_surf, egl_context)

    return egl_display, egl_surf, egl_context


def init_frame_buffer(frame_image: np.ndarray, num_samples: int = 16):
    """Create an FBO and assign a texture buffer to it for the purpose of offscreen rendering to the texture buffer
    """
    samples = min(num_samples, GL_SAMPLES - 1)

    width = frame_image.shape[1]
    height = frame_image.shape[0]

    if frame_image.shape[-1] == 3:
        texture_type = GL_RGB
        internal_texture_type = GL_RGB8
    elif frame_image.shape[-1] == 4:
        texture_type = GL_RGBA
        internal_texture_type = GL_RGBA8

    render_texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, render_texture)
    glTexImage2D(GL_TEXTURE_2D, 0, internal_texture_type, width,
                 height, 0, texture_type, GL_UNSIGNED_BYTE, None)

    glBindTexture(GL_TEXTURE_2D, 0)

    render_frame_object = glGenFramebuffers(1)

    glBindFramebuffer(GL_FRAMEBUFFER, render_frame_object)

    # Create color render buffer
    color_buffer = glGenRenderbuffers(1)

    glBindRenderbuffer(GL_RENDERBUFFER, color_buffer)
    glRenderbufferStorage(
        GL_RENDERBUFFER, internal_texture_type, width, height)
    glFramebufferRenderbuffer(
        GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, color_buffer)

    glFramebufferTexture2D(
        GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, render_texture, 0)

    glBindRenderbuffer(GL_RENDERBUFFER, 0)

    # Sees if your GPU can handle the FBO configuration defined above
    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        raise RuntimeError(
            "Framebuffer binding failed, probably because your GPU does not support this FBO configuration.")

    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    multisample_texture = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, multisample_texture)
    glTexImage2DMultisample(GL_TEXTURE_2D_MULTISAMPLE, samples,
                            internal_texture_type, width, height, GL_FALSE)
    glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, 0)

    render_frame_ms_object = glGenFramebuffers(1)

    glBindFramebuffer(GL_FRAMEBUFFER, render_frame_ms_object)

    color_buffer_ms = glGenRenderbuffers(1)

    glBindRenderbuffer(GL_RENDERBUFFER, color_buffer_ms)
    glRenderbufferStorageMultisample(
        GL_RENDERBUFFER, samples, internal_texture_type, width, height)
    glFramebufferRenderbuffer(
        GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, color_buffer_ms)

    glFramebufferTexture2D(
        GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D_MULTISAMPLE, multisample_texture, 0)

    glBindRenderbuffer(GL_RENDERBUFFER, 0)

    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        raise RuntimeError(
            "Framebuffer binding failed, probably because your GPU does not support this FBO configuration.")

    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    return render_frame_object, render_frame_ms_object
