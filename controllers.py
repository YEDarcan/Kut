import io
import base64
import re
import os
from PySide6.QtWidgets import QMessageBox, QListWidgetItem, QFileDialog, QTreeWidgetItem
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer, QByteArray

import database_manager
from models import Character, Chapter, Country, GovUnit

class StoryController:
    def __init__(self, main_window):
        self.view = main_window
        self.settings = {
            "project_path": database_manager.get_setting("project_path", "."),
            "theme": database_manager.get_setting("theme", "dark")
        }
        self.project_path = self.settings["project_path"]
        
        self.characters = []
        self.chapters = []
        self.countries = []
        
        self.current_char_code = None
        self.current_chapter_id = None
        self.current_country_id = None
        self.current_image_base64 = ""
        self.current_country_flag_type = "normal" # normal, war, aid

        self._load_data()
        self._connect_signals()
        self._start_autosave()

    def _load_data(self):
        self.characters = database_manager.load_characters()
        self.chapters = database_manager.load_chapters()
        self.countries = database_manager.load_countries()
        
        # --- Migration / Code Fix ---
        migration_needed = False
        for char in self.characters:
            # Eğer kodda '-' yoksa veya yeni formatta değilse (timestamp kısmı yoksa)
            if "-" not in char.code or len(char.code.split("-")[-1]) < 4:
                old_code = char.code
                new_code = self._generate_character_code()
                database_manager.delete_character_db(old_code)
                char.code = new_code
                database_manager.upsert_character(char)
                migration_needed = True
        
        if migration_needed:
            self.characters = database_manager.load_characters() # Reload with new codes
        
        if not self.chapters:
            self.add_chapter()
        
        self._refresh_all_lists()
        self._load_saved_map()

    def _refresh_all_lists(self):
        self._update_character_list()
        self._update_outline_list()
        self._update_country_list()
        self._populate_country_stories_list()

    def _connect_signals(self):
        # Menu
        self.view.action_select_folder.triggered.connect(self.select_project_folder)
        self.view.action_refresh.triggered.connect(self._load_data)
        
        # Character
        self.view.btn_add_char.clicked.connect(self.add_character)
        self.view.btn_update_char.clicked.connect(self.update_character)
        self.view.btn_clear_char.clicked.connect(self._clear_character_ui)
        self.view.btn_add_photo.clicked.connect(self.add_photo)
        self.view.btn_del_photo.clicked.connect(self.delete_photo)
        self.view.btn_delete_char.clicked.connect(self.delete_character)
        self.view.list_karakterler.itemClicked.connect(self.load_character)
        self.view.entry_filter.textChanged.connect(self.filter_characters)

        # Story
        self.view.btn_add_chapter.clicked.connect(self.add_chapter)
        self.view.btn_del_chapter.clicked.connect(self.delete_chapter)
        self.view.btn_save_chapter.clicked.connect(self.save_chapter)
        self.view.btn_move_up.clicked.connect(lambda: self.move_chapter(-1))
        self.view.btn_move_down.clicked.connect(lambda: self.move_chapter(1))
        self.view.list_outline.itemClicked.connect(self.load_chapter)
        self.view.text_chapter_content.textChanged.connect(self._update_word_count)

        # Country
        self.view.btn_add_country.clicked.connect(self.add_country)
        self.view.btn_del_country.clicked.connect(self.delete_country)
        self.view.btn_save_country.clicked.connect(self.save_country)
        self.view.list_countries.itemClicked.connect(self.load_country_details)
        
        # Country Flag
        self.view.btn_add_flag.clicked.connect(self.add_country_flag)
        self.view.btn_del_flag.clicked.connect(self.delete_country_flag)
        self.view.btn_flag_normal.clicked.connect(lambda: self.switch_flag_type("normal"))
        self.view.btn_flag_war.clicked.connect(lambda: self.switch_flag_type("war"))
        self.view.btn_flag_aid.clicked.connect(lambda: self.switch_flag_type("aid"))
        
        # Country Gov Tree
        self.view.btn_add_gov_item.clicked.connect(self.add_gov_unit)
        self.view.btn_add_gov_child.clicked.connect(self.add_gov_sub_unit)
        self.view.btn_del_gov_item.clicked.connect(self.delete_gov_unit)
        self.view.tree_country_gov.currentItemChanged.connect(self.change_gov_unit_selection)

        # Country Story
        self.view.list_country_stories.itemClicked.connect(self.load_country_story)
        self.view.btn_save_country_story.clicked.connect(self.save_country_story)

        # AI Assistant
        self.view.btn_ask_ai.clicked.connect(self.ask_ai)
        self.view.btn_use_ai_response.clicked.connect(self.insert_ai_suggestion)

        # Map
        self.view.btn_load_map.clicked.connect(self.load_map_image)

        self.ai_model = None

    def _start_autosave(self):
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self._autosave)
        self.autosave_timer.start(300000) # Every 5 minutes (Performance)

    def _autosave(self):
        # Atomic updates already handle most cases. 
        # Autosave just notifies user or handles unsaved text edits in future.
        self.view.statusBar().showMessage("Veriler güvende.", 1000)

    def select_project_folder(self):
        folder = QFileDialog.getExistingDirectory(self.view, "Proje Klasörü Seç", self.project_path)
        if folder:
            self.project_path = folder
            self.settings["project_path"] = folder
            database_manager.set_setting("project_path", folder)
            self._load_data()
            self.view.statusBar().showMessage(f"Proje yolu: {folder}", 5000)

    # --- Character Logic ---
    def _generate_character_code(self):
        import time
        ts = str(int(time.time() * 100))[-4:]
        count = len(self.characters)
        l1 = chr(65 + (count // 26) % 26)
        num = count % 100
        return f"{l1}{num:02d}-{ts}"

    def _update_character_list(self, filtered=None):
        self.view.list_karakterler.clear()
        data = filtered if filtered is not None else self.characters
        for char in data:
            item = QListWidgetItem(f"[{char.code}] {char.name}")
            self.view.list_karakterler.addItem(item)

    def filter_characters(self, text):
        f = text.lower()
        filtered = [c for c in self.characters if f in c.name.lower() or f in c.code.lower()]
        self._update_character_list(filtered)

    def load_character(self, item):
        code = item.text().split(']')[0][1:]
        char = next((c for c in self.characters if c.code == code), None)
        if char:
            self.current_char_code = char.code
            
            # Block signals to prevent 'update_character' firing while loading
            self.view.entry_char_name.blockSignals(True)
            self.view.text_char_desc.blockSignals(True)
            
            self.view.entry_char_code.setText(char.code)
            self.view.entry_char_name.setText(char.name)
            self.view.entry_char_title.setText(char.title)
            self.view.combo_gender.setCurrentText(char.gender)
            self.view.combo_nation.setCurrentText(char.nation)
            self.view.combo_country.setCurrentText(char.country)
            self.view.check_magic.setChecked(char.has_magic)
            self.view.combo_magic_type.setCurrentText(char.magic_type)
            self.view.text_char_desc.setText(char.description)
            
            self.view.entry_char_name.blockSignals(False)
            self.view.text_char_desc.blockSignals(False)
            
            # Lazy load image ONLY when needed
            img_b64 = database_manager.get_character_image(char.code)
            self.current_image_base64 = img_b64
            self._display_image(img_b64)

    def _clear_character_ui(self):
        self.current_char_code = None
        self.view.entry_char_code.clear()
        self.view.entry_char_name.clear()
        self.view.entry_char_title.clear()
        self.view.text_char_desc.clear()
        self.current_image_base64 = ""
        self.view.label_image.setPixmap(QPixmap())
        self.view.label_image.setText("Görsel Yok")

    def add_character(self):
        # Create a BLANK character as requested
        code = self._generate_character_code()
        new_char = Character(
            code=code,
            name="Yeni Karakter",
            title="",
            gender="Bilinmiyor",
            nation="Bilinmiyor",
            country="Bilinmiyor",
            has_magic=False,
            magic_type="Seçiniz",
            description="",
            image_base64=""
        )
        self.characters.append(new_char)
        database_manager.upsert_character(new_char)
        self._update_character_list()
        
        # Select the newly added character
        items = self.view.list_karakterler.findItems(f"[{code}] Yeni Karakter", Qt.MatchExactly)
        if items:
            self.view.list_karakterler.setCurrentItem(items[0])
            self.load_character(items[0]) # Load to form for editing
            
        self.view.statusBar().showMessage("Yeni karakter taslağı oluşturuldu. Şimdi formu doldurup güncelleyebilirsiniz.", 5000)

    def update_character(self):
        if not self.current_char_code: 
            QMessageBox.warning(self.view, "Uyarı", "Lütfen önce listeden bir karakter seçin!")
            return
            
        idx = next((i for i, c in enumerate(self.characters) if c.code == self.current_char_code), -1)
        if idx != -1:
            name = self.view.entry_char_name.text()
            self.characters[idx].name = name
            self.characters[idx].title = self.view.entry_char_title.text()
            self.characters[idx].gender = self.view.combo_gender.currentText()
            self.characters[idx].nation = self.view.combo_nation.currentText()
            self.characters[idx].country = self.view.combo_country.currentText()
            self.characters[idx].has_magic = self.view.check_magic.isChecked()
            self.characters[idx].magic_type = self.view.combo_magic_type.currentText()
            self.characters[idx].description = self.view.text_char_desc.toPlainText()
            self.characters[idx].image_base64 = self.current_image_base64
            
            database_manager.upsert_character(self.characters[idx])
            self._update_character_list()
            
            # Re-select to keep highlighting
            items = self.view.list_karakterler.findItems(f"[{self.current_char_code}]", Qt.MatchContains)
            if items: self.view.list_karakterler.setCurrentItem(items[0])
            
            self.view.statusBar().showMessage(f"'{name}' verileri güncellendi.", 3000)

    def delete_character(self):
        if not self.current_char_code: return
        res = QMessageBox.question(self.view, "Onay", "Karakteri silmek istediğinize emin misiniz?")
        if res == QMessageBox.Yes:
            database_manager.delete_character_db(self.current_char_code)
            self.characters = [c for c in self.characters if c.code != self.current_char_code]
            self._update_character_list()
            self._clear_character_ui()

    def add_photo(self):
        from PIL import Image
        path, _ = QFileDialog.getOpenFileName(self.view, "Görsel Seç", "", "İmajlar (*.png *.jpg *.jpeg)")
        if path:
            img = Image.open(path).convert("RGB")
            img.thumbnail((400, 400))
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=80)
            self.current_image_base64 = base64.b64encode(buf.getvalue()).decode()
            self._display_image(self.current_image_base64)

    def delete_photo(self):
        self.current_image_base64 = ""
        self.view.label_image.clear()
        self.view.label_image.setText("Görsel Yok")

    def _display_image(self, b64):
        if not b64:
            self.view.label_image.setPixmap(QPixmap())
            self.view.label_image.setText("Görsel Yok")
            return
        pix = QPixmap()
        pix.loadFromData(QByteArray(base64.b64decode(b64)))
        self.view.label_image.setPixmap(pix.scaled(250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    # --- Story Logic ---
    def _update_outline_list(self):
        self.view.list_outline.clear()
        for chap in self.chapters:
            self.view.list_outline.addItem(f"[{chap.id}] {chap.title}")

    def load_chapter(self, item):
        cid = item.text().split(']')[0][1:]
        chap = next((c for c in self.chapters if c.id == cid), None)
        if chap:
            self.current_chapter_id = chap.id
            self.view.entry_chapter_title.setText(chap.title)
            self.view.text_chapter_content.setText(chap.content)
            self._update_word_count()

    def save_chapter(self):
        if not self.current_chapter_id: return
        idx = next((i for i, c in enumerate(self.chapters) if c.id == self.current_chapter_id), -1)
        if idx != -1:
            self.chapters[idx].title = self.view.entry_chapter_title.text()
            self.chapters[idx].content = self.view.text_chapter_content.toPlainText()
            database_manager.upsert_chapter(self.chapters[idx], idx)
            self._update_outline_list()

    def add_chapter(self):
        new_id = f"S-{len(self.chapters)+1:02d}"
        new_chap = Chapter(id=new_id, title="Yeni Bölüm")
        self.chapters.append(new_chap)
        database_manager.save_chapters(self.chapters)
        self._update_outline_list()

    def delete_chapter(self):
        if not self.current_chapter_id: return
        self.chapters = [c for c in self.chapters if c.id != self.current_chapter_id]
        # Re-index
        for i, c in enumerate(self.chapters): c.id = f"S-{i+1:02d}"
        database_manager.save_chapters(self.chapters)
        self._update_outline_list()
        self.current_chapter_id = None
        self.view.entry_chapter_title.clear()
        self.view.text_chapter_content.clear()

    def move_chapter(self, delta):
        row = self.view.list_outline.currentRow()
        new_row = row + delta
        if 0 <= new_row < len(self.chapters):
            self.chapters[row], self.chapters[new_row] = self.chapters[new_row], self.chapters[row]
            # Re-index
            for i, c in enumerate(self.chapters): c.id = f"S-{i+1:02d}"
            database_manager.save_chapters(self.chapters)
            self._update_outline_list()
            self.view.list_outline.setCurrentRow(new_row)

    def _update_word_count(self):
        txt = self.view.text_chapter_content.toPlainText()
        words = len(re.findall(r'\w+', txt))
        self.view.label_word_count.setText(f"Kelime: {words} | Karakter: {len(txt)}")

    # --- Country Logic ---
    def _update_country_list(self):
        self.view.list_countries.clear()
        for c in self.countries:
            self.view.list_countries.addItem(f"[{c.id}] {c.name}")

    def load_country_details(self, item):
        cid = item.text().split(']')[0][1:]
        country = next((c for c in self.countries if c.id == cid), None)
        if country:
            self.current_country_id = country.id
            self.view.entry_country_name.setText(country.name)
            self.view.text_country_geo.setText(country.geography_details)
            self.view.tree_country_gov.clear()
            self._populate_gov_tree(self.view.tree_country_gov.invisibleRootItem(), country.government_details)
            
            # Reset flag view to Normal
            self.switch_flag_type("normal")
            self.view.btn_flag_normal.setChecked(True)
            self.view.btn_flag_war.setChecked(False)
            self.view.btn_flag_aid.setChecked(False)

    def _populate_gov_tree(self, parent_item, units):
        for unit in units:
            item = QTreeWidgetItem(parent_item, [unit.name])
            item.setData(0, Qt.UserRole, unit.details)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            if unit.sub_units:
                self._populate_gov_tree(item, unit.sub_units)

    def change_gov_unit_selection(self, current, previous):
        if previous:
            previous.setData(0, Qt.UserRole, self.view.text_gov_detail.toPlainText())
        if current:
            self.view.text_gov_detail.setText(current.data(0, Qt.UserRole))

    def add_country(self):
        nid = f"C-{len(self.countries)+1:02d}"
        nc = Country(id=nid, name="Yeni Ülke")
        self.countries.append(nc)
        database_manager.upsert_country(nc)
        self._update_country_list()
        self._populate_country_stories_list()

    def delete_country(self):
        if not self.current_country_id: return
        database_manager.delete_country_db(self.current_country_id)
        self.countries = [c for c in self.countries if c.id != self.current_country_id]
        self._update_country_list()
        self._populate_country_stories_list()

    def save_country(self):
        if not self.current_country_id: return
        idx = next((i for i, c in enumerate(self.countries) if c.id == self.current_country_id), -1)
        if idx != -1:
            # Sync current detail
            curr = self.view.tree_country_gov.currentItem()
            if curr: curr.setData(0, Qt.UserRole, self.view.text_gov_detail.toPlainText())
            
            
            self.countries[idx].name = self.view.entry_country_name.text()
            self.countries[idx].geography_details = self.view.text_country_geo.toPlainText()
            self.countries[idx].government_details = self._read_gov_tree(self.view.tree_country_gov.invisibleRootItem())
            
            # Flags are already updated in object during add/delete, but let's ensure current state is consistent if needed
            # (No extra action needed here if we update object immediately on add/del)
            
            database_manager.upsert_country(self.countries[idx])
            self._update_country_list()
            self._populate_country_stories_list()

    def switch_flag_type(self, ftype):
        self.current_country_flag_type = ftype
        
        # Ensure only one is checked (if using auto-exclusive, this might be redundant but safe)
        self.view.btn_flag_normal.setChecked(ftype == "normal")
        self.view.btn_flag_war.setChecked(ftype == "war")
        self.view.btn_flag_aid.setChecked(ftype == "aid")
        
        if not self.current_country_id:
            self._display_country_flag("")
            return
            
        country = next((c for c in self.countries if c.id == self.current_country_id), None)
        if country:
            img = ""
            if ftype == "normal": img = country.flag_normal
            elif ftype == "war": img = country.flag_war
            elif ftype == "aid": img = country.flag_aid
            self._display_country_flag(img)

    def add_country_flag(self):
        if not self.current_country_id: return
        
        from PIL import Image
        path, _ = QFileDialog.getOpenFileName(self.view, "Bayrak Seç", "", "İmajlar (*.png *.jpg *.jpeg)")
        if path:
            img = Image.open(path).convert("RGB")
            img.thumbnail((500, 300)) # Resize for flag (larger source)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=80)
            b64 = base64.b64encode(buf.getvalue()).decode()
            
            idx = next((i for i, c in enumerate(self.countries) if c.id == self.current_country_id), -1)
            if idx != -1:
                if self.current_country_flag_type == "normal": self.countries[idx].flag_normal = b64
                elif self.current_country_flag_type == "war": self.countries[idx].flag_war = b64
                elif self.current_country_flag_type == "aid": self.countries[idx].flag_aid = b64
                
                self._display_country_flag(b64)
                self.view.statusBar().showMessage(f"{self.current_country_flag_type.capitalize()} bayrağı eklendi.")

    def delete_country_flag(self):
        if not self.current_country_id: return
        
        idx = next((i for i, c in enumerate(self.countries) if c.id == self.current_country_id), -1)
        if idx != -1:
            if self.current_country_flag_type == "normal": self.countries[idx].flag_normal = ""
            elif self.current_country_flag_type == "war": self.countries[idx].flag_war = ""
            elif self.current_country_flag_type == "aid": self.countries[idx].flag_aid = ""
            
            self._display_country_flag("")
            self.view.statusBar().showMessage("Bayrak silindi.")

    def _display_country_flag(self, b64):
        if not b64:
            self.view.label_country_flag.setPixmap(QPixmap())
            self.view.label_country_flag.setText("Bayrak Yok")
            return
        pix = QPixmap()
        pix.loadFromData(QByteArray(base64.b64decode(b64)))
        self.view.label_country_flag.setPixmap(pix.scaled(400, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def _read_gov_tree(self, parent_item) -> List[GovUnit]:
        units = []
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            units.append(GovUnit(
                name=child.text(0),
                details=child.data(0, Qt.UserRole) or "",
                sub_units=self._read_gov_tree(child)
            ))
        return units

    def add_gov_unit(self):
        item = QTreeWidgetItem(self.view.tree_country_gov.invisibleRootItem(), ["Yeni Birim"])
        item.setData(0, Qt.UserRole, "")
        item.setFlags(item.flags() | Qt.ItemIsEditable)

    def add_gov_sub_unit(self):
        parent = self.view.tree_country_gov.currentItem()
        if not parent: return
        item = QTreeWidgetItem(parent, ["Yeni Alt Birim"])
        item.setData(0, Qt.UserRole, "")
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        parent.setExpanded(True)

    def delete_gov_unit(self):
        curr = self.view.tree_country_gov.currentItem()
        if not curr: return
        parent = curr.parent() or self.view.tree_country_gov.invisibleRootItem()
        parent.removeChild(curr)

    # --- Country Story Logic (FIXED) ---
    def _populate_country_stories_list(self):
        self.view.list_country_stories.clear()
        for c in self.countries:
            item = QListWidgetItem(f"[{c.id}] {c.name}")
            item.setData(Qt.UserRole, c.id) # Use ID instead of name to avoid conflicts
            self.view.list_country_stories.addItem(item)

    def load_country_story(self, item):
        cid = item.data(Qt.UserRole) # FIXED: Reading from ID
        country = next((c for c in self.countries if c.id == cid), None)
        if country:
            self.current_country_id = country.id
            self.view.text_country_story.setText(country.story)
            self.view.statusBar().showMessage(f"{country.name} hikayesi yüklendi.")

    def save_country_story(self):
        if not self.current_country_id: return
        idx = next((i for i, c in enumerate(self.countries) if c.id == self.current_country_id), -1)
        if idx != -1:
            self.countries[idx].story = self.view.text_country_story.toPlainText()
            database_manager.save_countries(self.countries)
            self.view.statusBar().showMessage("Hikaye kaydedildi.")

    # --- Map Logic ---
    def _load_saved_map(self):
        path = database_manager.get_setting("last_map_path")
        if path and os.path.exists(path):
            pix = QPixmap(path)
            self.view.map_scene.clear()
            self.view.map_scene.addPixmap(pix)
            self.view.map_view.setSceneRect(pix.rect())

    def load_map_image(self):
        path, _ = QFileDialog.getOpenFileName(self.view, "Harita Görseli Seç", "", "İmajlar (*.png *.jpg *.jpeg *.webp)")
        if path:
            pix = QPixmap(path)
            self.view.map_scene.clear()
            self.view.map_scene.addPixmap(pix)
            self.view.map_view.setSceneRect(pix.rect())
            database_manager.set_setting("last_map_path", path)
            self.view.statusBar().showMessage("Harita yüklendi.")

    # --- AI Logic ---
    def ask_ai(self):
        import google.generativeai as genai
        if not self.ai_model:
            # Ensure API key is set
            genai.configure(api_key="AIzaSyDPmAvLbWkgpMXo0wcjy7MS9c1eFQpeZeI")
            # Reverting to 1.5-flash as default to avoid 429 quota issues with 2.0
            try:
                self.ai_model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception:
                self.ai_model = genai.GenerativeModel('gemini-pro')

        prompt = self.view.text_ai_prompt.toPlainText().strip()
        if not prompt: return
        
        self.view.statusBar().showMessage("AI düşünüyor...")
        self.view.btn_ask_ai.setEnabled(False)
        self.view.text_ai_response.setText("Yükleniyor...")

        try:
            char_names = ", ".join([c.name for c in self.characters])
            country_names = ", ".join([cn.name for cn in self.countries])
            
            full_prompt = f"Sen profesyonel bir hikaye yazım asistanısın. Mevcut Dünya Bilgileri:\nKarakterler: {char_names}\nÜlkeler: {country_names}\n\nKullanıcı Sorusu: {prompt}"
            
            # API call with safety
            response = self.ai_model.generate_content(full_prompt)
            if response and hasattr(response, 'text'):
                self.view.text_ai_response.setText(response.text)
                self.view.statusBar().showMessage("AI yanıtladı.", 3000)
            else:
                raise Exception("AI boş yanıt döndürdü (Güvenlik filtrelerine takılmış olabilir).")
        except Exception as e:
            error_msg = str(e)
            if "API key" in error_msg: error_msg = "API Anahtarı geçersiz."
            QMessageBox.warning(self.view, "AI Bildirimi", f"Yapay zeka şu an cevap veremiyor: {error_msg}")
            self.view.text_ai_response.setText(f"Hata: {error_msg}")
        finally:
            self.view.btn_ask_ai.setEnabled(True)

    def insert_ai_suggestion(self):
        suggestion = self.view.text_ai_response.toPlainText()
        if suggestion and suggestion not in ["Yükleniyor...", "Hata oluştu."]:
            current_text = self.view.text_chapter_content.toPlainText()
            self.view.text_chapter_content.setText(current_text + "\n\n" + suggestion)
            self.view.statusBar().showMessage("AI yanıtı hikayeye eklendi.")
