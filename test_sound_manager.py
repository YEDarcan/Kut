try:
    from sound_manager import SoundManager
    print("SoundManager imported successfully.")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
