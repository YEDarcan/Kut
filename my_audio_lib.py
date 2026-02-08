import os
import sys

# Attempt safe import
try:
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
    from PySide6.QtCore import QUrl, QDir
except ImportError:
    print("QtMultimedia import failed")
    raise

class SoundManager:
    def __init__(self, main_window):
        self.main_window = main_window
        try:
            self.player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.player.setAudioOutput(self.audio_output)
            
            # Default volume
            self.audio_output.setVolume(0.5)
            
            # Loop functionality: Restart when media ends
            self.player.mediaStatusChanged.connect(self._handle_media_status)
        except Exception as e:
            print(f"Error initializing QMediaPlayer: {e}")
            self.player = None
        
        self.sound_dir = os.path.join(os.path.dirname(__file__), "sounds")
        if not os.path.exists(self.sound_dir):
            os.makedirs(self.sound_dir)

    def _handle_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.player.play()

    def get_available_sounds(self):
        sounds = []
        if os.path.exists(self.sound_dir):
            for file in os.listdir(self.sound_dir):
                if file.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')):
                    sounds.append(file)
        return sounds

    def play_sound(self, filename):
        if not self.player: return
        
        file_path = os.path.join(self.sound_dir, filename)
        if os.path.exists(file_path):
            self.player.setSource(QUrl.fromLocalFile(file_path))
            self.player.play()
            self.main_window.statusBar().showMessage(f"Caliniyor: {filename}") # Ascii safety
        else:
            self.main_window.statusBar().showMessage(f"Dosya bulunamadi: {filename}")

    def stop_sound(self):
        if self.player:
            self.player.stop()
            self.main_window.statusBar().showMessage("Ses durduruldu.")

    def set_volume(self, value):
        if self.player:
            # value 0-100
            self.audio_output.setVolume(value / 100.0)
