from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kernel-experience-tools",
    version="0.1.0",
    author="Artem Vozmishchev",
    author_email="your.email@example.com",
    description="Library for projecting memory kernels to experience functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BRUTALLOLOL/kernel-experience-tools",
    
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "scipy>=1.6.0",
        "matplotlib>=3.3.0",
    ],
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    
    include_package_data=True,
    zip_safe=False,
)
