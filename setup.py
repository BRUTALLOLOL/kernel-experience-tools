from setuptools import setup, find_packages
import sys

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Auto-detect Python version for appropriate dependency ranges
python_version = sys.version_info

if python_version.major == 3:
    if python_version.minor >= 12:
        # Python 3.12+ supports NumPy 2.0+
        numpy_req = "numpy>=2.0.0"
        scipy_req = "scipy>=1.13.0"
        matplotlib_req = "matplotlib>=3.8.0"
    elif python_version.minor >= 8:
        # Python 3.8-3.11: NumPy 1.x
        numpy_req = "numpy>=1.21.0,<2.0.0"
        scipy_req = "scipy>=1.6.0"
        matplotlib_req = "matplotlib>=3.3.0"
    else:
        # Python 3.7 (minimum supported)
        numpy_req = "numpy>=1.19.0,<2.0.0"
        scipy_req = "scipy>=1.6.0"
        matplotlib_req = "matplotlib>=3.3.0"
else:
    # Fallback for unexpected Python versions
    numpy_req = "numpy>=1.19.0"
    scipy_req = "scipy>=1.6.0"
    matplotlib_req = "matplotlib>=3.3.0"

setup(
    name="kernel-experience-tools",
    version="0.1.0",
    author="Artem Vozmishchev",
    author_email="xbrutallololx@gmail.com",
    description="Library for projecting memory kernels to experience functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BRUTALLOLOL/kernel-experience-tools",
    
    # Package structure
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    
    # Python version requirement
    python_requires=">=3.7",
    
    # Dynamic dependencies based on Python version
    install_requires=[
        numpy_req,
        scipy_req,
        matplotlib_req,
    ],
    
    # PyPI classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
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
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    # Keywords for PyPI search
    keywords=[
        "memory-kernels",
        "experience-functions",
        "scientific-computing",
        "mathematics",
        "physics",
        "data-analysis",
    ],
    
    # Build options
    include_package_data=True,
    zip_safe=False,
    
    # Optional: package data files
    package_data={
        "kernel_experience": ["*.txt", "*.md", "*.yaml", "*.json"],
    },
    
    # Optional: command-line interface
    # entry_points={
    #     "console_scripts": [
    #         "kernel-experience=kernel_experience.cli:main",
    #     ],
    # },
    
    # License
    license="MIT",
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/BRUTALLOLOL/kernel-experience-tools/issues",
        "Source": "https://github.com/BRUTALLOLOL/kernel-experience-tools",
        "Documentation": "https://github.com/BRUTALLOLOL/kernel-experience-tools#readme",
    },
)

