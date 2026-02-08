import streamlit as st
import database_manager
from models import Character, Chapter, Country

# Page Configuration
st.set_page_config(
    page_title="Antigravity Hikaye Yöneticisi",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Database
if "db_initialized" not in st.session_state:
    database_manager.init_db()
    st.session_state.db_initialized = True

def main():
    st.sidebar.title("📚 Hikaye Yöneticisi")
    
    # Navigation
    page = st.sidebar.radio(
        "Gezinti",
        ["Ana Sayfa", "Karakterler", "Hikaye (Bölümler)", "Dünya & Ülkeler", "Harita & Ses", "Ayarlar"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("v2.0 - Web Sürümü")

    if page == "Ana Sayfa":
        show_home()
    elif page == "Karakterler":
        show_characters()
    elif page == "Hikaye (Bölümler)":
        show_story()
    elif page == "Dünya & Ülkeler":
        show_world()
    elif page == "Harita & Ses":
        show_map_audio()
    elif page == "Ayarlar":
        show_settings()

def show_home():
    st.title("🧙‍♂️ Antigravity Yazarlık Stüdyosu")
    st.markdown("""
    Hoş geldiniz! Burası hikayenizi her yerden yazabileceğiniz yeni çalışma alanınız.
    
    ### 🚀 Neler Yapabilirsiniz?
    *   **Karakterler**: Karakterlerinizi oluşturun, düzenleyin ve fotoğraflarını yükleyin.
    *   **Hikaye**: Bölümler halinde hikayenizi yazın, kelime sayınızı takip edin.
    *   **Dünya**: Ülkeleri, yönetim biçimlerini ve bayraklarını yönetin.
    *   **Harita**: Dünyanızın haritasını yükleyin ve inceleyin.
    
    *Verileriniz güvende ve anlık olarak kaydediliyor.*
    """)
    
    # Dashboard / Stats
    col1, col2, col3 = st.columns(3)
    
    chars = database_manager.load_characters()
    chaps = database_manager.load_chapters()
    countries = database_manager.load_countries()
    
    with col1:
        st.metric("Karakter Sayısı", len(chars))
    with col2:
        st.metric("Yazılan Bölüm", len(chaps))
    with col3:
        st.metric("Oluşturulan Ülke", len(countries))

def show_characters():
    st.header("👥 Karakterler")
    
    # Load Data
    chars = database_manager.load_characters(include_image=True)
    
    # Sidebar Selection
    char_names = [f"{c.code} - {c.name}" for c in chars]
    selected_option = st.selectbox("Karakter Seç / Ara", ["➕ Yeni Karakter Ekle"] + char_names)
    
    if selected_option == "➕ Yeni Karakter Ekle":
        st.subheader("Yeni Karakter Oluştur")
        with st.form("new_char_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Ad")
                title = st.text_input("Ünvan")
                gender = st.selectbox("Cinsiyet", ["Erkek", "Kadın", "Bilinmiyor", "Diğer"])
                nation = st.text_input("Millet", "Bilinmiyor")
            with col2:
                country = st.text_input("Ülke", "Bilinmiyor")
                has_magic = st.checkbox("Büyü Gücü Var mı?")
                magic_type = st.selectbox("Büyü Tipi", ["Yok", "Ateş", "Su", "Hava", "Toprak", "Zihin", "Ruh", "Nekromansi", "Işık", "Karanlık", "Diğer"])
            
            desc = st.text_area("Detaylı Açıklama")
            
            # Image Upload
            img_file = st.file_uploader("Karakter Görseli", type=["png", "jpg", "jpeg"])
            
            submitted = st.form_submit_button("Kaydet")
            if submitted:
                import base64
                img_b64 = ""
                if img_file:
                    img_b64 = base64.b64encode(img_file.read()).decode()
                
                # Generate Code
                import time
                ts = str(int(time.time() * 100))[-4:]
                count = len(chars)
                l1 = chr(65 + (count // 26) % 26)
                num = count % 100
                new_code = f"{l1}{num:02d}-{ts}"
                
                new_char = Character(
                    code=new_code,
                    name=name if name else "Adsız",
                    title=title,
                    gender=gender,
                    nation=nation,
                    country=country,
                    has_magic=has_magic,
                    magic_type=magic_type,
                    description=desc,
                    image_base64=img_b64
                )
                database_manager.upsert_character(new_char)
                st.success(f"{name} oluşturuldu!")
                st.rerun()

    else:
        # Edit Existing
        code = selected_option.split(" - ")[0]
        char = next((c for c in chars if c.code == code), None)
        
        if char:
            st.divider()
            col_img, col_info = st.columns([1, 2])
            
            with col_img:
                if char.image_base64:
                    import io, base64
                    try:
                        img_data = base64.b64decode(char.image_base64)
                        st.image(img_data, width=250)
                    except:
                        st.error("Görsel yüklenemedi.")
                else:
                    st.info("Görsel Yok")
            
            with col_info:
                st.subheader(f"{char.name} {f'({char.title})' if char.title else ''}")
                st.markdown(f"**Kod:** `{char.code}`")
                st.markdown(f"**Cinsiyet:** {char.gender} | **Millet:** {char.nation}")
                st.markdown(f"**Ülke:** {char.country}")
                if char.has_magic:
                    st.warning(f"✨ Büyücü: {char.magic_type}")
                else:
                    st.markdown("Normal İnsan")
                
                with st.expander("📝 Detaylı Açıklama"):
                    st.write(char.description)

            st.divider()
            with st.expander("✏️ Düzenle", expanded=False):
                with st.form("edit_char_form"):
                    c1, c2 = st.columns(2)
                    with c1:
                        e_name = st.text_input("Ad", char.name)
                        e_title = st.text_input("Ünvan", char.title)
                        e_gender = st.selectbox("Cinsiyet", ["Erkek", "Kadın", "Bilinmiyor", "Diğer"], index=["Erkek", "Kadın", "Bilinmiyor", "Diğer"].index(char.gender) if char.gender in ["Erkek", "Kadın", "Bilinmiyor", "Diğer"] else 2)
                    with c2:
                        e_country = st.text_input("Ülke", char.country)
                        e_magic = st.checkbox("Büyü Gücü", char.has_magic)
                        e_mtype = st.selectbox("Büyü Tipi", ["Yok", "Ateş", "Su", "Hava", "Toprak", "Zihin", "Ruh", "Nekromansi", "Işık", "Karanlık", "Diğer"], index=["Yok", "Ateş", "Su", "Hava", "Toprak", "Zihin", "Ruh", "Nekromansi", "Işık", "Karanlık", "Diğer"].index(char.magic_type) if char.magic_type in ["Yok", "Ateş", "Su", "Hava", "Toprak", "Zihin", "Ruh", "Nekromansi", "Işık", "Karanlık", "Diğer"] else 0)

                    e_desc = st.text_area("Açıklama", char.description)
                    e_img = st.file_uploader("Yeni Görsel (Opsiyonel)", type=["png", "jpg"])
                    
                    if st.form_submit_button("Güncelle"):
                        char.name = e_name
                        char.title = e_title
                        char.gender = e_gender
                        char.country = e_country
                        char.has_magic = e_magic
                        char.magic_type = e_mtype
                        char.description = e_desc
                        
                        if e_img:
                             import base64
                             char.image_base64 = base64.b64encode(e_img.read()).decode()
                        
                        database_manager.upsert_character(char)
                        st.success("Güncellendi!")
                        st.rerun()

            if st.button("🗑️ Karakteri Sil", type="primary"):
                database_manager.delete_character_db(char.code)
                st.warning("Karakter silindi.")
                st.rerun()


def show_story():
    st.header("📖 Hikaye ve Bölümler")
    
    chapters = database_manager.load_chapters()
    
    # Sidebar: Chapter List & Management
    st.sidebar.subheader("Bölümler")
    
    if st.sidebar.button("➕ Yeni Bölüm Ekle"):
        new_id = f"S-{len(chapters)+1:02d}"
        new_chap = Chapter(id=new_id, title="Yeni Bölüm")
        database_manager.upsert_chapter(new_chap, len(chapters))
        st.success("Bölüm eklendi!")
        st.rerun()

    # Reorder functionality could be complex in Streamlit, skipping for now or simple "Move Up/Down" buttons next to selected chapter
    
    # Chapter Selection
    chap_options = [f"{c.id} - {c.title}" for c in chapters]
    
    if not chap_options:
        st.info("Henüz hiç bölüm yok. Yandaki butondan ekleyin.")
        return

    selected_chap_str = st.selectbox("Bölüm Seç", chap_options)
    selected_id = selected_chap_str.split(" - ")[0]
    
    chapter = next((c for c in chapters if c.id == selected_id), None)
    
    if chapter:
        # Edit Form
        with st.form("edit_chapter_form"):
            new_title = st.text_input("Bölüm Başlığı", chapter.title)
            
            # Toolbar helper
            st.markdown("ℹ️ *Metni biçimlendirmek için Markdown kullanabilirsiniz. (Örn: **Kalın**, *İtalik*)")
            
            new_content = st.text_area("Bölüm İçeriği", chapter.content, height=400)
            
            # Word Count
            import re
            words = len(re.findall(r'\w+', new_content)) if new_content else 0
            chars = len(new_content) if new_content else 0
            st.caption(f"📊 Kelime: {words} | Karakter: {chars}")
            
            c1, c2 = st.columns([1, 5])
            with c1:
                saved = st.form_submit_button("💾 Kaydet", type="primary")
            
            if saved:
                chapter.title = new_title
                chapter.content = new_content
                # Find current index
                idx = next((i for i, c in enumerate(chapters) if c.id == chapter.id), 0)
                database_manager.upsert_chapter(chapter, idx)
                st.success("Bölüm kaydedildi!")
                st.rerun()
        
        st.divider()
        if st.button("🗑️ Bu Bölümü Sil", type="primary"):
            database_manager.delete_chapter_db(chapter.id)
            st.warning("Bölüm silindi.")
            st.rerun()


def show_world():
    st.header("🌍 Dünya ve Ülkeler")
    
    countries = database_manager.load_countries()
    
    # Sidebar
    if st.sidebar.button("➕ Yeni Ülke Ekle"):
        nid = f"C-{len(countries)+1:02d}"
        nc = Country(id=nid, name="Yeni Ülke")
        database_manager.upsert_country(nc)
        st.rerun()
        
    country_opts = [f"{c.id} - {c.name}" for c in countries]
    
    if not country_opts:
        st.info("Henüz ülke yok.")
        return
        
    selected_c_str = st.selectbox("Ülke Seç", country_opts)
    selected_id = selected_c_str.split(" - ")[0]
    country = next((c for c in countries if c.id == selected_id), None)
    
    if country:
        st.subheader(country.name)
        
        tab1, tab2, tab3 = st.tabs(["Genel Bilgiler", "Yönetim & Politika", "Bayraklar"])
        
        with tab1:
            with st.form("c_gen_form"):
                new_name = st.text_input("Ülke Adı", country.name)
                geo = st.text_area("Coğrafya & İklim", country.geography_details, height=150)
                story = st.text_area("Ülke Hikayesi / Arkaplan", country.story, height=150)
                
                if st.form_submit_button("Genel Bilgileri Kaydet"):
                    country.name = new_name
                    country.geography_details = geo
                    country.story = story
                    database_manager.upsert_country(country)
                    st.success("Kaydedildi!")
                    st.rerun()

        with tab2:
            st.info("Yönetim birimleri şu an sadece masaüstü uygulamasında detaylı düzenlenebilir. Burada görüntülenir.")
            if country.government_details:
                for unit in country.government_details:
                    with st.expander(unit.name):
                        st.write(unit.details)
                        if unit.sub_units:
                            for sub in unit.sub_units:
                                st.markdown(f"- **{sub.name}**: {sub.details}")
            else:
                st.caption("Yönetim birimi tanımlanmamış.")

        with tab3:
            col_norm, col_war, col_aid = st.columns(3)
            
            def show_flag_uploader(label, attr_name):
                current_b64 = getattr(country, attr_name)
                if current_b64:
                    import base64
                    try:
                        st.image(base64.b64decode(current_b64), caption=label, use_container_width=True)
                    except: st.error("Görsel hatası")
                    
                    if st.button(f"🗑️ {label} Sil", key=f"del_{attr_name}"):
                        setattr(country, attr_name, "")
                        database_manager.upsert_country(country)
                        st.rerun()
                
                uploaded = st.file_uploader(f"{label} Yükle", type=["png", "jpg"], key=f"up_{attr_name}")
                if uploaded:
                    import base64
                    b64 = base64.b64encode(uploaded.read()).decode()
                    setattr(country, attr_name, b64)
                    database_manager.upsert_country(country)
                    st.rerun()

            with col_norm: show_flag_uploader("Normal Bayrak", "flag_normal")
            with col_war: show_flag_uploader("Savaş Bayrağı", "flag_war")
            with col_aid: show_flag_uploader("Yardım Bayrağı", "flag_aid")

        st.divider()
        if st.button("🗑️ Ülkeyi Sil", type="primary"):
            database_manager.delete_country_db(country.id)
            st.warning("Ülke silindi.")
            st.rerun()


def show_map_audio():
    st.header("🗺️ Harita ve 🎵 Ses")
    
    col_map, col_audio = st.columns([2, 1])
    
    with col_map:
        st.subheader("Dünya Haritası")
        # Load map from settings path OR upload new one
        last_map_path = database_manager.get_setting("last_map_path")
        
        # Check if local path exists (might not work on web if path is absolute local path)
        # For web, we should probably store map as base64 in DB or reliable relative path
        # But for now, let's allow upload to display
        
        map_file = st.file_uploader("Harita Görseli Yükle/Güncelle", type=["png", "jpg", "jpeg", "webp"])
        if map_file:
             st.image(map_file, use_container_width=True)
             # In a real web app, we'd save this file. 
             # For this local-web hybrid, we can just display it.
        elif last_map_path:
            import os
            if os.path.exists(last_map_path):
                st.image(last_map_path, caption="Mevcut Harita", use_container_width=True)
            else:
                st.warning(f"Kayıtlı harita dosyası bulunamadı: {last_map_path}")
    
    with col_audio:
        st.subheader("Müzik Çalar")
        import os
        sound_dir = os.path.join(os.path.dirname(__file__), "sounds")
        if not os.path.exists(sound_dir):
            os.makedirs(sound_dir)
            
        files = [f for f in os.listdir(sound_dir) if f.endswith(('.mp3', '.wav', '.ogg'))]
        
        if not files:
            st.info("Sounds klasöründe müzik dosyası yok.")
        else:
            selected_sound = st.selectbox("Parça Seç", files)
            st.audio(os.path.join(sound_dir, selected_sound))
            
        st.caption("Müzik dosyalarını 'sounds' klasörüne atabilirsiniz.")


def show_settings():
    st.header("⚙️ Ayarlar")
    st.write("Web sürümü için ayarlar şu anlık sınırlıdır.")
    
    st.subheader("Görünüm")
    st.info("Tema ayarları Streamlit'in kendi ayarlar menüsünden (sağ üst köşe) yapılmaktadır.")
    
    st.subheader("Veritabanı")
    if st.button("Veritabanı Bağlantısını Test Et"):
        try:
            conn = database_manager.get_connection()
            st.success("Bağlantı Başarılı!")
            conn.close()
        except Exception as e:
            st.error(f"Hata: {e}")


if __name__ == "__main__":
    main()
