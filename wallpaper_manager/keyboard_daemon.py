"""
Keyboard Daemon - System-wide keyboard shortcut listener
"""

import logging
import threading
import os
from typing import Callable, Optional
from Xlib import X, XK, display
from Xlib.ext import record
from Xlib.protocol import rq

logger = logging.getLogger(__name__)


class KeyboardDaemon:
    """
    Daemon that listens for system-wide keyboard shortcuts
    Uses python-xlib for X11 keyboard event monitoring
    """

    def __init__(self):
        """Initialize KeyboardDaemon"""
        self._display: Optional[display.Display] = None
        self._record_display: Optional[display.Display] = None
        self._context = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callback: Optional[Callable] = None
        
        # Hotkey configuration: Super+Alt+W
        self._modifiers = {
            'super': X.Mod4Mask,  # Super/Win key
            'alt': X.Mod1Mask,    # Alt key
        }
        self._key = 'w'
        self._key_pressed = {'super': False, 'alt': False, 'w': False}
        
        logger.info("KeyboardDaemon initialized")

    def register_hotkey(self, modifiers: list[str], key: str, callback: Callable) -> None:
        """
        Register a hotkey combination with a callback
        
        Args:
            modifiers: List of modifier keys (e.g., ['super', 'alt'])
            key: The main key (e.g., 'w')
            callback: Function to call when hotkey is pressed
        """
        logger.info(f"Registering hotkey: {'+'.join(modifiers)}+{key}")
        self._key = key.lower()
        self._callback = callback
        
        # Update modifiers configuration
        self._modifiers = {}
        for mod in modifiers:
            if mod.lower() == 'super':
                self._modifiers['super'] = X.Mod4Mask
            elif mod.lower() == 'alt':
                self._modifiers['alt'] = X.Mod1Mask
            elif mod.lower() == 'ctrl':
                self._modifiers['ctrl'] = X.ControlMask
            elif mod.lower() == 'shift':
                self._modifiers['shift'] = X.ShiftMask
        
        # Reset key pressed state
        self._key_pressed = {mod: False for mod in self._modifiers.keys()}
        self._key_pressed[self._key] = False

    def start(self) -> None:
        """
        Start the keyboard daemon
        
        Begins listening for keyboard events in a background thread
        """
        if self._running:
            logger.warning("KeyboardDaemon already running")
            return
        
        logger.info("Starting KeyboardDaemon")
        
        try:
            # Create X11 display connections
            self._display = display.Display()
            self._record_display = display.Display()
            
            # Check if RECORD extension is available
            if not self._record_display.has_extension("RECORD"):
                raise RuntimeError("RECORD extension not available")
            
            # Create recording context
            self._context = self._record_display.record_create_context(
                0,
                [record.AllClients],
                [{
                    'core_requests': (0, 0),
                    'core_replies': (0, 0),
                    'ext_requests': (0, 0, 0, 0),
                    'ext_replies': (0, 0, 0, 0),
                    'delivered_events': (0, 0),
                    'device_events': (X.KeyPress, X.KeyRelease),
                    'errors': (0, 0),
                    'client_started': False,
                    'client_died': False,
                }]
            )
            
            self._running = True
            
            # Start listening in background thread
            self._thread = threading.Thread(target=self._listen, daemon=True)
            self._thread.start()
            
            logger.info("KeyboardDaemon started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start KeyboardDaemon: {e}", exc_info=True)
            self._cleanup()
            raise

    def stop(self) -> None:
        """
        Stop the keyboard daemon
        
        Stops listening for keyboard events and cleans up resources
        """
        if not self._running:
            logger.warning("KeyboardDaemon not running")
            return
        
        logger.info("Stopping KeyboardDaemon")
        
        self._running = False
        
        # Free the recording context
        if self._context is not None and self._record_display is not None:
            try:
                self._record_display.record_free_context(self._context)
            except Exception as e:
                logger.error(f"Error freeing context: {e}")
        
        # Wait for thread to finish
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        
        self._cleanup()
        
        logger.info("KeyboardDaemon stopped")

    def _cleanup(self) -> None:
        """Clean up X11 display connections"""
        if self._display is not None:
            try:
                self._display.close()
            except Exception as e:
                logger.error(f"Error closing display: {e}")
            self._display = None
        
        if self._record_display is not None:
            try:
                self._record_display.close()
            except Exception as e:
                logger.error(f"Error closing record display: {e}")
            self._record_display = None
        
        self._context = None

    def _listen(self) -> None:
        """
        Main listening loop (runs in background thread)
        
        Processes keyboard events and triggers callback when hotkey is detected
        """
        logger.info("Keyboard listener thread started")
        
        try:
            self._record_display.record_enable_context(self._context, self._handle_event)
        except Exception as e:
            logger.error(f"Error in keyboard listener: {e}", exc_info=True)
        finally:
            logger.info("Keyboard listener thread stopped")

    def _handle_event(self, reply) -> None:
        """
        Handle keyboard event from X11 RECORD extension
        
        Args:
            reply: X11 event reply data
        """
        if not self._running:
            return
        
        if reply.category != record.FromServer:
            return
        
        if reply.client_swapped:
            return
        
        if not len(reply.data) or reply.data[0] < 2:
            return
        
        data = reply.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(
                data, self._record_display.display, None, None
            )
            
            if event.type == X.KeyPress:
                self._handle_key_press(event)
            elif event.type == X.KeyRelease:
                self._handle_key_release(event)

    def _handle_key_press(self, event) -> None:
        """
        Handle key press event
        
        Args:
            event: X11 KeyPress event
        """
        keycode = event.detail
        keysym = self._display.keycode_to_keysym(keycode, 0)
        key_char = XK.keysym_to_string(keysym)
        
        if key_char is None:
            return
        
        key_char = key_char.lower()
        
        # Track modifier keys
        for mod_name, mod_mask in self._modifiers.items():
            if event.state & mod_mask:
                self._key_pressed[mod_name] = True
        
        # Track main key
        if key_char == self._key:
            self._key_pressed[self._key] = True
        
        # Check if all keys in hotkey combination are pressed
        if self._is_hotkey_pressed():
            logger.info("Hotkey detected!")
            if self._callback is not None:
                try:
                    self._callback()
                except Exception as e:
                    logger.error(f"Error in hotkey callback: {e}", exc_info=True)

    def _handle_key_release(self, event) -> None:
        """
        Handle key release event
        
        Args:
            event: X11 KeyRelease event
        """
        keycode = event.detail
        keysym = self._display.keycode_to_keysym(keycode, 0)
        key_char = XK.keysym_to_string(keysym)
        
        if key_char is None:
            return
        
        key_char = key_char.lower()
        
        # Reset key state on release
        if key_char == self._key:
            self._key_pressed[self._key] = False
        
        # Reset modifier states
        for mod_name in self._modifiers.keys():
            if key_char in ['super_l', 'super_r'] and mod_name == 'super':
                self._key_pressed[mod_name] = False
            elif key_char in ['alt_l', 'alt_r'] and mod_name == 'alt':
                self._key_pressed[mod_name] = False
            elif key_char in ['control_l', 'control_r'] and mod_name == 'ctrl':
                self._key_pressed[mod_name] = False
            elif key_char in ['shift_l', 'shift_r'] and mod_name == 'shift':
                self._key_pressed[mod_name] = False

    def _is_hotkey_pressed(self) -> bool:
        """
        Check if all keys in the hotkey combination are currently pressed
        
        Returns:
            True if hotkey is pressed, False otherwise
        """
        return all(self._key_pressed.values())

    def is_running(self) -> bool:
        """
        Check if daemon is currently running
        
        Returns:
            True if running, False otherwise
        """
        return self._running
