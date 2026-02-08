import zipfile
import os

def zip_project(output_filename):
    # Files/Dirs to exclude
    EXCLUDES = {
        '.venv', 'venv', 'env', '__pycache__', '.git', '.vscode', 
        output_filename, 'Antigravity_Web_App.zip', 'create_zip.py', 'test_startup_fix.py',
        'startup_error.log', 'crash.log', 'error.log', 'debug_log.txt', 'sounds'
    }
    
    # Extensions to exclude
    EXCLUDE_EXT = {'.pyc', '.pyo', '.pyd', '.ds_store', '.zip'}

    print(f"Creating {output_filename}...")
    
    try:
        with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk the project directory (where script is located)
            root_dir = os.path.dirname(os.path.abspath(__file__))
            
            for root, dirs, files in os.walk(root_dir):
                # Modify dirs in-place to skip excluded directories
                dirs[:] = [d for d in dirs if d not in EXCLUDES]
                
                for file in files:
                    if file in EXCLUDES:
                        continue
                    if os.path.splitext(file)[1].lower() in EXCLUDE_EXT:
                        continue
                        
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, root_dir)
                    
                    print(f"Adding {arcname}...")
                    zipf.write(file_path, arcname)
                    
        print(f"Successfully created {output_filename}")
        
    except Exception as e:
        print(f"Error creating zip: {e}")

if __name__ == "__main__":
    zip_project('Antigravity_Upload.zip')
