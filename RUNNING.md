# Running Wallpaper Manager

This guide will help you run the Wallpaper Manager application for the first time.

## Prerequisites

### System Requirements
- Arch Linux (or compatible distribution)
- Python 3.11 or higher
- GTK 4.0
- Either X11 with `feh` or Wayland with `swaybg`

### Required Dependencies

#### Python Packages
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install PyGObject Pillow requests tomli-w
# For Python < 3.11:
pip install tomli
# For keyboard daemon (optional):
pip install python-xlib
```

#### System Packages (Arch Linux)
```bash
# Core dependencies
sudo pacman -S python python-gobject gtk4

# For X11 (choose one):
sudo pacman -S feh

# For Wayland (choose one):
sudo pacman -S swaybg

# Optional (for keyboard daemon):
sudo pacman -S python-xlib
```

## Pre-Flight Check

Before running the application, verify all dependencies are installed:

```bash
python3 check_dependencies.py
```

This will check:
- Python version
- Required Python packages
- GTK availability
- Wallpaper backend tools (feh/swaybg)

## Testing the Application

Run the startup test to verify everything is configured correctly:

```bash
python3 test_startup.py
```

This will:
- Test all module imports
- Verify configuration loading
- Detect display server type
- Initialize the wallpaper manager
- Check GTK availability

## Running the Application

### GUI Mode (Interactive)

Start the application with the import popup:

```bash
python3 -m wallpaper_manager
```

This will:
1. Create the configuration directory at `~/.local/share/wallpaper-manager/`
2. Show the Import Popup window
3. Allow you to import wallpapers from URLs or local files
4. Open the Selector Interface to browse and select wallpapers

### Daemon Mode (Background Service)

Start the daemon for keyboard shortcut support:

```bash
python3 -m wallpaper_manager.daemon
```

The daemon will:
- Run in the background
- Listen for the Win+Alt+W keyboard shortcut
- Show the Import Popup when the shortcut is pressed
- Log to `~/.local/share/wallpaper-manager/wallpaper-manager.log`

### Using systemd (Recommended for Daemon)

Install as a systemd user service:

```bash
# Copy the service file
mkdir -p ~/.config/systemd/user/
cp wallpaper-manager-daemon.service ~/.config/systemd/user/

# Enable and start the service
systemctl --user enable wallpaper-manager-daemon.service
systemctl --user start wallpaper-manager-daemon.service

# Check status
systemctl --user status wallpaper-manager-daemon.service

# View logs
journalctl --user -u wallpaper-manager-daemon.service -f
```

## First Run Workflow

1. **Start the application**:
   ```bash
   python3 -m wallpaper_manager
   ```

2. **Import wallpapers**:
   - The Import Popup will appear
   - Choose "Import from URL" or "Upload Your Wallpapers"
   - Add one or more wallpapers
   - Click "Confirm"

3. **Select a wallpaper**:
   - The Selector Interface will appear (fullscreen, transparent overlay)
   - Browse your wallpaper collection
   - Click on a wallpaper to apply it
   - Press ESC to close

4. **Using the keyboard shortcut** (if daemon is running):
   - Press Win+Alt+W to open the Import Popup
   - Import more wallpapers or close to open the Selector Interface

## Configuration

Configuration is stored at: `~/.local/share/wallpaper-manager/config.toml`

Default configuration:
```toml
storage_path = "/home/[user]/.local/share/wallpaper-manager"
wallpaper_backend = "auto"  # or "feh" or "swaybg"
thumbnail_size = [200, 150]
grid_columns = 5
current_wallpaper_id = null
```

## Storage Structure

```
~/.local/share/wallpaper-manager/
├── config.toml              # Application configuration
├── collection.toml          # Wallpaper metadata
├── wallpaper-manager.log    # Application logs
├── wallpapers/              # Full-size wallpaper images
│   ├── [hash1].jpg
│   ├── [hash2].png
│   └── ...
└── thumbnails/              # Thumbnail images
    ├── [hash1].jpg
    ├── [hash2].jpg
    └── ...
```

## Troubleshooting

### Application won't start

1. Run the dependency check:
   ```bash
   python3 check_dependencies.py
   ```

2. Check for missing dependencies and install them

3. Verify GTK 4.0 is installed:
   ```bash
   pkg-config --modversion gtk4
   ```

### Wallpaper won't change

1. Check which display server you're using:
   ```bash
   echo $XDG_SESSION_TYPE
   ```

2. Verify the correct backend tool is installed:
   - For X11: `which feh`
   - For Wayland: `which swaybg`

3. Check the logs:
   ```bash
   tail -f ~/.local/share/wallpaper-manager/wallpaper-manager.log
   ```

### Keyboard shortcut not working

1. Ensure the daemon is running:
   ```bash
   systemctl --user status wallpaper-manager-daemon.service
   ```

2. Check if python-xlib is installed:
   ```bash
   python3 -c "import Xlib; print('OK')"
   ```

3. Verify you're on X11 (keyboard daemon doesn't work on Wayland):
   ```bash
   echo $XDG_SESSION_TYPE
   ```

### Import from URL fails

1. Check internet connectivity
2. Verify the URL points to a valid image
3. Check the logs for detailed error messages
4. Try downloading the image manually first

### Thumbnails not showing

1. Check if Pillow is installed:
   ```bash
   python3 -c "from PIL import Image; print('OK')"
   ```

2. Verify thumbnail directory exists:
   ```bash
   ls -la ~/.local/share/wallpaper-manager/thumbnails/
   ```

3. Check file permissions

## Development Mode

For development, you can run the application directly from the source:

```bash
# Install in development mode
pip install -e .

# Run the application
wallpaper-manager

# Run the daemon
wallpaper-manager-daemon
```

## Logging

Logs are written to: `~/.local/share/wallpaper-manager/wallpaper-manager.log`

To view logs in real-time:
```bash
tail -f ~/.local/share/wallpaper-manager/wallpaper-manager.log
```

To increase log verbosity, edit the logging level in the source code:
- `wallpaper_manager/__main__.py` (for GUI mode)
- `wallpaper_manager/daemon.py` (for daemon mode)

Change `log_level="INFO"` to `log_level="DEBUG"` for more detailed logs.

## Next Steps

- Read [README.md](README.md) for project overview
- Check [DAEMON_FEATURE.md](DAEMON_FEATURE.md) for daemon details
- See [AUR_README.md](AUR_README.md) for AUR package information
