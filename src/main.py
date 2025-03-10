import sys
import os
import keyboard
import threading

from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, Qt, QTimer
from src.ui.label_window import LabelSelectionWindow
from src.utils.logger import Logger

class HotkeyListener(QObject):
    """A separate class to handle global hotkeys with signal support."""
    hotkey_triggered = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
    def start_listening(self):
        """Start listening for the hotkey in a separate thread."""
        # Run this in a separate thread to avoid blocking the Qt event loop
        self.listener_thread = threading.Thread(target=self._listen_for_hotkey, daemon=True)
        self.listener_thread.start()
        
    def _listen_for_hotkey(self):
        """Listen for the Ctrl+Space hotkey."""
        keyboard.add_hotkey('ctrl+space', self.hotkey_triggered.emit)
        # This is a blocking call that keeps the thread alive
        keyboard.wait()

class UrgeApp(QObject):  # Make UrgeApp inherit from QObject
    """Main application class that manages the system tray and hotkeys."""
    
    def __init__(self):
        super().__init__()  # Initialize the QObject base class first
        self.app = QApplication(sys.argv)
        self.logger = Logger()
        self.selection_window = None
        
        # Create system tray icon first
        self.setup_tray()
        
        # Create hotkey listener AFTER fully initializing the parent object
        self.hotkey_listener = HotkeyListener()
        # Connect the signal properly - this should work now
        self.hotkey_listener.hotkey_triggered.connect(self.show_selection_window)
        
        # Start listening for hotkeys
        self.register_hotkey()
        
        self.logger.info("Application starting in background")
        
    def setup_tray(self):
        """Set up the system tray icon and menu."""
        try:
            self.tray_icon = QSystemTrayIcon(self.app)
            
            # Try to load icon, use a fallback if not available
            icon_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'assets', 'images', 'tray_icon.png'
            )
            
            try:
                if os.path.exists(icon_path):
                    self.tray_icon.setIcon(QIcon(icon_path))
                else:
                    # Use a simple icon from Qt as fallback
                    self.tray_icon.setIcon(self.app.style().standardIcon(
                        self.app.style().SP_ComputerIcon))
                    self.logger.warning("Using fallback icon. Create 'assets/images/tray_icon.png' for custom icon.")
            except Exception as e:
                self.logger.warning(f"Could not load tray icon: {str(e)}")
                self.tray_icon.setIcon(self.app.style().standardIcon(
                    self.app.style().SP_ComputerIcon))
            
            # Create the menu
            tray_menu = QMenu()
            
            # Add actions to the menu
            show_action = QAction("Show Urge Input", self.tray_icon)
            show_action.triggered.connect(self.show_selection_window)
            tray_menu.addAction(show_action)
            
            exit_action = QAction("Exit", self.tray_icon)
            exit_action.triggered.connect(self.exit_app)
            tray_menu.addAction(exit_action)
            
            # Add the menu to the tray icon
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.setToolTip("Urge")
            self.tray_icon.show()
            
        except Exception as e:
            self.logger.error(f"Error setting up tray icon: {str(e)}")
            
    def register_hotkey(self):
        """Register the global hotkey."""
        try:
            # Start the hotkey listener in a separate thread
            self.hotkey_listener.start_listening()
            self.logger.info("Global hotkey registered (Ctrl+Space)")
        except Exception as e:
            self.logger.error(f"Error registering hotkey: {str(e)}")
    
    @pyqtSlot()        
    def show_selection_window(self):
        """Show the label selection window."""
        try:
            # Important: Log first to verify the hotkey is being detected
            self.logger.info("Hotkey triggered - attempting to show window")
            
            # If window already exists, close it first
            if self.selection_window is not None:
                self.selection_window.close()
                
            # Create and show the window
            self.selection_window = LabelSelectionWindow()
            
            # Set window flags to ensure it appears on top and gets focus
            self.selection_window.setWindowFlags(
                self.selection_window.windowFlags() | 
                Qt.WindowStaysOnTopHint | 
                Qt.WindowActive
            )
            
            # Show the window first so it has a size
            self.selection_window.show()
            
            # Center the window after it's shown and has proper geometry
            QTimer.singleShot(10, self.selection_window.center_on_screen)
            
            # On Windows, enhanced focus handling needs to be done after the window is shown
            if sys.platform == 'win32':
                try:
                    import ctypes
                    from ctypes import wintypes
                    
                    # Get window handle
                    hwnd = int(self.selection_window.winId())
                    
                    # More aggressive focus methods for Windows
                    # 1. Set as foreground window
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
                    
                    # 2. Force window to top and activate it
                    SW_SHOW = 5
                    ctypes.windll.user32.ShowWindow(hwnd, SW_SHOW)
                    
                    # 3. Set active window
                    ctypes.windll.user32.SetActiveWindow(hwnd)
                    
                    # 4. Flash window to get attention (more noticeable)
                    FLASHW_ALL = 0x00000003
                    FLASHW_TIMERNOFG = 0x0000000C
                    
                    class FLASHWINFO(ctypes.Structure):
                        _fields_ = [
                            ("cbSize", wintypes.UINT),
                            ("hwnd", wintypes.HWND),
                            ("dwFlags", wintypes.DWORD),
                            ("uCount", wintypes.UINT),
                            ("dwTimeout", wintypes.DWORD)
                        ]
                    
                    flash_info = FLASHWINFO(
                        ctypes.sizeof(FLASHWINFO),
                        hwnd,
                        FLASHW_ALL | FLASHW_TIMERNOFG,
                        3,  # flash count
                        0   # default flash rate
                    )
                    
                    ctypes.windll.user32.FlashWindowEx(ctypes.byref(flash_info))
                    
                    # 5. Simulate Alt key press to force window activation
                    keybd_event = ctypes.windll.user32.keybd_event
                    KEYEVENTF_KEYUP = 0x0002
                    VK_MENU = 0x12  # Alt key
                    
                    # Press and release Alt key to help focus
                    keybd_event(VK_MENU, 0, 0, 0)
                    keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)
                    
                    self.logger.info("Enhanced Windows focus methods applied")
                except Exception as e:
                    self.logger.warning(f"Could not use Windows-specific focus methods: {str(e)}")
            
            # Additional PyQt methods to ensure focus
            self.selection_window.raise_()
            self.selection_window.activateWindow()
            
            # Use a timer to make a second attempt at focusing the window
            QTimer.singleShot(100, lambda: self._force_focus_again())
            
            self.logger.info("Label selection window displayed via hotkey")
        except Exception as e:
            self.logger.error(f"Error showing selection window: {str(e)}")

    def _force_focus_again(self):
        """Make a second attempt to force focus after a short delay."""
        if self.selection_window and self.selection_window.isVisible():
            self.selection_window.raise_()
            self.selection_window.activateWindow()
            
            if sys.platform == 'win32':
                try:
                    import ctypes
                    hwnd = int(self.selection_window.winId())
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
                except Exception:
                    pass
            
    def exit_app(self):
        """Exit the application cleanly."""
        try:
            # Unregister hotkey before exit
            keyboard.unhook_all()
            self.logger.info("Application exiting via tray menu")
            self.app.quit()
        except Exception as e:
            self.logger.error(f"Error during application exit: {str(e)}")
    
    def run(self):
        """Run the application event loop."""
        return self.app.exec_()


def main():
    """Main entry point for the application."""
    try:
        # Create assets directories if they don't exist
        os.makedirs('./assets/images', exist_ok=True)
        
        # Initialize and run the application
        urge_app = UrgeApp()
        exit_code = urge_app.run()
        
        # Exit code
        print(f"Application exiting with code {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"Critical error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()