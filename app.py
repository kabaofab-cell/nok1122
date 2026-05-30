import json

import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
from app_utils import (
    append_audit_log,
    check_required_secrets,
    deduplicate_dataframe,
    export_section_csv,
    get_imgbb_api_key,
    get_thai_date,
    log_error,
    normalize_book_record,
    parse_links,
    safe_image,
    safe_parse_date,
    upload_to_imgbb,
    validate_book_editor_df,
    validate_books_data,
    validate_calendar_data,
    validate_finance_editor_df,
)
from ui_components import render_app_style, render_hero, render_sidebar_brand
from ui_dashboard import render_dashboard
from ui_calendar import render_calendar_page
from ui_books import render_books_page
from ui_finance import render_finance_page
from ui_panels import daily_manager_dialog, render_audit_log_viewer, render_system_health_panel

# ==========================================
# 🔑 0. การตั้งค่าความลับ (Secrets & Settings)
# ==========================================
st.set_page_config(page_title="Nok-kaew Admin Pro", layout="wide", page_icon="💎")

# ==========================================
# 🎨 1. ตั้งค่าและดีไซน์ (Modern Soft UI & Smart Flex)
# ==========================================
if 'selected_book_idx' not in st.session_state: 
    st.session_state.selected_book_idx = None

render_app_style()


@st.cache_data(ttl=300, show_spinner=False)
def fetch_all_google_sheets():
    try:
        b_df = conn.read(worksheet="Books")
        f_df = conn.read(worksheet="Finance")
        c_df = conn.read(worksheet="Calendar")
        s_df = conn.read(worksheet="Settings")
        return b_df, f_df, c_df, s_df
    except Exception as e:
        log_error("โหลดข้อมูลจาก Google Sheets ไม่สำเร็จ", e)
        return None, None, None, None

def initialize_data():
    check_required_secrets()
    b_df, f_df, c_df, s_df = fetch_all_google_sheets()
    
    if b_df is None:
        st.error("🚨 ไม่สามารถเชื่อมต่อกับ Google Sheets ได้ กรุณาตรวจสอบชื่อแผ่นงานให้ถูกต้อง")
        st.stop()
        
    books = b_df.to_dict('records')
    for b in books:
        normalize_book_record(b)
    st.session_state.books_data = books

    st.session_state.finance_db = f_df if not f_df.empty else pd.DataFrame(columns=['วันที่', 'ชื่อเรื่อง', 'แพลตฟอร์ม', 'ยอดดิบ', 'หักแพลตฟอร์ม (17%)', 'ยอดสุทธิ'])
    st.session_state.finance_db = deduplicate_dataframe(st.session_state.finance_db, ['วันที่', 'ชื่อเรื่อง', 'แพลตฟอร์ม'])
    
    if not c_df.empty:
        st.session_state.calendar_db = c_df.dropna(how='all').dropna(subset=['วันที่', 'ชื่อเรื่อง']).reset_index(drop=True)
        st.session_state.calendar_db = deduplicate_dataframe(st.session_state.calendar_db, ['วันที่', 'ชื่อเรื่อง', 'ตอนที่'])
    else:
        st.session_state.calendar_db = pd.DataFrame(columns=['วันที่', 'ชื่อเรื่อง', 'ตอนที่'])

    if 'audit_log' not in st.session_state:
        st.session_state.audit_log = pd.DataFrame(columns=['เวลา', 'การกระทำ', 'รายละเอียด'])
    
    if not s_df.empty:
        st.session_state.app_settings = {"categories": s_df['categories'].dropna().tolist(), "platforms": s_df['platforms'].dropna().tolist()}
    else:
        st.session_state.app_settings = {"categories": ["นิยายรัก", "แฟนตาซี", "นิยายวาย (BL)", "ทั่วไป"], "platforms": ["ReadToon", "KAIREW", "Facebook", "Meb", "Dek-D"]}

if 'books_data' not in st.session_state:
    initialize_data()

# ==========================================
# 🚀 ระบบบันทึกข้อมูลความเร็วสูง (Targeted Save)
# ==========================================
def save_data(sheets_to_save):
    """ส่งข้อมูลเฉพาะแผ่นงานที่มีการอัปเดต เพื่อลดระยะเวลาการบันทึกข้อมูล"""
    try:
        if "Books" in sheets_to_save:
            is_valid, message = validate_books_data(st.session_state.get('books_data'))
            if not is_valid:
                st.error(f"🚨 ข้อมูลหนังสือเสียหาย: {message}")
                return
            books_to_save = []
            for b in st.session_state.books_data:
                temp = b.copy()
                if '_orig_idx' in temp: 
                    del temp['_orig_idx']
                temp['ลิงก์อ่าน'] = json.dumps(b.get('ลิงก์อ่าน', []))
                temp['ลิงก์ต้นฉบับ'] = json.dumps(b.get('ลิงก์ต้นฉบับ', []))
                books_to_save.append(temp)
            df_save = pd.DataFrame(books_to_save)
            if df_save.empty: 
                df_save = pd.DataFrame(columns=['ชื่อเรื่อง', 'หมวดหมู่', 'QC', 'สถานะ', 'ตอนปัจจุบัน', 'เป้าหมาย', 'ภาพปก', 'เรื่องย่อ', 'หมายเหตุ', 'ลิงก์อ่าน', 'ลิงก์ต้นฉบับ'])
            conn.update(worksheet="Books", data=df_save)

        if "Finance" in sheets_to_save:
            st.session_state.finance_db = deduplicate_dataframe(st.session_state.finance_db, ['วันที่', 'ชื่อเรื่อง', 'แพลตฟอร์ม'])
            conn.update(worksheet="Finance", data=st.session_state.finance_db)

        if "Calendar" in sheets_to_save:
            df_cal = st.session_state.calendar_db.copy()
            is_valid_cal, cal_message = validate_calendar_data(df_cal)
            if not is_valid_cal:
                st.error(f"🚨 ข้อมูลปฏิทินเสียหาย: {cal_message}")
                return
            if not df_cal.empty:
                df_cal = df_cal.dropna(subset=['วันที่', 'ชื่อเรื่อง']).reset_index(drop=True)
                df_cal = deduplicate_dataframe(df_cal, ['วันที่', 'ชื่อเรื่อง', 'ตอนที่'])
            else:
                df_cal = pd.DataFrame(columns=['วันที่', 'ชื่อเรื่อง', 'ตอนที่'])
            conn.update(worksheet="Calendar", data=df_cal)

        if "Settings" in sheets_to_save:
            set_df = pd.DataFrame({"categories": pd.Series(st.session_state.app_settings['categories']), "platforms": pd.Series(st.session_state.app_settings['platforms'])})
            conn.update(worksheet="Settings", data=set_df)

        if "AuditLog" in sheets_to_save and 'audit_log' in st.session_state:
            conn.update(worksheet="AuditLog", data=st.session_state.audit_log)
            
        fetch_all_google_sheets.clear()
        st.toast(f"✅ บันทึกข้อมูลเรียบร้อยแล้ว!")
    except Exception as e: 
        log_error("Error saving", e)

# ==========================================
# 🌟 ระบบป๊อปอัปจัดการรายวัน (อุดช่องโหว่พิมพ์ค้างด้วย Form)
# ==========================================

# ==========================================
# 📱 3. ระบบนำทาง (Sidebar)
# ==========================================
render_sidebar_brand()

menu_options = [
    "📊 สรุปภาพรวม", 
    "📅 ปฏิทินคิวงาน", 
    "📚 จัดการนิยาย & ไฟล์", 
    "💰 บัญชี & ค่าตอบแทน", 
    "🧾 ประวัติการแก้ไข",
    "⚙️ ตั้งค่าระบบ"
]

if 'main_menu' not in st.session_state: 
    st.session_state.main_menu = "📊 สรุปภาพรวม"

menu = st.sidebar.radio("ระบบนำทาง", menu_options, key="main_menu")

if menu != "📚 จัดการนิยาย & ไฟล์": 
    st.session_state.selected_book_idx = None

# ------------------------------------------
# 📊 หน้า 1: สรุปภาพรวม (Dashboard)
# ------------------------------------------
if menu == "📊 สรุปภาพรวม":
    render_dashboard(fetch_all_google_sheets)

# ------------------------------------------
# 📅 หน้า 2: ปฏิทินคิวงาน (Smart Flex)
# ------------------------------------------
elif menu == "📅 ปฏิทินคิวงาน":
    render_calendar_page(get_thai_date, daily_manager_dialog, append_audit_log, deduplicate_dataframe, save_data)

# ------------------------------------------
# 📚 หน้า 3: จัดการนิยาย & ไฟล์
# ------------------------------------------
elif menu == "📚 จัดการนิยาย & ไฟล์":
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Library</div>
            <div class="hero-title">จัดการนิยาย & ไฟล์</div>
            <p class="hero-subtitle">เพิ่ม แก้ไข ลบ และอัปโหลดปกได้ในหน้าเดียว พร้อมโหมดแกลลอรี่และตารางเพื่อเลือกวิธีทำงานที่ถนัด</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.selected_book_idx is not None:
        idx = st.session_state.selected_book_idx
        b = st.session_state.books_data[idx]
        
        if st.button("🔙 กลับหน้าหลัก"): 
            st.session_state.selected_book_idx = None
            st.rerun()
            
        st.title(f"🛠️ แก้ไข: {b['ชื่อเรื่อง']}")
        st.markdown("---")
        
        c_img, c_form = st.columns([1, 3])
        with c_img: 
            safe_image(b.get('ภาพปก'))
            st.markdown("##### 📤 อัปโหลดปก")
            uploaded_file = st.file_uploader("เลือกรูปจากเครื่อง", type=["jpg", "jpeg", "png"])
            
            if uploaded_file and st.button("🚀 ยืนยันอัปโหลด", use_container_width=True):
                new_url = upload_to_imgbb(uploaded_file)
                if new_url: 
                    st.session_state.books_data[idx]['ภาพปก'] = new_url
                    append_audit_log('อัปโหลดปก', f"{b['ชื่อเรื่อง']}")
                    save_data(["Books", "AuditLog"]) # บันทึกเฉพาะนิยาย
                    st.rerun()
            
        with c_form:
            e_title = st.text_input("ชื่อเรื่อง", value=b['ชื่อเรื่อง'])
            
            c_f1, c_f2 = st.columns(2)
            e_cat = c_f1.selectbox("หมวดหมู่", st.session_state.app_settings['categories'], index=st.session_state.app_settings['categories'].index(b.get('หมวดหมู่','ทั่วไป')) if b.get('หมวดหมู่') in st.session_state.app_settings['categories'] else 0)
            e_stat = c_f2.selectbox("สถานะ", ["กำลังอัปเดต", "จบแล้ว", "พักการแปล"], index=["กำลังอัปเดต", "จบแล้ว", "พักการแปล"].index(b.get('สถานะ','กำลังอัปเดต')) if b.get('สถานะ') in ["กำลังอัปเดต", "จบแล้ว", "พักการแปล"] else 0)
            
            c_f3, c_f4, c_f5 = st.columns(3)
            e_qc = c_f3.radio("QC", ["ตอง", "ตาว"], index=["ตอง", "ตาว"].index(b.get('QC','ตอง')) if b.get('QC') in ["ตอง", "ตาว"] else 0, horizontal=True)
            e_tgt = c_f4.number_input("จำนวนตอนต้นฉบับ", value=int(b.get('เป้าหมาย',1)))
            e_curr = c_f5.number_input("แปลเสร็จแล้ว (ตอน)", value=int(b.get('ตอนปัจจุบัน',0)))
            
            e_cover = st.text_input("ลิงก์ภาพปก", value=b.get('ภาพปก',''))
            e_synopsis = st.text_area("📔 เรื่องย่อ", value=b.get('เรื่องย่อ',''), height=100)
            
            sv_col, del_col = st.columns(2)
            
            if sv_col.button("💾 บันทึกข้อมูลนิยาย", type="primary", use_container_width=True):
                st.session_state.books_data[idx].update({
                    'ชื่อเรื่อง': e_title, 'หมวดหมู่': e_cat, 'QC': e_qc, 'ภาพปก': e_cover,
                    'สถานะ': e_stat, 'ตอนปัจจุบัน': e_curr, 'เป้าหมาย': e_tgt, 'เรื่องย่อ': e_synopsis
                })
                append_audit_log('แก้ไขนิยาย', e_title)
                save_data(["Books", "AuditLog"]) # บันทึกเฉพาะนิยาย
                st.session_state.selected_book_idx = None
                st.rerun()
            
            st.markdown("<div class='btn-delete'>", unsafe_allow_html=True)
            if del_col.button("🗑️ ลบนิยายเรื่องนี้", use_container_width=True):
                deleted_title = st.session_state.books_data[idx].get('ชื่อเรื่อง', 'ไม่ทราบชื่อ')
                st.session_state.books_data.pop(idx)
                append_audit_log('ลบนิยาย', deleted_title)
                save_data(["Books", "AuditLog"]) # บันทึกเฉพาะนิยาย
                st.session_state.selected_book_idx = None
# ------------------------------------------
# ?? ???? 3: ??????????? & ????
# ------------------------------------------
elif menu == "?? ??????????? & ????":
    render_books_page(safe_image, upload_to_imgbb, append_audit_log, save_data, validate_book_editor_df)

# ------------------------------------------
# ?? ???? 4: ????? & ?????????
# ------------------------------------------
elif menu == "?? ????? & ?????????":
    render_finance_page(append_audit_log, save_data, validate_finance_editor_df)


# ------------------------------------------
# 🧾 หน้า 5: ประวัติการแก้ไข
# ------------------------------------------
elif menu == "🧾 ประวัติการแก้ไข":
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Audit</div>
            <div class="hero-title">ประวัติการแก้ไข</div>
            <p class="hero-subtitle">ดูว่ามีการเปลี่ยนแปลงอะไร เมื่อไหร่ และโดยใคร เพื่อให้ตามงานและตรวจสอบย้อนหลังได้ง่าย</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_audit_log_viewer()

# ------------------------------------------
# ⚙️ หน้า 6: ตั้งค่าระบบ
# ------------------------------------------
elif menu == "⚙️ ตั้งค่าระบบ":
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Settings</div>
            <div class="hero-title">ตั้งค่าระบบ</div>
            <p class="hero-subtitle">จัดการหมวดหมู่ แพลตฟอร์ม และสำรองข้อมูลได้จากหน้าเดียว</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.title("⚙️ ตั้งค่าหมวดหมู่และแพลตฟอร์ม")
    
    c1, c2 = st.columns(2)
    with c1: 
        st.subheader("📚 หมวดหมู่นิยาย")
        ed_c = st.data_editor(pd.DataFrame(st.session_state.app_settings['categories'], columns=['ชื่อหมวดหมู่']), num_rows="dynamic", use_container_width=True)
    with c2: 
        st.subheader("🌐 แพลตฟอร์มเผยแพร่")
        ed_p = st.data_editor(pd.DataFrame(st.session_state.app_settings['platforms'], columns=['ชื่อแพลตฟอร์ม']), num_rows="dynamic", use_container_width=True)
        
    st.markdown('---')
    st.subheader('📦 สำรองข้อมูล (Backup CSV)')
    e1, e2, e3 = st.columns(3)
    with e1:
        export_section_csv('Books', pd.DataFrame(st.session_state.books_data), 'books_backup.csv')
    with e2:
        export_section_csv('Finance', st.session_state.finance_db, 'finance_backup.csv')
    with e3:
        export_section_csv('Calendar', st.session_state.calendar_db, 'calendar_backup.csv')

    if st.button("💾 บันทึกการตั้งค่า", type="primary"):
        st.session_state.app_settings['categories'] = ed_c['ชื่อหมวดหมู่'].replace('', pd.NA).dropna().tolist()
        st.session_state.app_settings['platforms'] = ed_p['ชื่อแพลตฟอร์ม'].replace('', pd.NA).dropna().tolist()
        save_data(["Settings"]) # บันทึกเฉพาะการตั้งค่า
        st.rerun()
