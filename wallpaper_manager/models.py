"""
Data models for Wallpaper Manager
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Wallpaper:
    """Wallpaper data model"""
    id: str  # SHA256 hash of image
    file_path: Path
    thumbnail_path: Path
    original_url: Optional[str]
    added_date: datetime
    last_used: Optional[datetime]
    width: int
    height: int
    file_size: int

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Wallpaper to dictionary for TOML serialization
        
        Returns:
            Dictionary representation with serializable types
        """
        data = asdict(self)
        # Convert Path objects to strings
        data["file_path"] = str(self.file_path)
        data["thumbnail_path"] = str(self.thumbnail_path)
        # Convert datetime objects to ISO format strings
        data["added_date"] = self.added_date.isoformat()
        if self.last_used:
            data["last_used"] = self.last_used.isoformat()
        else:
            # Remove None values as TOML doesn't support them
            del data["last_used"]
        
        # Remove original_url if None
        if data.get("original_url") is None:
            del data["original_url"]
        
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Wallpaper":
        """
        Create Wallpaper instance from dictionary (TOML deserialization)
        
        Args:
            data: Dictionary with wallpaper data
            
        Returns:
            Wallpaper instance
        """
        # Convert string paths back to Path objects
        data["file_path"] = Path(data["file_path"])
        data["thumbnail_path"] = Path(data["thumbnail_path"])
        # Convert ISO format strings back to datetime objects
        data["added_date"] = datetime.fromisoformat(data["added_date"])
        data["last_used"] = datetime.fromisoformat(data["last_used"]) if data.get("last_used") else None
        # Handle optional original_url
        if "original_url" not in data:
            data["original_url"] = None
        return cls(**data)
