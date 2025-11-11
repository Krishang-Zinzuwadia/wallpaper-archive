"""
Daemon entry point for Wallpaper Manager keyboard shortcut listener
"""

import sys
import signal
import logging
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib

from wallpaper_manager.config import Config
from wallpaper_manager.controller import MainController
from wallpaper_manager.logging_config import setup_logging, get_default_log_file


class WallpaperManagerDaemon(Gtk.Application):
    """GTK Application for daemon mode"""
    
    def __init__(self):
        super().__init__(application_id='com.wallpaper_manager.daemon')
        self.controller = None
        self.logger = logging.getLogger(__name__)
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down")
        self.quit()
    
    def do_activate(self):
        """Called when the application is activated"""
        # In daemon mode, we don't show any window on activation
        # Windows are only shown when hotkey is pressed
        self.logger.info("Daemon activated (no window shown)")
    
    def do_startup(self):
        """Called when the application starts"""
        Gtk.Application.do_startup(self)
        self.logger.info("Daemon starting up")
        
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
            
            # Initialize main controller with daemon enabled
            self.controller = MainController(config, enable_daemon=True)
            self.logger.info("MainController initialized with keyboard daemon")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize daemon: {e}", exc_info=True)
            sys.exit(1)
    
    def do_shutdown(self):
        """Called when the application shuts down"""
        self.logger.info("Daemon shutting down")
        
        # Cleanup controller
        if self.controller:
            self.controller.shutdown()
        
        Gtk.Application.do_shutdown(self)


def main():
    """Main daemon entry point"""
    # Initialize logging
    setup_logging(
        log_level="INFO",
        log_file=get_default_log_file(),
        console_output=False  # Daemon mode - log to file only
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Wallpaper Manager Daemon")
    
    # Create and run GTK application in daemon mode
    app = WallpaperManagerDaemon()
    exit_status = app.run(sys.argv)
    
    logger.info(f"Daemon exited with status: {exit_status}")
    sys.exit(exit_status)


if __name__ == "__main__":
    main()
