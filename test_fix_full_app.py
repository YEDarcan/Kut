import sys
try:
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    print("QApplication started")
    
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
    p = QMediaPlayer()
    print("QMediaPlayer created")
    a = QAudioOutput()
    print("QAudioOutput created")
    p.setAudioOutput(a)
    print("Linked")
    
    print("SUCCESS")
except Exception as e:
    print(f"FAIL: {e}")
