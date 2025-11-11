"""
Selector Interface UI - Transparent fullscreen GTK4 window for wallpaper selection
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
import logging
from pathlib import Path
from typing import List, Optional, Callable

from ..manager import WallpaperManager
from ..models import Wallpaper

logger = logging.getLogger(__name__)


class SelectorInterface(Gtk.Window):
    """Transparent fullscreen overlay window for browsing and selecting wallpapers"""

    def __init__(self, wallpaper_manager: WallpaperManager, on_close: Optional[Callable] = None):
        """
        Initialize Selector Interface window
        
        Args:
            wallpaper_manager: WallpaperManager instance for retrieving and setting wallpapers
            on_close: Callback function to call when window closes
        """
        super().__init__()
        self.wallpaper_manager = wallpaper_manager
        self.on_close_callback = on_close
        
        # Track current wallpaper for UI indication
        self.current_wallpaper_id = None
        
        # Performance optimization: cache loaded pixbufs
        self._pixbuf_cache = {}
        
        # Performance optimization: track visible items for lazy loading
        self._loaded_items = set()
        
        # Configure window for fullscreen transparency
        self._configure_window()
        
        # Build UI
        self._build_ui()
        
        # Load wallpapers
        self.load_wallpapers()
        
        logger.info("Selector Interface initialized")

    def _configure_window(self):
        """Configure window for fullscreen transparent overlay"""
        # Set window to fullscreen
        self.fullscreen()
        
        # Set window title (not visible in fullscreen)
        self.set_title("Wallpaper Selector")
        
        # Make window transparent
        self.set_decorated(False)
        
        # Set up CSS for transparency
        self._setup_transparency_css()
        
        # Connect key press event for Escape and arrow keys
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self._on_key_pressed)
        self.add_controller(key_controller)
        
        # Track current selection for arrow key navigation
        self._current_selection = 0
        self._wallpapers_list = []
        
        logger.debug("Window configured for fullscreen transparency")

    def _setup_transparency_css(self):
        """Set up CSS styling for transparent background"""
        css_provider = Gtk.CssProvider()
        css_file = Path(__file__).parent / "styles.css"
        
        if css_file.exists():
            css_provider.load_from_path(str(css_file))
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            logger.debug("CSS styling loaded from file")
        else:
            logger.warning(f"CSS file not found: {css_file}, using fallback CSS")
            # Fallback CSS if file not found
            css = """
            window.selector-interface {
                background-color: rgba(0, 0, 0, 0.85);
            }
            .wallpaper-grid {
                background-color: transparent;
            }
            .wallpaper-item {
                background-color: rgba(40, 40, 40, 0.7);
                border-radius: 8px;
                padding: 8px;
                margin: 8px;
            }
            .wallpaper-item:hover {
                background-color: rgba(60, 60, 60, 0.9);
            }
            .wallpaper-item.current {
                background-color: rgba(80, 120, 200, 0.8);
                border: 2px solid rgba(100, 150, 255, 1.0);
            }
            .close-hint {
                background-color: rgba(0, 0, 0, 0.6);
                border-radius: 6px;
                padding: 10px 20px;
                margin: 20px;
                color: rgba(255, 255, 255, 0.9);
            }
            """
            css_provider.load_from_string(css)
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        
        # Add CSS class to window
        self.add_css_class("selector-interface")
        
        logger.debug("Transparency CSS applied")

    def _build_ui(self):
        """Build the complete UI structure - 3 rows with aligned columns"""
        # Main overlay container
        overlay = Gtk.Overlay()
        self.set_child(overlay)
        
        # Scrolled window for horizontal scrolling
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        
        # Use Grid for proper alignment
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(16)
        self.grid.set_column_spacing(16)
        self.grid.set_halign(Gtk.Align.CENTER)
        self.grid.set_valign(Gtk.Align.CENTER)
        self.grid.set_margin_top(40)
        self.grid.set_margin_bottom(40)
        self.grid.set_margin_start(40)
        self.grid.set_margin_end(40)
        
        scrolled.set_child(self.grid)
        overlay.set_child(scrolled)
        
        # Close hint overlay
        close_hint = self._create_close_hint()
        overlay.add_overlay(close_hint)
        
        logger.debug("UI structure built - Grid layout")

    def _create_close_hint(self) -> Gtk.Box:
        """Create close hint label overlay"""
        hint_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hint_box.set_halign(Gtk.Align.CENTER)
        hint_box.set_valign(Gtk.Align.END)
        hint_box.set_margin_bottom(30)
        
        hint_label = Gtk.Label(label="Press ESC to close")
        hint_label.add_css_class("close-hint")
        hint_box.append(hint_label)
        
        return hint_box

    def load_wallpapers(self):
        """Load and display all wallpapers in 3-row grid"""
        logger.info("Loading wallpapers...")
        
        # Get current wallpaper ID
        current_wallpaper = self.wallpaper_manager.get_current_wallpaper()
        if current_wallpaper:
            self.current_wallpaper_id = current_wallpaper.id
        
        # Get all wallpapers
        wallpapers = self.wallpaper_manager.get_all_wallpapers()
        
        if not wallpapers:
            logger.warning("No wallpapers in collection")
            self._show_empty_state()
            return
        
        logger.info(f"Loading {len(wallpapers)} wallpapers")
        
        # Store wallpapers list for navigation
        self._wallpapers_list = wallpapers
        
        # Find current selection index
        if self.current_wallpaper_id:
            for i, wp in enumerate(wallpapers):
                if wp.id == self.current_wallpaper_id:
                    self._current_selection = i
                    break
        
        # Clear existing items from grid
        child = self.grid.get_first_child()
        while child is not None:
            next_child = child.get_next_sibling()
            self.grid.remove(child)
            child = next_child
        
        # Memory optimization
        if len(wallpapers) > 100:
            self._clear_old_cache_entries(keep_recent=50)
        
        # Arrange in grid: 3 rows, items cycle through rows
        for i, wallpaper in enumerate(wallpapers):
            row = i % 3  # Row: 0, 1, 2, 0, 1, 2, ...
            col = i // 3  # Column: increases every 3 items
            self._create_wallpaper_item(wallpaper, row, col, i)
        
        logger.info(f"Loaded {len(wallpapers)} wallpapers in grid")
    
    def _clear_old_cache_entries(self, keep_recent: int = 50):
        """
        Clear old cache entries to manage memory for large collections
        
        Args:
            keep_recent: Number of recent entries to keep
        """
        if len(self._pixbuf_cache) <= keep_recent:
            return
        
        # Keep only the most recently loaded items
        cache_keys = list(self._pixbuf_cache.keys())
        to_remove = cache_keys[:-keep_recent] if len(cache_keys) > keep_recent else []
        
        for key in to_remove:
            del self._pixbuf_cache[key]
            if key in self._loaded_items:
                self._loaded_items.remove(key)
        
        logger.debug(f"Cleared {len(to_remove)} cache entries, {len(self._pixbuf_cache)} remaining")

    def _show_empty_state(self):
        """Show empty state message when no wallpapers exist"""
        empty_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        empty_box.set_halign(Gtk.Align.CENTER)
        empty_box.set_valign(Gtk.Align.CENTER)
        
        empty_label = Gtk.Label(label="No wallpapers")
        empty_label.add_css_class("title-1")
        empty_box.append(empty_label)
        
        hint_label = Gtk.Label(label="Import some to get started")
        hint_label.add_css_class("dim-label")
        empty_box.append(hint_label)
        
        # Center in middle row
        self.grid.attach(empty_box, 0, 1, 1, 1)

    def _create_wallpaper_item(self, wallpaper: Wallpaper, row: int, col: int, index: int):
        """
        Create a wallpaper item widget
        
        Args:
            wallpaper: Wallpaper instance to display
            row: Grid row (0, 1, or 2)
            col: Grid column
            index: Index in wallpapers list
        """
        # Container box - larger thumbnails
        item_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        item_box.add_css_class("niri-tile")
        item_box.set_size_request(280, 180)
        
        # Store index for navigation
        item_box.wallpaper_index = index
        
        # Mark current wallpaper or selected
        if wallpaper.id == self.current_wallpaper_id:
            item_box.add_css_class("current")
        if index == self._current_selection:
            item_box.add_css_class("selected")
        
        # Create picture widget
        picture = Gtk.Picture()
        picture.set_can_shrink(True)
        picture.set_content_fit(Gtk.ContentFit.COVER)
        picture.set_size_request(280, 180)
        
        # Load thumbnail
        self._load_thumbnail_cached(picture, wallpaper)
        
        item_box.append(picture)
        
        # Make clickable
        gesture = Gtk.GestureClick()
        gesture.connect("released", self._on_wallpaper_clicked, wallpaper)
        item_box.add_controller(gesture)
        
        # Add to grid at specified position
        self.grid.attach(item_box, col, row, 1, 1)
    
    def _load_thumbnail_cached(self, picture: Gtk.Picture, wallpaper: Wallpaper):
        """
        Load thumbnail with caching to improve performance
        
        Args:
            picture: Picture widget to load into
            wallpaper: Wallpaper instance
        """
        # Check if already in cache
        if wallpaper.id in self._pixbuf_cache:
            logger.debug(f"Using cached thumbnail for {wallpaper.id}")
            picture.set_pixbuf(self._pixbuf_cache[wallpaper.id])
            return
        
        # Load thumbnail
        if wallpaper.thumbnail_path.exists():
            try:
                # Load and cache the pixbuf
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(wallpaper.thumbnail_path))
                self._pixbuf_cache[wallpaper.id] = pixbuf
                picture.set_pixbuf(pixbuf)
                self._loaded_items.add(wallpaper.id)
                logger.debug(f"Loaded and cached thumbnail for {wallpaper.id}")
            except Exception as e:
                logger.error(f"Failed to load thumbnail for {wallpaper.id}: {e}")
                # Use filename as fallback
                picture.set_filename(str(wallpaper.thumbnail_path))
        else:
            logger.warning(f"Thumbnail not found for wallpaper {wallpaper.id}")

    def _on_wallpaper_clicked(self, gesture: Gtk.GestureClick, n_press: int, x: float, y: float, wallpaper: Wallpaper):
        """
        Handle wallpaper thumbnail click
        
        Args:
            gesture: Gesture controller
            n_press: Number of presses
            x: X coordinate
            y: Y coordinate
            wallpaper: Wallpaper that was clicked
        """
        logger.info(f"Wallpaper clicked: {wallpaper.id}")
        
        try:
            # Set wallpaper using manager
            self.wallpaper_manager.set_wallpaper(wallpaper)
            
            # Update UI to reflect new current wallpaper
            self._update_current_wallpaper_indicator(wallpaper.id)
            
            logger.info(f"Wallpaper set successfully: {wallpaper.id}")
            
        except Exception as e:
            logger.error(f"Failed to set wallpaper: {e}")
            self._show_error_dialog("Failed to Set Wallpaper", str(e))

    def _update_current_wallpaper_indicator(self, new_wallpaper_id: str):
        """
        Update UI to indicate which wallpaper is currently active
        
        Args:
            new_wallpaper_id: ID of the newly selected wallpaper
        """
        # Update current wallpaper ID
        old_id = self.current_wallpaper_id
        self.current_wallpaper_id = new_wallpaper_id
        
        # Reload wallpapers to update current indicator
        self.load_wallpapers()
        
        logger.debug(f"Updated current wallpaper indicator: {old_id} -> {new_wallpaper_id}")

    def _on_key_pressed(self, controller: Gtk.EventControllerKey, keyval: int, keycode: int, state: Gdk.ModifierType) -> bool:
        """
        Handle key press events
        
        Args:
            controller: Event controller
            keyval: Key value
            keycode: Key code
            state: Modifier state
            
        Returns:
            True if event was handled
        """
        # Check for Escape key
        if keyval == Gdk.KEY_Escape:
            logger.info("Escape key pressed - closing selector interface")
            self._on_close()
            return True
        
        # Arrow key navigation
        if not self._wallpapers_list:
            return False
        
        old_selection = self._current_selection
        
        if keyval == Gdk.KEY_Up:
            # Move up one row (subtract 1)
            if self._current_selection > 0:
                self._current_selection -= 1
        elif keyval == Gdk.KEY_Down:
            # Move down one row (add 1)
            if self._current_selection < len(self._wallpapers_list) - 1:
                self._current_selection += 1
        elif keyval == Gdk.KEY_Left:
            # Move left one column (subtract 3)
            if self._current_selection >= 3:
                self._current_selection -= 3
        elif keyval == Gdk.KEY_Right:
            # Move right one column (add 3)
            if self._current_selection + 3 < len(self._wallpapers_list):
                self._current_selection += 3
        elif keyval == Gdk.KEY_Return or keyval == Gdk.KEY_KP_Enter:
            # Enter key - select current wallpaper
            if 0 <= self._current_selection < len(self._wallpapers_list):
                wallpaper = self._wallpapers_list[self._current_selection]
                self._on_wallpaper_clicked(None, 0, 0, 0, wallpaper)
            return True
        else:
            return False
        
        # Update selection if changed
        if old_selection != self._current_selection:
            self._update_selection_highlight()
            return True
        
        return False
    
    def _update_selection_highlight(self):
        """Update visual highlight for keyboard selection"""
        # Remove old selection highlight
        child = self.grid.get_first_child()
        while child is not None:
            child.remove_css_class("selected")
            child = child.get_next_sibling()
        
        # Add new selection highlight
        child = self.grid.get_first_child()
        while child is not None:
            if hasattr(child, 'wallpaper_index') and child.wallpaper_index == self._current_selection:
                child.add_css_class("selected")
                break
            child = child.get_next_sibling()

    def _on_close(self):
        """Handle window close"""
        logger.info("Closing selector interface")
        
        # Clean up cache to free memory
        self._cleanup_resources()
        
        # Call close callback if provided
        if self.on_close_callback:
            self.on_close_callback()
        
        # Close the window
        self.close()
    
    def _cleanup_resources(self):
        """Clean up resources when closing"""
        logger.debug("Cleaning up resources")
        
        # Clear pixbuf cache
        self._pixbuf_cache.clear()
        self._loaded_items.clear()
        
        logger.debug("Resources cleaned up")

    def _show_error_dialog(self, title: str, message: str):
        """Show error dialog to user"""
        logger.error(f"{title}: {message}")
        
        # Create alert dialog
        dialog = Gtk.AlertDialog()
        dialog.set_message(title)
        dialog.set_detail(message)
        dialog.set_buttons(["OK"])
        dialog.set_default_button(0)
        dialog.set_cancel_button(0)
        
        # Show dialog
        dialog.choose(self, None, None)
