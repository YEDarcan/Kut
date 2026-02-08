print("Starting TRUE full import test...")
try:
    print("Importing QtMultimedia...")
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
    print("QtMultimedia OK")

    print("Importing QtCore...")
    from PySide6.QtCore import QUrl, QDir
    print("QtCore OK")

    print("Importing QtWidgets...")
    from PySide6.QtWidgets import QMenu, QAction
    print("QtWidgets OK")
    
    print("ALL IMPORTS SUCCESS")
except ImportError as e:
    print(f"FAIL: {e}")
except Exception as e:
    print(f"EXCEPTION: {e}")
