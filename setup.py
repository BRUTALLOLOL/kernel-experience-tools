from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

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
    
    # Python compatibility
    python_requires=">=3.7",
    
    # Dependencies - pip will handle version compatibility
    install_requires=[
        "numpy",
        "scipy>=1.6.0",
        "matplotlib>=3.3.0",
    ],
    
    # PyPI metadata
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
    
    # Build options
    include_package_data=True,
    zip_safe=False,
)
