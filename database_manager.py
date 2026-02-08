import sqlite3
import os
import json
from typing import List, Dict
from models import Character, Chapter, Country, GovUnit, MapPin

DB_NAME = "hikaye_veritabani.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL") # Performance improvement
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Karakterler Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS characters (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            title TEXT,
            gender TEXT,
            nation TEXT,
            country TEXT,
            has_magic INTEGER,
            magic_type TEXT,
            description TEXT,
            image_base64 TEXT
        )
    ''')
    
    # Bölümler Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chapters (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT,
            sequence_order INTEGER
        )
    ''')
    
    # Ülkeler Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS countries (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            geography_details TEXT,
            story TEXT,
            government_json TEXT,
            flag_normal TEXT,
            flag_war TEXT,
            flag_aid TEXT
        )
    ''')
    
    # Harita Pinleri Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS map_pins (
            id TEXT PRIMARY KEY,
            name TEXT,
            x REAL,
            y REAL,
            color TEXT,
            description TEXT
        )
    ''')
    
    # Ayarlar Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    # Migration: Check for new flag columns in countries table
    cursor.execute("PRAGMA table_info(countries)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if "flag_normal" not in columns:
        cursor.execute("ALTER TABLE countries ADD COLUMN flag_normal TEXT DEFAULT ''")
    if "flag_war" not in columns:
        cursor.execute("ALTER TABLE countries ADD COLUMN flag_war TEXT DEFAULT ''")
    if "flag_aid" not in columns:
        cursor.execute("ALTER TABLE countries ADD COLUMN flag_aid TEXT DEFAULT ''")
    
    conn.commit()
    conn.close()

# --- Karakter İşlemleri ---
def upsert_character(char: Character):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO characters (code, name, title, gender, nation, country, has_magic, magic_type, description, image_base64)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (char.code, char.name, char.title, char.gender, char.nation, char.country, 
          1 if char.has_magic else 0, char.magic_type, char.description, char.image_base64))
    conn.commit()
    conn.close()

def delete_character_db(code: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM characters WHERE code=?", (code,))
    conn.commit()
    conn.close()

def save_characters(characters: List[Character]):
    """Toplu kayıt (Hala gerekliyse, performans için optimize edildi)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("BEGIN")
    cursor.execute("DELETE FROM characters")
    for char in characters:
        cursor.execute('''
            INSERT INTO characters (code, name, title, gender, nation, country, has_magic, magic_type, description, image_base64)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (char.code, char.name, char.title, char.gender, char.nation, char.country, 
              1 if char.has_magic else 0, char.magic_type, char.description, char.image_base64))
    conn.commit()
    conn.close()

def load_characters(include_image=False) -> List[Character]:
    conn = get_connection()
    cursor = conn.cursor()
    if include_image:
        cursor.execute("SELECT * FROM characters")
    else:
        cursor.execute("SELECT code, name, title, gender, nation, country, has_magic, magic_type, description, '' FROM characters")
    rows = cursor.fetchall()
    conn.close()
    
    chars = []
    for r in rows:
        chars.append(Character(
            code=r[0], name=r[1], title=r[2], gender=r[3], 
            nation=r[4], country=r[5], has_magic=bool(r[6]), 
            magic_type=r[7], description=r[8], image_base64=r[9]
        ))
    return chars

def get_character_image(code: str) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT image_base64 FROM characters WHERE code=?", (code,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else ""

# --- Bölüm İşlemleri ---
def upsert_chapter(chap: Chapter, order: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO chapters (id, title, content, sequence_order)
        VALUES (?, ?, ?, ?)
    ''', (chap.id, chap.title, chap.content, order))
    conn.commit()
    conn.close()

def delete_chapter_db(cid: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chapters WHERE id=?", (cid,))
    conn.commit()
    conn.close()

def save_chapters(chapters: List[Chapter]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("BEGIN")
    cursor.execute("DELETE FROM chapters")
    for i, chap in enumerate(chapters):
        cursor.execute('''
            INSERT INTO chapters (id, title, content, sequence_order)
            VALUES (?, ?, ?, ?)
        ''', (chap.id, chap.title, chap.content, i))
    conn.commit()
    conn.close()

def load_chapters() -> List[Chapter]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chapters ORDER BY sequence_order")
    rows = cursor.fetchall()
    conn.close()
    return [Chapter(id=r[0], title=r[1], content=r[2]) for r in rows]

# --- Ülke İşlemleri ---
def upsert_country(c: Country):
    conn = get_connection()
    cursor = conn.cursor()
    gov_json = json.dumps([unit.to_dict() for unit in c.government_details], ensure_ascii=False)
    cursor.execute('''
        INSERT OR REPLACE INTO countries (id, name, geography_details, story, government_json, flag_normal, flag_war, flag_aid)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (c.id, c.name, c.geography_details, c.story, gov_json, c.flag_normal, c.flag_war, c.flag_aid))
    conn.commit()
    conn.close()

def delete_country_db(cid: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM countries WHERE id=?", (cid,))
    conn.commit()
    conn.close()

def save_countries(countries: List[Country]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("BEGIN")
    cursor.execute("DELETE FROM countries")
    for c in countries:
        gov_json = json.dumps([unit.to_dict() for unit in c.government_details], ensure_ascii=False)
        cursor.execute('''
            INSERT INTO countries (id, name, geography_details, story, government_json, flag_normal, flag_war, flag_aid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (c.id, c.name, c.geography_details, c.story, gov_json, c.flag_normal, c.flag_war, c.flag_aid))
    conn.commit()
    conn.close()

def load_countries() -> List[Country]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM countries")
    rows = cursor.fetchall()
    conn.close()
    
    countries = []
    for r in rows:
        gov_list = json.loads(r[4])
        gov_units = [GovUnit.from_dict(u) for u in gov_list]
        countries.append(Country(
            id=r[0], name=r[1], geography_details=r[2], 
            story=r[3], government_details=gov_units,
            flag_normal=r[5] if len(r) > 5 else "",
            flag_war=r[6] if len(r) > 6 else "",
            flag_aid=r[7] if len(r) > 7 else ""
        ))
    return countries

# Ayar İşlemleri
def get_setting(key: str, default=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default

def set_setting(key: str, value: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

# --- Harita İşlemleri ---
def save_map_pins(pins: List[MapPin]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("BEGIN")
    cursor.execute("DELETE FROM map_pins")
    for p in pins:
        cursor.execute('''
            INSERT INTO map_pins (id, name, x, y, color, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (p.id, p.name, p.x, p.y, p.color, p.description))
    conn.commit()
    conn.close()

def load_map_pins() -> List[MapPin]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM map_pins")
    rows = cursor.fetchall()
    conn.close()
    return [MapPin(id=r[0], name=r[1], x=r[2], y=r[3], color=r[4], description=r[5]) for r in rows]

def upsert_map_pin(p: MapPin):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO map_pins (id, name, x, y, color, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (p.id, p.name, p.x, p.y, p.color, p.description))
    conn.commit()
    conn.close()

def delete_map_pin_db(pid: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM map_pins WHERE id=?", (pid,))
    conn.commit()
    conn.close()

def migrate_from_json(project_path: str):
    """Mevcut JSON dosyalarını SQLite'a taşır."""
    import data_manager # Eski data manager
    
    # Karakterler
    json_chars = data_manager.load_characters(project_path)
    if json_chars: save_characters(json_chars)
    
    # Bölümler
    json_chaps = data_manager.load_story_data(project_path)
    if json_chaps: save_chapters(json_chaps)
    
    # Ülkeler
    json_countries = data_manager.load_country_data(project_path)
    if json_countries: save_countries(json_countries)
    
    # Ayarlar
    settings = data_manager.load_settings()
    for k, v in settings.items():
        set_setting(k, str(v))
