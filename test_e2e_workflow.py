#!/usr/bin/env python3
"""
End-to-end workflow integration test
Tests the complete user flow from keyboard shortcut to wallpaper selection
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
import sys
import time
import logging
from pathlib import Path

from wallpaper_manager.config import Config
from wallpaper_manager.controller import MainController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class E2EWorkflowTest:
    """End-to-end workflow test runner"""
    
    def __init__(self):
        self.config = Config()
        self.controller = MainController(self.config, enable_daemon=False)
        self.test_results = []
        
    def run_tests(self):
        """Run all end-to-end tests"""
        logger.info("=" * 60)
        logger.info("Starting End-to-End Workflow Tests")
        logger.info("=" * 60)
        
        # Test 1: Verify Import Popup can be triggered
        self.test_import_popup_trigger()
        
        # Test 2: Verify Selector Interface can be shown
        self.test_selector_interface_display()
        
        # Test 3: Verify window state management
        self.test_window_state_management()
        
        # Test 4: Verify persistence (config save/load)
        self.test_persistence()
        
        # Print results
        self.print_results()
        
    def test_import_popup_trigger(self):
        """Test 1: Verify keyboard shortcut triggers Import Popup"""
        logger.info("\n[Test 1] Testing Import Popup trigger...")
        
        try:
            # Trigger Import Popup
            self.controller.show_import_popup()
            
            # Verify window is open
            assert self.controller.is_import_popup_open(), "Import Popup should be open"
            assert self.controller.get_active_window() == 'import', "Active window should be 'import'"
            
            # Verify window properties
            assert self.controller._import_popup is not None, "Import Popup instance should exist"
            assert self.controller._import_popup.is_visible(), "Import Popup should be visible"
            
            # Close the window
            self.controller._import_popup.close()
            
            self.test_results.append(("Import Popup Trigger", "PASS", None))
            logger.info("✓ Test 1 PASSED")
            
        except AssertionError as e:
            self.test_results.append(("Import Popup Trigger", "FAIL", str(e)))
            logger.error(f"✗ Test 1 FAILED: {e}")
        except Exception as e:
            self.test_results.append(("Import Popup Trigger", "ERROR", str(e)))
            logger.error(f"✗ Test 1 ERROR: {e}")
    
    def test_selector_interface_display(self):
        """Test 2: Verify Selector Interface can be displayed"""
        logger.info("\n[Test 2] Testing Selector Interface display...")
        
        try:
            # Show Selector Interface
            self.controller.show_selector_interface()
            
            # Verify window is open
            assert self.controller.is_selector_interface_open(), "Selector Interface should be open"
            assert self.controller.get_active_window() == 'selector', "Active window should be 'selector'"
            
            # Verify window properties
            assert self.controller._selector_interface is not None, "Selector Interface instance should exist"
            assert self.controller._selector_interface.is_visible(), "Selector Interface should be visible"
            
            # Close the window
            self.controller._selector_interface.close()
            
            self.test_results.append(("Selector Interface Display", "PASS", None))
            logger.info("✓ Test 2 PASSED")
            
        except AssertionError as e:
            self.test_results.append(("Selector Interface Display", "FAIL", str(e)))
            logger.error(f"✗ Test 2 FAILED: {e}")
        except Exception as e:
            self.test_results.append(("Selector Interface Display", "ERROR", str(e)))
            logger.error(f"✗ Test 2 ERROR: {e}")
    
    def test_window_state_management(self):
        """Test 3: Verify window state management"""
        logger.info("\n[Test 3] Testing window state management...")
        
        try:
            # Initially no windows should be open
            assert not self.controller.is_import_popup_open(), "No windows should be open initially"
            assert not self.controller.is_selector_interface_open(), "No windows should be open initially"
            assert self.controller.get_active_window() is None, "No active window initially"
            
            # Open Import Popup
            self.controller.show_import_popup()
            assert self.controller.is_import_popup_open(), "Import Popup should be open"
            assert self.controller.get_active_window() == 'import', "Active window should be 'import'"
            
            # Trigger Import Popup again (should focus existing window)
            self.controller.show_import_popup()
            assert self.controller.is_import_popup_open(), "Import Popup should still be open"
            
            # Close Import Popup
            self.controller._import_popup.close()
            time.sleep(0.1)  # Allow time for close event
            
            # Open Selector Interface
            self.controller.show_selector_interface()
            assert self.controller.is_selector_interface_open(), "Selector Interface should be open"
            assert self.controller.get_active_window() == 'selector', "Active window should be 'selector'"
            
            # Hide all windows
            self.controller.hide_all_windows()
            assert not self.controller._selector_interface.is_visible(), "Selector should be hidden"
            
            # Cleanup
            self.controller._selector_interface.close()
            
            self.test_results.append(("Window State Management", "PASS", None))
            logger.info("✓ Test 3 PASSED")
            
        except AssertionError as e:
            self.test_results.append(("Window State Management", "FAIL", str(e)))
            logger.error(f"✗ Test 3 FAILED: {e}")
        except Exception as e:
            self.test_results.append(("Window State Management", "ERROR", str(e)))
            logger.error(f"✗ Test 3 ERROR: {e}")
    
    def test_persistence(self):
        """Test 4: Verify configuration persistence"""
        logger.info("\n[Test 4] Testing configuration persistence...")
        
        try:
            # Save current config
            original_wallpaper_id = self.config.current_wallpaper_id
            test_wallpaper_id = "test_wallpaper_12345"
            
            # Update config
            self.config.current_wallpaper_id = test_wallpaper_id
            self.config.save()
            
            # Create new config instance (simulates restart)
            new_config = Config()
            
            # Verify persistence
            assert new_config.current_wallpaper_id == test_wallpaper_id, \
                f"Config should persist wallpaper ID: expected {test_wallpaper_id}, got {new_config.current_wallpaper_id}"
            
            # Restore original config
            self.config.current_wallpaper_id = original_wallpaper_id
            self.config.save()
            
            self.test_results.append(("Configuration Persistence", "PASS", None))
            logger.info("✓ Test 4 PASSED")
            
        except AssertionError as e:
            self.test_results.append(("Configuration Persistence", "FAIL", str(e)))
            logger.error(f"✗ Test 4 FAILED: {e}")
        except Exception as e:
            self.test_results.append(("Configuration Persistence", "ERROR", str(e)))
            logger.error(f"✗ Test 4 ERROR: {e}")
    
    def print_results(self):
        """Print test results summary"""
        logger.info("\n" + "=" * 60)
        logger.info("Test Results Summary")
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
    app = Gtk.Application()
    
    def on_activate(app):
        test = E2EWorkflowTest()
        success = test.run_tests()
        
        # Cleanup
        test.controller.shutdown()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
    
    app.connect('activate', on_activate)
    app.run(None)


if __name__ == "__main__":
    main()
