# Keyboard Shortcut Daemon Feature

## Overview

The Wallpaper Manager includes an optional keyboard shortcut daemon that enables system-wide hotkey support. When enabled, you can press **Win+Alt+W** from anywhere to instantly open the wallpaper import popup.

## Key Features

- **System-wide hotkey:** Works regardless of which application has focus
- **Optional:** Main application works fine without the daemon
- **Lazy loading:** python-xlib is only loaded when daemon is enabled
- **Systemd integration:** Automatic startup on login
- **Graceful degradation:** Application continues to work if daemon fails to start

## Architecture

### Lazy Loading Design

The daemon uses a lazy-loading pattern to avoid requiring `python-xlib` for users who don't need the keyboard shortcut feature:

```python
# Import only happens when daemon is initialized
def _initialize_daemon(self):
    from .keyboard_daemon import KeyboardDaemon
    self._daemon = KeyboardDaemon()
```

This means:
- ✅ Main application works without python-xlib installed
- ✅ No import errors if python-xlib is missing
- ✅ Daemon functionality is completely optional
- ✅ Error handling gracefully disables daemon if initialization fails

### Thread Safety

The daemon runs in a background thread and uses `GLib.idle_add()` to ensure all GTK UI operations happen in the main thread:

```python
def _on_hotkey_pressed(self):
    # Safely dispatch to main GTK thread
    GLib.idle_add(self.show_import_popup)
```

## Usage Modes

### Mode 1: Without Daemon (Default)
```bash
# Launch application manually
wallpaper-manager
```

**Pros:**
- No additional dependencies
- Simpler setup
- Lower resource usage

**Cons:**
- No keyboard shortcut
- Must launch from menu/terminal

### Mode 2: With Daemon
```bash
# Install and enable daemon
systemctl --user enable wallpaper-manager-daemon.service
systemctl --user start wallpaper-manager-daemon.service
```

**Pros:**
- System-wide keyboard shortcut (Win+Alt+W)
- Instant access from anywhere
- Auto-starts on login

**Cons:**
- Requires python-xlib
- Uses background process
- X11 only (currently)

## Implementation Details

### Files Created

1. **wallpaper_manager/keyboard_daemon.py**
   - KeyboardDaemon class
   - X11 RECORD extension integration
   - Hotkey detection and callback system

2. **wallpaper_manager/daemon.py**
   - Standalone daemon entry point
   - GTK application for daemon mode
   - Signal handling for graceful shutdown

3. **wallpaper-manager-daemon.service**
   - Systemd user service definition
   - Auto-start configuration
   - Security hardening

### Controller Integration

The `MainController` class accepts an optional `enable_daemon` parameter:

```python
# Without daemon (default)
controller = MainController(config)

# With daemon
controller = MainController(config, enable_daemon=True)
```

### Error Handling

The daemon implementation includes comprehensive error handling:

- **Import errors:** Caught and logged if python-xlib is missing
- **X11 errors:** Caught during daemon initialization
- **Runtime errors:** Daemon stops gracefully on errors
- **Shutdown:** Proper cleanup of X11 resources

## Testing

### Test Without Installing

```bash
# Test daemon functionality directly
python test_daemon_manual.py
```

### Test With Systemd

```bash
# Check service status
systemctl --user status wallpaper-manager-daemon.service

# View real-time logs
journalctl --user -u wallpaper-manager-daemon.service -f
```

## Future Enhancements

- **Wayland support:** Use python-evdev or compositor-specific APIs
- **Configurable hotkeys:** Allow users to customize the key combination
- **Multiple hotkeys:** Support different actions (e.g., Win+Alt+S for selector)
- **Conflict detection:** Warn if hotkey is already in use
- **GUI configuration:** Settings panel for daemon options

## Troubleshooting

### Daemon won't start

1. Check if python-xlib is installed:
   ```bash
   python -c "import Xlib; print('OK')"
   ```

2. Verify X11 is running:
   ```bash
   echo $DISPLAY
   ```

3. Check for permission issues:
   ```bash
   ls -la ~/.local/share/wallpaper-manager
   ```

### Hotkey not working

1. Test if daemon is running:
   ```bash
   systemctl --user is-active wallpaper-manager-daemon.service
   ```

2. Check for conflicting keybindings in your desktop environment

3. View daemon logs for errors:
   ```bash
   journalctl --user -u wallpaper-manager-daemon.service -n 50
   ```

### Main app won't start

If the main application fails to start after adding daemon support:

1. Verify the import works:
   ```bash
   python -c "from wallpaper_manager.controller import MainController; print('OK')"
   ```

2. This should work even without python-xlib installed due to lazy loading

## Performance Impact

- **Memory:** ~5-10 MB additional memory for daemon process
- **CPU:** Negligible (event-driven, no polling)
- **Startup time:** No impact on main application (lazy loading)
- **Battery:** Minimal impact (daemon sleeps when idle)

## Security Considerations

The systemd service includes security hardening:

- `PrivateTmp=yes` - Isolated /tmp directory
- `NoNewPrivileges=yes` - Prevents privilege escalation
- `ProtectSystem=strict` - Read-only system directories
- `ProtectHome=read-only` - Limited home directory access
- `ReadWritePaths=...` - Explicit write permissions only where needed

## Conclusion

The keyboard shortcut daemon is a well-integrated optional feature that enhances the Wallpaper Manager experience without adding mandatory dependencies or complexity for users who don't need it.
