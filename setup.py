from setuptools import setup, find_packages
import os

# Read the contents of README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

# Get version from package __init__.py
def get_version():
    init_path = os.path.join(os.path.dirname(__file__), "src", "kernel_experience", "__init__.py")
    if os.path.exists(init_path):
        with open(init_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip("'\"")
    return "0.1.0"

setup(
    # Basic package information
    name="kernel-experience-tools",
    version=get_version(),
    author="Artem Vozmishchev",
    author_email="xbrutallololx@gmail.com",
    description="Library for projecting memory kernels to experience functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BRUTALLOLOL/kernel-experience-tools",
    
    # Package structure - using explicit package name to ensure correct installation
    packages=["kernel_experience"],
    package_dir={"kernel_experience": "src/kernel_experience"},
    
    # Alternatively, if you want automatic package discovery:
    # package_dir={"": "src"},
    # packages=find_packages(where="src"),
    
    # Python version requirements
    python_requires=">=3.7",
    
    # Dependencies
    install_requires=read_requirements() or [
        "numpy>=1.19.0",
        "scipy>=1.6.0",
        "matplotlib>=3.3.0",
    ],
    
    # PyPI classifiers for better discoverability
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    # Keywords for PyPI search
    keywords=["memory-kernels", "experience-functions", "scientific-computing", "mathematics", "physics"],
    
    # Build options
    include_package_data=True,
    zip_safe=False,
    
    # Optional: Additional files to include
    package_data={
        "kernel_experience": ["*.txt", "*.md", "*.yaml", "*.json"],
    },
    
    # Optional: Entry points for command-line tools
    # entry_points={
    #     "console_scripts": [
    #         "kernel-experience=kernel_experience.cli:main",
    #     ],
    # },
    
    # Optional: Test suite
    # test_suite="tests",
    # tests_require=["pytest>=6.0"],
    
    # Optional: Development dependencies
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
        ],
    },
    
    # License information
    license="MIT",
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/BRUTALLOLOL/kernel-experience-tools/issues",
        "Source": "https://github.com/BRUTALLOLOL/kernel-experience-tools",
        "Documentation": "https://github.com/BRUTALLOLOL/kernel-experience-tools#readme",
    },
)
