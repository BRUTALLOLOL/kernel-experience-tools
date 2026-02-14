from setuptools import setup, find_packages, Extension
import pybind11
import numpy as np
import sys

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Fix for Windows debug/release library conflict
compile_args = ['-O3', '-std=c++11']
link_args = []

if sys.platform == 'win32':
    # Force release mode on Windows to avoid pythonXYt.lib
    compile_args.append('/MD')
    # Explicitly tell linker to use release python library
    link_args.append('/NODEFAULTLIB:python{}t.lib'.format(sys.version_info.major))
    link_args.append('/DEFAULTLIB:python{}.lib'.format(sys.version_info.major))

# C++ module for fast Volterra solver
cpp_module = Extension(
    'kernel_experience._solvers_cpp',
    sources=['src/kernel_experience/solvers.cpp'],
    include_dirs=[pybind11.get_include(), np.get_include()],
    language='c++',
    extra_compile_args=compile_args,
    extra_link_args=link_args,
)

setup(
    name="kernel-experience-tools",
    version="1.0.0",  # 🚀 First stable release with C++ backend
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
