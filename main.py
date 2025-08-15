#!/usr/bin/env python3
"""
Main entry point for the Netball Tournament Stats Application
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Netball Tournament Stats")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Add a welcome label
        welcome_label = QLabel("Welcome to Netball Tournament Stats Application")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(welcome_label)
        
        # Add placeholder label
        placeholder_label = QLabel("Application is ready for development")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setStyleSheet("font-size: 14px; color: #666; margin: 10px;")
        layout.addWidget(placeholder_label)


def main():
    """Main application function"""
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
