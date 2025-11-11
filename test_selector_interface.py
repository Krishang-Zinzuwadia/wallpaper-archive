#!/usr/bin/env python3
"""
Test script for Selector Interface UI
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib

from wallpaper_manager.config import Config
from wallpaper_manager.manager import WallpaperManager
from wallpaper_manager.ui import SelectorInterface
from wallpaper_manager.logging_config import setup_logging


def on_close():
    """Handle window close"""
    print("Selector interface closed")
    # Don't quit the app, just close the window


def on_activate(app):
    """Handle application activation"""
    # Set up logging
    setup_logging()
    
    # Load configuration
    config = Config.load()
    
    # Initialize wallpaper manager
    manager = WallpaperManager(config)
    
    # Create selector interface
    selector = SelectorInterface(manager, on_close=on_close)
    selector.set_application(app)
    selector.present()
    
    print("Selector interface opened")
    print(f"Loaded {len(manager.get_all_wallpapers())} wallpapers")


def main():
    """Main entry point"""
    app = Gtk.Application(application_id="com.example.wallpaper_manager.selector_test")
    app.connect("activate", on_activate)
    app.run(None)


if __name__ == "__main__":
    main()
