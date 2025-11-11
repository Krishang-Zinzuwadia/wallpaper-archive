#!/usr/bin/env python
"""
Manual test script for keyboard daemon functionality

This script demonstrates how to test the keyboard daemon.
Note: Requires python-xlib to be installed and X11 display server.

Usage:
    python test_daemon_manual.py

Press Win+Alt+W to trigger the callback.
Press Ctrl+C to exit.
"""

import sys
import time
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

try:
    from wallpaper_manager.keyboard_daemon import KeyboardDaemon
except ImportError as e:
    logger.error(f"Failed to import KeyboardDaemon: {e}")
    logger.error("Make sure python-xlib is installed: pip install python-xlib")
    sys.exit(1)


def hotkey_callback():
    """Callback function triggered when hotkey is pressed"""
    logger.info("=" * 50)
    logger.info("HOTKEY PRESSED! Win+Alt+W detected!")
    logger.info("=" * 50)


def main():
    """Main test function"""
    logger.info("Starting keyboard daemon test")
    logger.info("Press Win+Alt+W to trigger the callback")
    logger.info("Press Ctrl+C to exit")
    logger.info("-" * 50)
    
    # Create and configure daemon
    daemon = KeyboardDaemon()
    daemon.register_hotkey(
        modifiers=['super', 'alt'],
        key='w',
        callback=hotkey_callback
    )
    
    try:
        # Start daemon
        daemon.start()
        logger.info("Daemon started successfully")
        logger.info("Listening for Win+Alt+W...")
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("\nReceived interrupt signal")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        # Cleanup
        logger.info("Stopping daemon...")
        daemon.stop()
        logger.info("Daemon stopped")


if __name__ == "__main__":
    main()
