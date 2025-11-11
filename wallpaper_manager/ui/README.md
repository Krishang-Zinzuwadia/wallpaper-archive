# Wallpaper Manager UI Components

This module contains GTK4 UI components for the Wallpaper Manager application.

## Import Popup

The `ImportPopup` class provides a GTK4 window for importing wallpapers from URLs or local files.

### Features

- **Dual Import Modes**:
  - URL Import: Download wallpapers from web URLs
  - File Upload: Select local image files

- **Real-time Validation**:
  - URL format validation
  - Image format validation (PNG, JPG, JPEG, WEBP)
  - File size validation (max 50MB)

- **User Feedback**:
  - Loading indicators during downloads
  - Preview list of pending imports
  - Error dialogs with detailed messages
  - Retry mechanism for network failures

- **Supported Image Formats**: PNG, JPG, JPEG, WEBP

### Usage

```python
from wallpaper_manager.config import Config
from wallpaper_manager.manager import WallpaperManager
from wallpaper_manager.ui import ImportPopup

# Initialize configuration and manager
config = Config.load()
wallpaper_manager = WallpaperManager(config)

# Create popup with callback
def on_confirm():
    print("User confirmed imports!")

popup = ImportPopup(wallpaper_manager, on_confirm=on_confirm)
popup.present()
```

### Testing

Run the test script to see the Import Popup in action:

```bash
python3 test_import_popup.py
```

## Requirements

- GTK4
- PyGObject >= 3.42
- Python >= 3.11 (or 3.10 with tomli)
