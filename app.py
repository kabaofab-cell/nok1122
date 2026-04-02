import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import json
import plotly.express as px
from datetime import datetime

# ==========================================
# 🎨 1. ตั้งค่าและดีไซน์ (Premium UI)
# ==========================================
st.set_page_config(page_title="Nok-kaew Admin Pro", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; background-color: #F8F9FA; }
    .book-card { background: white; border-radius: 20px; padding: 25px; margin-bottom: 25px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); border-left: 8px solid #6C63FF; }
    .link-badge { display: inline-block; background: #6C63FF; color: white !important; padding: 5px 15px; border-radius: 20px; text-decoration: none; font-size: 14px; margin-right: 10px; margin-bottom: 10px; transition: 0.3s; }
    .link-badge-orig { background: #FF6584; }
    .btn-revenue { background-color: #28a745 !important; color: white !important; border-radius: 10px; padding: 5px 15px; border: none; font-size: 14px; }
    .btn-delete>div>button { background: #FF4B4B !important; color: white !important; }
    .metric-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center; margin-bottom: 15px; }
    .synopsis-box { background: #F1F3F4; padding: 15px; border-radius: 10px; font-size: 14px; color: #555; margin-top: 10px; border-left: 4px solid #CCC; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 💾 2. ระบบฐานข้อมูล Google Sheets
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

def safe_update(sheet_name, df):
    try:
        conn.update(worksheet=sheet_name, data=df)
    except Exception as e:
        if "200" in str(e): pass
        else: st.error(f"Error {sheet_name}: {e}")

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
            b['สถานะ'] = b.get('สถานะ', 'กำลังอัปเดต')
            b['หมายเหตุ'] = b.get('หมายเหตุ', '')
            b['เรื่องย่อ'] = b.get('เรื่องย่อ', '') # โหลดเรื่องย่อ
        st.session_state.books_data = books
    except:
        st.session_state.books_data = []

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
        st.session_state.app_settings = {"categories": ["นิยายรัก", "แฟนตาซี", "นิยายวาย (BL)", "ทั่วไป"], "platforms": ["Meb", "ReadAWrite", "Dek-D"]}

def save_all_to_sheets():
    books_to_save = []
    for b in st.session_state.books_data:
        temp = b.copy()
        if '_orig_idx' in temp: del temp['_orig_idx']
        temp['ลิงก์อ่าน'] = json.dumps(b.get('ลิงก์อ่าน', []))
        temp['ลิงก์ต้นฉบับ'] = json.dumps(b.get('ลิงก์ต้นฉบับ', []))
        books_to_save.append(temp)
    
    df_books_save = pd.DataFrame(books_to_save)
    safe_update("Books", df_books_save)
    safe_update("Finance", st.session_state.finance_db)
    
    settings_df = pd.DataFrame({
        "categories": pd.Series(st.session_state.app_settings['categories']),
        "platforms": pd.Series(st.session_state.app_settings['platforms'])
    })
    safe_update("Settings", settings_df)
    st.toast("✅ บันทึกข้อมูลสำเร็จ!")

if 'books_data' not in st.session_state: load_data()

# ==========================================
# 📱 3. ระบบนำทาง (Sidebar)
# ==========================================
menu = st.sidebar.radio("เมนูหลัก", ["📊 Dashboard", "📚 คลังนิยาย", "💰 บัญชีรายรับ", "💰 แบ่งรายได้ (QC)", "⚙️ ตั้งค่าระบบ"])

# ------------------------------------------
# หน้า: คลังนิยาย (เพิ่มเรื่องย่อ + ปุ่มรายได้)
# ------------------------------------------
if menu == "📚 คลังนิยาย":
    st.title("📚 จัดการคลังนิยาย")
    
    # เพิ่มเรื่องใหม่
    with st.expander("✨ เพิ่มนิยายเรื่องใหม่"):
        with st.form("add_book_form"):
            c1, c2 = st.columns(2)
            new_title = c1.text_input("ชื่อเรื่องนิยาย")
            new_cat = c1.selectbox("หมวดหมู่", st.session_state.app_settings['categories'])
            new_cover = c2.text_input("ลิงก์รูปปก")
            new_qc = c2.radio("ผู้ดูแล (QC)", ["ตอง", "ตาว"], horizontal=True)
            new_synopsis = st.text_area("📔 เรื่องย่อ")
            
            if st.form_submit_button("บันทึก"):
                if new_title:
                    st.session_state.books_data.append({
                        'ชื่อเรื่อง': new_title, 'หมวดหมู่': new_cat, 'QC': new_qc, 'สถานะ': 'กำลังอัปเดต', 
                        'ตอนปัจจุบัน': 0, 'เป้าหมาย': 150, 'ภาพปก': new_cover, 'หมายเหตุ': '', 
                        'เรื่องย่อ': new_synopsis, 'ลิงก์อ่าน': [], 'ลิงก์ต้นฉบับ': []
                    })
                    save_all_to_sheets(); st.rerun()

    st.markdown("---")
    
    # ส่วนแสดงผลบัตรนิยาย
    for idx, b in enumerate(st.session_state.books_data):
        st.markdown("<div class='book-card'>", unsafe_allow_html=True)
        img_col, txt_col = st.columns([1, 4])
        
        with img_col:
            if b.get('ภาพปก'): st.image(b['ภาพปก'], use_container_width=True)
            else: st.info("ไม่มีรูปปก")
            
        with txt_col:
            h_col1, h_col2, h_col3 = st.columns([3, 1, 1])
            h_col1.markdown(f"### {b['ชื่อเรื่อง']}")
            
            # ปุ่มแสดงรายได้เฉพาะเรื่อง
            if h_col2.button("💰 ดูยอดขาย", key=f"rev_btn_{idx}"):
                st.session_state[f"show_rev_{idx}"] = not st.session_state.get(f"show_rev_{idx}", False)
            
            if h_col3.button("🛠️ แก้ไข", key=f"edit_btn_{idx}"):
                st.session_state[f"show_edit_{idx}"] = not st.session_state.get(f"show_edit_{idx}", False)

            st.write(f"**หมวดหมู่:** {b['หมวดหมู่']} | **QC:** {b.get('QC','-')} | **สถานะ:** {b.get('สถานะ', 'กำลังอัปเดต')}")
            
            # แสดงเรื่องย่อ
            if b.get('เรื่องย่อ'):
                st.markdown(f"<div class='synopsis-box'><b>เรื่องย่อ:</b><br>{b['เรื่องย่อ']}</div>", unsafe_allow_html=True)

            st.progress(min(int(b.get('ตอนปัจจุบัน',0)/max(b.get('เป้าหมาย',1),1)*100), 100))
            st.caption(f"ตอนที่: {b.get('ตอนปัจจุบัน',0)} / {b.get('เป้าหมาย',150)}")

        # --- ส่วนแสดงยอดขายเฉพาะเรื่อง (Popup/Expand) ---
        if st.session_state.get(f"show_rev_{idx}", False):
            st.markdown("#### 💵 สรุปยอดขายเรื่องนี้")
            df_f = st.session_state.finance_db
            df_this_book = df_f[df_f['ชื่อเรื่อง'] == b['ชื่อเรื่อง']]
            if not df_this_book.empty:
                df_this_book['ยอดสุทธิ'] = pd.to_numeric(df_this_book['ยอดสุทธิ'])
                total_b = df_this_book['ยอดสุทธิ'].sum()
                st.success(f"💰 **รายได้สุทธิรวมจากเรื่องนี้:** ฿{total_b:,.2f}")
                st.dataframe(df_this_book[['วันที่', 'แพลตฟอร์ม', 'ยอดสุทธิ']], use_container_width=True)
            else:
                st.warning("ยังไม่มีการบันทึกรายได้ของเรื่องนี้ครับ")

        # --- ส่วนแก้ไขข้อมูล ---
        if st.session_state.get(f"show_edit_{idx}", False):
            st.markdown("---")
            e1, e2 = st.columns(2)
            e_title = e1.text_input("ชื่อเรื่อง", value=b['ชื่อเรื่อง'], key=f"t_{idx}")
            e_synopsis = st.text_area("📔 เรื่องย่อ", value=b.get('เรื่องย่อ',''), key=f"syn_{idx}")
            e_curr = e2.number_input("ตอนปัจจุบัน", value=int(b.get('ตอนปัจจุบัน',0)), key=f"curr_{idx}")
            e_note = st.text_area("หมายเหตุ", value=b.get('หมายเหตุ',''), key=f"n_{idx}")
            
            if st.button("💾 บันทึกการแก้ไข", key=f"save_{idx}"):
                st.session_state.books_data[idx].update({'ชื่อเรื่อง': e_title, 'เรื่องย่อ': e_synopsis, 'ตอนปัจจุบัน': e_curr, 'หมายเหตุ': e_note})
                st.session_state[f"show_edit_{idx}"] = False
                save_all_to_sheets(); st.rerun()
            
            if st.button("🗑️ ลบ", key=f"del_{idx}"):
                st.session_state.books_data.pop(idx); save_all_to_sheets(); st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)

# (ส่วนเมนูอื่นๆ Dashboard, บัญชีรายรับ, แบ่งรายได้ คงเดิมจากเวอร์ชันที่แล้วเพื่อความสมบูรณ์)
elif menu == "📊 Dashboard":
    st.title("📊 Dashboard")
    # ... ก๊อปปี้ส่วน Dashboard จากโค้ดก่อนหน้ามาวาง ...
    st.info("หน้านี้แสดงภาพรวมสถิตินิยายและรายได้ทั้งหมดครับ")

elif menu == "💰 บัญชีรายรับ":
    st.title("💰 บัญชีรายรับ")
    # ... ก๊อปปี้ส่วน บัญชีรายรับ จากโค้ดก่อนหน้ามาวาง ...

elif menu == "💰 แบ่งรายได้ (QC)":
    st.title("💰 ระบบสรุปส่วนแบ่งรายได้ (QC)")
    # ... ก๊อปปี้ส่วน แบ่งรายได้ จากโค้ดก่อนหน้ามาวาง ...

elif menu == "⚙️ ตั้งค่าระบบ":
    st.title("⚙️ ตั้งค่าระบบ")
    # ... ก๊อปปี้ส่วน ตั้งค่าระบบ จากโค้ดก่อนหน้ามาวาง ...
