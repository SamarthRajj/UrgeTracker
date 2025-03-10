from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt

from src.config import Config
from src.ui.input_window import InputWindow
from src.utils.logger import Logger

class LabelSelectionWindow(QWidget):
    """Window for selecting urge labels."""
    
    def __init__(self):
        """Initialize the label selection window."""
        super().__init__()
        self.config = Config()
        self.logger = Logger()
        self.selected_label = None
        
        # Load labels from config
        self.options = {}
        labels_config = self.config.get('labels')
        for key, label in labels_config.items():
            self.options[getattr(Qt, f"Key_{key}")] = label
            
        self.initUI()
        self.logger.info("Label Selection Window initialized")

    def initUI(self):
        """Initialize the user interface."""
        try:
            # Get UI settings from config
            bg_color = self.config.get('ui', 'background_color')
            text_color = self.config.get('ui', 'text_color')
            font_size_large = self.config.get('ui', 'font_size_large')
            font_size_normal = self.config.get('ui', 'font_size_normal')
            window_width = self.config.get('app', 'window_width')
            
            self.setWindowTitle('Select a Label')
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setStyleSheet(f"background-color: {bg_color};")
            
            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)

            instruction = QLabel("Select a Urge:")
            instruction.setStyleSheet(f"font-size: {font_size_large}; color: {text_color};")
            layout.addWidget(instruction)
            
            # Create a horizontal layout for options
            hLayout = QHBoxLayout()
            hLayout.setContentsMargins(0, 10, 0, 0)
            hLayout.setSpacing(20)
            
            for key, label in self.options.items():
                option_label = QLabel(f"{key - Qt.Key_0}: {label}")
                option_label.setStyleSheet(f"font-size: {font_size_normal}; color: {text_color};")
                hLayout.addWidget(option_label)
                
            layout.addLayout(hLayout)
            self.setLayout(layout)
            self.adjustSize()
            self.setFixedWidth(window_width)
            
        except Exception as e:
            self.logger.error(f"Error initializing UI: {str(e)}")
            raise

    def keyPressEvent(self, event):
        """Handle key press events."""
        try:
            if event.key() in self.options:
                self.selected_label = self.options[event.key()]
                self.logger.info(f"Label selected: {self.selected_label}")
                self.input_window = InputWindow(selected_label=self.selected_label)
                self.input_window.show()
                self.close()
            elif event.key() == Qt.Key_Escape:
                self.logger.info("Label selection canceled")
                self.close()
        except Exception as e:
            self.logger.error(f"Error handling key press: {str(e)}")