"""
Wallpaper backend abstraction layer for different display servers
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import subprocess
import logging

logger = logging.getLogger(__name__)


class WallpaperBackend(ABC):
    """Abstract base class for wallpaper backends"""

    @abstractmethod
    def set_wallpaper(self, image_path: Path) -> None:
        """
        Set the desktop wallpaper to the specified image
        
        Args:
            image_path: Path to the wallpaper image file
            
        Raises:
            FileNotFoundError: If the image file doesn't exist
            RuntimeError: If wallpaper setting fails
        """
        pass

    @abstractmethod
    def get_current_wallpaper(self) -> Optional[Path]:
        """
        Get the path to the currently set wallpaper
        
        Returns:
            Path to current wallpaper, or None if unable to determine
        """
        pass


class FehBackend(WallpaperBackend):
    """Wallpaper backend for X11 systems using feh"""

    def set_wallpaper(self, image_path: Path) -> None:
        """
        Set wallpaper using feh with --bg-scale option
        
        Args:
            image_path: Path to the wallpaper image file
            
        Raises:
            FileNotFoundError: If the image file doesn't exist
            RuntimeError: If feh command fails
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Wallpaper image not found: {image_path}")
        
        try:
            # Use feh with --bg-scale to set wallpaper
            subprocess.run(
                ["feh", "--bg-scale", str(image_path)],
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"Set wallpaper using feh: {image_path}")
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to set wallpaper with feh: {e.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        except FileNotFoundError:
            error_msg = "feh command not found. Please install feh."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def get_current_wallpaper(self) -> Optional[Path]:
        """
        Get current wallpaper by parsing ~/.fehbg file
        
        Returns:
            Path to current wallpaper, or None if unable to determine
        """
        fehbg_path = Path.home() / ".fehbg"
        
        if not fehbg_path.exists():
            logger.debug("~/.fehbg file not found")
            return None
        
        try:
            with open(fehbg_path, "r") as f:
                content = f.read()
            
            # Parse the feh command from .fehbg
            # Typical format: feh --bg-scale '/path/to/wallpaper.jpg'
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("feh") and "--bg-" in line:
                    # Extract the image path (last argument, typically quoted)
                    parts = line.split()
                    if parts:
                        # Get the last part and remove quotes
                        image_path_str = parts[-1].strip("'\"")
                        image_path = Path(image_path_str)
                        if image_path.exists():
                            logger.debug(f"Current wallpaper from .fehbg: {image_path}")
                            return image_path
            
            logger.debug("Could not parse wallpaper path from .fehbg")
            return None
        except Exception as e:
            logger.error(f"Error reading .fehbg file: {e}")
            return None


class SwaybgBackend(WallpaperBackend):
    """Wallpaper backend for Wayland systems using swaybg"""

    def __init__(self):
        """Initialize SwaybgBackend"""
        self._current_process = None
        self._current_wallpaper = None

    def set_wallpaper(self, image_path: Path) -> None:
        """
        Set wallpaper using swaybg for Wayland compositors
        
        Args:
            image_path: Path to the wallpaper image file
            
        Raises:
            FileNotFoundError: If the image file doesn't exist
            RuntimeError: If swaybg command fails
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Wallpaper image not found: {image_path}")
        
        try:
            # Kill existing swaybg process if running
            if self._current_process is not None:
                try:
                    self._current_process.terminate()
                    self._current_process.wait(timeout=2)
                except Exception as e:
                    logger.warning(f"Failed to terminate previous swaybg process: {e}")
            
            # Kill any existing swaybg processes
            try:
                subprocess.run(
                    ["pkill", "swaybg"],
                    capture_output=True,
                    timeout=2
                )
            except Exception:
                pass  # Ignore if pkill fails or swaybg not running
            
            # Start new swaybg process in background
            self._current_process = subprocess.Popen(
                ["swaybg", "-i", str(image_path), "-m", "fill"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            
            # Store current wallpaper path
            self._current_wallpaper = image_path
            logger.info(f"Set wallpaper using swaybg: {image_path}")
            
        except FileNotFoundError:
            error_msg = "swaybg command not found. Please install swaybg."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Failed to set wallpaper with swaybg: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def get_current_wallpaper(self) -> Optional[Path]:
        """
        Get current wallpaper path
        
        Returns:
            Path to current wallpaper, or None if unable to determine
        """
        return self._current_wallpaper


def detect_display_server() -> str:
    """
    Detect the current display server type
    
    Returns:
        'x11' for X11, 'wayland' for Wayland, or 'unknown'
    """
    import os
    
    # Check XDG_SESSION_TYPE environment variable
    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
    if session_type == "wayland":
        logger.info("Detected Wayland via XDG_SESSION_TYPE")
        return "wayland"
    elif session_type == "x11":
        logger.info("Detected X11 via XDG_SESSION_TYPE")
        return "x11"
    
    # Check WAYLAND_DISPLAY environment variable
    if os.environ.get("WAYLAND_DISPLAY"):
        logger.info("Detected Wayland via WAYLAND_DISPLAY")
        return "wayland"
    
    # Check DISPLAY environment variable
    if os.environ.get("DISPLAY"):
        logger.info("Detected X11 via DISPLAY")
        return "x11"
    
    logger.warning("Could not detect display server type")
    return "unknown"


def get_backend(backend_name: str = "auto") -> WallpaperBackend:
    """
    Get wallpaper backend instance
    
    Args:
        backend_name: Backend name ('auto', 'feh', 'swaybg')
        
    Returns:
        WallpaperBackend instance
        
    Raises:
        RuntimeError: If backend cannot be determined or created
    """
    if backend_name == "auto":
        display_server = detect_display_server()
        if display_server == "x11":
            backend_name = "feh"
        elif display_server == "wayland":
            backend_name = "swaybg"
        else:
            logger.warning("Could not detect display server, defaulting to feh")
            backend_name = "feh"
    
    if backend_name == "feh":
        logger.info("Using FehBackend for X11")
        return FehBackend()
    elif backend_name == "swaybg":
        logger.info("Using SwaybgBackend for Wayland")
        return SwaybgBackend()
    else:
        raise RuntimeError(f"Unknown backend: {backend_name}")
