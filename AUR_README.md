# Wallpaper Manager - AUR Package

A modern, transparent wallpaper manager for Arch Linux with an intuitive interface for importing, organizing, and switching desktop wallpapers.

## Installation

### Using an AUR Helper (Recommended)

```bash
yay -S wallpaper-manager
```

or

```bash
paru -S wallpaper-manager
```

### Manual Installation

```bash
git clone https://aur.archlinux.org/wallpaper-manager.git
cd wallpaper-manager
makepkg -si
```

## Post-Installation Setup

After installation, enable the keyboard shortcut daemon:

```bash
systemctl --user enable --now wallpaper-manager-daemon.service
```

Verify the daemon is running:

```bash
systemctl --user status wallpaper-manager-daemon.service
```

## Usage

### Quick Start

1. Press `Win+Alt+W` (Super+Alt+W) to open the wallpaper manager
2. Choose "Import from URL" or "Upload Your Wallpapers"
3. Add wallpapers to your collection
4. Click "Confirm" to save and view your collection
5. Click any wallpaper thumbnail to apply it instantly

### Keyboard Shortcuts

- `Win+Alt+W` - Open wallpaper manager
- `Escape` - Close selector interface

## Configuration

Configuration is automatically created at `~/.local/share/wallpaper-manager/config.toml`

### Default Configuration

```toml
storage_path = "~/.local/share/wallpaper-manager"
wallpaper_backend = "auto"
thumbnail_size = [200, 150]
grid_columns = 5
```

### Configuration Options

- `storage_path`: Directory where wallpapers and thumbnails are stored
- `wallpaper_backend`: Backend to use for setting wallpapers
  - `auto` - Automatically detect (recommended)
  - `feh` - Use feh (X11)
  - `swaybg` - Use swaybg (Wayland)
- `thumbnail_size`: Size of thumbnail images [width, height]
- `grid_columns`: Number of columns in the wallpaper grid

## Supported Backends

### X11 (Default)
- **feh** (installed by default)
- **nitrogen** (optional)

### Wayland
- **swaybg** (optional dependency)
  ```bash
  sudo pacman -S swaybg
  ```

## Directory Structure

```
~/.local/share/wallpaper-manager/
├── wallpapers/          # Full-size wallpaper images
├── thumbnails/          # Generated thumbnails
└── config.toml          # Configuration file
```

## Troubleshooting

### Keyboard Shortcut Not Working

**Check if the daemon is running:**
```bash
systemctl --user status wallpaper-manager-daemon.service
```

**Restart the daemon:**
```bash
systemctl --user restart wallpaper-manager-daemon.service
```

**Check daemon logs:**
```bash
journalctl --user -u wallpaper-manager-daemon.service -f
```

### Wallpaper Not Applying

**Check which backend is being used:**
```bash
cat ~/.local/share/wallpaper-manager/config.toml | grep wallpaper_backend
```

**For X11 users:**
- Ensure `feh` is installed: `pacman -Q feh`
- Test manually: `feh --bg-scale /path/to/image.jpg`

**For Wayland users:**
- Install swaybg: `sudo pacman -S swaybg`
- Test manually: `swaybg -i /path/to/image.jpg`

### Import from URL Fails

**Check network connectivity:**
```bash
ping -c 3 google.com
```

**Verify URL is accessible:**
```bash
curl -I <your-image-url>
```

**Check permissions:**
```bash
ls -la ~/.local/share/wallpaper-manager/
```

### UI Not Appearing

**Check GTK4 installation:**
```bash
pacman -Q gtk4
```

**Check PyGObject installation:**
```bash
python -c "import gi; print(gi.__version__)"
```

**Run in debug mode:**
```bash
wallpaper-manager --debug
```

### Permission Errors

**Fix storage directory permissions:**
```bash
mkdir -p ~/.local/share/wallpaper-manager
chmod 755 ~/.local/share/wallpaper-manager
```

### High Memory Usage

If you have a large collection (100+ wallpapers), the application uses lazy loading to minimize memory usage. However, if you experience issues:

1. Reduce `grid_columns` in config.toml
2. Clear unused wallpapers
3. Reduce `thumbnail_size` in config.toml

## Uninstallation

### Remove Package

```bash
sudo pacman -R wallpaper-manager
```

### Remove All Data (Optional)

```bash
rm -rf ~/.local/share/wallpaper-manager
rm -rf ~/.config/wallpaper-manager
```

## Dependencies

### Required
- python (>=3.11)
- python-gobject
- gtk4
- python-pillow
- python-requests
- python-tomli-w
- python-xlib
- feh

### Optional
- swaybg: Wayland wallpaper support
- nitrogen: Alternative X11 backend

## Known Issues

### Multi-Monitor Support
Currently, the same wallpaper is applied to all monitors. Independent per-monitor wallpapers are planned for a future release.

### Wayland Compositor Compatibility
- **Sway**: Fully supported with swaybg
- **Niri**: Fully supported with swaybg
- **Hyprland**: May require additional configuration
- **GNOME Wayland**: Use gsettings backend (not yet implemented)

## Support

- **Issues**: https://github.com/user/wallpaper-manager/issues
- **AUR Package**: https://aur.archlinux.org/packages/wallpaper-manager
- **Documentation**: https://github.com/user/wallpaper-manager

## License

MIT License - See LICENSE file for details
