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

    # Ключевое исправление: используем src/ layout
    package_dir={"": "src"},
    packages=find_packages(where="src"),

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "scipy>=1.6.0",
        "matplotlib>=3.3.0",
    ],

    # Опционально: точки входа для CLI
    entry_points={
        "console_scripts": [
            "kernel-experience=kernel_experience.cli:main",
        ],
    } if False else {},  # пока отключено, можно включить позже

    # Для лучшей поддержки pip
    include_package_data=True,
    zip_safe=False,
)