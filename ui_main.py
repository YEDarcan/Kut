from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QMenuBar, QStatusBar, QTabWidget, QLabel, 
    QLineEdit, QPushButton, QComboBox, QCheckBox, 
    QListWidget, QGridLayout, QFrame, QTextEdit, 
    QTreeWidget, QTreeWidgetItem, QStackedWidget,
    QSpacerItem, QSizePolicy, QGraphicsView, QGraphicsScene,
    QGraphicsPixmapItem, QGraphicsEllipseItem, QFontComboBox, QSpinBox,
    QDialog, QFileDialog, QMessageBox, QSlider, QWidgetAction
)
from PySide6.QtGui import QAction, QPainter, QFont, QTextCharFormat, QFontDatabase
from PySide6.QtCore import Qt, Signal
from data_manager import load_settings
import os
try:
    from my_audio_lib import SoundManager
    SOUND_AVAILABLE = True
except ImportError:
    print("Warning: SoundManager module failed to import.")
    SOUND_AVAILABLE = False


# UI Constants
MILLTETLER = ["Zhaerri", "Nyrim", "Rhazir", "Vandrell", "Tharien", "Cyta", "Valionis", "Bilinmiyor"]
ULKELER = ["Zhaerri İmparatorluğu", "Nyrim Klanları", "Rhazir", "Vandrell Cumhuriyeti", "Tharien Cumhuriyeti", "Birtan Krallığı", "Güney Adalar Federasyonu", "Kuzey Adalar Federasyonu", "Valionis Halkları", "Tenebris Diktası", "Bilinmiyor"]
BUYU_TIPLERI = ["Işık", "Kan", "Kara", "Toprak", "Fırtına", "Ateş"]
CINSIYETLER = ["Erkek", "Kadın", "Bilinmiyor"]

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)

class FontSettingsDialog(QDialog):
    fonts_updated = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yazı Tipi Yöneticisi")
        self.resize(500, 400)
        self.settings = load_settings()
        self.favorite_fonts = self.settings.get("favorite_fonts", [])
        
        self.layout = QVBoxLayout(self)
        
        # Lists Layout
        lists_layout = QHBoxLayout()
        
        # Left: Favorites
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Favori Yazı Tipleri"))
        self.list_favorites = QListWidget()
        self.list_favorites.addItems(self.favorite_fonts)
        left_layout.addWidget(self.list_favorites)
        
        self.btn_remove = QPushButton("<< Sil")
        self.btn_remove.setObjectName("danger")
        self.btn_remove.clicked.connect(self._remove_font)
        left_layout.addWidget(self.btn_remove)
        
        lists_layout.addLayout(left_layout)
        
        # Right: System Fonts
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Sistemdeki Yazı Tipleri"))
        self.combo_system_fonts = QFontComboBox()
        self.combo_system_fonts.setEditable(False) # Just list them
        right_layout.addWidget(self.combo_system_fonts)
        
        self.btn_add = QPushButton("Ekle >>")
        self.btn_add.setObjectName("primary")
        self.btn_add.clicked.connect(self._add_font)
        right_layout.addWidget(self.btn_add)
        
        # Load from file
        self.btn_load_file = QPushButton("Dosyadan Font Yükle (.ttf)...")
        self.btn_load_file.clicked.connect(self._load_font_from_file)
        right_layout.addWidget(self.btn_load_file)
        
        right_layout.addStretch()
        lists_layout.addLayout(right_layout)
        
        self.layout.addLayout(lists_layout)
        
        # Save Button
        self.btn_save = QPushButton("Kaydet ve Kapat")
        self.btn_save.setObjectName("primary")
        self.btn_save.clicked.connect(self._save_and_close)
        self.layout.addWidget(self.btn_save)

    def _add_font(self):
        font_family = self.combo_system_fonts.currentFont().family()
        if font_family not in self.favorite_fonts:
            self.favorite_fonts.append(font_family)
            self.favorite_fonts.sort()
            self.list_favorites.clear()
            self.list_favorites.addItems(self.favorite_fonts)

    def _remove_font(self):
        current_row = self.list_favorites.currentRow()
        if current_row >= 0:
            item = self.list_favorites.takeItem(current_row)
            font_name = item.text()
            if font_name in self.favorite_fonts:
                self.favorite_fonts.remove(font_name)

    def _load_font_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Font Dosyası Seç", "", "Font Files (*.ttf *.otf)")
        if file_path:
            font_id = QFontDatabase.addApplicationFont(file_path)
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                if families:
                    font_name = families[0]
                    if font_name not in self.favorite_fonts:
                        self.favorite_fonts.append(font_name)
                        self.favorite_fonts.sort()
                        self.list_favorites.clear()
                        self.list_favorites.addItems(self.favorite_fonts)
                        QMessageBox.information(self, "Başarılı", f"'{font_name}' başarıyla eklendi!")
            else:
                QMessageBox.warning(self, "Hata", "Font dosyası yüklenemedi.")

    def _save_and_close(self):
        self.settings["favorite_fonts"] = self.favorite_fonts
        save_settings(self.settings)
        self.fonts_updated.emit()
        self.accept()

class MainWindowUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KUT Story Engine v3.3")
        self.resize(1400, 900)

        # Main Widget and Layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True) # Cleaner look
        self.main_layout.addWidget(self.tabs)

        self.setStatusBar(QStatusBar(self))
        self._create_menu_bar()
        
        # Initial font load
        self.font_combos = []
        self._refresh_fonts()

        # Audio Manager Initialization
        global SOUND_AVAILABLE
        self.sound_manager = None
        if SOUND_AVAILABLE:
            try:
                self.sound_manager = SoundManager(self)
            except Exception as e:
                print(f"Failed to initialize SoundManager: {e}")
                SOUND_AVAILABLE = False
        
        self._update_sound_menu()
        self._setup_pages()

    def _setup_pages(self):
        # Index 0: Character
        self.character_page = QWidget()
        self._setup_character_tab()
        self.tabs.addTab(self.character_page, "Karakterler")

        # Index 1: Story
        self.story_page = QWidget()
        self._setup_story_tab()
        self.tabs.addTab(self.story_page, "Hikaye")

        # Index 2: World (Countries)
        self.country_page = QWidget()
        self._setup_country_tab()
        self.tabs.addTab(self.country_page, "Ülkeler")

        # Index 3: Country Story
        self.country_story_page = QWidget()
        self._setup_country_story_tab()
        self.tabs.addTab(self.country_story_page, "Ülke Hikayeleri")

        # Index 4: Map
        self.map_page = QWidget()
        self._setup_map_page()
        self.tabs.addTab(self.map_page, "Harita")

        # Index 5: AI
        self.ai_page = QWidget()
        self._setup_ai_page()
        self.tabs.addTab(self.ai_page, "AI Asistan")
        
        # Initial font load
        self.font_combos = []
        self._refresh_fonts()

        # Audio Manager Initialization
        self.sound_manager = None
        if SOUND_AVAILABLE:
            try:
                self.sound_manager = SoundManager(self)
            except Exception as e:
                print(f"Failed to initialize SoundManager: {e}")

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("Dosya")
        self.action_select_folder = QAction("Proje Klasörü Seç...", self)
        file_menu.addAction(self.action_select_folder)
        self.action_refresh = QAction("Yenile", self)
        file_menu.addAction(self.action_refresh)
        file_menu.addSeparator()
        self.action_exit = QAction("Çıkış", self)
        file_menu.addAction(self.action_exit)

        theme_menu = menu_bar.addMenu("Tema")
        self.action_theme_light = QAction("Açık", self)
        self.action_theme_dark = QAction("Koyu", self)
        self.action_theme_green = QAction("Yeşil", self)
        self.action_theme_orange = QAction("Turuncu", self)
        
        theme_menu.addActions([
            self.action_theme_light, 
            self.action_theme_dark, 
            self.action_theme_green, 
            self.action_theme_orange
        ])

        settings_menu = menu_bar.addMenu("Ayarlar")
        self.action_font_settings = QAction("Yazı Tipi Yöneticisi...", self)
        self.action_font_settings.triggered.connect(self._open_font_settings)
        settings_menu.addAction(self.action_font_settings)

        # Audio Menu (Dynamic)
        self.sound_menu = menu_bar.addMenu("Ses (🎵)")
        self.sound_menu.aboutToShow.connect(self._update_sound_menu)

    def _open_font_settings(self):
        dialog = FontSettingsDialog(self)
        dialog.fonts_updated.connect(self._refresh_fonts)
        dialog.exec()

    def _update_sound_menu(self):
        self.sound_menu.clear()
        
        if not SOUND_AVAILABLE or not self.sound_manager:
            err_action = QAction("⚠️ Modül Yüklenemedi", self)
            err_action.setEnabled(False)
            self.sound_menu.addAction(err_action)
            return

        # Volume Slider
        vol_action = QWidgetAction(self.sound_menu)
        vol_widget = QWidget()
        vol_layout = QHBoxLayout(vol_widget)
        vol_layout.setContentsMargins(10, 5, 10, 5)
        vol_layout.addWidget(QLabel("Ses:"))
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(50)
        slider.setFixedWidth(100)
        slider.valueChanged.connect(self.sound_manager.set_volume)
        vol_layout.addWidget(slider)
        vol_action.setDefaultWidget(vol_widget)
        self.sound_menu.addAction(vol_action)
        
        self.sound_menu.addSeparator()
        
        # Stop Action
        stop_action = QAction("⏹ Sessiz", self)
        stop_action.triggered.connect(self.sound_manager.stop_sound)
        self.sound_menu.addAction(stop_action)
        
        self.sound_menu.addSeparator()
        
        # Files
        sounds = self.sound_manager.get_available_sounds()
        if not sounds:
            no_sound = QAction("(Klasör boş)", self)
            no_sound.setEnabled(False)
            self.sound_menu.addAction(no_sound)
        else:
            for s in sounds:
                action = QAction(f"▶ {s}", self)
                action.triggered.connect(lambda checked, f=s: self.sound_manager.play_sound(f))
                self.sound_menu.addAction(action)
        
        self.sound_menu.addSeparator()
        open_folder = QAction("Klasörü Aç...", self)
        open_folder.triggered.connect(lambda: os.startfile(self.sound_manager.sound_dir))
        self.sound_menu.addAction(open_folder)

    def _refresh_fonts(self):
        settings = load_settings()
        fav_fonts = settings.get("favorite_fonts", [])
        if not fav_fonts: 
            fav_fonts = ["Arial", "Courier New", "Georgia", "Impact", "Segoe UI", "Tahoma", "Times New Roman", "Verdana"]
        
        for combo in self.font_combos:
            current_font = combo.currentText()
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(fav_fonts)
            
            # Restore selection if possible, otherwise default
            index = combo.findText(current_font)
            if index != -1:
                combo.setCurrentIndex(index)
            elif fav_fonts:
                combo.setCurrentIndex(0)
            
            combo.blockSignals(False)



    # --- Character Page UI ---
    def _setup_character_tab(self):
        layout = QHBoxLayout(self.character_page)
        
        # Left Panel: Info
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        
        self.label_image = QLabel("Görsel Yok")
        self.label_image.setFixedSize(250, 250)
        self.label_image.setAlignment(Qt.AlignCenter)
        self.label_image.setStyleSheet("border: 2px dashed #666; border-radius: 10px;")
        left_layout.addWidget(self.label_image, alignment=Qt.AlignCenter)
        
        btn_layout = QHBoxLayout()
        self.btn_add_photo = QPushButton("Fotoğraf Ekle")
        self.btn_del_photo = QPushButton("Fotoğraf Sil")
        self.btn_del_photo.setObjectName("danger")
        btn_layout.addWidget(self.btn_add_photo)
        btn_layout.addWidget(self.btn_del_photo)
        left_layout.addLayout(btn_layout)
        
        form_layout = QGridLayout()
        self.entry_char_code = QLineEdit(); self.entry_char_code.setReadOnly(True)
        self.entry_char_name = QLineEdit()
        self.entry_char_title = QLineEdit()
        self.combo_gender = QComboBox(); self.combo_gender.addItems(CINSIYETLER)
        self.combo_nation = QComboBox(); self.combo_nation.addItems(MILLTETLER)
        self.combo_country = QComboBox(); self.combo_country.addItems(ULKELER)
        self.check_magic = QCheckBox("Büyü Gücü Var mı?")
        self.combo_magic_type = QComboBox(); self.combo_magic_type.addItems(["Seçiniz"] + BUYU_TIPLERI)
        
        widgets = [
            ("Kod:", self.entry_char_code),
            ("Ad:", self.entry_char_name),
            ("Ünvan:", self.entry_char_title),
            ("Cinsiyet:", self.combo_gender),
            ("Millet:", self.combo_nation),
            ("Ülke:", self.combo_country),
            ("", self.check_magic),
            ("Büyü Tipi:", self.combo_magic_type)
        ]
        
        for i, (label, widget) in enumerate(widgets):
            if label: form_layout.addWidget(QLabel(label), i, 0)
            form_layout.addWidget(widget, i, 1)
            
        left_layout.addLayout(form_layout)
        
        ctrl_layout = QHBoxLayout()
        self.btn_add_char = QPushButton("Yeni Karakter Ekle")
        self.btn_add_char.setObjectName("primary")
        self.btn_update_char = QPushButton("Seçileni Güncelle")
        self.btn_clear_char = QPushButton("Formu Temizle")
        self.btn_clear_char.setObjectName("secondary")
        
        ctrl_layout.addWidget(self.btn_add_char)
        ctrl_layout.addWidget(self.btn_update_char)
        ctrl_layout.addWidget(self.btn_clear_char)
        left_layout.addLayout(ctrl_layout)
        
        layout.addWidget(left_panel, 3)

        # Middle Panel: Description
        self.text_char_desc = QTextEdit()
        self.text_char_desc.setPlaceholderText("Karakter detaylı açıklaması...")
        layout.addWidget(self.text_char_desc, 6)

        # Right Panel: List
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        
        self.entry_filter = QLineEdit()
        self.entry_filter.setPlaceholderText("Ara...")
        right_layout.addWidget(self.entry_filter)
        
        self.list_karakterler = QListWidget()
        right_layout.addWidget(self.list_karakterler)
        
        self.btn_delete_char = QPushButton("Karakteri Sil")
        self.btn_delete_char.setObjectName("danger")
        right_layout.addWidget(self.btn_delete_char)
        
        layout.addWidget(right_panel, 2)


    def _setup_ai_page(self):
        layout = QVBoxLayout(self.ai_page)
        
        header = QLabel("AI Hikaye Asistanı (Gemini)")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #3b82f6;")
        layout.addWidget(header)
        
        self.text_ai_prompt = QTextEdit()
        self.text_ai_prompt.setPlaceholderText("AI'ya ne sormak istersin? (örn: Bu sahne için bir diyalog önerisi ver...)")
        self.text_ai_prompt.setMaximumHeight(80)
        layout.addWidget(self.text_ai_prompt)
        
        self.btn_ask_ai = QPushButton("AI'ya Sor")
        layout.addWidget(self.btn_ask_ai)
        
        self.text_ai_response = QTextEdit()
        self.text_ai_response.setReadOnly(True)
        self.text_ai_response.setPlaceholderText("AI yanıtı burada belirecek...")
        layout.addWidget(self.text_ai_response)
        
        self.btn_use_ai_response = QPushButton("Hikayeye Ekle")
        layout.addWidget(self.btn_use_ai_response)

    def _setup_map_page(self):
        main_layout = QVBoxLayout(self.map_page)
        
        ctrl_layout = QHBoxLayout()
        self.btn_load_map = QPushButton("Harita Yükle")
        self.btn_load_map.setObjectName("primary")
        
        ctrl_layout.addWidget(self.btn_load_map)
        ctrl_layout.addStretch()
        main_layout.addLayout(ctrl_layout)
        
        # Harita Görünümü (Full Width)
        self.map_scene = QGraphicsScene()
        self.map_view = ZoomableGraphicsView(self.map_scene)
        self.map_view.setStyleSheet("background-color: #0c0c0d; border: 1px solid #2c2c2e; border-radius: 4px;")
        main_layout.addWidget(self.map_view)

        self.label_map_info = QLabel("Mouse tekerleği ile zoom yapabilir, sürükleyerek gezinebilirsiniz.")
        main_layout.addWidget(self.label_map_info)

    # --- Rich Text Format Helper ---
    def _create_format_layout(self, text_edit: QTextEdit):
        layout = QHBoxLayout()
        
        # Font Family (QComboBox -> Managed list)
        font_combo = QComboBox()
        font_combo.setEditable(False)
        font_combo.setMinimumWidth(150)
        # Connect change event
        font_combo.currentTextChanged.connect(lambda f: text_edit.setCurrentFont(QFont(f)) if f else None)
        layout.addWidget(font_combo)
        
        # Register to managed list
        self.font_combos.append(font_combo)
        
        # Font Size
        size_spin = QSpinBox()
        size_spin.setRange(8, 96)
        size_spin.setValue(11) # Default
        size_spin.valueChanged.connect(lambda s: text_edit.setFontPointSize(s))
        layout.addWidget(size_spin)
        
        # Bold
        btn_bold = QPushButton("B")
        btn_bold.setCheckable(True)
        btn_bold.setFixedWidth(30)
        btn_bold.setStyleSheet("font-weight: bold;")
        btn_bold.clicked.connect(lambda: self._set_text_format(text_edit, "bold", btn_bold.isChecked()))
        layout.addWidget(btn_bold)

        # Italic
        btn_italic = QPushButton("I")
        btn_italic.setCheckable(True)
        btn_italic.setFixedWidth(30)
        btn_italic.setStyleSheet("font-style: italic;")
        btn_italic.clicked.connect(lambda: self._set_text_format(text_edit, "italic", btn_italic.isChecked()))
        layout.addWidget(btn_italic)

        # Underline
        btn_underline = QPushButton("U")
        btn_underline.setCheckable(True)
        btn_underline.setFixedWidth(30)
        btn_underline.setStyleSheet("text-decoration: underline;")
        btn_underline.clicked.connect(lambda: self._set_text_format(text_edit, "underline", btn_underline.isChecked()))
        layout.addWidget(btn_underline)
        
        return layout

    def _set_text_format(self, text_edit, fmt_type, active):
        fmt = QTextCharFormat()
        if fmt_type == "bold":
            fmt.setFontWeight(QFont.Bold if active else QFont.Normal)
        elif fmt_type == "italic":
            fmt.setFontItalic(active)
        elif fmt_type == "underline":
            fmt.setFontUnderline(active)
        text_edit.mergeCurrentCharFormat(fmt)

    # --- Story Page UI ---
    def _setup_story_tab(self):
        layout = QHBoxLayout(self.story_page)
        
        # Left: Content
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.entry_chapter_title = QLineEdit()
        self.entry_chapter_title.setPlaceholderText("Bölüm Başlığı...")
        left_layout.addWidget(self.entry_chapter_title)
        
        self.text_chapter_content = QTextEdit()
        left_layout.addWidget(self.text_chapter_content)
        
        self.label_word_count = QLabel("Kelime: 0")
        self.label_word_count.setAlignment(Qt.AlignRight)
        left_layout.addWidget(self.label_word_count)
        
        # Footer Layout: Format Controls + Save Button
        footer_layout = QHBoxLayout()
        
        format_controls = self._create_format_layout(self.text_chapter_content)
        footer_layout.addLayout(format_controls)
        
        footer_layout.addStretch() # Spacer
        
        self.btn_save_chapter = QPushButton("✔ Bölümü Kaydet")
        footer_layout.addWidget(self.btn_save_chapter)
        
        left_layout.addLayout(footer_layout)
        
        layout.addWidget(left_panel, 8)
        
        # Right: Outline
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        
        right_layout.addWidget(QLabel("Bölüm Listesi"))
        self.list_outline = QListWidget()
        self.list_outline.setDragDropMode(QListWidget.InternalMove)
        right_layout.addWidget(self.list_outline)
        
        btn_layout = QGridLayout()
        self.btn_add_chapter = QPushButton("Yeni")
        self.btn_del_chapter = QPushButton("Sil")
        self.btn_move_up = QPushButton("Yukarı")
        self.btn_move_down = QPushButton("Aşağı")
        
        btn_layout.addWidget(self.btn_add_chapter, 0, 0)
        btn_layout.addWidget(self.btn_del_chapter, 0, 1)
        btn_layout.addWidget(self.btn_move_up, 1, 0)
        btn_layout.addWidget(self.btn_move_down, 1, 1)
        right_layout.addLayout(btn_layout)
        
        layout.addWidget(right_panel, 2)

    # --- Country Page UI ---
    def _setup_country_tab(self):
        layout = QHBoxLayout(self.country_page)
        
        # Left: List
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("🌍 Ülkeler"))
        self.list_countries = QListWidget()
        left_layout.addWidget(self.list_countries)
        
        self.btn_add_country = QPushButton("Yeni Ülke")
        self.btn_del_country = QPushButton("Sil")
        self.btn_del_country.setObjectName("danger")
        left_layout.addWidget(self.btn_add_country)
        left_layout.addWidget(self.btn_del_country)
        layout.addWidget(left_panel, 2)
        
        # Middle: Geo + Flag
        mid_panel = QWidget()
        mid_layout = QVBoxLayout(mid_panel)
        
        # --- Flag Area ---
        flag_wrapper = QFrame()
        flag_wrapper.setStyleSheet("background-color: #1e1e1e; border-radius: 8px;")
        flag_wrapper_layout = QVBoxLayout(flag_wrapper)
        flag_wrapper_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header: Toggles (Right Aligned)
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        for btn_text, btn_obj_name in [("N", "btn_flag_normal"), ("S", "btn_flag_war"), ("Y", "btn_flag_aid")]:
            btn = QPushButton(btn_text)
            btn.setCheckable(True)
            btn.setFixedSize(24, 24)
            btn.setStyleSheet("""
                QPushButton { font-size: 11px; font-weight: bold; border-radius: 4px; background-color: #333; }
                QPushButton:checked { background-color: #3b82f6; color: white; }
                QPushButton:hover { background-color: #444; }
            """)
            setattr(self, btn_obj_name, btn)
            header_layout.addWidget(btn)
            
        # Select first by default
        self.btn_flag_normal.setChecked(True)
        self.btn_flag_normal.setToolTip("Normal Bayrak")
        self.btn_flag_war.setToolTip("Savaş Bayrağı")
        self.btn_flag_aid.setToolTip("Yardım Bayrağı")
            
        flag_wrapper_layout.addLayout(header_layout)
        
        # Flag Image
        self.label_country_flag = QLabel("Bayrak Yok")
        self.label_country_flag.setFixedSize(400, 240)
        self.label_country_flag.setAlignment(Qt.AlignCenter)
        self.label_country_flag.setStyleSheet("border: 1px dashed #555; border-radius: 4px; background-color: #252525; color: #777;")
        flag_wrapper_layout.addWidget(self.label_country_flag, alignment=Qt.AlignCenter)
        
        # Footer: Actions (Small)
        footer_layout = QHBoxLayout()
        footer_layout.setAlignment(Qt.AlignCenter)
        
        self.btn_add_flag = QPushButton("+ Ekle")
        self.btn_add_flag.setFixedSize(60, 24)
        self.btn_add_flag.setStyleSheet("font-size: 10px; padding: 0;")
        
        self.btn_del_flag = QPushButton("- Sil")
        self.btn_del_flag.setObjectName("danger")
        self.btn_del_flag.setFixedSize(60, 24)
        self.btn_del_flag.setStyleSheet("font-size: 10px; padding: 0;")

        footer_layout.addWidget(self.btn_add_flag)
        footer_layout.addSpacing(10)
        footer_layout.addWidget(self.btn_del_flag)
        flag_wrapper_layout.addLayout(footer_layout)
        
        mid_layout.addWidget(flag_wrapper)
        mid_layout.addSpacing(10)
        # ----------------
        
        self.entry_country_name = QLineEdit()
        self.entry_country_name.setPlaceholderText("Ülke Adı...")
        mid_layout.addWidget(QLabel("Ad:"))
        mid_layout.addWidget(self.entry_country_name)
        
        self.text_country_geo = QTextEdit()
        self.text_country_geo.setPlaceholderText("Coğrafya detayları...")
        mid_layout.addWidget(QLabel("Coğrafya:"))
        mid_layout.addWidget(self.text_country_geo)
        layout.addWidget(mid_panel, 3)
        
        # Right: Gov
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.tree_country_gov = QTreeWidget()
        self.tree_country_gov.setHeaderLabel("Yönetim Hiyerarşisi")
        right_layout.addWidget(self.tree_country_gov, 3)
        
        self.text_gov_detail = QTextEdit()
        self.text_gov_detail.setPlaceholderText("Birim detayı...")
        right_layout.addWidget(self.text_gov_detail, 2)
        
        tree_btn_layout = QHBoxLayout()
        self.btn_add_gov_item = QPushButton("+ Ana")
        self.btn_add_gov_child = QPushButton("+ Alt")
        self.btn_del_gov_item = QPushButton("- Sil")
        tree_btn_layout.addWidget(self.btn_add_gov_item)
        tree_btn_layout.addWidget(self.btn_add_gov_child)
        tree_btn_layout.addWidget(self.btn_del_gov_item)
        right_layout.addLayout(tree_btn_layout)
        
        self.btn_save_country = QPushButton("Ülkeyi Kaydet")
        right_layout.addWidget(self.btn_save_country, alignment=Qt.AlignRight)
        layout.addWidget(right_panel, 5)

    # --- Country Stories Page UI ---
    def _setup_country_story_tab(self):
        layout = QHBoxLayout(self.country_story_page)
        
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("🌍 Ülkeler"))
        self.list_country_stories = QListWidget()
        left_layout.addWidget(self.list_country_stories)
        layout.addWidget(left_panel, 2)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(QLabel("Ülke Hikayesi"))
        self.text_country_story = QTextEdit()
        right_layout.addWidget(self.text_country_story)
        
        # Footer Layout: Format Controls + Save Button
        footer_layout = QHBoxLayout()
        
        format_controls = self._create_format_layout(self.text_country_story)
        footer_layout.addLayout(format_controls)
        
        footer_layout.addStretch() # Spacer
        
        self.btn_save_country_story = QPushButton("Hikayeyi Kaydet")
        footer_layout.addWidget(self.btn_save_country_story)
        
        right_layout.addLayout(footer_layout)
        
        layout.addWidget(right_panel, 8)
