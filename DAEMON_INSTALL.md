# Wallpaper Manager Daemon Installation

This document describes how to install and configure the Wallpaper Manager keyboard shortcut daemon.

## Prerequisites

- Arch Linux or compatible distribution
- X11 display server (Wayland support coming soon)
- Python 3.11 or higher
- python-xlib package (only required for daemon functionality)

**Note:** The main Wallpaper Manager application works without the daemon. The daemon is an optional feature that enables the system-wide keyboard shortcut (Win+Alt+W). If you don't need the keyboard shortcut, you can skip the daemon installation and just use `wallpaper-manager` command to launch the application manually.

## Installation

### 1. Install the package

```bash
# Install from AUR (recommended)
yay -S wallpaper-manager

# Or install manually
pip install -e .
```

### 2. Install the systemd user service

```bash
# Copy the service file to systemd user directory
mkdir -p ~/.config/systemd/user
cp wallpaper-manager-daemon.service ~/.config/systemd/user/

# Or if installed system-wide
sudo cp wallpaper-manager-daemon.service /usr/lib/systemd/user/
```

### 3. Enable and start the daemon

```bash
# Reload systemd user daemon
systemctl --user daemon-reload

# Enable the service to start on login
systemctl --user enable wallpaper-manager-daemon.service

# Start the service now
systemctl --user start wallpaper-manager-daemon.service
```

## Usage

Once the daemon is running, press **Win+Alt+W** (Super+Alt+W) to open the wallpaper import popup.

## Managing the Daemon

### Check daemon status

```bash
systemctl --user status wallpaper-manager-daemon.service
```

### View daemon logs

```bash
journalctl --user -u wallpaper-manager-daemon.service -f
```

### Stop the daemon

```bash
systemctl --user stop wallpaper-manager-daemon.service
```

### Disable the daemon

```bash
systemctl --user disable wallpaper-manager-daemon.service
```

### Restart the daemon

```bash
systemctl --user restart wallpaper-manager-daemon.service
```

## Troubleshooting

### Daemon fails to start

1. Check the logs:
   ```bash
   journalctl --user -u wallpaper-manager-daemon.service -n 50
   ```

2. Verify python-xlib is installed:
   ```bash
   python -c "import Xlib; print('OK')"
   ```

3. Check if DISPLAY environment variable is set:
   ```bash
   echo $DISPLAY
   ```

### Hotkey not working

1. Verify the daemon is running:
   ```bash
   systemctl --user status wallpaper-manager-daemon.service
   ```

2. Check for conflicting keybindings in your desktop environment

3. Test the application manually:
   ```bash
   wallpaper-manager
   ```

### Permission issues

Ensure the storage directories are writable:
```bash
mkdir -p ~/.local/share/wallpaper-manager/{wallpapers,thumbnails}
chmod 755 ~/.local/share/wallpaper-manager
```

## Uninstallation

```bash
# Stop and disable the service
systemctl --user stop wallpaper-manager-daemon.service
systemctl --user disable wallpaper-manager-daemon.service

# Remove the service file
rm ~/.config/systemd/user/wallpaper-manager-daemon.service

# Reload systemd
systemctl --user daemon-reload

# Optionally remove data
rm -rf ~/.local/share/wallpaper-manager
rm -rf ~/.config/wallpaper-manager
```
