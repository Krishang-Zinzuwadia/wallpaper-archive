#!/usr/bin/env python3
"""
Test script to verify the application can start without errors
"""

import sys
import logging
from pathlib import Path

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from wallpaper_manager.config import Config
        print("✅ Config imported")
    except Exception as e:
        print(f"❌ Failed to import Config: {e}")
        return False
    
    try:
        from wallpaper_manager.models import Wallpaper
        print("✅ Models imported")
    except Exception as e:
        print(f"❌ Failed to import Models: {e}")
        return False
    
    try:
        from wallpaper_manager.backends import WallpaperBackend, FehBackend, detect_display_server
        print("✅ Backends imported")
    except Exception as e:
        print(f"❌ Failed to import Backends: {e}")
        return False
    
    try:
        from wallpaper_manager.manager import WallpaperManager
        print("✅ Manager imported")
    except Exception as e:
        print(f"❌ Failed to import Manager: {e}")
        return False
    
    try:
        from wallpaper_manager.logging_config import setup_logging
        print("✅ Logging config imported")
    except Exception as e:
        print(f"❌ Failed to import Logging config: {e}")
        return False
    
    try:
        from wallpaper_manager.controller import MainController
        print("✅ Controller imported")
    except Exception as e:
        print(f"❌ Failed to import Controller: {e}")
        return False
    
    try:
        from wallpaper_manager.ui.import_popup import ImportPopup
        print("✅ Import Popup imported")
    except Exception as e:
        print(f"❌ Failed to import Import Popup: {e}")
        return False
    
    try:
        from wallpaper_manager.ui.selector_interface import SelectorInterface
        print("✅ Selector Interface imported")
    except Exception as e:
        print(f"❌ Failed to import Selector Interface: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from wallpaper_manager.config import Config
        
        # Test default storage path
        storage_path = Config.get_default_storage_path()
        print(f"✅ Default storage path: {storage_path}")
        
        # Test config file path
        config_path = Config.get_config_file_path()
        print(f"✅ Config file path: {config_path}")
        
        # Test loading config (will use defaults if not exists)
        config = Config.load()
        print(f"✅ Config loaded: storage_path={config.storage_path}")
        
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_detection():
    """Test backend detection"""
    print("\nTesting backend detection...")
    
    try:
        from wallpaper_manager.backends import detect_display_server
        
        display_server = detect_display_server()
        print(f"✅ Detected display server: {display_server}")
        
        return True
    except Exception as e:
        print(f"❌ Backend detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_manager_initialization():
    """Test WallpaperManager initialization"""
    print("\nTesting WallpaperManager initialization...")
    
    try:
        from wallpaper_manager.config import Config
        from wallpaper_manager.manager import WallpaperManager
        
        config = Config.load()
        manager = WallpaperManager(config)
        
        print(f"✅ WallpaperManager initialized")
        print(f"   Storage path: {config.storage_path}")
        print(f"   Backend: {manager.backend.__class__.__name__}")
        
        # Test getting wallpapers (should be empty initially)
        wallpapers = manager.get_all_wallpapers()
        print(f"✅ Found {len(wallpapers)} wallpapers in collection")
        
        return True
    except Exception as e:
        print(f"❌ Manager initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gtk_availability():
    """Test GTK availability"""
    print("\nTesting GTK availability...")
    
    try:
        import gi
        gi.require_version('Gtk', '4.0')
        from gi.repository import Gtk
        
        print(f"✅ GTK 4.0 is available")
        print(f"   GTK version: {Gtk.get_major_version()}.{Gtk.get_minor_version()}.{Gtk.get_micro_version()}")
        
        return True
    except Exception as e:
        print(f"❌ GTK test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Wallpaper Manager Startup Test")
    print("=" * 60)
    print()
    
    all_ok = True
    
    # Run tests
    all_ok &= test_imports()
    all_ok &= test_config()
    all_ok &= test_backend_detection()
    all_ok &= test_manager_initialization()
    all_ok &= test_gtk_availability()
    
    print()
    print("=" * 60)
    
    if all_ok:
        print("✅ All tests passed!")
        print("\nThe application should be ready to run.")
        print("\nTo start the application:")
        print("  python3 -m wallpaper_manager")
        print("\nTo start the daemon:")
        print("  python3 -m wallpaper_manager.daemon")
        return 0
    else:
        print("❌ Some tests failed!")
        print("\nPlease fix the issues above before running the application.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
