print("Starting full import test...")
try:
    print("Importing QMediaPlayer...")
    from PySide6.QtMultimedia import QMediaPlayer
    print("QMediaPlayer OK")

    print("Importing QAudioOutput...")
    from PySide6.QtMultimedia import QAudioOutput
    print("QAudioOutput OK")

    print("Importing QUrl, QDir...")
    from PySide6.QtCore import QUrl, QDir
    print("QtCore OK")

    print("Importing QMenu, QAction...")
    from PySide6.QtWidgets import QMenu, QAction
    print("QtWidgets OK")
    
    print("All imports SUCCESS")
except ImportError as e:
    print(f"ImportError FAIL: {e}")
except Exception as e:
    print(f"Exception FAIL: {e}")
