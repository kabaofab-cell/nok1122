import streamlit as st
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection
import json
import plotly.express as px
from datetime import datetime
import os  # ✅ เพิ่มใหม่
from dotenv import load_dotenv  # ✅ เพิ่มใหม่
load_dotenv()  # ✅ เพิ่มใหม่
from readtoon_scraper import fetch_readtoon_data  # ✅ เพิ่มใหม่

# ==========================================
# 🔑 0. การตั้งค่าความลับ (Secrets & Settings)
# ==========================================
IMGBB_API_KEY = "c2632e406b68246bd02423be8f9bf384"
ADMIN_PASSWORD = "nokkaew2026" # <-- เปลี่ยนรหัสผ่านเข้าหลังบ้านตรงนี้

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
# 🎨 1. ตั้งค่าและดีไซน์ (Modern Premium UI)
# ==========================================
if 'selected_book_idx' not in st.session_state: st.session_state.selected_book_idx = None
if 'selected_promo_idx' not in st.session_state: st.session_state.selected_promo_idx = None
if 'readtoon_cache' not in st.session_state: st.session_state.readtoon_cache = None  # ✅ เพิ่มใหม่

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, input, button { 
        font-family: 'Kanit', sans-serif !important; 
    }
    
    .stApp { background-color: #f7f9fc; }
    
    /* แก้บั๊กฟอนต์ Sidebar โหมดมืด/สว่าง */
    [data-testid="stSidebar"] { background-color: #ffffff; box-shadow: 4px 0 15px rgba(0,0,0,0.03); }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: #1e293b !important; font-weight: 600 !important; font-size: 15px !important; }
    @media (prefers-color-scheme: dark) {
        [data-testid="stSidebar"] { background-color: #1e293b; }
        [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: #f8fafc !important; }
    }
    
    div[role="radiogroup"] > label { padding: 10px 20px; background: transparent; border-radius: 12px; transition: 0.3s ease; cursor: pointer; margin-bottom: 5px; }
    div[role="radiogroup"] > label:hover { background: rgba(108, 99, 255, 0.1); transform: translateX(5px); }

    .stButton > button { border-radius: 25px; border: none; background: linear-gradient(135deg, #6C63FF 0%, #8A84FF 100%); color: white; font-weight: 500; transition: all 0.3s ease; }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(108, 99, 255, 0.35); color: white; }
    
    .metric-card { background: white; padding: 25px 20px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); text-align: center; margin-bottom: 20px; border: 1px solid #f0f4f8; transition: 0.3s ease; }
    @media (prefers-color-scheme: dark) { .metric-card { background: #1e293b; border-color: #334155; } }
    .metric-card:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.06); }
    .metric-card h2 { color: #6C63FF; font-size: 2.2rem; font-weight: 700; margin-top: 10px; }
    
    .split-box-blue { background: linear-gradient(180deg, #e0f2fe 0%, #ffffff 100%); border: 1px solid #bae6fd; border-radius: 24px; padding: 25px; margin-bottom: 20px; height: 100%; }
    .split-box-pink { background: linear-gradient(180deg, #fce7f3 0%, #ffffff 100%); border: 1px solid #fbcfe8; border-radius: 24px; padding: 25px; margin-bottom: 20px; height: 100%; }
    @media (prefers-color-scheme: dark) { 
        .split-box-blue { background: #0f172a; border-color: #0284c7; }
        .split-box-pink { background: #0f172a; border-color: #be185d; }
    }
    
    .rank-card { background: white; padding: 15px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); transition: 0.3s ease; text-align: center; border: 1px solid #f0f0f0; margin-bottom: 20px; }
    @media (prefers-color-scheme: dark) { .rank-card { background: #1e293b; border-color: #334155; } }
    .rank-card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(108,99,255,0.15); border-color: #6C63FF; }
    .rank-img { width: 100%; aspect-ratio: 2/3; object-fit: cover; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 12px; }
    
    .ai-main { background: linear-gradient(135deg, #f3f0ff 0%, #ffffff 100%); border-left: 6px solid #6C63FF; padding: 20px; border-radius: 16px; margin-bottom: 15px; }
    .ai-tong { background: linear-gradient(135deg, #fff0f3 0%, #ffffff 100%); border-left: 6px solid #FF6584; padding: 20px; border-radius: 16px; margin-bottom: 15px; }
    .ai-tao { background: linear-gradient(135deg, #f0f7ff 0%, #ffffff 100%); border-left: 6px solid #38bdf8; padding: 20px; border-radius: 16px; margin-bottom: 15px; }
    @media (prefers-color-scheme: dark) { 
        .ai-main, .ai-tong, .ai-tao { background: #1e293b; }
    }
    
    .btn-delete>div>button { background: linear-gradient(135deg, #FF4B4B 0%, #ff7676 100%) !important; color: white !important; }
    
    /* สไตล์ตกแต่งหน้าความคืบหน้า */
    .progress-box { background: white; border-radius: 16px; padding: 20px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.03); border: 1px solid #f0f4f8; height: 100%; }
    .progress-box h4 { color: #475569; font-size: 1.1rem; margin-bottom: 15px; }
    .progress-value { font-size: 2.5rem; font-weight: 700; }
    .val-tong { color: #FF6584; }
    .val-tao { color: #38bdf8; }
    </style>
    """, unsafe_allow_html=True)

def safe_image(url, img_class="rank-img"):
    if url and str(url).strip() != "": st.markdown(f'<img src="{url}" class="{img_class}" onerror=\"this.onerror=null;this.src=\'https://via.placeholder.com/300x450?text=Error\';\">', unsafe_allow_html=True)
    else: st.markdown(f'<img src="https://via.placeholder.com/300x450?text=No+Cover" class="{img_class}">', unsafe_allow_html=True)

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
            def clean_str(val):
                return str(val) if pd.notna(val) and str(val).lower() != 'nan' else ''
            
            b['ภาพปก'] = clean_str(b.get('ภาพปก'))
            b['เรื่องย่อ'] = clean_str(b.get('เรื่องย่อ'))
            b['หมายเหตุ'] = clean_str(b.get('หมายเหตุ'))
            
            try: 
                l_read = b.get('ลิงก์อ่าน')
                b['ลิงก์อ่าน'] = json.loads(l_read) if pd.notna(l_read) and str(l_read).strip() not in ['', 'nan'] else []
            except: b['ลิงก์อ่าน'] = []
            if not isinstance(b['ลิงก์อ่าน'], list): b['ลิงก์อ่าน'] = []
        
        df_a = conn.read(worksheet="Authors", ttl=0)
        authors = df_a.to_dict('records')
        
        df_c = conn.read(worksheet="Chapters", ttl=0)
        chapters = df_c.to_dict('records')
        
        df_r = conn.read(worksheet="Reviews", ttl=0)
        reviews = df_r.to_dict('records') if not df_r.empty else []
        
        df_p = conn.read(worksheet="Promos", ttl=0)
        promos = df_p.to_dict('records') if not df_p.empty else []
        
        df_f = conn.read(worksheet="Finance", ttl=0)
        finance = df_f if not df_f.empty else pd.DataFrame()
        
        df_a = conn.read(worksheet="Announcements", ttl=0)
        announcements = df_a.to_dict('records') if not df_a.empty else []
        
        df_s = conn.read(worksheet="Settings", ttl=0)
        settings = {'categories': [], 'platforms': []}
        if not df_s.empty:
            for _, row in df_s.iterrows():
                if row.get('Type') == 'Category': settings['categories'].append(row.get('Value', ''))
                if row.get('Type') == 'Platform': settings['platforms'].append(row.get('Value', ''))
        
        return books, authors, chapters, reviews, promos, finance, announcements, settings
    except Exception as e:
        st.error(f"Database Error: {e}")
        return [], [], [], [], [], pd.DataFrame(), [], {'categories': [], 'platforms': []}

books_data, authors_data, chapters_data, reviews_data, promos_data, finance_db, announcements_db, app_settings = load_admin_data()
st.session_state.books_data = books_data
st.session_state.authors_data = authors_data
st.session_state.chapters_data = chapters_data
st.session_state.reviews_data = reviews_data
st.session_state.promos_data = promos_data
st.session_state.finance_db = finance_db
st.session_state.announcements_db = announcements_db
st.session_state.app_settings = app_settings

def save_all():
    try:
        conn.write(pd.DataFrame(st.session_state.books_data), worksheet="Books")
        conn.write(pd.DataFrame(st.session_state.authors_data), worksheet="Authors")
        conn.write(pd.DataFrame(st.session_state.chapters_data), worksheet="Chapters")
        conn.write(pd.DataFrame(st.session_state.reviews_data), worksheet="Reviews")
        conn.write(pd.DataFrame(st.session_state.promos_data), worksheet="Promos")
        conn.write(st.session_state.finance_db, worksheet="Finance")
        conn.write(pd.DataFrame(st.session_state.announcements_db), worksheet="Announcements")
        st.success("✅ บันทึกข้อมูลสำเร็จ!")
    except Exception as e: st.error(f"❌ Save Error: {e}")

# ==========================================
# 📌 3. เมนูหลัก
# ==========================================
menu = st.sidebar.radio(
    "📌 เลือกหน้าที่ต้องการ",
    [
        "🏠 หน้าหลัก",
        "📚 จัดการนิยาย",
        "👥 จัดการผู้เขียน",
        "📖 จัดการตอน",
        "⭐ จัดการความเห็น",
        "🎁 จัดการส่วนลด",
        "📣 ประกาศ",
        "💰 บัญชีรายรับ",
        "💸 สรุปส่วนแบ่ง (QC)",
        "🏆 อันดับนิยายขายดี",
        "🎯 ReadToon Creator",  # ✅ เพิ่มใหม่
        "⚙️ ตั้งค่าระบบ"
    ]
)

# ==========================================
# 📊 หน้า 1: Dashboard
# ==========================================
if menu == "🏠 หน้าหลัก":
    st.title("💎 Nok-kaew Admin Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(f"<div class='metric-card'><h3 style='color:#6C63FF;'>📚 นิยายทั้งหมด</h3><h2>{len(st.session_state.books_data)}</h2></div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div class='metric-card'><h3 style='color:#FF6584;'>👥 ผู้เขียน</h3><h2>{len(st.session_state.authors_data)}</h2></div>", unsafe_allow_html=True)
    with col3: st.markdown(f"<div class='metric-card'><h3 style='color:#38bdf8;'>📖 ตอนทั้งหมด</h3><h2>{len(st.session_state.chapters_data)}</h2></div>", unsafe_allow_html=True)
    with col4: st.markdown(f"<div class='metric-card'><h3 style='color:#10b981;'>⭐ ความเห็น</h3><h2>{len(st.session_state.reviews_data)}</h2></div>", unsafe_allow_html=True)
    st.markdown("---")

# ==========================================
# 🎯 หน้า ReadToon Creator Dashboard
# ==========================================
elif menu == "🎯 ReadToon Creator":  # ✅ เพิ่มใหม่
    st.title("🎯 ReadToon Creator Dashboard")
    st.markdown("---")
    
    # ปุ่มดึงข้อมูล
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
            if st.button("🔄 ดึงข้อมูลใหม่จาก ReadToon Creator", type="primary", use_container_width=True):
    # เปลี่ยนมาใช้ st.secrets.get() เพื่อให้รองรับบน Streamlit Cloud
    email = st.secrets.get("READTOON_EMAIL", os.getenv("READTOON_EMAIL"))
    password = st.secrets.get("READTOON_PASSWORD", os.getenv("READTOON_PASSWORD"))
            
            if not email or not password:
                st.error("❌ ยังไม่ได้ตั้งค่า READTOON_EMAIL และ READTOON_PASSWORD ใน Secrets")
            else:
                with st.spinner("🔄 กำลังดึงข้อมูลจาก ReadToon..."):
                    readtoon_data = fetch_readtoon_data(email, password)
                    if "error" in readtoon_data:
                        st.error(f"❌ {readtoon_data['error']}")
                    else:
                        st.session_state.readtoon_cache = readtoon_data
                        st.success("✅ ดึงข้อมูลสำเร็จ!")
                        st.rerun()
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 สรุปยอด", "📈 รายละเอียด", "💹 เทรนด์", "⚙️ ตั้งค่า"])
    
    # Tab 1: สรุปยอด
    with tab1:
        st.subheader("📊 สรุปข้อมูลการขายจาก ReadToon Creator")
        
        if st.session_state.readtoon_cache:
            data = st.session_state.readtoon_cache
            revenue = data.get("revenue", {})
            
            col1, col2, col3 = st.columns(3)
            with col1:
                total = revenue.get('total_revenue', 0)
                st.metric("💰 รายได้รวม", f"฿{total:,.2f}", delta=None)
            with col2:
                net = revenue.get('net_revenue', 0)
                st.metric("💸 รายได้สุทธิ", f"฿{net:,.2f}", delta=None)
            with col3:
                comm = revenue.get('commission', 0)
                st.metric("📊 หักแพลตฟอร์ม", f"฿{comm:,.2f}", delta=None)
            
            st.markdown("---")
            
            # แสดงข้อมูลรายเดือน
            if "monthly" in revenue and revenue["monthly"]:
                st.subheader("📅 รายได้รายเดือน (6 เดือนล่าสุด)")
                monthly_data = revenue.get("monthly", [])
                
                if monthly_data:
                    df_monthly = pd.DataFrame(monthly_data)
                    if not df_monthly.empty and 'month' in df_monthly.columns and 'amount' in df_monthly.columns:
                        fig = px.bar(df_monthly, x='month', y='amount', title="รายได้รายเดือน", color_discrete_sequence=["#6C63FF"])
                        fig.update_layout(font_family="Kanit", height=400)
                        st.plotly_chart(fig, use_container_width=True)
                        st.dataframe(df_monthly, use_container_width=True)
        else:
            st.info("🔍 กดปุ่ม 'ดึงข้อมูลใหม่' เพื่อโหลดข้อมูลจาก ReadToon Creator")
    
    # Tab 2: รายละเอียด
    with tab2:
        st.subheader("📈 รายละเอียดการขาย")
        
        if st.session_state.readtoon_cache:
            data = st.session_state.readtoon_cache
            sales = data.get("sales", [])
            
            if sales:
                df_sales = pd.DataFrame(sales)
                st.dataframe(df_sales, use_container_width=True)
                
                csv = df_sales.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 ดาวน์โหลด CSV",
                    data=csv,
                    file_name=f"readtoon_sales_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("❌ ไม่มีข้อมูลการขาย")
        else:
            st.info("🔍 กดปุ่ม 'ดึงข้อมูลใหม่' เพื่อโหลดข้อมูล")
    
    # Tab 3: เทรนด์
    with tab3:
        st.subheader("💹 วิเคราะห์เทรนด์")
        
        if st.session_state.readtoon_cache:
            data = st.session_state.readtoon_cache
            revenue = data.get("revenue", {})
            
            if "daily" in revenue and revenue["daily"]:
                daily_data = revenue.get("daily", [])
                if daily_data:
                    df_daily = pd.DataFrame(daily_data)
                    if not df_daily.empty and 'date' in df_daily.columns and 'amount' in df_daily.columns:
                        fig = px.line(df_daily, x='date', y='amount', title="เทรนด์รายได้รายวัน (14 วันล่าสุด)", markers=True, color_discrete_sequence=["#6C63FF"])
                        fig.update_layout(font_family="Kanit", height=400)
                        st.plotly_chart(fig, use_container_width=True)
                        st.dataframe(df_daily, use_container_width=True)
            else:
                st.warning("❌ ไม่มีข้อมูลรายวัน")
        else:
            st.info("🔍 กดปุ่ม 'ดึงข้อมูลใหม่' เพื่อโหลดข้อมูล")
    
    # Tab 4: ตั้งค่า
    with tab4:
        st.subheader("⚙️ ตั้งค่า ReadToon Creator Integration")
        
        st.info("""
        **วิธีการตั้งค่า Credentials (Streamlit Cloud):**
        
        1. ไปที่ App Settings
        2. ไปที่ Secrets
        3. เพิ่มข้อมูล:
        ```toml
        READTOON_EMAIL = "kabaofab@gmail.com"
        READTOON_PASSWORD = "รหัสของคุณ"
        ```
        4. Save และ Reboot script
        """)
        
        email_status = "✅ ตั้งค่าแล้ว" if os.getenv("READTOON_EMAIL") else "❌ ยังไม่ตั้งค่า"
        pass_status = "✅ ตั้งค่าแล้ว" if os.getenv("READTOON_PASSWORD") else "❌ ยังไม่ตั้งค่า"
        
        st.write(f"**สถานะการตั้งค่า:**")
        st.write(f"  {email_status}")
        st.write(f"  {pass_status}")

# ==========================================
# ⚙️ หน้า 11: ตั้งค่าระบบ
# ==========================================
elif menu == "⚙️ ตั้งค่าระบบ":
    st.title("⚙️ ตั้งค่าระบบ")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📚 หมวดหมู่นิยาย")
        ed_c = st.data_editor(pd.DataFrame(st.session_state.app_settings['categories'], columns=['ชื่อหมวดหมู่']), num_rows="dynamic", use_container_width=True)
    with c2:
        st.subheader("🌐 แพลตฟอร์ม (รวมในลิงก์อ่านด้วย)")
        ed_p = st.data_editor(pd.DataFrame(st.session_state.app_settings['platforms'], columns=['ชื่อแพลตฟอร์ม']), num_rows="dynamic", use_container_width=True)
    st.markdown("---")
    if st.button("💾 บันทึกการตั้งค่าทั้งหมด", type="primary"):
        st.session_state.app_settings['categories'] = ed_c['ชื่อหมวดหมู่'].replace('', pd.NA).dropna().tolist()
        st.session_state.app_settings['platforms'] = ed_p['ชื่อแพลตฟอร์ม'].replace('', pd.NA).dropna().tolist()
        save_all(); st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**📊 Nok-kaew Admin Pro** v2.0 | ✅ Streamlit Cloud Ready")
