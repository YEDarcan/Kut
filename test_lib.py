try:
    print("Importing my_audio_lib...")
    import my_audio_lib
    print("Module imported.")
    print("SoundManager class:", my_audio_lib.SoundManager)
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
