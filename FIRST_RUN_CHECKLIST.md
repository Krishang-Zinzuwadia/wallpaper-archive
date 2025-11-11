# First Run Checklist

Use this checklist to ensure a smooth first run of Wallpaper Manager.

## Pre-Flight Checks

### System Requirements
- [ ] Running Arch Linux (or compatible)
- [ ] Python 3.11 or higher installed
- [ ] GTK 4.0 installed
- [ ] Either X11 with feh OR Wayland with swaybg

### Dependency Verification
```bash
# Run the dependency checker
python3 check_dependencies.py
```

- [ ] All Python packages installed
- [ ] GTK 4.0 available
- [ ] Wallpaper backend tool installed (feh or swaybg)
- [ ] python-xlib installed (optional, for keyboard daemon)

### Startup Test
```bash
# Run the startup test
python3 test_startup.py
```

- [ ] All modules import successfully
- [ ] Configuration loads correctly
- [ ] Backend detection works
- [ ] Manager initializes
- [ ] GTK is available

## First Run Steps

### 1. Start the Application
```bash
# Option A: Use the quick start script
./run.sh

# Option B: Run directly
python3 -m wallpaper_manager
```

- [ ] Application starts without errors
- [ ] Import Popup window appears
- [ ] Window is properly styled

### 2. Import Wallpapers

#### Test File Upload
- [ ] Click "Upload Your Wallpapers"
- [ ] Click "Choose Files"
- [ ] Select one or more image files
- [ ] Files appear in "Pending Imports" list
- [ ] No error messages appear

#### Test URL Import
- [ ] Click "Import from URL"
- [ ] Enter a valid image URL (e.g., https://picsum.photos/1920/1080)
- [ ] Click "Add" or press Enter
- [ ] Loading indicator appears
- [ ] URL appears in "Pending Imports" list
- [ ] No error messages appear

### 3. Confirm Imports
- [ ] Click "Confirm" button
- [ ] Import Popup closes
- [ ] Selector Interface opens

### 4. Test Selector Interface
- [ ] Fullscreen transparent overlay appears
- [ ] Wallpaper thumbnails are visible
- [ ] Thumbnails are properly sized
- [ ] "Press ESC to close" hint is visible
- [ ] Can scroll through wallpapers

### 5. Select a Wallpaper
- [ ] Click on a wallpaper thumbnail
- [ ] Desktop wallpaper changes
- [ ] Selected wallpaper is highlighted
- [ ] No error messages appear

### 6. Close Selector Interface
- [ ] Press ESC key
- [ ] Selector Interface closes
- [ ] Wallpaper remains changed

## Daemon Testing (Optional)

### Start the Daemon
```bash
# Option A: Run directly
python3 -m wallpaper_manager.daemon

# Option B: Use systemd
systemctl --user start wallpaper-manager-daemon.service
```

- [ ] Daemon starts without errors
- [ ] No immediate crashes
- [ ] Logs show successful startup

### Test Keyboard Shortcut (X11 only)
- [ ] Press Win+Alt+W
- [ ] Import Popup appears
- [ ] Can import wallpapers
- [ ] Can open Selector Interface

### Stop the Daemon
```bash
# If running directly: Press Ctrl+C

# If using systemd:
systemctl --user stop wallpaper-manager-daemon.service
```

- [ ] Daemon stops gracefully
- [ ] No error messages in logs

## Verification

### Check Storage Directory
```bash
ls -la ~/.local/share/wallpaper-manager/
```

Expected structure:
```
~/.local/share/wallpaper-manager/
├── config.toml
├── collection.toml
├── wallpaper-manager.log
├── wallpapers/
│   └── [hash].jpg
└── thumbnails/
    └── [hash].jpg
```

- [ ] config.toml exists
- [ ] collection.toml exists
- [ ] wallpapers/ directory contains images
- [ ] thumbnails/ directory contains thumbnails
- [ ] Log file exists

### Check Configuration
```bash
cat ~/.local/share/wallpaper-manager/config.toml
```

- [ ] storage_path is set
- [ ] wallpaper_backend is set
- [ ] current_wallpaper_id is set (after selecting a wallpaper)

### Check Logs
```bash
tail -50 ~/.local/share/wallpaper-manager/wallpaper-manager.log
```

- [ ] No ERROR level messages
- [ ] Backend detection logged
- [ ] Wallpaper imports logged
- [ ] Wallpaper selection logged

## Troubleshooting

### If Application Won't Start

1. Check dependencies:
   ```bash
   python3 check_dependencies.py
   ```

2. Check Python version:
   ```bash
   python3 --version
   ```

3. Check GTK installation:
   ```bash
   pkg-config --modversion gtk4
   ```

4. Check logs:
   ```bash
   tail -f ~/.local/share/wallpaper-manager/wallpaper-manager.log
   ```

### If Wallpaper Won't Change

1. Check display server:
   ```bash
   echo $XDG_SESSION_TYPE
   ```

2. Check backend tool:
   ```bash
   # For X11:
   which feh
   feh --version
   
   # For Wayland:
   which swaybg
   swaybg --version
   ```

3. Test backend manually:
   ```bash
   # For X11:
   feh --bg-scale /path/to/test/image.jpg
   
   # For Wayland:
   swaybg -i /path/to/test/image.jpg -m fill
   ```

### If Import Fails

1. Check file permissions:
   ```bash
   ls -la ~/.local/share/wallpaper-manager/
   ```

2. Check disk space:
   ```bash
   df -h ~/.local/share/
   ```

3. For URL imports, check network:
   ```bash
   curl -I https://picsum.photos/1920/1080
   ```

4. Check image file validity:
   ```bash
   file /path/to/image.jpg
   python3 -c "from PIL import Image; Image.open('/path/to/image.jpg').verify()"
   ```

### If Keyboard Shortcut Doesn't Work

1. Check if daemon is running:
   ```bash
   ps aux | grep wallpaper-manager-daemon
   ```

2. Check if on X11:
   ```bash
   echo $XDG_SESSION_TYPE
   # Should output: x11
   ```

3. Check python-xlib:
   ```bash
   python3 -c "import Xlib; print('OK')"
   ```

4. Check daemon logs:
   ```bash
   journalctl --user -u wallpaper-manager-daemon.service -f
   ```

## Performance Checks

### Memory Usage
```bash
# While Selector Interface is open:
ps aux | grep wallpaper-manager
```

- [ ] Memory usage is reasonable (< 200MB for small collections)
- [ ] No memory leaks after multiple opens/closes

### Startup Time
- [ ] Application starts in < 2 seconds
- [ ] Import Popup appears quickly
- [ ] Selector Interface opens in < 1 second

### UI Responsiveness
- [ ] Import Popup is responsive
- [ ] Selector Interface scrolls smoothly
- [ ] Wallpaper selection is instant
- [ ] No UI freezing or lag

## Success Criteria

All of the following should be true:

- [ ] Application starts without errors
- [ ] Can import wallpapers from files
- [ ] Can import wallpapers from URLs
- [ ] Thumbnails are generated correctly
- [ ] Can browse wallpapers in Selector Interface
- [ ] Can select and apply wallpapers
- [ ] Desktop wallpaper actually changes
- [ ] Configuration is saved correctly
- [ ] Logs show no errors

## Post-First-Run

### Optional: Install as System Service
```bash
# Copy service file
mkdir -p ~/.config/systemd/user/
cp wallpaper-manager-daemon.service ~/.config/systemd/user/

# Enable and start
systemctl --user enable wallpaper-manager-daemon.service
systemctl --user start wallpaper-manager-daemon.service
```

### Optional: Install System-Wide
```bash
# Install with pip
pip install -e .

# Or build and install package
python3 setup.py install --user
```

### Optional: Create Desktop Entry
```bash
# Copy desktop file
mkdir -p ~/.local/share/applications/
cp wallpaper-manager.desktop ~/.local/share/applications/

# Update desktop database
update-desktop-database ~/.local/share/applications/
```

## Feedback

After completing the first run, please note:

1. **What worked well**:
   - 

2. **What didn't work**:
   - 

3. **Error messages encountered**:
   - 

4. **Performance issues**:
   - 

5. **Suggestions for improvement**:
   - 

## Next Steps

- [ ] Import more wallpapers
- [ ] Organize wallpapers (future feature)
- [ ] Set up automatic wallpaper rotation (future feature)
- [ ] Configure keyboard shortcuts (if using daemon)
- [ ] Share feedback and report bugs

---

**Date Completed**: _______________

**Status**: ⬜ Success | ⬜ Partial Success | ⬜ Failed

**Notes**:
