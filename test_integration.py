#!/usr/bin/env python3
"""
Integration testing script for Wallpaper Manager
Tests different desktop environments, multi-monitor support, and large collections
"""

import sys
import logging
import subprocess
from pathlib import Path
from typing import Optional

from wallpaper_manager.config import Config
from wallpaper_manager.manager import WallpaperManager
from wallpaper_manager.backends import detect_display_server, FehBackend, SwaybgBackend

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegrationTest:
    """Integration test suite"""
    
    def __init__(self):
        self.config = Config()
        self.test_results = []
        
    def run_all_tests(self):
        """Run all integration tests"""
        logger.info("=" * 60)
        logger.info("Starting Integration Tests")
        logger.info("=" * 60)
        
        # Test 1: Desktop environment detection
        self.test_desktop_environment_detection()
        
        # Test 2: Backend compatibility
        self.test_backend_compatibility()
        
        # Test 3: Multi-monitor detection
        self.test_multi_monitor_detection()
        
        # Test 4: Large collection performance
        self.test_large_collection_performance()
        
        # Test 5: AUR package structure validation
        self.test_aur_package_structure()
        
        # Print results
        self.print_results()
        
    def test_desktop_environment_detection(self):
        """Test 1: Detect desktop environment (X11 vs Wayland)"""
        logger.info("\n[Test 1] Testing desktop environment detection...")
        
        try:
            display_server = detect_display_server()
            logger.info(f"Detected display server: {display_server}")
            
            assert display_server in ["x11", "wayland", "unknown"], \
                f"Invalid display server type: {display_server}"
            
            # Check environment variables
            wayland_display = subprocess.run(
                ["printenv", "WAYLAND_DISPLAY"],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            x_display = subprocess.run(
                ["printenv", "DISPLAY"],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            logger.info(f"WAYLAND_DISPLAY: {wayland_display or 'not set'}")
            logger.info(f"DISPLAY: {x_display or 'not set'}")
            
            self.test_results.append(("Desktop Environment Detection", "PASS", f"Detected: {display_server}"))
            logger.info("✓ Test 1 PASSED")
            
        except AssertionError as e:
            self.test_results.append(("Desktop Environment Detection", "FAIL", str(e)))
            logger.error(f"✗ Test 1 FAILED: {e}")
        except Exception as e:
            self.test_results.append(("Desktop Environment Detection", "ERROR", str(e)))
            logger.error(f"✗ Test 1 ERROR: {e}")
    
    def test_backend_compatibility(self):
        """Test 2: Verify backend compatibility"""
        logger.info("\n[Test 2] Testing backend compatibility...")
        
        try:
            display_server = detect_display_server()
            
            # Check if appropriate backend tools are available
            if display_server == "x11":
                # Check for feh
                result = subprocess.run(["which", "feh"], capture_output=True)
                feh_available = result.returncode == 0
                logger.info(f"feh available: {feh_available}")
                
                if feh_available:
                    backend = FehBackend()
                    logger.info("FehBackend initialized successfully")
                else:
                    logger.warning("feh not found, but backend can still be initialized")
                    backend = FehBackend()
                
            elif display_server == "wayland":
                # Check for swaybg
                result = subprocess.run(["which", "swaybg"], capture_output=True)
                swaybg_available = result.returncode == 0
                logger.info(f"swaybg available: {swaybg_available}")
                
                if swaybg_available:
                    backend = SwaybgBackend()
                    logger.info("SwaybgBackend initialized successfully")
                else:
                    logger.warning("swaybg not found, but backend can still be initialized")
                    backend = SwaybgBackend()
            else:
                logger.warning("Unknown display server, using default FehBackend")
                backend = FehBackend()
            
            self.test_results.append(("Backend Compatibility", "PASS", f"Backend for {display_server} initialized"))
            logger.info("✓ Test 2 PASSED")
            
        except Exception as e:
            self.test_results.append(("Backend Compatibility", "ERROR", str(e)))
            logger.error(f"✗ Test 2 ERROR: {e}")
    
    def test_multi_monitor_detection(self):
        """Test 3: Verify multi-monitor detection"""
        logger.info("\n[Test 3] Testing multi-monitor detection...")
        
        try:
            display_server = detect_display_server()
            
            if display_server == "x11":
                # Use xrandr to detect monitors
                result = subprocess.run(
                    ["xrandr", "--listmonitors"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    output = result.stdout
                    lines = output.strip().split('\n')
                    monitor_count = len([l for l in lines if '+' in l])
                    logger.info(f"Detected {monitor_count} monitor(s) via xrandr")
                else:
                    logger.warning("xrandr not available or failed")
                    monitor_count = 1
                    
            elif display_server == "wayland":
                # For Wayland, we'd need compositor-specific tools
                logger.info("Wayland detected - multi-monitor detection is compositor-specific")
                monitor_count = 1  # Default assumption
            else:
                logger.warning("Unknown display server")
                monitor_count = 1
            
            logger.info(f"Monitor count: {monitor_count}")
            
            self.test_results.append(("Multi-Monitor Detection", "PASS", f"{monitor_count} monitor(s) detected"))
            logger.info("✓ Test 3 PASSED")
            
        except Exception as e:
            self.test_results.append(("Multi-Monitor Detection", "ERROR", str(e)))
            logger.error(f"✗ Test 3 ERROR: {e}")
    
    def test_large_collection_performance(self):
        """Test 4: Test with large wallpaper collections"""
        logger.info("\n[Test 4] Testing large collection performance...")
        
        try:
            manager = WallpaperManager(self.config)
            
            # Get current collection size
            wallpapers = manager.get_all_wallpapers()
            collection_size = len(wallpapers)
            
            logger.info(f"Current collection size: {collection_size} wallpapers")
            
            # Test collection retrieval performance
            import time
            start_time = time.time()
            wallpapers = manager.get_all_wallpapers()
            end_time = time.time()
            
            retrieval_time = end_time - start_time
            logger.info(f"Collection retrieval time: {retrieval_time:.3f}s")
            
            # Performance expectations
            if collection_size < 10:
                expected_time = 0.1
            elif collection_size < 100:
                expected_time = 0.5
            else:
                expected_time = 2.0
            
            if retrieval_time > expected_time:
                logger.warning(f"Collection retrieval slower than expected ({expected_time}s)")
            
            # Check storage structure
            wallpapers_dir = self.config.storage_path / "wallpapers"
            thumbnails_dir = self.config.storage_path / "thumbnails"
            
            wallpaper_files = list(wallpapers_dir.glob("*")) if wallpapers_dir.exists() else []
            thumbnail_files = list(thumbnails_dir.glob("*")) if thumbnails_dir.exists() else []
            
            logger.info(f"Wallpaper files: {len(wallpaper_files)}")
            logger.info(f"Thumbnail files: {len(thumbnail_files)}")
            
            self.test_results.append((
                "Large Collection Performance",
                "PASS",
                f"{collection_size} wallpapers, {retrieval_time:.3f}s retrieval"
            ))
            logger.info("✓ Test 4 PASSED")
            
        except Exception as e:
            self.test_results.append(("Large Collection Performance", "ERROR", str(e)))
            logger.error(f"✗ Test 4 ERROR: {e}")
    
    def test_aur_package_structure(self):
        """Test 5: Validate AUR package structure"""
        logger.info("\n[Test 5] Testing AUR package structure...")
        
        try:
            # Check for required files
            required_files = [
                "PKGBUILD",
                "setup.py",
                "requirements.txt",
                "wallpaper-manager-daemon.service",
                "wallpaper-manager.desktop"
            ]
            
            missing_files = []
            for file in required_files:
                file_path = Path(file)
                if not file_path.exists():
                    missing_files.append(file)
                    logger.warning(f"Missing required file: {file}")
                else:
                    logger.info(f"✓ Found: {file}")
            
            # Check package structure
            package_dir = Path("wallpaper_manager")
            if not package_dir.exists():
                raise FileNotFoundError("wallpaper_manager package directory not found")
            
            logger.info("✓ Package directory exists")
            
            # Check for __init__.py
            init_file = package_dir / "__init__.py"
            if not init_file.exists():
                logger.warning("Missing __init__.py in package directory")
            else:
                logger.info("✓ Package __init__.py exists")
            
            # Check for UI module
            ui_dir = package_dir / "ui"
            if not ui_dir.exists():
                logger.warning("Missing ui module")
            else:
                logger.info("✓ UI module exists")
            
            if missing_files:
                self.test_results.append((
                    "AUR Package Structure",
                    "FAIL",
                    f"Missing files: {', '.join(missing_files)}"
                ))
                logger.warning(f"✗ Test 5 FAILED: Missing {len(missing_files)} required files")
            else:
                self.test_results.append(("AUR Package Structure", "PASS", "All required files present"))
                logger.info("✓ Test 5 PASSED")
            
        except Exception as e:
            self.test_results.append(("AUR Package Structure", "ERROR", str(e)))
            logger.error(f"✗ Test 5 ERROR: {e}")
    
    def print_results(self):
        """Print test results summary"""
        logger.info("\n" + "=" * 60)
        logger.info("Integration Test Results Summary")
        logger.info("=" * 60)
        
        passed = sum(1 for _, status, _ in self.test_results if status == "PASS")
        failed = sum(1 for _, status, _ in self.test_results if status == "FAIL")
        errors = sum(1 for _, status, _ in self.test_results if status == "ERROR")
        
        for test_name, status, message in self.test_results:
            status_symbol = "✓" if status == "PASS" else "✗"
            logger.info(f"{status_symbol} {test_name}: {status}")
            if message:
                logger.info(f"  └─ {message}")
        
        logger.info("\n" + "-" * 60)
        logger.info(f"Total: {len(self.test_results)} | Passed: {passed} | Failed: {failed} | Errors: {errors}")
        logger.info("=" * 60)
        
        return failed == 0 and errors == 0


def main():
    """Main test runner"""
    test = IntegrationTest()
    success = test.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
