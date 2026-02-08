from PySide6.QtGui import QColor, QPalette

def get_stylesheet(theme: str) -> str:
    # Colors
    text_main = "#e0e0e0"       
    text_dim = "#a0a0a0"        
    border_color = "#333333"    
    
    if theme == "green":
        accent_color = "#2e7d32" 
        accent_hover = "#1b5e20"
        bg_main = "#0b1a10"     # Deep Forest
        bg_panel = "#16261b"    # Panel Forest
        border_color = "#2d4a35"
        text_on_accent = "#ffffff"
    elif theme == "orange":
        accent_color = "#ef6c00" 
        accent_hover = "#e65100"
        bg_main = "#1a1008"     # Deep Earth
        bg_panel = "#261a10"    # Panel Earth
        border_color = "#4a3525"
        text_on_accent = "#ffffff"
    elif theme == "dark":
        accent_color = "#3f51b5" 
        accent_hover = "#303f9f"
        bg_main = "#121212"
        bg_panel = "#1e1e1e"
        border_color = "#333333"
        text_on_accent = "#ffffff"
    elif theme == "light":
        return _get_light_stylesheet()
    else:
        # Default fallback
        accent_color = "#3f51b5"
        accent_hover = "#303f9f"
        bg_main = "#121212"
        bg_panel = "#1e1e1e"
        text_on_accent = "#ffffff"

    return f"""
        /* --- General Defaults --- */
        QMainWindow, QWidget {{
            background-color: {bg_main};
            color: {text_main};
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 11px;
        }}

        /* --- Tabs --- */
        QTabWidget::pane {{
            border: 1px solid {border_color};
            background: {bg_panel};
        }}
        QTabBar::tab {{
            background: {bg_main};
            border: 1px solid {border_color};
            padding: 4px 12px;
            color: {text_dim};
            margin-right: -1px; /* Connect tabs */
        }}
        QTabBar::tab:selected {{
            background: {bg_panel};
            color: {accent_color};
            border-bottom-color: {bg_panel}; /* Merge with pane */
            border-top: 2px solid {accent_color};
        }}
        QTabBar::tab:hover:!selected {{
            background: #2d2e31;
            color: {text_main};
        }}

        /* --- Panels & Frames --- */
        QFrame, QGroupBox {{
            background: {bg_panel};
            border: 1px solid {border_color};
            border-radius: 0px; 
        }}

        /* --- Data Views --- */
        QListWidget, QTreeWidget, QTableWidget {{
            background-color: {bg_main};
            border: 1px solid {border_color};
            border-radius: 0px;
            outline: none;
            padding: 2px;
        }}
        QListWidget::item, QTreeWidget::item {{
            padding: 2px;
        }}
        QListWidget::item:selected, QTreeWidget::item:selected {{
            background-color: {accent_color};
            color: {text_on_accent};
        }}
        QListWidget::item:hover, QTreeWidget::item:hover {{
            background-color: #35363a;
        }}

        /* --- Inputs --- */
        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {{
            background-color: {bg_main};
            color: {text_main};
            border: 1px solid {border_color};
            border-radius: 0px; 
            padding: 2px 4px;
            selection-background-color: {accent_color};
            selection-color: {text_on_accent};
            min-height: 20px;
        }}
        QLineEdit:focus, QTextEdit:focus {{
            border: 1px solid {accent_color};
            background-color: #28292c;
        }}

        /* --- Buttons --- */
        QPushButton {{
            background-color: {bg_panel};
            color: {text_main};
            border: 1px solid {border_color};
            padding: 4px 12px;
            border-radius: 0px; 
            min-height: 22px;
        }}
        QPushButton:hover {{
            background-color: #3c4043;
            border-color: #5f6368;
        }}
        QPushButton:pressed {{
            background-color: #4a4d52;
            border-color: {accent_color};
        }}

        /* --- Primary Action Buttons --- */
        QPushButton[objectName="primary"] {{
            background-color: {accent_color};
            color: {text_on_accent};
            border: 1px solid {accent_color};
        }}
        QPushButton[objectName="primary"]:hover {{
            background-color: {accent_hover};
            border-color: {accent_hover};
        }}

        /* --- Danger Buttons --- */
        QPushButton[objectName="danger"] {{
            background-color: transparent;
            color: #f28b82;
            border: 1px solid #f28b82;
        }}
        QPushButton[objectName="danger"]:hover {{
            background-color: #f28b82;
            color: #202124;
        }}

        /* --- Scrollbars --- */
        QScrollBar:vertical {{
            border: none;
            background: {bg_main};
            width: 8px;
        }}
        QScrollBar::handle:vertical {{
            background: #5f6368;
            min-height: 15px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """

def _get_light_stylesheet() -> str:
    return """
        QMainWindow, QWidget {
            background-color: #ffffff;
            color: #202124;
            font-family: 'Segoe UI', sans-serif;
            font-size: 11px;
        }
        QTabWidget::pane {
            border: 1px solid #dadce0;
            background: #f8f9fa;
        }
        QTabBar::tab {
            background: #ffffff;
            border: 1px solid #dadce0;
            padding: 4px 12px;
            min-width: 60px;
        }
        QTabBar::tab:selected {
            background: #f8f9fa;
            border-bottom-color: #f8f9fa;
            border-top: 2px solid #1a73e8;
            color: #1a73e8;
        }
        QPushButton {
            background-color: #ffffff;
            border: 1px solid #dadce0;
            padding: 4px 12px;
            min-height: 22px;
            border-radius: 0px;
            color: #3c4043;
        }
        QPushButton:hover {
            background-color: #f1f3f4;
            color: #202124;
        }
        QPushButton[objectName="primary"] {
            background-color: #1a73e8;
            color: white;
            border: 1px solid #1a73e8;
        }
        QPushButton[objectName="primary"]:hover {
            background-color: #1967d2;
        }
        QLineEdit, QTextEdit {
            background-color: #ffffff;
            border: 1px solid #dadce0;
            border-radius: 0px;
            padding: 2px 4px;
        }
    """

def apply_palette(app, theme: str):
    # Palette is largely overridden by stylesheet, but accurate defaults help
    palette = QPalette()
    if theme in ["dark", "green", "orange"]:
        palette.setColor(QPalette.Window, QColor(32, 33, 36))
        palette.setColor(QPalette.WindowText, QColor(232, 234, 237))
        palette.setColor(QPalette.Base, QColor(32, 33, 36))
        palette.setColor(QPalette.Text, QColor(232, 234, 237))
        palette.setColor(QPalette.Button, QColor(41, 42, 45))
        palette.setColor(QPalette.ButtonText, QColor(232, 234, 237))
    else:
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.WindowText, QColor(32, 33, 36))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(32, 33, 36))
    
    app.setPalette(palette)
