# Wallpaper Manager

A modern, transparent wallpaper manager for Arch Linux with an intuitive interface for importing, organizing, and switching desktop wallpapers.

## Features

- **Keyboard shortcut activation** - Press Win+Alt+W to instantly access your wallpapers
- **Multiple import methods** - Import from URLs or upload local files
- **Transparent overlay interface** - Beautiful, non-intrusive UI with scrollable grid
- **Real-time preview** - Apply wallpapers instantly with a single click
- **Multi-backend support** - Works with feh (X11) and swaybg (Wayland)
- **Automatic thumbnail generation** - Fast browsing with optimized thumbnails
- **Persistent collection** - Your wallpapers are saved and organized automatically
- **AUR package** - Easy installation and updates

## Installation

### From AUR (Recommended) in future

Using an AUR helper:
```bash
yay -S wallpaper-manager
# or
paru -S wallpaper-manager
```

Manual installation:  in future
```bash
git clone https://aur.archlinux.org/wallpaper-manager.git
cd wallpaper-manager
makepkg -si
```

### From Source

```bash
git clone https://github.com/user/wallpaper-manager.git
cd wallpaper-manager
pip install -e .
```

### Post-Installation

Enable the keyboard shortcut daemon:
```bash
systemctl --user enable --now wallpaper-manager-daemon.service
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

- `storage_path` - Directory where wallpapers and thumbnails are stored
- `wallpaper_backend` - Backend to use (`auto`, `feh`, `swaybg`)
- `thumbnail_size` - Size of thumbnail images [width, height]
- `grid_columns` - Number of columns in the wallpaper grid

## Supported Backends

### X11
- **feh** (default, installed automatically)
- **nitrogen** (optional alternative)

### Wayland
- **swaybg** (install with: `sudo pacman -S swaybg`)

## Requirements

### Required
- Python 3.11+
- GTK4
- PyGObject
- Pillow
- python-requests
- python-tomli-w
- python-xlib
- feh (X11 backend)

### Optional
- swaybg (Wayland backend)
- nitrogen (alternative X11 backend)

## Troubleshooting

### Keyboard Shortcut Not Working

Check if the daemon is running:
```bash
systemctl --user status wallpaper-manager-daemon.service
```

Restart the daemon:
```bash
systemctl --user restart wallpaper-manager-daemon.service
```

### Wallpaper Not Applying

For X11 users, ensure feh is installed:
```bash
pacman -Q feh
```

For Wayland users, install swaybg:
```bash
sudo pacman -S swaybg
```

### More Help

See [AUR_README.md](AUR_README.md) for comprehensive troubleshooting guide.

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Project Structure

```
wallpaper_manager/
├── __init__.py
├── __main__.py          # Entry point
├── backends.py          # Wallpaper backend abstraction
├── config.py            # Configuration management
├── controller.py        # Main application controller
├── daemon.py            # Keyboard shortcut daemon
├── manager.py           # Wallpaper management logic
├── models.py            # Data models
└── ui/
    ├── import_popup.py      # Import dialog UI
    └── selector_interface.py # Wallpaper selector UI
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See [LICENSE](LICENSE) file for details

## Support

- **Issues**: https://github.com/user/wallpaper-manager/issues
- **AUR Package**: https://aur.archlinux.org/packages/wallpaper-manager
