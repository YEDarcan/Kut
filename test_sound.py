try:
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
    print("QtMultimedia imported successfully.")
    
    player = QMediaPlayer()
    audio = QAudioOutput()
    player.setAudioOutput(audio)
    print("MediaPlayer initialized successfully.")
    
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
