import sys
import os

from PyQt5.QtWidgets import QApplication
from src.ui.label_window import LabelSelectionWindow
from src.utils.logger import Logger

def main():
    """Main entry point for the application."""
    try:
        # Create assets directories if they don't exist
        os.makedirs('./assets/images', exist_ok=True)
        
        # Initialize logger
        logger = Logger()
        logger.info("Application starting")
        
        # Start the application
        app = QApplication(sys.argv)
        selection_window = LabelSelectionWindow()
        selection_window.show()
        
        # Exit code
        exit_code = app.exec_()
        logger.info(f"Application exiting with code {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        if 'logger' in locals():
            logger.error(f"Critical error: {str(e)}")
        else:
            print(f"Critical error before logger initialization: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()