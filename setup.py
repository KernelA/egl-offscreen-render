from setuptools import setup, find_packages

with open("requirements.txt", encoding="utf-8") as file:
      req_list = list(filter(lambda x: len(x) > 0, map(str.strip, file.readlines())))

setup(name="egl_rendering",
      packages=find_packages(include=["gl_offscreen*"])
      version="0.0.1",
      author="KernelA",
      author_email= "None",
      license="MIT",
      install_requires=req_list,
      py_modules=["main"],
      python_requires=">=3.8",
      )
