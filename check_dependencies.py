#!/usr/bin/env python3
"""
Pre-flight check script to verify all dependencies are installed
"""

import sys
import importlib.util

def check_module(module_name, package_name=None):
    """Check if a module is available"""
    if package_name is None:
        package_name = module_name
    
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        print(f"❌ {package_name} is NOT installed")
        return False
    else:
        print(f"✅ {package_name} is installed")
        return True

def check_gi_version(version_name, version_number):
    """Check if a specific GI version is available"""
    try:
        import gi
        gi.require_version(version_name, version_number)
        print(f"✅ {version_name} {version_number} is available")
        return True
    except (ImportError, ValueError) as e:
        print(f"❌ {version_name} {version_number} is NOT available: {e}")
        return False

def main():
    print("Checking Wallpaper Manager dependencies...\n")
    
    all_ok = True
    
    # Check Python version
    print(f"Python version: {sys.version}")
    if sys.version_info < (3, 11):
        print("⚠️  Warning: Python 3.11+ is recommended")
    print()
    
    # Check core dependencies
    print("Core Dependencies:")
    all_ok &= check_module("PIL", "Pillow")
    all_ok &= check_module("requests")
    all_ok &= check_module("tomli_w", "tomli-w")
    
    # Check tomllib (built-in for Python 3.11+) or tomli
    if sys.version_info >= (3, 11):
        all_ok &= check_module("tomllib", "tomllib (built-in)")
    else:
        all_ok &= check_module("tomli")
    
    print()
    
    # Check GTK dependencies
    print("GTK Dependencies:")
    all_ok &= check_module("gi", "PyGObject")
    if check_module("gi"):
        all_ok &= check_gi_version("Gtk", "4.0")
        all_ok &= check_gi_version("Gdk", "4.0")
        all_ok &= check_gi_version("GdkPixbuf", "2.0")
    
    print()
    
    # Check optional dependencies
    print("Optional Dependencies (for keyboard daemon):")
    xlib_ok = check_module("Xlib", "python-xlib")
    if not xlib_ok:
        print("  ℹ️  Keyboard daemon will not work without python-xlib")
    
    print()
    
    # Check system tools
    print("System Tools:")
    import shutil
    feh_path = shutil.which("feh")
    swaybg_path = shutil.which("swaybg")
    
    if feh_path:
        print(f"✅ feh is installed at {feh_path}")
    else:
        print("❌ feh is NOT installed (needed for X11)")
    
    if swaybg_path:
        print(f"✅ swaybg is installed at {swaybg_path}")
    else:
        print("❌ swaybg is NOT installed (needed for Wayland)")
    
    if not feh_path and not swaybg_path:
        print("⚠️  Warning: Neither feh nor swaybg is installed!")
        all_ok = False
    
    print()
    
    # Summary
    if all_ok:
        print("✅ All required dependencies are installed!")
        print("\nYou can now run the application with:")
        print("  python3 -m wallpaper_manager")
        return 0
    else:
        print("❌ Some dependencies are missing!")
        print("\nTo install missing Python dependencies:")
        print("  pip install -r requirements.txt")
        print("\nTo install system dependencies on Arch Linux:")
        print("  sudo pacman -S python-gobject gtk4 feh")
        print("  # or for Wayland: sudo pacman -S swaybg")
        return 1

if __name__ == "__main__":
    sys.exit(main())
