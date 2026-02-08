import sys
from PySide6.QtWidgets import QApplication

def test_startup():
    print("Initializing QApplication...")
    app = QApplication(sys.argv)
    
    print("Importing MainWindowUI...")
    try:
        from ui_main import MainWindowUI
        print("MainWindowUI imported successfully.")
    except Exception as e:
        print(f"FAILED to import MainWindowUI: {e}")
        return

    print("Instantiating MainWindowUI...")
    try:
        window = MainWindowUI()
        print("MainWindowUI instantiated successfully.")
        
        if hasattr(window, 'list_karakterler'):
             print("SUCCESS: list_karakterler exists.")
        else:
             print("FAILURE: list_karakterler DOES NOT EXIST.")
             sys.exit(1)
             
    except Exception as e:
        import traceback
        with open("startup_error.log", "w") as f:
            traceback.print_exc(file=f)
        print(f"FAILED to instantiate MainWindowUI: {e}")
        sys.exit(1)

    print("Startup test PASSED.")

if __name__ == "__main__":
    test_startup()
