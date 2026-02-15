from setuptools import setup, find_packages
import pybind11
from pybind11.setup_helpers import Pybind11Extension, build_ext
import numpy as np
import sys
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

compile_args = []
link_args = []

if sys.platform == 'win32':
    # Base Windows compile flags
    compile_args = ['/MD', '/EHsc']  # EHsc enables C++ exception handling
    
    # Check if running in CI environment (GitHub Actions)
    if os.getenv('GITHUB_ACTIONS') == 'true':
        # Conservative flags for CI to prevent timeouts and crashes
        compile_args.insert(0, '/O2')  # Best optimizations
        print("Windows CI detected: using conservative compile flags (/O2)")
    else:
        # Full optimizations for local builds
        compile_args.insert(0, '/O2')  # Maximum optimizations
        print("Local Windows build: using aggressive optimizations (/O2)")
    
    # Python version for linking
    py_version = f"{sys.version_info.major}{sys.version_info.minor}"
    link_args = [
        f'/NODEFAULTLIB:python{py_version}t.lib',
        f'/DEFAULTLIB:python{py_version}.lib'
    ]
    
    # Add debug info in CI for better error reporting
    if os.getenv('GITHUB_ACTIONS') == 'true':
        compile_args.append('/Zi')  # Debug symbols
        link_args.append('/DEBUG')  # Debug information in executable
        
else:
    # Unix-like systems (Linux, macOS)
    compile_args = ['-O3', '-fPIC']
    
    # Detect pybind11 version for C++ standard
    pybind11_version = tuple(map(int, pybind11.__version__.split('.')[:2]))
    if pybind11_version >= (2, 13):
        compile_args.append('-std=c++17')
        print(f"Using C++17 (pybind11 {pybind11.__version__})")
    else:
        compile_args.append('-std=c++11')
        print(f"Using C++11 (pybind11 {pybind11.__version__})")
    
    # Add debugging symbols in CI for Unix as well
    if os.getenv('GITHUB_ACTIONS') == 'true':
        compile_args.append('-g')  # Debug symbols
        print("CI detected: adding debug symbols")

print(f"Compile flags: {compile_args}")
print(f"Link flags: {link_args}")

# C++ module for Volterra solver (original)
solver_module = Pybind11Extension(
    'kernel_experience._solvers_cpp', 
    sources=['src/kernel_experience/solvers.cpp'],
    include_dirs=[np.get_include()],
    language='c++',
    extra_compile_args=compile_args,
    extra_link_args=link_args,
)

# NEW: C++ module for projection acceleration
projection_module = Pybind11Extension(
    'kernel_experience._projection_cpp',
    sources=['src/kernel_experience/projection.cpp'],
    include_dirs=[np.get_include()],
    language='c++',
    extra_compile_args=compile_args,
    extra_link_args=link_args,
)

setup(
    name="kernel-experience-tools",
    version="1.1.2",  
    author="Artem Vozmishchev",
    author_email="xbrutallololx@gmail.com",
    description="Library for projecting memory kernels to experience functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BRUTALLOLOL/kernel-experience-tools",
    license="MIT", 
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0", 
        "scipy>=1.6.0",
        "matplotlib>=3.3.0",
    ],
    ext_modules=[solver_module, projection_module], 
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



