import os
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QLineEdit, QHBoxLayout, QLabel, QWidgetAction
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon

from src.config import Config
from src.utils.logger import Logger

class InputWindow(QWidget):
    """Window for user input after label selection."""
    input_complete = pyqtSignal(str,str)
    def __init__(self, selected_label=None):
        """Initialize the input window."""
        super().__init__()
        self.config = Config()
        self.logger = Logger()
        self.selected_label = selected_label
        
        # Set window flags to ensure focus
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)
        self.setFocusPolicy(Qt.StrongFocus)
        
        self.initUI()
        self.startTimer()
        self.logger.info(f"Input Window initialized with label: {selected_label}")

    def initUI(self):
        """Initialize the user interface."""
        try:
            # Get UI settings from config
            bg_color = self.config.get('ui', 'background_color')
            text_color = self.config.get('ui', 'text_color')
            window_width = self.config.get('app', 'window_width')
            
            title = 'User Input'
            if self.selected_label:
                title += f" - {self.selected_label}"
            self.setWindowTitle(title)
            self.setWindowFlags(Qt.FramelessWindowHint)
            
            self.textInput = QLineEdit()
            self.textInput.setPlaceholderText('Enter your text...')
            self.textInput.returnPressed.connect(self.onSubmit)
            self.textInput.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {bg_color};
                    color: {text_color};
                    border: none;
                    padding: 10px;
                }}
                QLineEdit:focus {{
                    border: none;
                    outline: none;
                }}
            """)
            
            now = datetime.now()
            self.timeLabel = QLabel("{:02d}:{:02d}".format(now.hour, now.minute))
            self.timeLabel.setStyleSheet(f"color: {text_color}; background: transparent;")
            
            # Try to load enter icon from assets
            icon_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'assets', 'images', 'enter.png'
            )
            
            try:
                enter_icon = QIcon(icon_path)
                self.textInput.addAction(enter_icon, QLineEdit.TrailingPosition)
            except Exception as e:
                self.logger.warning(f"Could not load enter icon: {str(e)}")

            spacer = QWidget(self.textInput)
            spacer.setFixedWidth(10)
            spacer_action = QWidgetAction(self.textInput)
            spacer_action.setDefaultWidget(spacer)
            self.textInput.addAction(spacer_action, QLineEdit.TrailingPosition)

            time_action = QWidgetAction(self.textInput)
            self.timeLabel.setMinimumWidth(50)
            time_action.setDefaultWidget(self.timeLabel)
            self.textInput.addAction(time_action, QLineEdit.TrailingPosition)

            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.textInput)
            self.setLayout(layout)

            self.textInput.adjustSize()
            height = self.textInput.sizeHint().height()
            self.setFixedSize(window_width, height)
            
        except Exception as e:
            self.logger.error(f"Error initializing input UI: {str(e)}")
            raise
        
    def startTimer(self):
        """Start the timer for updating the time display."""
        try:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.updateTime)
            self.timer.start(1000)
        except Exception as e:
            self.logger.error(f"Error starting timer: {str(e)}")

    def updateTime(self):
        """Update the displayed time."""
        try:
            self.timeLabel.setText(datetime.now().strftime("%H:%M"))
        except Exception as e:
            self.logger.error(f"Error updating time: {str(e)}")
        
    def onSubmit(self):
        """Handle text submission."""
        try:
            current_time = datetime.now().strftime("%H:%M")
            text = self.textInput.text()
            
            if text:
                self.logger.log_input(text, self.selected_label)
                # self.input_complete.emit(text,self.selected_label)
                self.close()
            else:
                self.logger.warning("Empty text submitted")
                
            self.textInput.clear()
            
        except Exception as e:
            self.logger.error(f"Error handling submission: {str(e)}")
        
    def keyPressEvent(self, event):
        """Handle key press events."""
        try:
            if event.key() == Qt.Key_Escape:
                self.logger.info("Input window closed")
                self.close()
        except Exception as e:
            self.logger.error(f"Error handling key press in input window: {str(e)}")

    def showEvent(self, event):
        """Handle window show event."""
        super().showEvent(event)
        # Set focus to the text input when shown
        QTimer.singleShot(10, lambda: self.textInput.setFocus())