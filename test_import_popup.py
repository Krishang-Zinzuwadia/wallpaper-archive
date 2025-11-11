#!/usr/bin/env python3
"""
Test script for Import Popup UI
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
import sys
import logging

from wallpaper_manager.config import Config
from wallpaper_manager.manager import WallpaperManager
from wallpaper_manager.ui import ImportPopup
from wallpaper_manager.logging_config import setup_logging


def on_confirm_callback():
    """Callback when user confirms imports"""
    print("User confirmed imports!")
    # In real application, this would transition to Selector Interface


def on_activate(app):
    """Application activation handler"""
    # Initialize configuration
    config = Config.load()
    config.initialize_storage()
    
    # Initialize wallpaper manager
    wallpaper_manager = WallpaperManager(config)
    
    # Create and show Import Popup
    popup = ImportPopup(wallpaper_manager, on_confirm=on_confirm_callback)
    popup.set_application(app)
    popup.present()


def main():
    """Main entry point"""
    # Setup logging
    setup_logging(log_level="INFO", console_output=True)
    
    # Create GTK application
    app = Gtk.Application(application_id="com.wallpaper_manager.test")
    app.connect("activate", on_activate)
    
    # Run application
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
