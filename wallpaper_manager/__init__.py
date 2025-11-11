"""
Wallpaper Manager - A modern, transparent wallpaper manager for Arch Linux
"""

__version__ = "1.0.0"
__author__ = "Wallpaper Manager Team"

from .controller import MainController
from .config import Config
from .manager import WallpaperManager

__all__ = ['MainController', 'Config', 'WallpaperManager']
