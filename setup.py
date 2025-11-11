"""
Setup script for Wallpaper Manager
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README if it exists
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="wallpaper-manager",
    version="1.0.0",
    author="Wallpaper Manager Team",
    description="A modern, transparent wallpaper manager for Arch Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "PyGObject>=3.42",
        "Pillow>=10.0",
        "requests>=2.31",
        "tomli-w>=1.0",
        "python-xlib>=0.33",
    ],
    entry_points={
        "console_scripts": [
            "wallpaper-manager=wallpaper_manager.__main__:main",
            "wallpaper-manager-daemon=wallpaper_manager.daemon:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Desktop Environment",
    ],
)
