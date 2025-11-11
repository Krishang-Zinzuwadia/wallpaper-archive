"""
Wallpaper Manager Core - Business logic for wallpaper management
"""

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

import tomli_w
import hashlib
import logging
import shutil
import requests
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from PIL import Image

from .models import Wallpaper
from .config import Config
from .backends import WallpaperBackend, get_backend

logger = logging.getLogger(__name__)


class WallpaperManager:
    """Core wallpaper management functionality"""

    SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".webp"}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    def __init__(self, config: Config, backend: Optional[WallpaperBackend] = None):
        """Initialize WallpaperManager"""
        self.config = config
        self.config.initialize_storage()
        
        if backend is None:
            backend = self._detect_backend()
        self.backend = backend
        
        self._wallpapers: Dict[str, Wallpaper] = {}
        self._load_collection()

    def _detect_backend(self) -> WallpaperBackend:
        """Detect and instantiate appropriate wallpaper backend"""
        try:
            return get_backend(self.config.wallpaper_backend)
        except Exception as e:
            logger.error(f"Failed to initialize backend: {e}")
            raise RuntimeError(f"Failed to initialize wallpaper backend: {e}") from e

    def _get_collection_file(self) -> Path:
        """Get path to wallpaper collection metadata file"""
        return self.config.storage_path / "collection.toml"

    def _load_collection(self) -> None:
        """Load wallpaper collection from TOML file"""
        collection_file = self._get_collection_file()
        
        if not collection_file.exists():
            logger.info("No existing collection found, starting fresh")
            self._wallpapers = {}
            return
        
        try:
            with open(collection_file, "rb") as f:
                data = tomllib.load(f)
            
            self._wallpapers = {}
            for wp_id, wp_data in data.get("wallpapers", {}).items():
                try:
                    wallpaper = Wallpaper.from_dict(wp_data)
                    self._wallpapers[wp_id] = wallpaper
                except Exception as e:
                    logger.error(f"Failed to load wallpaper {wp_id}: {e}")
            
            logger.info(f"Loaded {len(self._wallpapers)} wallpapers from collection")
        except Exception as e:
            logger.error(f"Failed to load collection: {e}")
            self._wallpapers = {}

    def _save_collection(self) -> None:
        """Save wallpaper collection to TOML file"""
        collection_file = self._get_collection_file()
        
        try:
            data = {
                "wallpapers": {
                    wp_id: wp.to_dict()
                    for wp_id, wp in self._wallpapers.items()
                }
            }
            
            with open(collection_file, "wb") as f:
                tomli_w.dump(data, f)
            
            logger.info(f"Saved {len(self._wallpapers)} wallpapers to collection")
        except Exception as e:
            logger.error(f"Failed to save collection: {e}")
            raise

    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _validate_image(self, file_path: Path) -> tuple[int, int]:
        """Validate image file and get dimensions"""
        if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported image format: {file_path.suffix}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        file_size = file_path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(
                f"File too large: {file_size / 1024 / 1024:.1f}MB. "
                f"Maximum size: {self.MAX_FILE_SIZE / 1024 / 1024:.0f}MB"
            )
        
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                img.verify()
            return width, height
        except Exception as e:
            raise ValueError(f"Invalid or corrupted image file: {e}")


    def import_from_file(self, file_path: Path, original_url: Optional[str] = None) -> Wallpaper:
        """
        Import wallpaper from local file
        
        Args:
            file_path: Path to local image file
            original_url: Optional URL if file was downloaded
            
        Returns:
            Imported Wallpaper instance
            
        Raises:
            ValueError: If file is invalid
            RuntimeError: If import process fails
        """
        logger.info(f"Importing wallpaper from file: {file_path}")
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Validate image and get dimensions
        width, height = self._validate_image(file_path)
        
        # Calculate hash for unique ID
        file_hash = self._calculate_hash(file_path)
        
        # Check if already imported
        if file_hash in self._wallpapers:
            logger.info(f"Wallpaper already exists: {file_hash}")
            return self._wallpapers[file_hash]
        
        # Determine target filename with proper extension
        extension = file_path.suffix.lower()
        target_filename = f"{file_hash}{extension}"
        target_path = self.config.storage_path / "wallpapers" / target_filename
        
        # Copy file to wallpapers directory
        try:
            shutil.copy2(file_path, target_path)
            logger.info(f"Copied wallpaper to: {target_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to copy wallpaper file: {e}")
        
        # Generate thumbnail
        thumbnail_path = self.generate_thumbnail(target_path, file_hash)
        
        # Create Wallpaper instance
        wallpaper = Wallpaper(
            id=file_hash,
            file_path=target_path,
            thumbnail_path=thumbnail_path,
            original_url=original_url,
            added_date=datetime.now(),
            last_used=None,
            width=width,
            height=height,
            file_size=target_path.stat().st_size
        )
        
        # Add to collection and save
        self._wallpapers[file_hash] = wallpaper
        self._save_collection()
        
        logger.info(f"Successfully imported wallpaper: {file_hash}")
        return wallpaper

    def import_from_url(self, url: str) -> Wallpaper:
        """
        Download and import wallpaper from URL
        
        Args:
            url: URL of the image to download
            
        Returns:
            Imported Wallpaper instance
            
        Raises:
            ValueError: If URL is invalid or download fails
            RuntimeError: If import process fails
        """
        logger.info(f"Importing wallpaper from URL: {url}")
        
        temp_file = self.config.storage_path / f"temp_{datetime.now().timestamp()}"
        
        try:
            # Download with timeout and size limit
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                raise ValueError(f"URL does not point to an image (content-type: {content_type})")
            
            # Download with size limit
            downloaded_size = 0
            with open(temp_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    downloaded_size += len(chunk)
                    if downloaded_size > self.MAX_FILE_SIZE:
                        raise ValueError(f"File too large (>{self.MAX_FILE_SIZE / 1024 / 1024:.0f}MB)")
                    f.write(chunk)
            
            # Determine file extension
            extension = None
            if "png" in content_type:
                extension = ".png"
            elif "jpeg" in content_type or "jpg" in content_type:
                extension = ".jpg"
            elif "webp" in content_type:
                extension = ".webp"
            else:
                url_path = Path(url.split("?")[0])
                if url_path.suffix.lower() in self.SUPPORTED_FORMATS:
                    extension = url_path.suffix.lower()
                else:
                    extension = ".jpg"
            
            # Rename temp file with proper extension
            temp_file_with_ext = temp_file.with_suffix(extension)
            temp_file.rename(temp_file_with_ext)
            temp_file = temp_file_with_ext
            
            # Import the downloaded file
            wallpaper = self.import_from_file(temp_file, original_url=url)
            
            # Clean up temp file
            temp_file.unlink()
            
            logger.info(f"Successfully imported wallpaper from URL: {wallpaper.id}")
            return wallpaper
            
        except requests.RequestException as e:
            if temp_file.exists():
                temp_file.unlink()
            raise ValueError(f"Failed to download image: {e}")
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            raise


    def generate_thumbnail(self, image_path: Path, image_hash: str) -> Path:
        """
        Generate thumbnail for wallpaper image
        
        Args:
            image_path: Path to original image
            image_hash: Hash ID of the image
            
        Returns:
            Path to generated thumbnail
            
        Raises:
            RuntimeError: If thumbnail generation fails
        """
        thumbnail_filename = f"{image_hash}.jpg"
        thumbnail_path = self.config.storage_path / "thumbnails" / thumbnail_filename
        
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ("RGBA", "LA", "P"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                    img = background
                elif img.mode != "RGB":
                    img = img.convert("RGB")
                
                # Calculate thumbnail size maintaining aspect ratio
                thumb_width, thumb_height = self.config.thumbnail_size
                img.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
                
                # Create letterboxed thumbnail
                thumbnail = Image.new("RGB", (thumb_width, thumb_height), (0, 0, 0))
                offset_x = (thumb_width - img.width) // 2
                offset_y = (thumb_height - img.height) // 2
                thumbnail.paste(img, (offset_x, offset_y))
                
                # Save thumbnail
                thumbnail.save(thumbnail_path, "JPEG", quality=85)
                logger.info(f"Generated thumbnail: {thumbnail_path}")
                
            return thumbnail_path
            
        except Exception as e:
            logger.error(f"Failed to generate thumbnail: {e}")
            raise RuntimeError(f"Failed to generate thumbnail: {e}")

    def get_all_wallpapers(self) -> List[Wallpaper]:
        """
        Get all wallpapers in the collection
        
        Returns:
            List of Wallpaper instances
        """
        return list(self._wallpapers.values())

    def set_wallpaper(self, wallpaper: Wallpaper) -> None:
        """
        Apply wallpaper and update metadata
        
        Args:
            wallpaper: Wallpaper to apply
            
        Raises:
            RuntimeError: If wallpaper setting fails
        """
        logger.info(f"Setting wallpaper: {wallpaper.id}")
        
        # Apply wallpaper using backend
        self.backend.set_wallpaper(wallpaper.file_path)
        
        # Update last_used timestamp
        wallpaper.last_used = datetime.now()
        
        # Update current wallpaper in config
        self.config.current_wallpaper_id = wallpaper.id
        self.config.save()
        
        # Save collection with updated metadata
        self._save_collection()
        
        logger.info(f"Wallpaper set successfully: {wallpaper.id}")

    def get_current_wallpaper(self) -> Optional[Wallpaper]:
        """
        Get the currently active wallpaper
        
        Returns:
            Current Wallpaper instance or None
        """
        if self.config.current_wallpaper_id:
            return self._wallpapers.get(self.config.current_wallpaper_id)
        return None
