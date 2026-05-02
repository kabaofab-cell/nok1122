import streamlit as st
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection
import json
import plotly.express as px
from datetime import datetime
import re
from streamlit_calendar import calendar

# ==========================================
# 🔑 0. Settings
# ==========================================
IMGBB_API_KEY = "c2632e406b68246bd02423be8f9bf384"
st.set_page_config(page_title="Nok-kaew Admin Pro", layout="wide", page_icon="💎")

# ==========================================
# 🎨 1. Styles
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, input, button { font-family: 'Kanit', sans-serif !important; }
    .stApp { background-color: #f7f9fc; }
    .metric-card { background: white; padding: 20px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); text-align: center; border: 1px solid #f0f4f8; }
    .metric-card h2 { color: #6C63FF; font-size: 2.2rem; font-weight: 700; }
    .rank-card { background: white; padding: 15px; border-radius: 16px; text-align: center; border: 1px solid #f0f0f0; margin-bottom: 20px; }
    .rank-img { width: 100%; aspect-ratio: 2/3; object-fit: cover; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 💾 2. Database Connection
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=300)
def load_all_data():
    try:
        books = conn.read(worksheet="Books", ttl=0).to_dict('records')
        finance = conn.read(worksheet="Finance", ttl=0)
        calendar_df = conn.read(worksheet="Calendar", ttl=0)
        # ล้างข้อมูลวันที่ที่เป็น NaT หรือ NaN
        calendar_df = calendar_df.dropna(subset=['วันที่'])
        return books, finance, calendar_df
    except:
        return [], pd.DataFrame(), pd.DataFrame(columns=['วันที่', 'ชื่อเรื่อง', 'ตอนที่'])

if 'books_data' not in st.session_state:
    st.session_state.books_data, st.session_state.finance_db, st.session_state.calendar_db = load_all_data()

def save_all():
    try:
        conn.update(worksheet="Books", data=pd.DataFrame(st.session_state.books_data))
        conn.update(worksheet="Finance", data=st.session_state.finance_db)
        conn.update(worksheet="Calendar", data=st.session_state.calendar_db)
        st.cache_data.clear()
        st.toast("✅ บันทึกข้อมูลเรียบร้อย!")
    except Exception as e:
        st.error(f"Error: {e}")

# ==========================================
# 🌟 Dialogs (Popups)
# ==========================================
@st.dialog("📌 บันทึกคิวงาน")
def add_event_dialog(date_str):
    st.write(f"**วันที่เลือก:** {date_str}")
    novels = [b['ชื่อเรื่อง'] for b in st.session_state.books_data]
    sel = st.selectbox("เลือกนิยาย", novels if novels else ["ไม่มีข้อมูล"])
    chap = st.text_input("ระบุตอน (เช่น 1-10)")
    
    if st.button("💾 บันทึกข้อมูล", type="primary", use_container_width=True):
        new_row = pd.DataFrame([{'วันที่': date_str, 'ชื่อเรื่อง': sel, 'ตอนที่': chap}])
        st.session_state.calendar_db = pd.concat([st.session_state.calendar_db, new_row], ignore_index=True)
        save_all()
        st.rerun()

@st.dialog("🛠️ แก้ไขคิวงาน")
def edit_event_dialog(idx, date_str, novel, chap):
    st.write(f"**วันที่:** {date_str}")
    novels = [b['ชื่อเรื่อง'] for b in st.session_state.books_data]
    new_sel = st.selectbox("ชื่อเรื่อง", novels, index=novels.index(novel) if novel in novels else 0)
    new_chap = st.text_input("ระบุตอน", value=chap)
    
    c1, c2 = st.columns(2)
    if c1.button("💾 แก้ไข", type="primary", use_container_width=True):
        st.session_state.calendar_db.at[idx, 'ชื่อเรื่อง'] = new_sel
        st.session_state.calendar_db.at[idx, 'ตอนที่'] = new_chap
        save_all()
        st.rerun()
    if c2.button("🗑️ ลบ", use_container_width=True):
        st.session_state.calendar_db = st.session_state.calendar_db.drop(idx).reset_index(drop=True)
        save_all()
        st.rerun()

# ==========================================
# 📱 Navigation
# ==========================================
menu = st.sidebar.radio("เมนู", ["📊 สรุปภาพรวม", "📅 ปฏิทินคิวงาน", "📚 จัดการนิยาย"])

if menu == "📅 ปฏิทินคิวงาน":
    st.title("📅 ปฏิทินจัดคิวลงนิยาย")
    
    # 🌈 เตรียมข้อมูล Events
    evs = []
    unique_novels = [b['ชื่อเรื่อง'] for b in st.session_state.books_data]
    colors = ["#FF6C6C", "#6C9DFF", "#6CFF8A", "#FFC86C", "#D16CFF"]
    c_map = {n: colors[i % len(colors)] for i, n in enumerate(unique_novels)}

    for i, row in st.session_state.calendar_db.iterrows():
        evs.append({
            "id": str(i),
            "title": f"{row['ตอนที่']} {row['ชื่อเรื่อง']}",
            "start": str(row['วันที่']),
            "color": c_map.get(row['ชื่อเรื่อง'], "#6C63FF"),
            "extendedProps": {"novel": row['ชื่อเรื่อง'], "chap": row['ตอนที่']}
        })

    # 🚀 แก้ไขจุดคลิกวันที่ (ตัด Timezone ทิ้ง 100%)
    cal_state = calendar(options={"headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"}, "selectable": True, "events": evs}, key="novel_calendar")

    if cal_state:
        if cal_state.get("callback") == "dateClick":
            # ใช้การหั่นสตริง 10 ตัวแรกเท่านั้น (YYYY-MM-DD) เพื่อกันวันถอยหลัง
            target_date = cal_state["dateClick"]["date"][:10]
            add_event_dialog(target_date)
            
        elif cal_state.get("callback") == "eventClick":
            eid = int(cal_state["eventClick"]["event"]["id"])
            edate = cal_state["eventClick"]["event"]["start"][:10]
            enovel = cal_state["eventClick"]["event"]["extendedProps"]["novel"]
            echap = cal_state["eventClick"]["event"]["extendedProps"]["chap"]
            edit_event_dialog(eid, edate, enovel, echap)

    st.markdown("---")
    st.write("**ตารางจัดการด่วน**")
    new_df = st.data_editor(st.session_state.calendar_db, num_rows="dynamic", use_container_width=True)
    if st.button("💾 บันทึกการแก้ไขตาราง"):
        st.session_state.calendar_db = new_df
        save_all()
        st.rerun()

elif menu == "📊 สรุปภาพรวม":
    st.title("📊 สรุปภาพรวม")
    st.write("ยินดีต้อนรับ! เลือกเมนูปฏิทินเพื่อเริ่มจัดคิวงาน")

elif menu == "📚 จัดการนิยาย":
    st.title("📚 รายชื่อนิยาย")
    st.write("แก้ไขรายชื่อนิยายที่นี่เพื่อให้ระบบปฏิทินดึงไปใช้งาน")
    # โค้ดส่วนจัดการนิยายเดิมของคุณ
