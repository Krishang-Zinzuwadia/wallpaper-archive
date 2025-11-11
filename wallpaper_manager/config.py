"""
Configuration management for Wallpaper Manager
"""

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

import tomli_w
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Application configuration"""
    storage_path: Path
    current_wallpaper_id: Optional[str] = None
    wallpaper_backend: str = "auto"
    thumbnail_size: Tuple[int, int] = (200, 150)
    grid_columns: int = 5

    def __post_init__(self):
        """Ensure storage_path is a Path object"""
        if not isinstance(self.storage_path, Path):
            self.storage_path = Path(self.storage_path)

    @classmethod
    def get_default_storage_path(cls) -> Path:
        """Get the default storage path for wallpapers"""
        return Path.home() / ".local" / "share" / "wallpaper-manager"

    @classmethod
    def get_config_file_path(cls) -> Path:
        """Get the configuration file path"""
        return cls.get_default_storage_path() / "config.toml"

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Config":
        """
        Load configuration from TOML file
        
        Args:
            config_path: Path to config file, defaults to standard location
            
        Returns:
            Config instance with loaded or default values
        """
        if config_path is None:
            config_path = cls.get_config_file_path()

        if not config_path.exists():
            logger.info(f"Config file not found at {config_path}, using defaults")
            return cls(storage_path=cls.get_default_storage_path())

        try:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
            
            # Convert storage_path string to Path
            if "storage_path" in data:
                data["storage_path"] = Path(data["storage_path"])
            else:
                data["storage_path"] = cls.get_default_storage_path()
            
            # Convert thumbnail_size list to tuple
            if "thumbnail_size" in data:
                data["thumbnail_size"] = tuple(data["thumbnail_size"])
            
            logger.info(f"Loaded configuration from {config_path}")
            return cls(**data)
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            logger.info("Using default configuration")
            return cls(storage_path=cls.get_default_storage_path())

    def save(self, config_path: Optional[Path] = None) -> None:
        """
        Save configuration to TOML file
        
        Args:
            config_path: Path to save config file, defaults to standard location
        """
        if config_path is None:
            config_path = self.get_config_file_path()

        # Ensure parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Convert to dict and handle Path serialization
            data = asdict(self)
            data["storage_path"] = str(data["storage_path"])
            data["thumbnail_size"] = list(data["thumbnail_size"])
            
            # Remove None values as TOML doesn't support them
            data = {k: v for k, v in data.items() if v is not None}
            
            with open(config_path, "wb") as f:
                tomli_w.dump(data, f)
            
            logger.info(f"Saved configuration to {config_path}")
        except Exception as e:
            logger.error(f"Failed to save config to {config_path}: {e}")
            raise

    def initialize_storage(self) -> None:
        """
        Initialize storage directory structure
        Creates necessary directories if they don't exist
        """
        directories = [
            self.storage_path,
            self.storage_path / "wallpapers",
            self.storage_path / "thumbnails",
        ]

        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Initialized directory: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                raise
