from setuptools import setup, find_packages
import pybind11
from pybind11.setup_helpers import Pybind11Extension, build_ext
import numpy as np
import sys
import platform

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
compile_args = []
link_args = []

if sys.platform == 'win32':
    compile_args = ['/O2', '/MD']
    py_version = f"{sys.version_info.major}{sys.version_info.minor}"
    link_args = [
        f'/NODEFAULTLIB:python{py_version}t.lib',
        f'/DEFAULTLIB:python{py_version}.lib'
    ]
else:
    compile_args = ['-O3', '-fPIC']

    pybind11_version = tuple(map(int, pybind11.__version__.split('.')[:2]))
    if pybind11_version >= (2, 13):
        compile_args.append('-std=c++17')
    else:
        compile_args.append('-std=c++11')

cpp_module = Pybind11Extension(
    'kernel_experience._solvers_cpp',
    sources=['src/kernel_experience/solvers.cpp'],
    include_dirs=[np.get_include()],
    language='c++',
    extra_compile_args=compile_args,
    extra_link_args=link_args,
)

setup(
    name="kernel-experience-tools",
    version="1.0.1",
    author="Artem Vozmishchev",
    author_email="xbrutallololx@gmail.com",
    description="Library for projecting memory kernels to experience functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BRUTALLOLOL/kernel-experience-tools",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=[
        "numpy",
        "scipy>=1.6.0",
        "matplotlib>=3.3.0",
    ],
    ext_modules=[cpp_module],
    cmdclass={"build_ext": build_ext},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    include_package_data=True,
    zip_safe=False,
)
