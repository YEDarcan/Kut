try:
    print("Importing models...")
    import models
    print("Models imported.")
except Exception as e:
    print(f"Error importing models: {e}")

try:
    print("Importing database_manager...")
    import database_manager
    print("Database Manager imported.")
except Exception as e:
    print(f"Error importing database_manager: {e}")

try:
    print("Importing styles...")
    import styles
    print("Styles imported.")
except Exception as e:
    print(f"Error importing styles: {e}")

try:
    print("Importing ui_main...")
    from ui_main import MainWindowUI
    print("UI Main imported.")
except Exception as e:
    print(f"Error importing ui_main: {e}")

try:
    print("Importing controllers...")
    from controllers import StoryController
    print("Controllers imported.")
except Exception as e:
    print(f"Error importing controllers: {e}")
