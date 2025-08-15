"""
Tests for the main application
"""

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
import sys
import os

# Add the parent directory to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import MainWindow


class TestMainWindow:
    """Test cases for the MainWindow class"""
    
    def test_main_window_creation(self, qtbot):
        """Test that MainWindow can be created without errors"""
        window = MainWindow()
        assert window is not None
        assert window.windowTitle() == "Netball Tournament Stats"
        
    def test_main_window_geometry(self, qtbot):
        """Test that MainWindow has correct geometry"""
        window = MainWindow()
        assert window.geometry().width() == 800
        assert window.geometry().height() == 600
        
    def test_main_window_central_widget(self, qtbot):
        """Test that MainWindow has a central widget"""
        window = MainWindow()
        central_widget = window.centralWidget()
        assert central_widget is not None


def test_application_launch(qtbot):
    """Test that the application can be launched"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    # Use qtbot to wait for the window to be shown
    qtbot.wait(100)
    
    assert window.isVisible()
    assert window.isActiveWindow()
