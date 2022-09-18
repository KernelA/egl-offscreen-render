# OpenGL offscreen rendering with EGL and antialiasing

## Description

This repository demonstrates an example of rendering with OpenGL without a display manager.

[![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/gist/KernelA/3658aabaf858748eecf9396d3d3b1bde/egl_offscreen_rednering.ipynb)

## Requirements

1. Python 3.7 or higher.
2. Driver for videocard with [EGL 1.5](https://registry.khronos.org/EGL/specs/eglspec.1.5.pdf)
3. OpenGL 3.2 or higher

## How to run

Install dependencies:
```
pip install -r. /requirements.txt
```

For development:
```
pip install -r ./requirements.txt -r ./requirements.dev.txt
```

Run:
```
python ./main.py --out_image ./render.jpg
```

