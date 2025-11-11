"""
Tests for MainController
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from wallpaper_manager.controller import MainController
from wallpaper_manager.config import Config


@pytest.fixture
def temp_config(tmp_path):
    """Create a temporary configuration for testing"""
    config = Config(storage_path=tmp_path / "wallpaper-manager")
    config.initialize_storage()
    return config


@pytest.fixture
def controller(temp_config):
    """Create a MainController instance for testing"""
    return MainController(temp_config)


def test_controller_initialization(controller, temp_config):
    """Test that MainController initializes correctly"""
    assert controller.config == temp_config
    assert controller.wallpaper_manager is not None
    assert controller._import_popup is None
    assert controller._selector_interface is None
    assert controller._active_window is None


def test_get_active_window(controller):
    """Test getting active window state"""
    assert controller.get_active_window() is None
    
    controller._active_window = 'import'
    assert controller.get_active_window() == 'import'
    
    controller._active_window = 'selector'
    assert controller.get_active_window() == 'selector'


def test_is_import_popup_open(controller):
    """Test checking if import popup is open"""
    assert controller.is_import_popup_open() is False
    
    # Mock an open import popup
    mock_popup = Mock()
    mock_popup.is_visible.return_value = True
    controller._import_popup = mock_popup
    
    assert controller.is_import_popup_open() is True
    
    # Test with closed popup
    mock_popup.is_visible.return_value = False
    assert controller.is_import_popup_open() is False


def test_is_selector_interface_open(controller):
    """Test checking if selector interface is open"""
    assert controller.is_selector_interface_open() is False
    
    # Mock an open selector interface
    mock_selector = Mock()
    mock_selector.is_visible.return_value = True
    controller._selector_interface = mock_selector
    
    assert controller.is_selector_interface_open() is True
    
    # Test with closed selector
    mock_selector.is_visible.return_value = False
    assert controller.is_selector_interface_open() is False


def test_shutdown(controller):
    """Test controller shutdown"""
    # Mock windows
    mock_popup = Mock()
    mock_selector = Mock()
    
    controller._import_popup = mock_popup
    controller._selector_interface = mock_selector
    controller._active_window = 'selector'
    
    # Shutdown
    controller.shutdown()
    
    # Verify windows were closed
    mock_popup.close.assert_called_once()
    mock_selector.close.assert_called_once()
    
    # Verify state was cleared
    assert controller._import_popup is None
    assert controller._selector_interface is None
    assert controller._active_window is None


def test_on_import_confirmed(controller):
    """Test import confirmation callback"""
    with patch.object(controller, 'show_selector_interface') as mock_show:
        controller._on_import_confirmed()
        mock_show.assert_called_once()


def test_on_import_popup_closed(controller):
    """Test import popup close handler"""
    mock_window = Mock()
    controller._import_popup = mock_window
    controller._active_window = 'import'
    
    result = controller._on_import_popup_closed(mock_window)
    
    assert result is False  # Allow window to close
    assert controller._import_popup is None
    assert controller._active_window is None


def test_on_selector_interface_closed(controller):
    """Test selector interface close handler"""
    mock_window = Mock()
    controller._selector_interface = mock_window
    controller._active_window = 'selector'
    
    result = controller._on_selector_interface_closed(mock_window)
    
    assert result is False  # Allow window to close
    assert controller._selector_interface is None
    assert controller._active_window is None
