import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import json
import plotly.express as px
from datetime import datetime

# ==========================================
# 🎨 1. ตั้งค่าหน้าตาโปรแกรม (Premium UI)
# ==========================================
st.set_page_config(page_title="Nok-kaew Admin Pro", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }
    .stButton>button { border-radius: 10px; width: 100%; }
    .book-card { background: white; border-radius: 15px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #6C63FF; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 💾 2. ระบบเชื่อมต่อ Google Sheets (หัวใจหลัก)
# ==========================================
# สร้างการเชื่อมต่อ
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # โหลดข้อมูลนิยาย
    try:
        df_books = conn.read(worksheet="Books", ttl=0)
        books = df_books.to_dict('records')
        for b in books:
            # แปลงลิงก์จากข้อความกลับเป็นรายการ (List)
            if isinstance(b.get('ลิงก์อ่าน'), str): 
                try: b['ลิงก์อ่าน'] = json.loads(b['ลิงก์อ่าน'])
                except: b['ลิงก์อ่าน'] = []
            if isinstance(b.get('ลิงก์ต้นฉบับ'), str):
                try: b['ลิงก์ต้นฉบับ'] = json.loads(b['ลิงก์ต้นฉบับ'])
                except: b['ลิงก์ต้นฉบับ'] = []
        st.session_state.books_data = books
    except:
        st.session_state.books_data = []

    # โหลดข้อมูลบัญชี
    try:
        st.session_state.finance_db = conn.read(worksheet="Finance", ttl=0)
    except:
        st.session_state.finance_db = pd.DataFrame(columns=['วันที่', 'ชื่อเรื่อง', 'แพลตฟอร์ม', 'ยอดดิบ', 'หักแพลตฟอร์ม (17%)', 'ยอดสุทธิ'])

    # โหลดการตั้งค่า
    try:
        df_settings = conn.read(worksheet="Settings", ttl=0)
        st.session_state.app_settings = {
            "categories": df_settings['categories'].dropna().tolist(),
            "platforms": df_settings['platforms'].dropna().tolist()
        }
    except:
        st.session_state.app_settings = {"categories": ["นิยายรัก", "แฟนตาซี", "นิยายวาย (BL)"], "platforms": ["Meb", "ReadAWrite"]}

def save_all_to_sheets():
    # เตรียมข้อมูลนิยาย (แปลง List เป็น JSON String ก่อนเซฟลง Sheets)
    books_to_save = []
    for b in st.session_state.books_data:
        temp = b.copy()
        temp['ลิงก์อ่าน'] = json.dumps(b.get('ลิงก์อ่าน', []))
        temp['ลิงก์ต้นฉบับ'] = json.dumps(b.get('ลิงก์ต้นฉบับ', []))
        books_to_save.append(temp)
    
    # อัปเดตข้อมูลทั้ง 3 ชีต
    conn.update(worksheet="Books", data=pd.DataFrame(save_ready_books))
    conn.update(worksheet="Finance", data=st.session_state.finance_db)
    
    # อัปเดตการตั้งค่า
    settings_df = pd.DataFrame({
        "categories": pd.Series(st.session_state.app_settings['categories']),
        "platforms": pd.Series(st.session_state.app_settings['platforms'])
    })
    conn.update(worksheet="Settings", data=settings_df)
    st.toast("✅ บันทึกข้อมูลลง Google Sheets สำเร็จ!")

# โหลดข้อมูลเมื่อเปิดแอปครั้งแรก
if 'books_data' not in st.session_state:
    load_data()

# ==========================================
# 📱 3. ส่วนหน้าจอใช้งาน (UI)
# ==========================================
st.sidebar.title("💎 Nok-kaew Admin")
menu = st.sidebar.radio("เมนูหลัก", ["📊 Dashboard", "📚 คลังนิยาย", "💰 บัญชีรายรับ", "⚙️ ตั้งค่าระบบ"])

if menu == "📚 คลังนิยาย":
    st.title("📚 จัดการคลังนิยาย")
    
    col_btn1, col_btn2 = st.columns([1, 4])
    if col_btn1.button("🔄 รีเฟรชข้อมูล"):
        load_data()
        st.rerun()

    # ส่วนเพิ่มนิยายใหม่
    with st.expander("✨ เพิ่มนิยายเรื่องใหม่"):
        with st.form("add_book_form"):
            new_title = st.text_input("ชื่อเรื่องนิยาย")
            new_cat = st.selectbox("หมวดหมู่", st.session_state.app_settings['categories'])
            new_qc = st.radio("ผู้ดูแล (QC)", ["ตอง", "ตาว"], horizontal=True)
            if st.form_submit_button("บันทึกนิยาย"):
                if new_title:
                    new_entry = {
                        'ชื่อเรื่อง': new_title, 'หมวดหมู่': new_cat, 'QC': new_qc,
                        'สถานะ': 'กำลังอัปเดต', 'ตอนปัจจุบัน': 0, 'เป้าหมาย': 150,
                        'ลิงก์อ่าน': [], 'ลิงก์ต้นฉบับ': [], 'หมายเหตุ': ''
                    }
                    st.session_state.books_data.append(new_entry)
                    save_all_to_sheets()
                    st.rerun()

    # แสดงรายการนิยาย
    for idx, book in enumerate(st.session_state.books_data):
        st.markdown(f"""<div class="book-card">
            <h3>{book['ชื่อเรื่อง']}</h3>
            <p>หมวดหมู่: {book['หมวดหมู่']} | QC: {book['QC']}</p>
        </div>""", unsafe_allow_html=True)
        
        # ปุ่มแก้ไข/ลบ
        c1, c2 = st.columns([1, 5])
        if c1.button("🗑️ ลบ", key=f"del_{idx}"):
            st.session_state.books_data.pop(idx)
            save_all_to_sheets()
            st.rerun()

# (หมายเหตุ: ส่วน Dashboard และ บัญชีรายรับ พี่สามารถนำโค้ดเดิมมาใส่ต่อท้ายได้เลยครับ)
st.sidebar.markdown("---")
st.sidebar.write(f"ผู้ใช้งาน: พี่นกแก้ว")
