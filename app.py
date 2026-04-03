import streamlit as st
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection
import json
import plotly.express as px
from datetime import datetime

# ==========================================
# 🔑 0. การตั้งค่าความลับ (Secrets & Settings)
# ==========================================
IMGBB_API_KEY = "c2632e406b68246bd02423be8f9bf384"
ADMIN_PASSWORD = "nokkaew2026" # <-- เปลี่ยนรหัสผ่านตรงนี้ได้เลยครับ

st.set_page_config(page_title="Nok-kaew Admin", layout="wide", page_icon="💎")

# --- ระบบ Login ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center; color:#6C63FF; margin-top:100px;'>💎 Nok-kaew Admin Login</h1>", unsafe_allow_html=True)
    c_l, c_m, c_r = st.columns([1,2,1])
    with c_m:
        pwd = st.text_input("กรุณาใส่รหัสผ่านเพื่อเข้าใช้งาน", type="password")
        if st.button("เข้าสู่ระบบ", use_container_width=True, type="primary"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.auth = True; st.rerun()
            else: st.error("❌ รหัสผ่านไม่ถูกต้องค๊า!")
    st.stop()

# ==========================================
# 🎨 1. ตั้งค่าดีไซน์ & แก้บั๊ก Sidebar Font
# ==========================================
if 'selected_book_idx' not in st.session_state: st.session_state.selected_book_idx = None
if 'selected_promo_idx' not in st.session_state: st.session_state.selected_promo_idx = None

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"], .stMarkdown, p, label, input, button { font-family: 'Prompt', sans-serif !important; }
    
    /* แก้บั๊กฟอนต์ Sidebar ให้เห็นชัดทั้งโหมดมืด/สว่าง */
    [data-testid="stSidebar"] { box-shadow: 4px 0 15px rgba(0,0,0,0.05); }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: #1e293b !important; font-weight: 500; }
    @media (prefers-color-scheme: dark) {
        [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: #f8fafc !important; font-weight: 500; }
    }
    
    div[role="radiogroup"] > label { padding: 10px 20px; background: transparent; border-radius: 12px; transition: 0.3s; margin-bottom: 5px; cursor: pointer; }
    div[role="radiogroup"] > label:hover { transform: translateX(5px); background: rgba(108, 99, 255, 0.1); }

    .stButton > button { border-radius: 25px; border: none; background: linear-gradient(135deg, #6C63FF 0%, #8A84FF 100%); color: white; font-weight: 500; transition: 0.3s; }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(108, 99, 255, 0.35); color: white; }
    
    .metric-card { background: white; padding: 25px 20px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); text-align: center; margin-bottom: 20px; border: 1px solid #f0f4f8; }
    @media (prefers-color-scheme: dark) { .metric-card { background: #1e293b; border-color: #334155; } }
    .metric-card h2 { color: #6C63FF; font-size: 2.2rem; font-weight: 700; margin-top: 10px; }
    
    .rank-card { background: white; padding: 12px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align: center; border: 1px solid #f0f0f0; margin-bottom: 15px; }
    @media (prefers-color-scheme: dark) { .rank-card { background: #1e293b; border-color: #334155; } }
    .rank-img { width: 100%; aspect-ratio: 2/3; object-fit: cover; border-radius: 8px; margin-bottom: 10px; }
    
    .btn-delete>div>button { background: linear-gradient(135deg, #FF4B4B 0%, #ff7676 100%) !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 💾 2. ระบบฐานข้อมูล & ฟังก์ชันอัปโหลด
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

def upload_to_imgbb(file):
    with st.spinner("กำลังอัปโหลดรูปภาพไปยัง ImgBB..."):
        try:
            res = requests.post("https://api.imgbb.com/1/upload", data={"key": IMGBB_API_KEY}, files={"image": file.getvalue()})
            if res.status_code == 200: return res.json()["data"]["url"]
            else: st.error("เกิดข้อผิดพลาดจาก ImgBB"); return None
        except Exception as e: st.error(f"Upload Failed: {e}"); return None

@st.cache_data(ttl=300)
def load_admin_data():
    try:
        df_b = conn.read(worksheet="Books", ttl=0)
        books = df_b.to_dict('records')
        for b in books:
            b['ลิงก์อ่าน'] = json.loads(b['ลิงก์อ่าน']) if isinstance(b.get('ลิงก์อ่าน'), str) else []
            b['ลิงก์ต้นฉบับ'] = json.loads(b['ลิงก์ต้นฉบับ']) if isinstance(b.get('ลิงก์ต้นฉบับ'), str) else []
            b['สถานะ'] = b.get('สถานะ', 'กำลังอัปเดต')
            b['หมวดหมู่'] = b.get('หมวดหมู่', 'ทั่วไป')
            b['QC'] = b.get('QC', 'ตอง')
            b['ตอนปัจจุบัน'] = int(b.get('ตอนปัจจุบัน', 0)) if pd.notna(b.get('ตอนปัจจุบัน')) else 0
            b['เป้าหมาย'] = int(b.get('เป้าหมาย', 1)) if pd.notna(b.get('เป้าหมาย')) else 1
            b['เรื่องย่อ'] = str(b.get('เรื่องย่อ', '')) if pd.notna(b.get('เรื่องย่อ')) else ''
            b['ภาพปก'] = str(b.get('ภาพปก', '')) if pd.notna(b.get('ภาพปก')) else ''
        return books
    except: return []

@st.cache_data(ttl=300)
def load_finance_data():
    try: return conn.read(worksheet="Finance", ttl=0)
    except: return pd.DataFrame(columns=['วันที่', 'ชื่อเรื่อง', 'แพลตฟอร์ม', 'ยอดดิบ', 'หักแพลตฟอร์ม (17%)', 'ยอดสุทธิ'])

if 'books_data' not in st.session_state: st.session_state.books_data = load_admin_data()
if 'finance_db' not in st.session_state: st.session_state.finance_db = load_finance_data()
if 'app_settings' not in st.session_state:
    try: df_s = conn.read(worksheet="Settings", ttl=0); st.session_state.app_settings = {"categories": df_s['categories'].dropna().tolist(), "platforms": df_s['platforms'].dropna().tolist()}
    except: st.session_state.app_settings = {"categories": ["นิยายรัก", "แฟนตาซี", "นิยายวาย (BL)", "ทั่วไป"], "platforms": ["ReadAWrite", "KAIREW"]}

def save_and_refresh():
    try:
        books_to_save = []
        for b in st.session_state.books_data:
            temp = b.copy()
            if '_orig_idx' in temp: del temp['_orig_idx']
            temp['ลิงก์อ่าน'] = json.dumps(b.get('ลิงก์อ่าน', []))
            temp['ลิงก์ต้นฉบับ'] = json.dumps(b.get('ลิงก์ต้นฉบับ', []))
            books_to_save.append(temp)
        
        df_save = pd.DataFrame(books_to_save)
        if df_save.empty: df_save = pd.DataFrame(columns=['ชื่อเรื่อง', 'หมวดหมู่', 'QC', 'สถานะ', 'ตอนปัจจุบัน', 'เป้าหมาย', 'ภาพปก', 'เรื่องย่อ', 'ลิงก์อ่าน', 'ลิงก์ต้นฉบับ'])
        
        conn.update(worksheet="Books", data=df_save)
        conn.update(worksheet="Finance", data=st.session_state.finance_db)
        
        set_df = pd.DataFrame({"categories": pd.Series(st.session_state.app_settings['categories']), "platforms": pd.Series(st.session_state.app_settings['platforms'])})
        conn.update(worksheet="Settings", data=set_df)
        
        st.cache_data.clear() # เคลียร์แคชเพื่อให้เว็บหน้าบ้านอัปเดตตามทันที
        st.toast("✅ บันทึกข้อมูลเรียบร้อย!")
    except Exception as e: st.error(f"Error saving: {e}")

# ==========================================
# 📱 3. ระบบนำทาง (Sidebar)
# ==========================================
st.sidebar.markdown("<h2 style='text-align: center; color: #6C63FF; font-weight: 700; margin-bottom: 20px;'>💎 Nok-kaew Admin</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("Navigation Menu", ["📊 Dashboard", "📚 คลังนิยาย", "⚡ แก้ไขด่วน (Quick Edit)", "📢 แนะนำนิยาย", "💰 บัญชีรายรับ", "💸 สรุปส่วนแบ่ง (QC)", "🏆 อันดับนิยายขายดี", "⚙️ ตั้งค่าระบบ"])

if menu != "📚 คลังนิยาย": st.session_state.selected_book_idx = None
if menu != "📢 แนะนำนิยาย": st.session_state.selected_promo_idx = None

# ------------------------------------------
# 📊 Dashboard
# ------------------------------------------
if menu == "📊 Dashboard":
    st.title("📊 ภาพรวมระบบ (Dashboard)")
    if st.button("🔄 ดึงข้อมูลล่าสุด (Clear Cache)", type="primary"): st.cache_data.clear(); st.rerun()
    
    total_books = len(st.session_state.books_data)
    active_books = sum(1 for b in st.session_state.books_data if b.get('สถานะ') == 'กำลังอัปเดต')
    total_revenue = pd.to_numeric(st.session_state.finance_db['ยอดสุทธิ'], errors='coerce').sum() if not st.session_state.finance_db.empty else 0

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div class='metric-card'><h3>📚 นิยายทั้งหมด</h3><h2>{total_books}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='metric-card'><h3>🔥 กำลังแปล</h3><h2>{active_books}</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='metric-card'><h3>💰 รายได้สุทธิรวม</h3><h2>฿{total_revenue:,.0f}</h2></div>", unsafe_allow_html=True)

# ------------------------------------------
# 📚 คลังนิยาย (รวมระบบอัปโหลด ImgBB)
# ------------------------------------------
elif menu == "📚 คลังนิยาย":
    if st.session_state.selected_book_idx is not None:
        idx = st.session_state.selected_book_idx
        b = st.session_state.books_data[idx]
        if st.button("🔙 กลับหน้าคลังนิยาย"): st.session_state.selected_book_idx = None; st.rerun()
            
        st.title(f"🛠️ จัดการ: {b['ชื่อเรื่อง']}")
        st.markdown("---")
        
        c_img, c_form = st.columns([1, 3])
        with c_img: 
            img_show = b.get('ภาพปก') if b.get('ภาพปก') else "https://via.placeholder.com/300x450?text=No+Cover"
            st.markdown(f"<img src='{img_show}' class='rank-img' style='margin-bottom:20px;'>", unsafe_allow_html=True)
            
            st.markdown("##### 📤 อัปโหลดหน้าปกใหม่")
            uploaded_file = st.file_uploader("เลือกไฟล์รูปภาพ (ฝากอัตโนมัติลง ImgBB)", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                if st.button("🚀 ยืนยันอัปโหลดรูปนี้", use_container_width=True):
                    new_url = upload_to_imgbb(uploaded_file)
                    if new_url:
                        st.session_state.books_data[idx]['ภาพปก'] = new_url
                        save_and_refresh()
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
            
            e_cover = st.text_input("ลิงก์ภาพปก (ช่องนี้จะอัปเดตเองถ้าอัปโหลดรูปทางซ้าย)", value=b.get('ภาพปก',''))
            e_synopsis = st.text_area("📔 เรื่องย่อ", value=b.get('เรื่องย่อ',''), height=150)
            
            l1, l2 = st.columns(2)
            with l1:
                st.write("**📖 ลิงก์ช่องทางอ่าน (เช่น ReadToon, KAIREW)**")
                df_read = pd.DataFrame(b.get('ลิงก์อ่าน', [{"url":"", "note":""}]))
                if df_read.empty: df_read = pd.DataFrame([{"url":"", "note":""}])
                edited_read = st.data_editor(df_read, num_rows="dynamic", use_container_width=True, key=f"edit_read_{idx}")
            with l2:
                st.write("**🇰🇷 ลิงก์ต้นฉบับ**")
                df_orig = pd.DataFrame(b.get('ลิงก์ต้นฉบับ', [{"url":"", "note":""}]))
                if df_orig.empty: df_orig = pd.DataFrame([{"url":"", "note":""}])
                edited_orig = st.data_editor(df_orig, num_rows="dynamic", use_container_width=True, key=f"edit_orig_{idx}")

            sv_col, del_col = st.columns(2)
            if sv_col.button("💾 บันทึกการเปลี่ยนแปลงข้อมูล", type="primary"):
                st.session_state.books_data[idx].update({'ชื่อเรื่อง': e_title, 'หมวดหมู่': e_cat, 'QC': e_qc, 'ภาพปก': e_cover, 'สถานะ': e_stat, 'ตอนปัจจุบัน': e_curr, 'เป้าหมาย': e_tgt, 'เรื่องย่อ': e_synopsis, 'ลิงก์อ่าน': [r for r in edited_read.to_dict('records') if r.get('url')], 'ลิงก์ต้นฉบับ': [r for r in edited_orig.to_dict('records') if r.get('url')]})
                save_and_refresh()
                st.session_state.selected_book_idx = None; st.rerun()
                
            st.markdown("<div class='btn-delete'>", unsafe_allow_html=True)
            if del_col.button("🗑️ ลบนิยายเรื่องนี้ทิ้ง"):
                st.session_state.books_data.pop(idx); save_and_refresh()
                st.session_state.selected_book_idx = None; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.title("📚 จัดการคลังนิยาย")
        with st.expander("✨ เพิ่มนิยายเรื่องใหม่"):
            with st.form("add_book_form"):
                c_new1, c_new2 = st.columns(2)
                new_title = c_new1.text_input("ชื่อเรื่องนิยาย")
                new_cat = c_new1.selectbox("หมวดหมู่", st.session_state.app_settings['categories'])
                new_cover = c_new2.text_input("ลิงก์รูปปก (สามารถไปอัปโหลดเอาทีหลังได้)")
                new_qc = c_new2.radio("ผู้ดูแล (QC)", ["ตอง", "ตาว"], horizontal=True)
                if st.form_submit_button("เพิ่มนิยายเข้าระบบ"):
                    if new_title:
                        st.session_state.books_data.append({'ชื่อเรื่อง': new_title, 'หมวดหมู่': new_cat, 'QC': new_qc, 'สถานะ': 'กำลังอัปเดต', 'ตอนปัจจุบัน': 0, 'เป้าหมาย': 1, 'ภาพปก': new_cover, 'เรื่องย่อ': '', 'ลิงก์อ่าน': [], 'ลิงก์ต้นฉบับ': []})
                        save_and_refresh(); st.rerun()

        st.markdown("---")
        filtered_books = [b for idx, b in enumerate(st.session_state.books_data)]
        for i, b in enumerate(filtered_books): b['_orig_idx'] = i

        for i in range(0, len(filtered_books), 6):
            cols = st.columns(6)
            for j, col in enumerate(cols):
                if i + j < len(filtered_books):
                    b = filtered_books[i+j]
                    with col:
                        img_url = b.get('ภาพปก') if b.get('ภาพปก') else "https://via.placeholder.com/300x450?text=No+Cover"
                        card = f"<div class='rank-card'><img src='{img_url}' class='rank-img' onerror=\"this.onerror=null;this.src='https://via.placeholder.com/300x450?text=Error';\"><div style='font-size:13px; font-weight:600; line-height:1.2; margin-bottom:5px; height:32px; overflow:hidden;'>{b['ชื่อเรื่อง']}</div></div>"
                        st.markdown(card.replace('\n', ''), unsafe_allow_html=True)
                        if st.button("✏️ จัดการ", key=f"edit_{b['_orig_idx']}", use_container_width=True):
                            st.session_state.selected_book_idx = b['_orig_idx']; st.rerun()

# ------------------------------------------
# ⚡ แก้ไขด่วน
# ------------------------------------------
elif menu == "⚡ แก้ไขด่วน (Quick Edit)":
    st.title("⚡ แก้ไขด่วนแบบตาราง")
    if not st.session_state.books_data: st.warning("ไม่มีข้อมูล")
    else:
        df_quick = pd.DataFrame(st.session_state.books_data)
        edit_cols = ['ชื่อเรื่อง', 'หมวดหมู่', 'สถานะ', 'QC', 'ตอนปัจจุบัน', 'เป้าหมาย']
        edited_df = st.data_editor(df_quick[edit_cols], use_container_width=True, height=500)
        if st.button("💾 บันทึกตาราง", type="primary"):
            for i in range(len(edited_df)):
                for col in edit_cols: st.session_state.books_data[i][col] = edited_df.iloc[i][col]
            save_and_refresh(); st.rerun()

# ------------------------------------------
# 📢 แนะนำนิยาย
# ------------------------------------------
elif menu == "📢 แนะนำนิยาย":
    if st.session_state.selected_promo_idx is not None:
        idx = st.session_state.selected_promo_idx
        b = st.session_state.books_data[idx]
        if st.button("🔙 กลับ"): st.session_state.selected_promo_idx = None; st.rerun()
        
        img_url = b.get('ภาพปก') if b.get('ภาพปก') else "https://via.placeholder.com/300x450"
        synopsis = str(b.get('เรื่องย่อ', '')).replace('\n', '<br>')
        
        links_html = ""
        for link in b.get('ลิงก์อ่าน', []):
            if link.get('url'): links_html += f"<span style='background: linear-gradient(135deg, #6C63FF 0%, #8A84FF 100%); color:white; padding:8px 20px; border-radius:25px; font-weight:600; margin-right:10px;'>📖 {link.get('note','อ่านเลย')}</span>"

        promo_html = f"<div style='background: #ffffff; padding: 40px; border-radius: 30px; border: 1px solid #eef2f6; display: flex; flex-wrap: wrap; gap: 40px; align-items: flex-start; max-width: 1000px; margin: 0 auto; box-shadow: 0 10px 30px rgba(0,0,0,0.05);'><div style='flex: 0 0 320px;'><img src='{img_url}' style='width: 100%; border-radius: 20px; box-shadow: 0 12px 30px rgba(0,0,0,0.15);' onerror=\"this.onerror=null;this.src='https://via.placeholder.com/300x450?text=Error';\"></div><div style='flex: 1; min-width: 300px;'><div style='color: #6C63FF; font-weight: 700; font-size: 14px; margin-bottom: 10px;'>NOK-KAEW TRANSLATION</div><h1 style='color: #1e293b; font-size: 2.2rem; margin-top: 0;'>{b['ชื่อเรื่อง']}</h1><div style='background: #f8fafc; padding: 25px; border-radius: 20px; border-left: 6px solid #6C63FF; margin: 20px 0;'><h3 style='margin-top: 0; color: #475569;'>📝 เรื่องย่อ</h3><p style='color: #334155; line-height: 1.8;'>{synopsis}</p></div><div style='margin-top:20px;'>{links_html}</div></div></div>"
        st.markdown(promo_html.replace('\n',''), unsafe_allow_html=True)
    else:
        st.title("📢 สร้างภาพโปรโมท")
        for i in range(0, len(st.session_state.books_data), 6):
            cols = st.columns(6)
            for j, col in enumerate(cols):
                if i + j < len(st.session_state.books_data):
                    b = st.session_state.books_data[i+j]
                    with col:
                        img_url = b.get('ภาพปก') if b.get('ภาพปก') else "https://via.placeholder.com/300x450?text=No+Cover"
                        card = f"<div class='rank-card'><img src='{img_url}' class='rank-img' onerror=\"this.onerror=null;this.src='https://via.placeholder.com/300x450?text=Error';\"><div style='font-size:13px; font-weight:600; line-height:1.2; margin-bottom:10px; height:32px; overflow:hidden;'>{b['ชื่อเรื่อง']}</div></div>"
                        st.markdown(card.replace('\n', ''), unsafe_allow_html=True)
                        if st.button("👁️ สร้างภาพ", key=f"promo_{i+j}", use_container_width=True):
                            st.session_state.selected_promo_idx = i+j; st.rerun()

# ------------------------------------------
# 💰 บัญชีรายรับ & 💸 สรุปส่วนแบ่ง & 🏆 อันดับขายดี & ⚙️ ตั้งค่า (รวมไว้)
# ------------------------------------------
elif menu in ["💰 บัญชีรายรับ", "💸 สรุปส่วนแบ่ง (QC)", "🏆 อันดับนิยายขายดี", "⚙️ ตั้งค่าระบบ"]:
    st.info("💡 เลือกเมนูและจัดการข้อมูลตามปกติได้เลยครับ หากแก้ไขเสร็จแล้วอย่าลืมกดบันทึกนะครับ")
    
    if menu == "💰 บัญชีรายรับ":
        st.title("💰 บัญชีรายรับ")
        with st.form("add_finance"):
            c1, c2 = st.columns(2)
            d = c1.date_input("วันที่")
            b = c1.selectbox("ชื่อเรื่อง", [bk['ชื่อเรื่อง'] for bk in st.session_state.books_data])
            p = c2.selectbox("แพลตฟอร์ม", st.session_state.app_settings['platforms'])
            amt = c2.number_input("ยอดรายได้ดิบ (฿)", min_value=0.0)
            if st.form_submit_button("บันทึกรายได้"):
                new_f = pd.DataFrame([{'วันที่':d.strftime("%Y-%m-%d"), 'ชื่อเรื่อง':b, 'แพลตฟอร์ม':p, 'ยอดดิบ':amt, 'หักแพลตฟอร์ม (17%)':amt*0.17, 'ยอดสุทธิ':amt*0.83}])
                st.session_state.finance_db = pd.concat([st.session_state.finance_db, new_f], ignore_index=True)
                save_and_refresh(); st.rerun()
        edited_finance = st.data_editor(st.session_state.finance_db, num_rows="dynamic", use_container_width=True)
        if st.button("💾 บันทึกตารางบัญชี"): st.session_state.finance_db = edited_finance; save_and_refresh(); st.rerun()

    elif menu == "⚙️ ตั้งค่าระบบ":
        st.title("⚙️ ตั้งค่าระบบ")
        c1, c2 = st.columns(2)
        with c1: ed_c = st.data_editor(pd.DataFrame(st.session_state.app_settings['categories'], columns=['ชื่อหมวดหมู่']), num_rows="dynamic", use_container_width=True)
        with c2: ed_p = st.data_editor(pd.DataFrame(st.session_state.app_settings['platforms'], columns=['ชื่อแพลตฟอร์ม']), num_rows="dynamic", use_container_width=True)
        if st.button("💾 บันทึกการตั้งค่า"):
            st.session_state.app_settings['categories'] = ed_c['ชื่อหมวดหมู่'].dropna().tolist()
            st.session_state.app_settings['platforms'] = ed_p['ชื่อแพลตฟอร์ม'].dropna().tolist()
            save_and_refresh(); st.rerun()
            
    elif menu == "💸 สรุปส่วนแบ่ง (QC)":
        st.title("💸 สรุปส่วนแบ่ง")
        df_merge = pd.merge(st.session_state.finance_db, pd.DataFrame(st.session_state.books_data)[['ชื่อเรื่อง', 'QC']], on='ชื่อเรื่อง', how='left')
        df_merge['ยอดสุทธิ'] = pd.to_numeric(df_merge['ยอดสุทธิ'], errors='coerce').fillna(0)
        df_merge['เดือน-ปี'] = pd.to_datetime(df_merge['วันที่']).dt.strftime('%Y-%m')
        av_months = sorted(df_merge['เดือน-ปี'].dropna().unique(), reverse=True)
        sel_month = st.selectbox("เลือกรอบเดือน", av_months if av_months else [datetime.now().strftime('%Y-%m')])
        df_month = df_merge[df_merge['เดือน-ปี'] == sel_month]
        
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='metric-card'><h3 style='color:#FF6584;'>💖 ตอง</h3><h2>฿{df_month[df_month['QC'] == 'ตอง']['ยอดสุทธิ'].sum():,.2f}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><h3 style='color:#38bdf8;'>💙 ตาว</h3><h2>฿{df_month[df_month['QC'] == 'ตาว']['ยอดสุทธิ'].sum():,.2f}</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'><h3>🌍 รวม</h3><h2>฿{df_month['ยอดสุทธิ'].sum():,.2f}</h2></div>", unsafe_allow_html=True)
        st.dataframe(df_month[['วันที่', 'ชื่อเรื่อง', 'QC', 'ยอดสุทธิ']], use_container_width=True)
        
    elif menu == "🏆 อันดับนิยายขายดี":
        st.title("🏆 อันดับขายดี")
        df_merge = pd.merge(st.session_state.finance_db, pd.DataFrame(st.session_state.books_data)[['ชื่อเรื่อง', 'QC', 'ภาพปก']], on='ชื่อเรื่อง', how='left')
        df_merge['ยอดสุทธิ'] = pd.to_numeric(df_merge['ยอดสุทธิ'], errors='coerce').fillna(0)
        top_10 = df_merge.groupby('ชื่อเรื่อง').agg({'ยอดสุทธิ':'sum'}).sort_values('ยอดสุทธิ', ascending=False).head(10).reset_index()
        st.dataframe(top_10, use_container_width=True)
