"""
Main entry point for Wallpaper Manager
"""

import sys
import logging
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib

from wallpaper_manager.config import Config
from wallpaper_manager.controller import MainController
from wallpaper_manager.logging_config import setup_logging, get_default_log_file


class WallpaperManagerApp(Gtk.Application):
    """GTK Application wrapper for Wallpaper Manager"""
    
    def __init__(self):
        super().__init__(application_id='com.wallpaper_manager.app')
        self.controller = None
        self.logger = logging.getLogger(__name__)
    
    def do_activate(self):
        """Called when the application is activated"""
        self.logger.info("Application activated")
        
        # Show Import Popup on activation
        if self.controller:
            self.controller.show_import_popup()
    
    def do_startup(self):
        """Called when the application starts"""
        Gtk.Application.do_startup(self)
        self.logger.info("Application starting up")
        
        try:
            # Load or create configuration
            config = Config.load()
            
            # Initialize storage directories
            config.initialize_storage()
            
            # Save configuration if it's new
            if not Config.get_config_file_path().exists():
                config.save()
                self.logger.info("Created default configuration")
            
            self.logger.info(f"Storage path: {config.storage_path}")
            self.logger.info(f"Wallpaper backend: {config.wallpaper_backend}")
            
            # Initialize main controller
            self.controller = MainController(config)
            self.logger.info("MainController initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize application: {e}", exc_info=True)
            sys.exit(1)
    
    def do_shutdown(self):
        """Called when the application shuts down"""
        self.logger.info("Application shutting down")
        
        # Cleanup controller
        if self.controller:
            self.controller.shutdown()
        
        Gtk.Application.do_shutdown(self)


def main():
    """Main application entry point"""
    # Initialize logging
    setup_logging(
        log_level="INFO",
        log_file=get_default_log_file(),
        console_output=True
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Wallpaper Manager")
    
    # Create and run GTK application
    app = WallpaperManagerApp()
    exit_status = app.run(sys.argv)
    
    logger.info(f"Application exited with status: {exit_status}")
    sys.exit(exit_status)


if __name__ == "__main__":
    main()
