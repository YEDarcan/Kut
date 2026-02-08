# Force load QtMultimedia to avoid import errors later
try:
    from PySide6.QtMultimedia import QMediaPlayer
except ImportError:
    pass

from PySide6.QtWidgets import QApplication
from ui_main import MainWindowUI
from controllers import StoryController
import sys
import styles
import database_manager

def main():
    app = QApplication(sys.argv)
    
    database_manager.init_db()
    
    # Load settings from DB
    theme = database_manager.get_setting("theme", "dark")
    
    # Create UI
    window = MainWindowUI()
    
    # Setup styling
    styles.apply_palette(app, theme)
    app.setStyleSheet(styles.get_stylesheet(theme))
    
    # Setup Controller
    controller = StoryController(window)
    
    # Handle theme change signals
    def update_theme(new_theme):
        database_manager.set_setting("theme", new_theme)
        styles.apply_palette(app, new_theme)
        app.setStyleSheet(styles.get_stylesheet(new_theme))
        window.statusBar().showMessage(f"Tema {new_theme} olarak güncellendi.", 3000)

    window.action_theme_light.triggered.connect(lambda: update_theme("light"))
    window.action_theme_dark.triggered.connect(lambda: update_theme("dark"))
    window.action_theme_green.triggered.connect(lambda: update_theme("green"))
    window.action_theme_orange.triggered.connect(lambda: update_theme("orange"))

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
