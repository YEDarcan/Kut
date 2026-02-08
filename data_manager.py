import json
import os
from typing import List, Dict
from models import Character, Chapter, Country

SETTINGS_FILE = "settings.json"
CHARACTERS_FILE = "characters.json"
STORY_FILE = "story.json"
COUNTRY_FILE = "countries.json"

def load_settings() -> Dict:
    """Ayarları settings.json dosyasından yükler."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {
        "theme": "dark", 
        "project_path": os.getcwd(),
        "favorite_fonts": ["Arial", "Courier New", "Georgia", "Impact", "Segoe UI", "Tahoma", "Times New Roman", "Verdana"]
    }

def save_settings(settings: Dict):
    """Ayarları settings.json dosyasına kaydeder."""
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

def load_characters(project_path: str) -> List[Character]:
    """Karakter verilerini characters.json dosyasından yükler."""
    file_path = os.path.join(project_path, CHARACTERS_FILE)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Character.from_dict(c) for c in data]
        except json.JSONDecodeError:
            pass
    return []

def save_characters(project_path: str, characters: List[Character]):
    """Karakter verilerini characters.json dosyasına kaydeder."""
    file_path = os.path.join(project_path, CHARACTERS_FILE)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump([c.to_dict() for c in characters], f, indent=4, ensure_ascii=False)

def load_story_data(project_path: str) -> List[Chapter]:
    """Hikaye verilerini story.json dosyasından yükler."""
    file_path = os.path.join(project_path, STORY_FILE)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Chapter.from_dict(c) for c in data]
        except json.JSONDecodeError:
            pass
    return []

def save_story_data(project_path: str, chapters: List[Chapter]):
    """Hikaye verilerini story.json dosyasına kaydeder."""
    file_path = os.path.join(project_path, STORY_FILE)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump([c.to_dict() for c in chapters], f, indent=4, ensure_ascii=False)

def load_country_data(project_path: str) -> List[Country]:
    """Ülke verilerini countries.json dosyasından yükler."""
    file_path = os.path.join(project_path, COUNTRY_FILE)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Country.from_dict(c) for c in data]
        except json.JSONDecodeError:
            pass
    return []

def save_country_data(project_path: str, countries: List[Country]):
    """Ülke verilerini countries.json dosyasına kaydeder."""
    file_path = os.path.join(project_path, COUNTRY_FILE)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump([c.to_dict() for c in countries], f, indent=4, ensure_ascii=False)
