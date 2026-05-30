import json

import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from app_utils import (
    append_audit_log,
    check_required_secrets,
    deduplicate_dataframe,
    get_thai_date,
    log_error,
    normalize_book_record,
    safe_image,
    validate_book_editor_df,
    validate_books_data,
    validate_calendar_data,
    validate_finance_editor_df,
)
from ui_components import render_app_style, render_sidebar_brand
from ui_dashboard import render_dashboard
from ui_calendar import render_calendar_page
from ui_books import render_books_page
from ui_finance import render_finance_page
from ui_audit import render_audit_page
from ui_settings import render_settings_page
from ui_panels import daily_manager_dialog

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
    render_books_page(safe_image, upload_to_imgbb, append_audit_log, save_data, validate_book_editor_df)

# ------------------------------------------
# 💰 หน้า 4: บัญชี & ค่าตอบแทน
# ------------------------------------------
elif menu == "💰 บัญชี & ค่าตอบแทน":
    render_finance_page(append_audit_log, save_data, validate_finance_editor_df)

# ------------------------------------------
# 🧾 หน้า 5: ประวัติการแก้ไข
# ------------------------------------------
elif menu == "🧾 ประวัติการแก้ไข":
    render_audit_page()

# ------------------------------------------
# ⚙️ หน้า 6: ตั้งค่าระบบ
# ------------------------------------------
elif menu == "⚙️ ตั้งค่าระบบ":
    render_settings_page(save_data)

