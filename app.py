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
ADMIN_PASSWORD = "nokkaew2026" # <-- พี่เปลี่ยนรหัสผ่านตรงนี้ได้เลยครับ

st.set_page_config(page_title="Nok-kaew Admin Pro", layout="wide", page_icon="💎")

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
# 🎨 1. ดีไซน์ & แก้บั๊ก Sidebar Font
# ==========================================
if 'selected_book_idx' not in st.session_state: st.session_state.selected_book_idx = None

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"], .stMarkdown, p, label, input, button { font-family: 'Prompt', sans-serif !important; }
    
    /* แก้บั๊กฟอนต์ Sidebar ให้เห็นชัดทั้งโหมดมืด/สว่าง */
    [data-testid="stSidebar"] { box-shadow: 4px 0 15px rgba(0,0,0,0.05); }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: #1e293b !important; font-weight: 600 !important; font-size: 15px !important; }
    @media (prefers-color-scheme: dark) {
        [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: #f8fafc !important; }
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
    with st.spinner("กำลังอัปโหลดรูปภาพ..."):
        try:
            res = requests.post("https://api.imgbb.com/1/upload", data={"key": IMGBB_API_KEY}, files={"image": file.getvalue()})
            if res.status_code == 200: return res.json()["data"]["url"]
            return None
        except: return None

@st.cache_data(ttl=300)
def load_admin_data():
    try:
        df_b = conn.read(worksheet="Books", ttl=0)
        books = df_b.to_dict('records')
        for b in books:
            # จัดการแปลงข้อมูลลิงก์จาก JSON String เป็น List ของ Dictionary
            try: b['ลิงก์อ่าน'] = json.loads(b['ลิงก์อ่าน']) if b.get('ลิงก์อ่าน') and b['ลิงก์อ่าน'] != '[]' else []
            except: b['ลิงก์อ่าน'] = []
            b['สถานะ'] = b.get('สถานะ', 'กำลังอัปเดต')
            b['ตอนปัจจุบัน'] = int(b.get('ตอนปัจจุบัน', 0)) if pd.notna(b.get('ตอนปัจจุบัน')) else 0
            b['ภาพปก'] = str(b.get('ภาพปก', ''))
        return books
    except: return []

@st.cache_data(ttl=300)
def load_finance_data():
    try: return conn.read(worksheet="Finance", ttl=0)
    except: return pd.DataFrame(columns=['วันที่', 'ชื่อเรื่อง', 'แพลตฟอร์ม', 'ยอดดิบ', 'หักแพลตฟอร์ม (17%)', 'ยอดสุทธิ'])

if 'books_data' not in st.session_state: st.session_state.books_data = load_admin_data()
if 'finance_db' not in st.session_state: st.session_state.finance_db = load_finance_data()
if 'app_settings' not in st.session_state:
    try:
        df_s = conn.read(worksheet="Settings", ttl=0)
        st.session_state.app_settings = {"categories": df_s['categories'].dropna().tolist(), "platforms": df_s['platforms'].dropna().tolist()}
    except:
        st.session_state.app_settings = {"categories": ["นิยายรัก", "แฟนตาซี", "ทั่วไป"], "platforms": ["ReadToon", "KAIREW", "Facebook", "Meb", "Dek-D"]}

def save_all():
    try:
        books_to_save = []
        for b in st.session_state.books_data:
            temp = b.copy()
            if '_orig_idx' in temp: del temp['_orig_idx']
            temp['ลิงก์อ่าน'] = json.dumps(b.get('ลิงก์อ่าน', []))
            books_to_save.append(temp)
        
        conn.update(worksheet="Books", data=pd.DataFrame(books_to_save))
        conn.update(worksheet="Finance", data=st.session_state.finance_db)
        
        st.cache_data.clear()
        st.toast("✅ บันทึกข้อมูลสำเร็จ!")
    except Exception as e: st.error(f"Save Error: {e}")

# ==========================================
# 📱 3. ระบบนำทาง (Sidebar)
# ==========================================
st.sidebar.markdown("<h2 style='text-align: center; color: #6C63FF; font-weight: 700; margin-bottom: 20px;'>💎 Nok-kaew Admin</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("เมนูจัดการ", ["📊 Dashboard", "📚 คลังนิยาย", "⚡ แก้ไขด่วน (Quick Edit)", "💰 บัญชีรายรับ", "💸 ส่วนแบ่ง QC", "⚙️ ตั้งค่าระบบ"])

# ------------------------------------------
# 📊 หน้า 1: Dashboard
# ------------------------------------------
if menu == "📊 Dashboard":
    st.title("📊 ภาพรวมระบบ")
    col1, col2, col3 = st.columns(3)
    col1.metric("นิยายทั้งหมด", len(st.session_state.books_data))
    col2.metric("รายได้สุทธิรวม", f"฿{pd.to_numeric(st.session_state.finance_db['ยอดสุทธิ'], errors='coerce').sum():,.0f}")
    if st.button("🔄 ล้างข้อมูลจำ (Clear Cache)"): st.cache_data.clear(); st.rerun()

# ------------------------------------------
# 📚 หน้า 2: คลังนิยาย (หัวใจหลัก)
# ------------------------------------------
elif menu == "📚 คลังนิยาย":
    if st.session_state.selected_book_idx is not None:
        idx = st.session_state.selected_book_idx
        b = st.session_state.books_data[idx]
        if st.button("🔙 กลับ"): st.session_state.selected_book_idx = None; st.rerun()
            
        st.title(f"🛠️ จัดการ: {b['ชื่อเรื่อง']}")
        c_img, c_form = st.columns([1, 2])
        
        with c_img:
            st.image(b.get('ภาพปก') if b.get('ภาพปก') else "https://via.placeholder.com/300x450")
            up_file = st.file_uploader("เปลี่ยนรูปปก (ฝากรูปอัตโนมัติ)", type=["jpg","png","jpeg"])
            if up_file and st.button("🚀 อัปโหลดรูปใหม่"):
                new_url = upload_to_imgbb(up_file)
                if new_url: b['ภาพปก'] = new_url; save_all(); st.rerun()
        
        with c_form:
            e_title = st.text_input("ชื่อเรื่อง", value=b['ชื่อเรื่อง'])
            e_cat = st.selectbox("หมวดหมู่", st.session_state.app_settings['categories'], index=0)
            e_stat = st.selectbox("สถานะ", ["กำลังอัปเดต", "จบแล้ว", "พักการแปล"], index=0)
            e_curr = st.number_input("ตอนปัจจุบัน", value=int(b.get('ตอนปัจจุบัน',0)))
            e_syn = st.text_area("📔 เรื่องย่อ", value=b.get('เรื่องย่อ',''), height=150)
            
            st.markdown("#### 🔗 ลิงก์ช่องทางอ่าน (จัดการปุ่มหน้าสาธารณะ)")
            # ระบบ Data Editor สำหรับจัดการลิงก์และเลือกแพลตฟอร์ม
            df_links = pd.DataFrame(b.get('ลิงก์อ่าน', []))
            if df_links.empty: df_links = pd.DataFrame([{"note": "ReadToon", "url": ""}])
            
            edited_links = st.data_editor(
                df_links,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "note": st.column_config.SelectboxColumn(
                        "แพลตฟอร์ม",
                        options=["ReadToon", "KAIREW", "Facebook", "Meb", "Dek-D", "อื่นๆ"],
                        required=True,
                    ),
                    "url": st.column_config.LinkColumn("ลิงก์ URL (ก๊อปมาวาง)", required=True)
                },
                key=f"link_editor_{idx}"
            )
            
            if st.button("💾 บันทึกข้อมูลทั้งหมด", type="primary", use_container_width=True):
                st.session_state.books_data[idx].update({
                    'ชื่อเรื่อง': e_title, 'หมวดหมู่': e_cat, 'สถานะ': e_stat, 
                    'ตอนปัจจุบัน': e_curr, 'เรื่องย่อ': e_syn, 
                    'ลิงก์อ่าน': edited_links.to_dict('records')
                })
                save_all(); st.session_state.selected_book_idx = None; st.rerun()
            
            if st.button("🗑️ ลบเรื่องนี้", use_container_width=True):
                st.session_state.books_data.pop(idx); save_all(); st.session_state.selected_book_idx = None; st.rerun()

    else:
        st.title("📚 คลังนิยายทั้งหมด")
        if st.button("✨ เพิ่มเรื่องใหม่"):
            st.session_state.books_data.append({'ชื่อเรื่อง': 'ชื่อนิยายใหม่', 'หมวดหมู่': 'ทั่วไป', 'สถานะ': 'กำลังอัปเดต', 'ตอนปัจจุบัน': 0, 'ภาพปก': '', 'เรื่องย่อ': '', 'ลิงก์อ่าน': []})
            save_all(); st.rerun()
            
        for i in range(0, len(st.session_state.books_data), 6):
            cols = st.columns(6)
            for j, col in enumerate(cols):
                if i+j < len(st.session_state.books_data):
                    bk = st.session_state.books_data[i+j]
                    with col:
                        st.markdown(f"<div class='rank-card'><img src='{bk.get('ภาพปก','https://via.placeholder.com/300')}' class='rank-img'><div style='font-size:13px; font-weight:600; height:35px; overflow:hidden;'>{bk['ชื่อเรื่อง']}</div></div>", unsafe_allow_html=True)
                        if st.button("✏️ จัดการ", key=f"ed_{i+j}", use_container_width=True):
                            st.session_state.selected_book_idx = i+j; st.rerun()

# ------------------------------------------
# ⚡ หน้า 3: แก้ไขด่วน (Quick Edit)
# ------------------------------------------
elif menu == "⚡ แก้ไขด่วน (Quick Edit)":
    st.title("⚡ แก้ไขข้อมูลด่วน")
    df_q = pd.DataFrame(st.session_state.books_data)[['ชื่อเรื่อง', 'หมวดหมู่', 'สถานะ', 'ตอนปัจจุบัน']]
    edited_df = st.data_editor(df_q, use_container_width=True)
    if st.button("💾 บันทึกตาราง", type="primary"):
        for i in range(len(edited_df)):
            st.session_state.books_data[i].update(edited_df.iloc[i].to_dict())
        save_all(); st.rerun()

# ------------------------------------------
# 💰 หน้า 4: บัญชีรายรับ
# ------------------------------------------
elif menu == "💰 บัญชีรายรับ":
    st.title("💰 บันทึกรายได้")
    with st.form("fin_form"):
        c1, c2 = st.columns(2)
        d = c1.date_input("วันที่")
        b_name = c1.selectbox("ชื่อเรื่อง", [bk['ชื่อเรื่อง'] for bk in st.session_state.books_data])
        plat = c2.selectbox("แพลตฟอร์ม", st.session_state.app_settings['platforms'])
        amt = c2.number_input("ยอดดิบ (฿)", min_value=0.0)
        if st.form_submit_button("บันทึก"):
            new_f = pd.DataFrame([{'วันที่':d.strftime("%Y-%m-%d"), 'ชื่อเรื่อง':b_name, 'แพลตฟอร์ม':plat, 'ยอดดิบ':amt, 'หักแพลตฟอร์ม (17%)':amt*0.17, 'ยอดสุทธิ':amt*0.83}])
            st.session_state.finance_db = pd.concat([st.session_state.finance_db, new_f], ignore_index=True)
            save_all(); st.rerun()
    
    st.markdown("#### ✏️ รายการล่าสุด")
    edited_fin = st.data_editor(st.session_state.finance_db, num_rows="dynamic", use_container_width=True)
    if st.button("💾 บันทึกการแก้ไขตาราง"): st.session_state.finance_db = edited_fin; save_all(); st.rerun()

# ------------------------------------------
# 💸 หน้า 5: ส่วนแบ่ง QC & 🏆 ตั้งค่า
# ------------------------------------------
elif menu == "💸 ส่วนแบ่ง QC":
    st.title("💸 สรุปส่วนแบ่ง")
    df_books = pd.DataFrame(st.session_state.books_data)[['ชื่อเรื่อง', 'QC']]
    df_m = pd.merge(st.session_state.finance_db, df_books, on='ชื่อเรื่อง', how='left')
    df_m['ยอดสุทธิ'] = pd.to_numeric(df_m['ยอดสุทธิ'], errors='coerce').fillna(0)
    st.write(f"ยอดสุทธิรวม: ฿{df_m['ยอดสุทธิ'].sum():,.2f}")
    st.dataframe(df_m, use_container_width=True)

elif menu == "⚙️ ตั้งค่าระบบ":
    st.title("⚙️ ตั้งค่าพื้นฐาน")
    c1, c2 = st.columns(2)
    with c1: ed_c = st.data_editor(pd.DataFrame(st.session_state.app_settings['categories'], columns=['หมวดหมู่']), num_rows="dynamic", use_container_width=True)
    with c2: ed_p = st.data_editor(pd.DataFrame(st.session_state.app_settings['platforms'], columns=['แพลตฟอร์ม']), num_rows="dynamic", use_container_width=True)
    if st.button("💾 บันทึกการตั้งค่า"):
        st.session_state.app_settings['categories'] = ed_c['หมวดหมู่'].dropna().tolist()
        st.session_state.app_settings['platforms'] = ed_p['แพลตฟอร์ม'].dropna().tolist()
        save_all(); st.rerun()
