#!/usr/bin/env python3
"""
Integration test for Selector Interface
Tests the selector interface with actual wallpaper data
"""

import tempfile
import shutil
from pathlib import Path
from PIL import Image

from wallpaper_manager.config import Config
from wallpaper_manager.manager import WallpaperManager
from wallpaper_manager.ui import SelectorInterface


def create_test_image(path: Path, width: int = 800, height: int = 600, color: tuple = (100, 150, 200)):
    """Create a test image file"""
    img = Image.new('RGB', (width, height), color)
    img.save(path, 'JPEG')


def test_selector_interface():
    """Test selector interface with mock data"""
    print("Testing Selector Interface...")
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test configuration
        config = Config(storage_path=temp_path)
        config.initialize_storage()
        
        # Create wallpaper manager
        manager = WallpaperManager(config)
        
        # Create and import test images
        print("Creating test wallpapers...")
        for i in range(5):
            test_image = temp_path / f"test_image_{i}.jpg"
            create_test_image(test_image, color=(i*50, 100, 200-i*30))
            
            try:
                wallpaper = manager.import_from_file(test_image)
                print(f"  ✓ Imported test wallpaper {i+1}: {wallpaper.id[:8]}...")
            except Exception as e:
                print(f"  ✗ Failed to import test wallpaper {i+1}: {e}")
                return False
        
        # Verify wallpapers were imported
        wallpapers = manager.get_all_wallpapers()
        print(f"\n✓ Total wallpapers in collection: {len(wallpapers)}")
        
        if len(wallpapers) != 5:
            print(f"✗ Expected 5 wallpapers, got {len(wallpapers)}")
            return False
        
        # Test selector interface creation (without showing UI)
        print("\nTesting SelectorInterface instantiation...")
        try:
            selector = SelectorInterface(manager)
            print("✓ SelectorInterface created successfully")
            
            # Verify wallpapers are loaded
            if selector.wallpaper_grid:
                print("✓ Wallpaper grid initialized")
            else:
                print("✗ Wallpaper grid not initialized")
                return False
            
            # Test that current wallpaper tracking works
            if selector.current_wallpaper_id is None:
                print("✓ No current wallpaper set (expected)")
            else:
                print(f"✓ Current wallpaper: {selector.current_wallpaper_id[:8]}...")
            
        except Exception as e:
            print(f"✗ Failed to create SelectorInterface: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n✓ All tests passed!")
    return True


if __name__ == "__main__":
    import sys
    success = test_selector_interface()
    sys.exit(0 if success else 1)
