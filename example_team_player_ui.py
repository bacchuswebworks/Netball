#!/usr/bin/env python3
"""
Example usage of Team and Player Management UI
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from models.database_manager import DatabaseManager
from models.schema import DatabaseSchema
from ui.team_player_management import TeamPlayerManagementWidget


class MainWindow(QMainWindow):
    """Main window for the team and player management example"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Netball Team & Player Management")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create database and schema
        self.db_manager = DatabaseManager("team_player_example.db")
        self.schema = DatabaseSchema(self.db_manager)
        
        # Create tables and insert sample data
        self.schema.create_tables()
        self.schema.insert_sample_data()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Create and add the team/player management widget
        self.management_widget = TeamPlayerManagementWidget(self.db_manager)
        layout.addWidget(self.management_widget)
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.db_manager.close()
        event.accept()


def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
