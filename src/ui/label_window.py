from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt

from src.config import Config
from src.ui.input_window import InputWindow
from src.utils.logger import Logger
from PyQt5.QtWidgets import QSizePolicy

class LabelSelectionWindow(QWidget):
    """Window for selecting urge labels."""
    
    def __init__(self):
        """Initialize the label selection window."""
        super().__init__()
        self.config = Config()
        self.logger = Logger()
        self.selected_label = None
        
        # Load labels from config and create mapping of shortcuts to text
        self.options = {}  # mapping of key code to default label
        labels_config = self.config.get('labels')
        for key, label in labels_config.items():
            key_val = getattr(Qt, f"Key_{key}")
            self.options[key_val] = label
            
        # Dictionary to hold QLineEdit widgets for each option
        self.option_edits = {}
        
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
            instruction.setStyleSheet(f"font-size: {font_size_large}; color: {text_color}; margin-bottom: 5px;")
            layout.addWidget(instruction)
            
            # Create a horizontal layout for options
            hLayout = QHBoxLayout()
            hLayout.setContentsMargins(0, 10, 0, 0)
            hLayout.setSpacing(20)
            
            # For each option, create a label for the shortcut and an editable QLineEdit
            for key, label_text in self.options.items():
                # Create a vertical layout for the key and its editable label
                optionLayout = QVBoxLayout()
                optionLayout.setSpacing(5)
                
                # Show the key number (assumes keys are numeric)
                key_label = QLabel(f"{key - Qt.Key_0}:")
                key_label.setStyleSheet(f"font-size: {font_size_normal}; color: {text_color}; margin: 0;")
                optionLayout.addWidget(key_label)
                
                # Create an editable line for the label text, with no border to look cleaner.
                edit = QLineEdit()
                edit.setText(label_text)
                edit.setReadOnly(True)
                edit.setStyleSheet(f"""
                    font-size: {font_size_normal};
                    color: {text_color};
                    border: none;
                    background: transparent;
                """)
                optionLayout.addWidget(edit)
                
                # Store the QLineEdit widget for later access on key press
                self.option_edits[key] = edit
                
                hLayout.addLayout(optionLayout)
                
            layout.addLayout(hLayout)

            # Add the toggle button to allow switching between editing and selection mode.
            top_layout = QHBoxLayout()
            top_layout.addStretch()  # Push the button to the right side
            self.toggle_button = QPushButton("Edit")
            self.toggle_button.setStyleSheet(f"""
                font-size: {font_size_normal};
                color: {text_color};
                padding: 5px 10px;
                border: 1px solid {text_color};
                background: transparent;
            """)
            # Set size policy so that the button is just wide as its text
            self.toggle_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
            self.toggle_button.clicked.connect(self.toggle_edit)
            top_layout.addWidget(self.toggle_button)
            layout.insertLayout(0, top_layout)
            
            self.setLayout(layout)
            self.adjustSize()
            self.setFixedWidth(window_width)
            
        except Exception as e:
            self.logger.error(f"Error initializing UI: {str(e)}")
            raise

    def toggle_edit(self):
        """Toggle between editing and selection mode."""
        try:
            if all(edit.isReadOnly() for edit in self.option_edits.values()):
                # Currently not editing, so enable editing.
                for edit in self.option_edits.values():
                    edit.setReadOnly(False)
                self.toggle_button.setText("Save")
            else:
                # Save the new names and disable editing.
                for key, edit in self.option_edits.items():
                    self.options[key] = edit.text()
                    edit.setReadOnly(True)
                self.toggle_button.setText("Edit")
                # Remove focus from the edits so key presses are registered by the window.
                self.setFocus()
        except Exception as e:
            self.logger.error(f"Error toggling edit mode: {str(e)}")

    def keyPressEvent(self, event):
        """Handle key press events."""
        try:
            if event.key() in self.option_edits and all(edit.isReadOnly() for edit in self.option_edits.values()):
                # Retrieve the text from the corresponding editable field
                self.selected_label = self.option_edits[event.key()].text()
                self.logger.info(f"Label selected: {self.selected_label}")
                self.input_window = InputWindow(selected_label=self.selected_label)
                self.input_window.show()
                self.close()
            elif event.key() == Qt.Key_Escape:
                self.logger.info("Label selection canceled")
                self.close()
        except Exception as e:
            self.logger.error(f"Error handling key press: {str(e)}")