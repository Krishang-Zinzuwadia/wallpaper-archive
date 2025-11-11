"""
Unit tests for WallpaperManager core functionality
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from PIL import Image

from wallpaper_manager.manager import WallpaperManager
from wallpaper_manager.config import Config
from wallpaper_manager.models import Wallpaper


class TestWallpaperManager(unittest.TestCase):
    """Test WallpaperManager core functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.test_storage = Path(self.test_dir) / "storage"
        self.config = Config(storage_path=self.test_storage)
        
        # Mock backend
        self.mock_backend = Mock()
        self.manager = WallpaperManager(self.config, backend=self.mock_backend)

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_test_image(self, filename: str, size=(800, 600)) -> Path:
        """Create a test image file"""
        image_path = Path(self.test_dir) / filename
        img = Image.new("RGB", size, color="red")
        img.save(image_path)
        return image_path

    def test_import_from_file(self):
        """Test importing wallpaper from local file"""
        test_image = self._create_test_image("test.jpg")
        
        wallpaper = self.manager.import_from_file(test_image)
        
        self.assertIsNotNone(wallpaper)
        self.assertEqual(wallpaper.width, 800)
        self.assertEqual(wallpaper.height, 600)
        self.assertTrue(wallpaper.file_path.exists())
        self.assertTrue(wallpaper.thumbnail_path.exists())
        self.assertIsNone(wallpaper.original_url)

    def test_import_from_file_with_url(self):
        """Test importing downloaded file with original URL"""
        test_image = self._create_test_image("test.png")
        test_url = "https://example.com/wallpaper.png"
        
        wallpaper = self.manager.import_from_file(test_image, original_url=test_url)
        
        self.assertEqual(wallpaper.original_url, test_url)

    def test_import_duplicate_file(self):
        """Test importing the same file twice returns existing wallpaper"""
        test_image = self._create_test_image("test.jpg")
        
        wallpaper1 = self.manager.import_from_file(test_image)
        wallpaper2 = self.manager.import_from_file(test_image)
        
        self.assertEqual(wallpaper1.id, wallpaper2.id)

    @patch('wallpaper_manager.manager.requests.get')
    def test_import_from_url(self, mock_get):
        """Test importing wallpaper from URL with mocked HTTP request"""
        test_image = self._create_test_image("test.jpg")
        
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "image/jpeg"}
        mock_response.raise_for_status = Mock()
        
        with open(test_image, "rb") as f:
            image_data = f.read()
        
        mock_response.iter_content = Mock(return_value=[image_data])
        mock_get.return_value = mock_response
        
        test_url = "https://example.com/wallpaper.jpg"
        wallpaper = self.manager.import_from_url(test_url)
        
        self.assertIsNotNone(wallpaper)
        self.assertEqual(wallpaper.original_url, test_url)
        mock_get.assert_called_once()

    def test_thumbnail_generation(self):
        """Test thumbnail generation"""
        test_image = self._create_test_image("test.jpg", size=(1920, 1080))
        
        wallpaper = self.manager.import_from_file(test_image)
        
        self.assertTrue(wallpaper.thumbnail_path.exists())
        
        with Image.open(wallpaper.thumbnail_path) as thumb:
            self.assertEqual(thumb.size, (200, 150))

    def test_get_all_wallpapers(self):
        """Test retrieving all wallpapers"""
        test_image1 = self._create_test_image("test1.jpg")
        test_image2 = self._create_test_image("test2.png")
        
        self.manager.import_from_file(test_image1)
        self.manager.import_from_file(test_image2)
        
        wallpapers = self.manager.get_all_wallpapers()
        
        self.assertEqual(len(wallpapers), 2)

    def test_set_wallpaper(self):
        """Test setting wallpaper and updating metadata"""
        test_image = self._create_test_image("test.jpg")
        wallpaper = self.manager.import_from_file(test_image)
        
        self.assertIsNone(wallpaper.last_used)
        
        self.manager.set_wallpaper(wallpaper)
        
        self.assertIsNotNone(wallpaper.last_used)
        self.assertEqual(self.config.current_wallpaper_id, wallpaper.id)
        self.mock_backend.set_wallpaper.assert_called_once_with(wallpaper.file_path)

    def test_collection_persistence(self):
        """Test that collection is persisted and can be reloaded"""
        test_image = self._create_test_image("test.jpg")
        wallpaper = self.manager.import_from_file(test_image)
        
        # Create new manager instance with same config
        new_manager = WallpaperManager(self.config, backend=self.mock_backend)
        
        wallpapers = new_manager.get_all_wallpapers()
        self.assertEqual(len(wallpapers), 1)
        self.assertEqual(wallpapers[0].id, wallpaper.id)


if __name__ == "__main__":
    unittest.main()
