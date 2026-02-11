from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip()]

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
    
    # Requirements
    python_requires=">=3.7",
    install_requires=requirements,
    
    # Metadata
    classifiers=[
        "Programming Language :: Python :: 3",
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
