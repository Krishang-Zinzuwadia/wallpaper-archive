"""
Main Controller - Coordinates application state and window management
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
import logging
from typing import Optional, TYPE_CHECKING

from .config import Config
from .manager import WallpaperManager
from .ui.import_popup import ImportPopup
from .ui.selector_interface import SelectorInterface

# Lazy import for keyboard_daemon to avoid requiring python-xlib at module load time
if TYPE_CHECKING:
    from .keyboard_daemon import KeyboardDaemon

logger = logging.getLogger(__name__)


class MainController:
    """
    Main application controller that manages window lifecycle and coordinates
    transitions between Import Popup and Selector Interface
    """

    def __init__(self, config: Config, enable_daemon: bool = False):
        """
        Initialize MainController
        
        Args:
            config: Application configuration
            enable_daemon: Whether to enable keyboard daemon (default: False)
        """
        self.config = config
        self.wallpaper_manager = WallpaperManager(config)
        
        # Track active windows
        self._import_popup: Optional[ImportPopup] = None
        self._selector_interface: Optional[SelectorInterface] = None
        
        # Track which window is currently active
        self._active_window: Optional[str] = None  # 'import' or 'selector'
        
        # Keyboard daemon (optional)
        self._daemon: Optional['KeyboardDaemon'] = None
        self._daemon_enabled = enable_daemon
        
        if self._daemon_enabled:
            self._initialize_daemon()
        
        logger.info("MainController initialized")

    def show_import_popup(self) -> None:
        """
        Show the Import Popup window
        
        If the window is already open, bring it to focus.
        Otherwise, create a new window instance.
        """
        logger.info("Showing Import Popup")
        
        # If Import Popup already exists and is visible, bring to focus
        if self._import_popup is not None and self._import_popup.is_visible():
            logger.debug("Import Popup already open, bringing to focus")
            self._import_popup.present()
            self._active_window = 'import'
            return
        
        # Create new Import Popup window
        self._import_popup = ImportPopup(
            wallpaper_manager=self.wallpaper_manager,
            on_confirm=self._on_import_confirmed
        )
        
        # Set the application for the window (important for GTK Application lifecycle)
        from gi.repository import Gtk
        app = Gtk.Application.get_default()
        if app:
            self._import_popup.set_application(app)
        
        # Connect destroy signal to clean up reference
        self._import_popup.connect('close-request', self._on_import_popup_closed)
        
        # Show the window
        self._import_popup.present()
        self._active_window = 'import'
        
        logger.info("Import Popup window created and shown")

    def show_selector_interface(self) -> None:
        """
        Show the Selector Interface window
        
        If the window is already open, bring it to focus.
        Otherwise, create a new window instance.
        """
        logger.info("Showing Selector Interface")
        
        # If Selector Interface already exists and is visible, bring to focus
        if self._selector_interface is not None and self._selector_interface.is_visible():
            logger.debug("Selector Interface already open, bringing to focus")
            self._selector_interface.present()
            self._active_window = 'selector'
            return
        
        # Create new Selector Interface window
        self._selector_interface = SelectorInterface(
            wallpaper_manager=self.wallpaper_manager,
            on_close=self._on_selector_closed
        )
        
        # Set the application for the window (important for GTK Application lifecycle)
        from gi.repository import Gtk
        app = Gtk.Application.get_default()
        if app:
            self._selector_interface.set_application(app)
        
        # Connect destroy signal to clean up reference
        self._selector_interface.connect('close-request', self._on_selector_interface_closed)
        
        # Show the window
        self._selector_interface.present()
        self._active_window = 'selector'
        
        logger.info("Selector Interface window created and shown")

    def hide_all_windows(self) -> None:
        """
        Hide all application windows
        """
        logger.info("Hiding all windows")
        
        if self._import_popup is not None and self._import_popup.is_visible():
            self._import_popup.set_visible(False)
            logger.debug("Import Popup hidden")
        
        if self._selector_interface is not None and self._selector_interface.is_visible():
            self._selector_interface.set_visible(False)
            logger.debug("Selector Interface hidden")
        
        self._active_window = None

    def shutdown(self) -> None:
        """
        Shutdown the application and cleanup resources
        """
        logger.info("Shutting down MainController")
        
        # Stop keyboard daemon if running
        if self._daemon is not None and self._daemon.is_running():
            logger.info("Stopping keyboard daemon")
            self._daemon.stop()
        
        # Close all windows
        if self._import_popup is not None:
            self._import_popup.close()
            self._import_popup = None
        
        if self._selector_interface is not None:
            self._selector_interface.close()
            self._selector_interface = None
        
        self._active_window = None
        
        logger.info("MainController shutdown complete")

    def _on_import_confirmed(self) -> None:
        """
        Handle Import Popup confirm action
        
        Transition from Import Popup to Selector Interface
        """
        logger.info("Import confirmed - transitioning to Selector Interface")
        
        # Close Import Popup (will be handled by the window itself)
        # Show Selector Interface
        self.show_selector_interface()

    def _on_import_popup_closed(self, window: Gtk.Window) -> bool:
        """
        Handle Import Popup window close event
        
        Args:
            window: The window being closed
            
        Returns:
            False to allow the window to close
        """
        logger.debug("Import Popup closed")
        
        # Clean up reference
        self._import_popup = None
        
        if self._active_window == 'import':
            self._active_window = None
        
        # Return False to allow window to close
        return False

    def _on_selector_closed(self) -> None:
        """
        Handle Selector Interface close callback
        """
        logger.debug("Selector Interface close callback triggered")
        
        # Persist last selected wallpaper (already handled by WallpaperManager)
        # No additional action needed

    def _on_selector_interface_closed(self, window: Gtk.Window) -> bool:
        """
        Handle Selector Interface window close event
        
        Args:
            window: The window being closed
            
        Returns:
            False to allow the window to close
        """
        logger.debug("Selector Interface closed")
        
        # Clean up reference
        self._selector_interface = None
        
        if self._active_window == 'selector':
            self._active_window = None
        
        # Return False to allow window to close
        return False

    def get_active_window(self) -> Optional[str]:
        """
        Get the currently active window
        
        Returns:
            'import', 'selector', or None
        """
        return self._active_window

    def is_import_popup_open(self) -> bool:
        """
        Check if Import Popup is currently open
        
        Returns:
            True if Import Popup is open and visible
        """
        return (self._import_popup is not None and 
                self._import_popup.is_visible())

    def is_selector_interface_open(self) -> bool:
        """
        Check if Selector Interface is currently open
        
        Returns:
            True if Selector Interface is open and visible
        """
        return (self._selector_interface is not None and 
                self._selector_interface.is_visible())

    def _initialize_daemon(self) -> None:
        """
        Initialize and start the keyboard daemon
        """
        try:
            logger.info("Initializing keyboard daemon")
            
            # Lazy import to avoid requiring python-xlib at module load time
            from .keyboard_daemon import KeyboardDaemon
            
            self._daemon = KeyboardDaemon()
            
            # Register Win+Alt+W hotkey
            self._daemon.register_hotkey(
                modifiers=['super', 'alt'],
                key='w',
                callback=self._on_hotkey_pressed
            )
            
            # Start the daemon
            self._daemon.start()
            
            logger.info("Keyboard daemon initialized and started")
        except ImportError as e:
            logger.error(f"Failed to import keyboard daemon (python-xlib not installed?): {e}")
            self._daemon = None
        except Exception as e:
            logger.error(f"Failed to initialize keyboard daemon: {e}", exc_info=True)
            self._daemon = None

    def _on_hotkey_pressed(self) -> None:
        """
        Callback triggered when the hotkey (Win+Alt+W) is pressed
        
        Shows the Import Popup using GLib.idle_add to ensure it runs in the main GTK thread
        """
        logger.info("Hotkey pressed - triggering Import Popup")
        
        # Use GLib.idle_add to ensure UI operations happen in the main GTK thread
        GLib.idle_add(self.show_import_popup)

    def start_daemon(self) -> None:
        """
        Start the keyboard daemon if not already running
        """
        if self._daemon is None:
            self._initialize_daemon()
        elif not self._daemon.is_running():
            try:
                self._daemon.start()
                logger.info("Keyboard daemon started")
            except Exception as e:
                logger.error(f"Failed to start keyboard daemon: {e}", exc_info=True)

    def stop_daemon(self) -> None:
        """
        Stop the keyboard daemon if running
        """
        if self._daemon is not None and self._daemon.is_running():
            self._daemon.stop()
            logger.info("Keyboard daemon stopped")

    def is_daemon_running(self) -> bool:
        """
        Check if keyboard daemon is currently running
        
        Returns:
            True if daemon is running, False otherwise
        """
        return self._daemon is not None and self._daemon.is_running()
