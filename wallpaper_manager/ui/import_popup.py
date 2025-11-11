"""
Import Popup UI - GTK4 window for importing wallpapers
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio, Gdk
import logging
from pathlib import Path
from typing import List, Optional, Callable
import threading

from ..manager import WallpaperManager

logger = logging.getLogger(__name__)


class ImportPopup(Gtk.Window):
    """GTK4 window for importing wallpapers from URLs or local files"""

    def __init__(self, wallpaper_manager: WallpaperManager, on_confirm: Optional[Callable] = None):
        """
        Initialize Import Popup window
        
        Args:
            wallpaper_manager: WallpaperManager instance for importing wallpapers
            on_confirm: Callback function to call when user confirms imports
        """
        super().__init__()
        self.wallpaper_manager = wallpaper_manager
        self.on_confirm_callback = on_confirm
        
        # Track pending imports
        self.pending_imports: List[dict] = []
        
        # Configure window as a centered popup (like LocalSend)
        self.set_title("Add Wallpapers")
        self.set_default_size(600, 500)
        self.set_resizable(False)
        
        # Make it a modal dialog-like window
        self.set_modal(True)
        
        # Add rounded corners and shadow effect
        self.set_decorated(True)
        
        # Load CSS styling
        self._load_css()
        
        # Build UI
        self._build_ui()
        
        logger.info("Import Popup initialized")

    def _load_css(self):
        """Load CSS styling for the Import Popup"""
        css_provider = Gtk.CssProvider()
        css_file = Path(__file__).parent / "styles.css"
        
        if css_file.exists():
            css_provider.load_from_path(str(css_file))
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            logger.debug("CSS styling loaded")
        else:
            logger.warning(f"CSS file not found: {css_file}")

    def _build_ui(self):
        """Build the complete UI structure"""
        # Add CSS class to window
        self.add_css_class("import-popup")
        
        # Main vertical box container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_box.add_css_class("import-popup-content")
        self.set_child(main_box)
        
        # Header section
        header_box = self._create_header()
        main_box.append(header_box)
        
        # Mode selector buttons
        mode_selector_box = self._create_mode_selector()
        main_box.append(mode_selector_box)
        
        # Stack for switching between URL and Upload modes
        self.content_stack = Gtk.Stack()
        self.content_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.content_stack.set_transition_duration(200)
        self.content_stack.set_vexpand(True)
        
        # Create URL mode page
        url_mode_box = self._create_url_mode()
        self.content_stack.add_named(url_mode_box, "url_mode")
        
        # Create Upload mode page
        upload_mode_box = self._create_upload_mode()
        self.content_stack.add_named(upload_mode_box, "upload_mode")
        
        main_box.append(self.content_stack)
        
        # Preview list for pending imports
        preview_section = self._create_preview_list()
        main_box.append(preview_section)
        
        # Action bar with Confirm/Cancel buttons
        action_bar = self._create_action_bar()
        main_box.append(action_bar)

    def _create_header(self) -> Gtk.Box:
        """Create header section with title"""
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        header_box.add_css_class("import-header")
        header_box.set_margin_top(0)
        header_box.set_margin_bottom(0)
        header_box.set_margin_start(0)
        header_box.set_margin_end(0)
        
        title_label = Gtk.Label(label="Add Wallpapers")
        title_label.add_css_class("title-1")
        header_box.append(title_label)
        
        return header_box

    def _create_mode_selector(self) -> Gtk.Box:
        """Create mode selector buttons (URL/Upload)"""
        mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        mode_box.add_css_class("mode-selector")
        mode_box.set_margin_top(0)
        mode_box.set_margin_bottom(0)
        mode_box.set_margin_start(0)
        mode_box.set_margin_end(0)
        mode_box.set_halign(Gtk.Align.CENTER)
        
        # URL mode button
        self.url_mode_button = Gtk.Button(label="Import from URL")
        self.url_mode_button.connect("clicked", self._on_mode_changed, "url_mode")
        self.url_mode_button.add_css_class("suggested-action")
        mode_box.append(self.url_mode_button)
        
        # Upload mode button
        self.upload_mode_button = Gtk.Button(label="Upload Your Wallpapers")
        self.upload_mode_button.connect("clicked", self._on_mode_changed, "upload_mode")
        mode_box.append(self.upload_mode_button)
        
        return mode_box

    def _create_url_mode(self) -> Gtk.Box:
        """Create URL import mode interface"""
        url_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        url_box.add_css_class("import-content-area")
        url_box.set_margin_top(0)
        url_box.set_margin_bottom(0)
        url_box.set_margin_start(0)
        url_box.set_margin_end(0)
        
        # Instruction label
        instruction_label = Gtk.Label(label="Enter image URL:")
        instruction_label.set_halign(Gtk.Align.START)
        url_box.append(instruction_label)
        
        # URL entry field with Add button
        entry_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        self.url_entry = Gtk.Entry()
        self.url_entry.add_css_class("url-entry")
        self.url_entry.set_placeholder_text("https://example.com/image.jpg")
        self.url_entry.set_hexpand(True)
        self.url_entry.connect("activate", self._on_url_add_clicked)  # Enter key triggers add
        entry_box.append(self.url_entry)
        
        self.url_add_button = Gtk.Button(label="Add")
        self.url_add_button.connect("clicked", self._on_url_add_clicked)
        self.url_add_button.add_css_class("suggested-action")
        entry_box.append(self.url_add_button)
        
        url_box.append(entry_box)
        
        # Loading indicator (hidden by default)
        self.url_loading_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.url_loading_box.add_css_class("loading-indicator")
        self.url_loading_box.set_visible(False)
        
        self.url_spinner = Gtk.Spinner()
        self.url_loading_box.append(self.url_spinner)
        
        self.url_loading_label = Gtk.Label(label="Downloading...")
        self.url_loading_box.append(self.url_loading_label)
        
        url_box.append(self.url_loading_box)
        
        return url_box

    def _on_url_add_clicked(self, widget):
        """Handle Add button click for URL import"""
        url = self.url_entry.get_text().strip()
        
        if not url:
            logger.warning("Empty URL provided")
            return
        
        # Validate URL format
        validation_error = self._validate_url(url)
        if validation_error:
            self._show_validation_message(validation_error)
            return
        
        logger.info(f"Adding URL: {url}")
        
        # Show loading indicator
        self._set_url_loading(True)
        
        # Download in background thread to avoid blocking UI
        thread = threading.Thread(target=self._download_url, args=(url,))
        thread.daemon = True
        thread.start()

    def _validate_url(self, url: str) -> Optional[str]:
        """
        Validate URL format
        
        Returns:
            Error message if invalid, None if valid
        """
        if not url.startswith(("http://", "https://")):
            return "URL must start with http:// or https://"
        
        # Check for common image extensions
        url_lower = url.lower()
        has_image_ext = any(url_lower.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp'])
        
        # Warn if no image extension (but don't block)
        if not has_image_ext and '?' not in url:
            logger.warning(f"URL does not have a common image extension: {url}")
        
        return None

    def _download_url(self, url: str):
        """Download image from URL in background thread"""
        try:
            wallpaper = self.wallpaper_manager.import_from_url(url)
            
            # Update UI on main thread
            GLib.idle_add(self._on_url_download_success, url, wallpaper)
            
        except Exception as e:
            logger.error(f"Failed to download URL {url}: {e}")
            # Update UI on main thread
            GLib.idle_add(self._on_url_download_error, url, str(e))

    def _on_url_download_success(self, url: str, wallpaper):
        """Handle successful URL download (runs on main thread)"""
        self._set_url_loading(False)
        
        # Add to pending imports
        self.pending_imports.append({
            "type": "url",
            "url": url,
            "wallpaper": wallpaper,
            "status": "success"
        })
        
        # Update preview list
        self._add_preview_item(f"✓ {url}", "success")
        
        # Clear URL entry
        self.url_entry.set_text("")
        
        # Update confirm button state
        self._update_confirm_button_state()
        
        logger.info(f"Successfully added URL: {url}")

    def _on_url_download_error(self, url: str, error_message: str):
        """Handle URL download error (runs on main thread)"""
        self._set_url_loading(False)
        
        # Check if it's a network error (offer retry)
        if "network" in error_message.lower() or "connection" in error_message.lower() or "timeout" in error_message.lower():
            # Show retry dialog for network failures
            self._show_retry_dialog(
                "Download Failed",
                f"Failed to download image from URL:\n{error_message}\n\nWould you like to retry?",
                lambda: self._retry_url_download(url)
            )
        else:
            # Show regular error dialog for other errors
            self._show_error_dialog("Download Failed", f"Failed to download image from URL:\n{error_message}")
        
        logger.error(f"Failed to download URL {url}: {error_message}")

    def _retry_url_download(self, url: str):
        """Retry downloading a URL"""
        logger.info(f"Retrying URL download: {url}")
        self.url_entry.set_text(url)
        self._on_url_add_clicked(None)

    def _set_url_loading(self, loading: bool):
        """Show/hide URL loading indicator"""
        self.url_loading_box.set_visible(loading)
        self.url_entry.set_sensitive(not loading)
        self.url_add_button.set_sensitive(not loading)
        
        if loading:
            self.url_spinner.start()
        else:
            self.url_spinner.stop()

    def _add_preview_item(self, text: str, status: str = "pending"):
        """Add item to preview list"""
        row = Gtk.ListBoxRow()
        
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_margin_top(5)
        box.set_margin_bottom(5)
        box.set_margin_start(10)
        box.set_margin_end(10)
        
        label = Gtk.Label(label=text)
        label.set_halign(Gtk.Align.START)
        label.set_ellipsize(3)  # Ellipsize at end
        label.set_hexpand(True)
        box.append(label)
        
        # Add status indicator
        if status == "success":
            label.add_css_class("success")
        elif status == "error":
            label.add_css_class("error")
        
        row.set_child(box)
        self.preview_list.append(row)

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

    def _show_validation_message(self, message: str):
        """Show validation message to user"""
        logger.warning(f"Validation: {message}")
        self._show_error_dialog("Validation Error", message)

    def _show_retry_dialog(self, title: str, message: str, retry_callback: Callable):
        """Show error dialog with retry option"""
        logger.error(f"{title}: {message}")
        
        # Create alert dialog with retry option
        dialog = Gtk.AlertDialog()
        dialog.set_message(title)
        dialog.set_detail(message)
        dialog.set_buttons(["Cancel", "Retry"])
        dialog.set_default_button(1)
        dialog.set_cancel_button(0)
        
        # Show dialog and handle response
        dialog.choose(self, None, self._on_retry_dialog_response, retry_callback)

    def _on_retry_dialog_response(self, dialog: Gtk.AlertDialog, result, retry_callback: Callable):
        """Handle retry dialog response"""
        try:
            button_index = dialog.choose_finish(result)
            
            if button_index == 1:  # Retry button
                logger.info("User chose to retry")
                retry_callback()
            else:
                logger.info("User cancelled retry")
                
        except Exception as e:
            logger.error(f"Error handling retry dialog response: {e}")

    def _create_upload_mode(self) -> Gtk.Box:
        """Create file upload mode interface"""
        upload_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        upload_box.add_css_class("import-content-area")
        upload_box.set_margin_top(0)
        upload_box.set_margin_bottom(0)
        upload_box.set_margin_start(0)
        upload_box.set_margin_end(0)
        
        # Instruction label
        instruction_label = Gtk.Label(label="Select image files to upload:")
        instruction_label.set_halign(Gtk.Align.START)
        upload_box.append(instruction_label)
        
        # File picker button
        self.file_picker_button = Gtk.Button(label="Choose Files")
        self.file_picker_button.connect("clicked", self._on_file_picker_clicked)
        self.file_picker_button.add_css_class("suggested-action")
        self.file_picker_button.set_halign(Gtk.Align.START)
        upload_box.append(self.file_picker_button)
        
        return upload_box

    def _on_file_picker_clicked(self, button: Gtk.Button):
        """Handle file picker button click"""
        # Create file chooser dialog
        dialog = Gtk.FileDialog()
        dialog.set_title("Select Wallpaper Images")
        
        # Configure file filter for image formats
        filter_images = Gtk.FileFilter()
        filter_images.set_name("Image Files")
        filter_images.add_mime_type("image/png")
        filter_images.add_mime_type("image/jpeg")
        filter_images.add_mime_type("image/webp")
        filter_images.add_pattern("*.png")
        filter_images.add_pattern("*.jpg")
        filter_images.add_pattern("*.jpeg")
        filter_images.add_pattern("*.webp")
        
        filter_list = Gio.ListStore.new(Gtk.FileFilter)
        filter_list.append(filter_images)
        dialog.set_filters(filter_list)
        dialog.set_default_filter(filter_images)
        
        # Open dialog for multiple file selection
        dialog.open_multiple(self, None, self._on_files_selected)

    def _on_files_selected(self, dialog: Gtk.FileDialog, result):
        """Handle file selection from dialog"""
        try:
            files = dialog.open_multiple_finish(result)
            
            if files is None:
                logger.info("No files selected")
                return
            
            # Process each selected file
            file_count = files.get_n_items()
            logger.info(f"Selected {file_count} files")
            
            for i in range(file_count):
                file = files.get_item(i)
                file_path = Path(file.get_path())
                self._import_file(file_path)
                
        except Exception as e:
            logger.error(f"Error selecting files: {e}")
            self._show_error_dialog("File Selection Error", str(e))

    def _import_file(self, file_path: Path):
        """Import a single file"""
        try:
            logger.info(f"Importing file: {file_path}")
            
            # Import using wallpaper manager
            wallpaper = self.wallpaper_manager.import_from_file(file_path)
            
            # Add to pending imports
            self.pending_imports.append({
                "type": "file",
                "path": str(file_path),
                "wallpaper": wallpaper,
                "status": "success"
            })
            
            # Update preview list
            self._add_preview_item(f"✓ {file_path.name}", "success")
            
            # Update confirm button state
            self._update_confirm_button_state()
            
            logger.info(f"Successfully imported file: {file_path.name}")
            
        except Exception as e:
            logger.error(f"Failed to import file {file_path}: {e}")
            
            # Add to pending imports with error status
            self.pending_imports.append({
                "type": "file",
                "path": str(file_path),
                "wallpaper": None,
                "status": "error",
                "error": str(e)
            })
            
            # Update preview list
            self._add_preview_item(f"✗ {file_path.name} - {str(e)}", "error")
            
            # Show error dialog
            self._show_error_dialog("Import Failed", f"Failed to import {file_path.name}:\n{str(e)}")

    def _create_preview_list(self) -> Gtk.Box:
        """Create preview list for pending imports"""
        preview_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        preview_box.set_margin_top(10)
        preview_box.set_margin_bottom(10)
        preview_box.set_margin_start(24)
        preview_box.set_margin_end(24)
        
        # Label
        preview_label = Gtk.Label(label="Pending Imports:")
        preview_label.set_halign(Gtk.Align.START)
        preview_label.add_css_class("heading")
        preview_box.append(preview_label)
        
        # Scrolled window for list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_min_content_height(100)
        
        # ListBox for pending imports
        self.preview_list = Gtk.ListBox()
        self.preview_list.add_css_class("boxed-list")
        self.preview_list.add_css_class("preview-list")
        scrolled.set_child(self.preview_list)
        
        preview_box.append(scrolled)
        
        return preview_box

    def _create_action_bar(self) -> Gtk.Box:
        """Create action bar with buttons"""
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        action_box.add_css_class("action-bar")
        action_box.set_margin_top(0)
        action_box.set_margin_bottom(0)
        action_box.set_margin_start(0)
        action_box.set_margin_end(0)
        
        # See Your Wallpapers button (left side)
        see_wallpapers_button = Gtk.Button(label="See Your Wallpapers")
        see_wallpapers_button.connect("clicked", self._on_see_wallpapers)
        see_wallpapers_button.set_halign(Gtk.Align.START)
        see_wallpapers_button.set_hexpand(True)
        action_box.append(see_wallpapers_button)
        
        # Spacer
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        action_box.append(spacer)
        
        # Cancel button (right side)
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", self._on_cancel)
        action_box.append(cancel_button)
        
        # Confirm button (right side)
        self.confirm_button = Gtk.Button(label="Confirm")
        self.confirm_button.connect("clicked", self._on_confirm)
        self.confirm_button.add_css_class("suggested-action")
        self.confirm_button.set_sensitive(False)  # Disabled until imports are added
        action_box.append(self.confirm_button)
        
        return action_box

    def _on_mode_changed(self, button: Gtk.Button, mode: str):
        """Handle mode selector button clicks"""
        self.content_stack.set_visible_child_name(mode)
        
        # Update button styles
        if mode == "url_mode":
            self.url_mode_button.add_css_class("suggested-action")
            self.upload_mode_button.remove_css_class("suggested-action")
        else:
            self.upload_mode_button.add_css_class("suggested-action")
            self.url_mode_button.remove_css_class("suggested-action")
        
        logger.debug(f"Switched to {mode}")

    def _on_cancel(self, button: Gtk.Button):
        """Handle Cancel button click"""
        logger.info("Cancel button clicked - discarding imports")
        
        # Clear pending imports
        self.pending_imports.clear()
        
        # Close the window
        self.close()

    def _on_confirm(self, button: Gtk.Button):
        """Handle Confirm button click"""
        logger.info(f"Confirm button clicked - {len(self.pending_imports)} imports to process")
        
        # Filter out failed imports
        successful_imports = [
            imp for imp in self.pending_imports 
            if imp.get("status") == "success" and imp.get("wallpaper") is not None
        ]
        
        logger.info(f"Successfully imported {len(successful_imports)} wallpapers")
        
        # Call the callback if provided
        if self.on_confirm_callback:
            self.on_confirm_callback()
        
        # Close the window
        self.close()

    def _on_see_wallpapers(self, button: Gtk.Button):
        """Handle See Your Wallpapers button click"""
        logger.info("See Your Wallpapers button clicked")
        
        # Call the callback to show selector interface
        if self.on_confirm_callback:
            self.on_confirm_callback()
        
        # Close the window
        self.close()

    def _update_confirm_button_state(self):
        """Update Confirm button enabled state based on pending imports"""
        has_imports = len(self.pending_imports) > 0
        self.confirm_button.set_sensitive(has_imports)
