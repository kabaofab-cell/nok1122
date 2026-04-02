import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import json
import plotly.express as px
from datetime import datetime

# ==========================================
# 🎨 1. ดีไซน์พรีเมียม (Modern UI)
# ==========================================
st.set_page_config(page_title="Nok-kaew Admin Pro", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; background-color: #F8F9FA; }
    .stButton>button { border-radius: 12px; font-weight: 600; }
    .book-card { background: white; border-radius: 20px; padding: 25px; margin-bottom: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); border-left: 8px solid #6C63FF; }
    .link-badge { display: inline-block; background: #6C63FF; color: white !important; padding: 5px 15px; border-radius: 20px; text-decoration: none; font-size: 14px; margin-right: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 💾 2. ระบบเชื่อมต่อ Google Sheets
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df_books = conn.read(worksheet="Books", ttl=0)
        books = df_books.to_dict('records')
        for b in books:
            if isinstance(b.get('ลิงก์อ่าน'), str):
                try: b['ลิงก์อ่าน'] = json.loads(b['ลิงก์อ่าน'])
                except: b['ลิงก์อ่าน'] = []
            if isinstance(b.get('ลิงก์ต้นฉบับ'), str):
                try: b['ลิงก์ต้นฉบับ'] = json.loads(b['ลิงก์ต้นฉบับ'])
                except: b['ลิงก์ต้นฉบับ'] = []
        st.session_state.books_data = books
    except: st.session_state.books_data = []

    try:
        st.session_state.finance_db = conn.read(worksheet="Finance", ttl=0)
    except:
        st.session_state.finance_db = pd.DataFrame(columns=['วันที่', 'ชื่อเรื่อง', 'แพลตฟอร์ม', 'ยอดดิบ', 'หักแพลตฟอร์ม (17%)', 'ยอดสุทธิ'])

    try:
        df_settings = conn.read(worksheet="Settings", ttl=0)
        st.session_state.app_settings = {
            "categories": df_settings['categories'].dropna().tolist(),
            "platforms": df_settings['platforms'].dropna().tolist()
        }
    except:
        st.session_state.app_settings = {"categories": ["นิยายรัก", "แฟนตาซี", "นิยายวาย (BL)"], "platforms": ["Meb", "ReadAWrite"]}

def save_all_to_sheets():
    # แก้ไขชื่อตัวแปรให้ถูกต้องตรงกัน
    books_to_save = []
    for b in st.session_state.books_data:
        temp = b.copy()
        temp['ลิงก์อ่าน'] = json.dumps(b.get('ลิงก์อ่าน', []))
        temp['ลิงก์ต้นฉบับ'] = json.dumps(b.get('ลิงก์ต้นฉบับ', []))
        books_to_save.append(temp)
    
    # อัปเดตชีตต่างๆ
    if books_to_save:
        conn.update(worksheet="Books", data=pd.DataFrame(books_to_save))
    
    conn.update(worksheet="Finance", data=st.session_state.finance_db)
    
    settings_df = pd.DataFrame({
        "categories": pd.Series(st.session_state.app_settings['categories']),
        "platforms": pd.Series(st.session_state.app_settings['platforms'])
    })
    conn.update(worksheet="Settings", data=settings_df)
    st.toast("✅ ข้อมูลซิงค์กับ Google Sheets แล้ว!")

if 'books_data' not in st.session_state:
    load_data()

# ==========================================
# 📱 3. UI
# ==========================================
st.sidebar.title("💎 Nok-kaew Admin")
menu = st.sidebar.radio("เมนูหลัก", ["📊 Dashboard", "📚 คลังนิยาย", "💰 บัญชีรายรับ", "⚙️ ตั้งค่าระบบ"])

if menu == "📚 คลังนิยาย":
    st.title("📚 จัดการคลังนิยาย")
    
    if st.button("🔄 ดึงข้อมูลล่าสุดจาก Sheets"):
        load_data()
        st.rerun()

    with st.expander("✨ เพิ่มนิยายใหม่"):
        with st.form("add_form"):
            new_t = st.text_input("ชื่อเรื่อง")
            new_g = st.selectbox("หมวดหมู่", st.session_state.app_settings['categories'])
            new_q = st.radio("QC", ["ตอง", "ตาว"], horizontal=True)
            if st.form_submit_button("บันทึก"):
                if new_t:
                    new_b = {'ชื่อเรื่อง': new_t, 'หมวดหมู่': new_g, 'QC': new_q, 'สถานะ': 'กำลังอัปเดต', 'ตอนปัจจุบัน': 0, 'เป้าหมาย': 150, 'ลิงก์อ่าน': [], 'ลิงก์ต้นฉบับ': [], 'หมายเหตุ': '', 'ภาพปก': ''}
                    st.session_state.books_data.append(new_b)
                    save_all_to_sheets()
                    st.rerun()

    for idx, book in enumerate(st.session_state.books_data):
        st.markdown(f"""<div class="book-card">
            <h3>{book['ชื่อเรื่อง']}</h3>
            <p>หมวดหมู่: {book['หมวดหมู่']} | QC: {book['QC']} | สถานะ: {book['สถานะ']}</p>
        </div>""", unsafe_allow_html=True)
        
        c1, c2 = st.columns([1, 5])
        if c1.button("🗑️ ลบ", key=f"del_{idx}"):
            st.session_state.books_data.pop(idx)
            save_all_to_sheets()
            st.rerun()
