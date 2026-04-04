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

st.set_page_config(page_title="Nok-kaew Admin Pro", layout="wide", page_icon="💎")

# ==========================================
# 🎨 1. ตั้งค่าและดีไซน์ (Modern Premium UI)
# ==========================================
if 'selected_book_idx' not in st.session_state: st.session_state.selected_book_idx = None
if 'selected_promo_idx' not in st.session_state: st.session_state.selected_promo_idx = None

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
            
            try: 
                l_orig = b.get('ลิงก์ต้นฉบับ')
                b['ลิงก์ต้นฉบับ'] = json.loads(l_orig) if pd.notna(l_orig) and str(l_orig).strip() not in ['', 'nan'] else []
            except: b['ลิงก์ต้นฉบับ'] = []
            if not isinstance(b['ลิงก์ต้นฉบับ'], list): b['ลิงก์ต้นฉบับ'] = []
            
            b['สถานะ'] = b.get('สถานะ', 'กำลังอัปเดต')
            b['หมวดหมู่'] = b.get('หมวดหมู่', 'ทั่วไป')
            b['QC'] = b.get('QC', 'ตอง')
            b['ตอนปัจจุบัน'] = int(b.get('ตอนปัจจุบัน', 0)) if pd.notna(b.get('ตอนปัจจุบัน')) else 0
            b['เป้าหมาย'] = int(b.get('เป้าหมาย', 1)) if pd.notna(b.get('เป้าหมาย')) else 1

        return books
    except: return []

@st.cache_data(ttl=300)
def load_finance_data():
    try: return conn.read(worksheet="Finance", ttl=0)
    except: return pd.DataFrame(columns=['วันที่', 'ชื่อเรื่อง', 'แพลตฟอร์ม', 'ยอดดิบ', 'หักแพลตฟอร์ม (17%)', 'ยอดสุทธิ'])

@st.cache_data(ttl=300)
def load_settings():
    try:
        df_s = conn.read(worksheet="Settings", ttl=0)
        return {"categories": df_s['categories'].dropna().tolist(), "platforms": df_s['platforms'].dropna().tolist()}
    except:
        return {"categories": ["นิยายรัก", "แฟนตาซี", "นิยายวาย (BL)", "ทั่วไป"], "platforms": ["ReadToon", "KAIREW", "Facebook", "Meb", "Dek-D"]}

@st.cache_data(ttl=300)
def load_announcements():
    try: return conn.read(worksheet="Announcements", ttl=0)
    except: return pd.DataFrame(columns=['วันที่', 'หัวข้อประกาศ', 'เนื้อหา', 'สถานะ'])

# 🚀 ฟังก์ชันโหลดตารางบันทึกความคืบหน้า
@st.cache_data(ttl=300)
def load_progress_data():
    try: return conn.read(worksheet="ProgressLog", ttl=0)
    except: return pd.DataFrame(columns=['วันที่', 'ชื่อเรื่อง', 'QC', 'จำนวนตอนที่เพิ่ม'])

if 'books_data' not in st.session_state: st.session_state.books_data = load_admin_data()
if 'finance_db' not in st.session_state: st.session_state.finance_db = load_finance_data()
if 'app_settings' not in st.session_state: st.session_state.app_settings = load_settings()
if 'announcements_db' not in st.session_state: st.session_state.announcements_db = load_announcements()
if 'progress_log_db' not in st.session_state: st.session_state.progress_log_db = load_progress_data()

def save_all():
    try:
        books_to_save = []
        for b in st.session_state.books_data:
            temp = b.copy()
            if '_orig_idx' in temp: del temp['_orig_idx']
            temp['ลิงก์อ่าน'] = json.dumps(b.get('ลิงก์อ่าน', []))
            temp['ลิงก์ต้นฉบับ'] = json.dumps(b.get('ลิงก์ต้นฉบับ', []))
            books_to_save.append(temp)
        
        df_save = pd.DataFrame(books_to_save)
        if df_save.empty: df_save = pd.DataFrame(columns=['ชื่อเรื่อง', 'หมวดหมู่', 'QC', 'สถานะ', 'ตอนปัจจุบัน', 'เป้าหมาย', 'ภาพปก', 'เรื่องย่อ', 'หมายเหตุ', 'ลิงก์อ่าน', 'ลิงก์ต้นฉบับ'])
        
        conn.update(worksheet="Books", data=df_save)
        conn.update(worksheet="Finance", data=st.session_state.finance_db)
        
        set_df = pd.DataFrame({"categories": pd.Series(st.session_state.app_settings['categories']), "platforms": pd.Series(st.session_state.app_settings['platforms'])})
        conn.update(worksheet="Settings", data=set_df)
        
        if not st.session_state.announcements_db.empty:
            conn.update(worksheet="Announcements", data=st.session_state.announcements_db)
        else:
            conn.update(worksheet="Announcements", data=pd.DataFrame(columns=['วันที่', 'หัวข้อประกาศ', 'เนื้อหา', 'สถานะ']))
            
        # 🚀 บันทึกข้อมูลความคืบหน้าลง Sheets
        if not st.session_state.progress_log_db.empty:
            conn.update(worksheet="ProgressLog", data=st.session_state.progress_log_db)
        else:
            conn.update(worksheet="ProgressLog", data=pd.DataFrame(columns=['วันที่', 'ชื่อเรื่อง', 'QC', 'จำนวนตอนที่เพิ่ม']))
            
        st.cache_data.clear()
        st.toast("✅ บันทึกข้อมูลเรียบร้อย!")
    except Exception as e: st.error(f"Error saving: {e}")

# ==========================================
# 📱 3. ระบบนำทาง (Sidebar)
# ==========================================
st.sidebar.markdown("<h2 style='text-align: center; color: #6C63FF; font-weight: 700; margin-bottom: 20px;'>💎 Nok-kaew Admin</h2>", unsafe_allow_html=True)

menu_options = [
    "📊 Dashboard", 
    "📚 คลังนิยาย", 
    "📝 อัปเดตตอนใหม่", 
    "📈 ความคืบหน้างานแปล",
    "⚡ แก้ไขด่วน (Quick Edit)", 
    "📢 แนะนำนิยาย", 
    "📰 จัดการประกาศ",
    "💰 บัญชีรายรับ", 
    "💸 สรุปส่วนแบ่ง (QC)", 
    "🏆 อันดับนิยายขายดี", 
    "⚙️ ตั้งค่าระบบ"
]

if 'main_menu' not in st.session_state:
    st.session_state.main_menu = "📊 Dashboard"

menu = st.sidebar.radio("Navigation Menu", menu_options, key="main_menu")

if menu != "📚 คลังนิยาย": st.session_state.selected_book_idx = None
if menu != "📢 แนะนำนิยาย": st.session_state.selected_promo_idx = None

# ------------------------------------------
# 📊 หน้า 1: Dashboard
# ------------------------------------------
if menu == "📊 Dashboard":
    st.title("📊 ภาพรวมระบบ (Dashboard)")
    if st.button("🔄 ดึงข้อมูลล่าสุด (Clear Cache & Reload)", type="primary"): st.cache_data.clear(); st.rerun()
    
    total_books = len(st.session_state.books_data)
    active_books = sum(1 for b in st.session_state.books_data if b.get('สถานะ') == 'กำลังอัปเดต')
    finished_books = sum(1 for b in st.session_state.books_data if b.get('สถานะ') == 'จบแล้ว')
    
    df_finance = st.session_state.finance_db.copy()
    total_revenue = pd.to_numeric(df_finance['ยอดสุทธิ'], errors='coerce').sum() if not df_finance.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(f"<div class='metric-card'><h3>📚 นิยายทั้งหมด</h3><h2>{total_books}</h2></div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div class='metric-card'><h3>🔥 กำลังแปล</h3><h2>{active_books}</h2></div>", unsafe_allow_html=True)
    with col3: st.markdown(f"<div class='metric-card'><h3>🎉 จบแล้ว</h3><h2>{finished_books}</h2></div>", unsafe_allow_html=True)
    with col4: st.markdown(f"<div class='metric-card'><h3>💰 รายได้สุทธิรวม</h3><h2 style='color:#6C63FF;'>฿{total_revenue:,.0f}</h2></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.title("🤖 AI Executive Report (รายงานเจาะลึก)")
    
    if not df_finance.empty and st.session_state.books_data:
        df_books = pd.DataFrame(st.session_state.books_data)[['ชื่อเรื่อง', 'QC', 'หมวดหมู่', 'ตอนปัจจุบัน', 'เป้าหมาย', 'สถานะ']]
        df_merge = pd.merge(df_finance, df_books, on='ชื่อเรื่อง', how='left')
        df_merge['ยอดสุทธิ'] = pd.to_numeric(df_merge['ยอดสุทธิ'], errors='coerce').fillna(0)
        
        top_cat = df_merge.groupby('หมวดหมู่')['ยอดสุทธิ'].sum().idxmax() if 'หมวดหมู่' in df_merge else "ไม่มีข้อมูล"
        top_book = df_merge.groupby('ชื่อเรื่อง')['ยอดสุทธิ'].sum().idxmax()
        near_finish = [b['ชื่อเรื่อง'] for b in st.session_state.books_data if b.get('สถานะ') == 'กำลังอัปเดต' and (int(b.get('ตอนปัจจุบัน',0))/max(int(b.get('เป้าหมาย',1)),1)) >= 0.8]
        
        main_insight = f"<div class='ai-main'><h4 style='color:#6C63FF; margin-bottom:10px;'>🌟 ภาพรวมและทิศทางอนาคต (Overall Trends)</h4><p><b>นิยายชูโรงของเรา:</b> ตอนนี้เรื่อง <b>\"{top_book}\"</b> ยืนหนึ่งเรื่องการสร้างรายได้ครับ ในขณะที่หมวดหมู่ที่นักอ่านเปย์หนักที่สุดตกเป็นของ <b>\"{top_cat}\"</b></p><p><b>💡 AI ขอแนะนำ:</b> ในการซื้อลิขสิทธิ์เรื่องต่อไป แนะนำให้เล็งหมวด <b>\"{top_cat}\"</b> เพิ่มเติมครับ</p>"
        if near_finish: main_insight += f"<p><b>🚀 โอกาสทอง:</b> มีนิยายที่แปลไปแล้วเกิน 80% คือ <b>{', '.join(near_finish)}</b> เตรียมจัดแพ็กเกจ E-Book ได้เลย!</p>"
        main_insight += "</div>"
        st.markdown(main_insight.replace('\n', ''), unsafe_allow_html=True)
        
        col_qc1, col_qc2 = st.columns(2)
        with col_qc1:
            df_tong = df_merge[df_merge['QC'] == 'ตอง']
            if not df_tong.empty and df_tong['ยอดสุทธิ'].sum() > 0:
                tong_top = df_tong.groupby('ชื่อเรื่อง')['ยอดสุทธิ'].sum().idxmax()
                st.markdown(f"<div class='ai-tong'><h4 style='color:#FF6584; margin-bottom:10px;'>💖 ผลงานของ ตอง (Tong)</h4><p><b>ยอดเงินที่ทำได้รวม:</b> ฿{df_tong['ยอดสุทธิ'].sum():,.0f}</p><p><b>ลูกรักทำเงิน:</b> เรื่อง <b>\"{tong_top}\"</b> ทำยอดทะลุเป้าได้อย่างสวยงามครับ</p></div>".replace('\n', ''), unsafe_allow_html=True)
            else: st.markdown("<div class='ai-tong'><h4>💖 ตอง (Tong)</h4><p>กำลังรอสร้างผลงานยอดขายแรกอยู่ครับ!</p></div>", unsafe_allow_html=True)
                
        with col_qc2:
            df_tao = df_merge[df_merge['QC'] == 'ตาว']
            if not df_tao.empty and df_tao['ยอดสุทธิ'].sum() > 0:
                tao_top = df_tao.groupby('ชื่อเรื่อง')['ยอดสุทธิ'].sum().idxmax()
                st.markdown(f"<div class='ai-tao'><h4 style='color:#38bdf8; margin-bottom:10px;'>💙 ผลงานของ ตาว (Tao)</h4><p><b>ยอดเงินที่ทำได้รวม:</b> ฿{df_tao['ยอดสุทธิ'].sum():,.0f}</p><p><b>ลูกรักทำเงิน:</b> เรื่อง <b>\"{tao_top}\"</b> คือตัวท็อปในมือตาวตอนนี้เลยครับ</p></div>".replace('\n', ''), unsafe_allow_html=True)
            else: st.markdown("<div class='ai-tao'><h4>💙 ตาว (Tao)</h4><p>รอเปิดตัวยอดขายสุดปังอยู่ครับ!</p></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📈 กราฟสรุปภาพรวม")
    c_c1, c_c2 = st.columns(2)
    with c_c1:
        if total_books > 0:
            fig_cat = px.pie(pd.DataFrame(st.session_state.books_data), names='หมวดหมู่', title='สัดส่วนนิยายแยกตามหมวดหมู่', hole=0.45, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_cat.update_layout(font_family="Kanit")
            st.plotly_chart(fig_cat, use_container_width=True)
    with c_c2:
        if not df_finance.empty and total_revenue > 0:
            fig_plat = px.bar(df_finance.groupby('แพลตฟอร์ม')['ยอดสุทธิ'].sum().reset_index(), x='แพลตฟอร์ม', y='ยอดสุทธิ', title='รายได้สุทธิแยกตามแพลตฟอร์ม', text_auto='.2s', color='แพลตฟอร์ม', color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_plat.update_layout(font_family="Kanit", showlegend=False)
            st.plotly_chart(fig_plat, use_container_width=True)

# ------------------------------------------
# 📚 หน้า 2: คลังนิยาย
# ------------------------------------------
elif menu == "📚 คลังนิยาย":
    # 📌 โหมดแก้ไขนิยายเดี่ยว
    if st.session_state.selected_book_idx is not None:
        idx = st.session_state.selected_book_idx
        b = st.session_state.books_data[idx]
        
        c_back, _ = st.columns([1, 5])
        if c_back.button("🔙 กลับหน้าคลังนิยาย"): st.session_state.selected_book_idx = None; st.rerun()
            
        st.title(f"🛠️ จัดการ: {b['ชื่อเรื่อง']}")
        st.markdown("---")
        
        c_img, c_form = st.columns([1, 3])
        with c_img: 
            safe_image(b.get('ภาพปก'))
            st.markdown("##### 📤 อัปโหลดปกใหม่")
            uploaded_file = st.file_uploader("เลือกรูปจากเครื่อง (อัปโหลดเข้า ImgBB อัตโนมัติ)", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                if st.button("🚀 ยืนยันอัปโหลด", use_container_width=True):
                    new_url = upload_to_imgbb(uploaded_file)
                    if new_url:
                        st.session_state.books_data[idx]['ภาพปก'] = new_url
                        save_all(); st.rerun()
            
        with c_form:
            e_title = st.text_input("ชื่อเรื่อง", value=b['ชื่อเรื่อง'])
            
            c_f1, c_f2 = st.columns(2)
            e_cat = c_f1.selectbox("หมวดหมู่", st.session_state.app_settings['categories'], index=st.session_state.app_settings['categories'].index(b.get('หมวดหมู่','ทั่วไป')) if b.get('หมวดหมู่') in st.session_state.app_settings['categories'] else 0)
            e_stat = c_f2.selectbox("สถานะ", ["กำลังอัปเดต", "จบแล้ว", "พักการแปล"], index=["กำลังอัปเดต", "จบแล้ว", "พักการแปล"].index(b.get('สถานะ','กำลังอัปเดต')) if b.get('สถานะ') in ["กำลังอัปเดต", "จบแล้ว", "พักการแปล"] else 0)
            
            c_f3, c_f4, c_f5 = st.columns(3)
            e_qc = c_f3.radio("QC", ["ตอง", "ตาว"], index=["ตอง", "ตาว"].index(b.get('QC','ตอง')) if b.get('QC') in ["ตอง", "ตาว"] else 0, horizontal=True)
            e_tgt = c_f4.number_input("จำนวนตอนต้นฉบับ", value=int(b.get('เป้าหมาย',1)))
            e_curr = c_f5.number_input("แปลเสร็จแล้ว (ตอน)", value=int(b.get('ตอนปัจจุบัน',0)))
            
            e_cover = st.text_input("ลิงก์ภาพปก (อัปเดตเองเมื่ออัปโหลดรูปทางซ้าย)", value=b.get('ภาพปก',''))
            e_synopsis = st.text_area("📔 เรื่องย่อ", value=b.get('เรื่องย่อ',''), height=150)
            e_note = st.text_area("📝 หมายเหตุ (Note)", value=b.get('หมายเหตุ',''))
            
            l1, l2 = st.columns(2)
            with l1:
                st.write("**📖 ลิงก์ช่องทางอ่าน (แสดงผลหน้า Public)**")
                read_data = b.get('ลิงก์อ่าน', [])
                if not isinstance(read_data, list) or len(read_data) == 0:
                    read_data = [{"note":"ReadToon", "url":""}]
                df_read = pd.DataFrame(read_data)
                
                edited_read = st.data_editor(
                    df_read, 
                    num_rows="dynamic", 
                    use_container_width=True, 
                    key=f"edit_read_{idx}",
                    column_config={
                        "note": st.column_config.SelectboxColumn("แพลตฟอร์ม", options=st.session_state.app_settings['platforms'], required=True),
                        "url": st.column_config.LinkColumn("ลิงก์ URL", required=True)
                    }
                )
            with l2:
                st.write("**🇰🇷 ลิงก์ต้นฉบับ**")
                orig_data = b.get('ลิงก์ต้นฉบับ', [])
                if not isinstance(orig_data, list) or len(orig_data) == 0:
                    orig_data = [{"url":"", "note":""}]
                df_orig = pd.DataFrame(orig_data)
                edited_orig = st.data_editor(df_orig, num_rows="dynamic", use_container_width=True, key=f"edit_orig_{idx}")

            sv_col, del_col = st.columns(2)
            if sv_col.button("💾 บันทึกการเปลี่ยนแปลง", type="primary", use_container_width=True):
                st.session_state.books_data[idx].update({
                    'ชื่อเรื่อง': e_title, 'หมวดหมู่': e_cat, 'QC': e_qc, 'ภาพปก': e_cover, 
                    'สถานะ': e_stat, 'ตอนปัจจุบัน': e_curr, 'เป้าหมาย': e_tgt, 'เรื่องย่อ': e_synopsis, 'หมายเหตุ': e_note, 
                    'ลิงก์อ่าน': [r for r in edited_read.to_dict('records') if r.get('url')], 
                    'ลิงก์ต้นฉบับ': [r for r in edited_orig.to_dict('records') if r.get('url')]
                })
                save_all()
                st.session_state.selected_book_idx = None; st.rerun()
            
            st.markdown("<div class='btn-delete'>", unsafe_allow_html=True)
            if del_col.button("🗑️ ลบนิยายเรื่องนี้ทิ้ง", use_container_width=True):
                st.session_state.books_data.pop(idx)
                save_all()
                st.session_state.selected_book_idx = None; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # 📌 โหมดแกลลอรี่
    else:
        st.title("📚 จัดการคลังนิยาย")
        
        with st.expander("✨ เพิ่มนิยายเรื่องใหม่ (คลิกเพื่อกางออก)"):
            with st.form("add_book_form"):
                c_new1, c_new2 = st.columns(2)
                new_title = c_new1.text_input("ชื่อเรื่องนิยาย")
                new_cat = c_new1.selectbox("หมวดหมู่", st.session_state.app_settings['categories'])
                new_cover = c_new2.text_input("ลิงก์รูปปก (หรือไปอัปโหลดเอาทีหลังได้)")
                new_qc = c_new2.radio("ผู้ดูแล (QC)", ["ตอง", "ตาว"], horizontal=True)
                c_chap1, c_chap2 = st.columns(2)
                new_target = c_chap1.number_input("จำนวนตอนต้นฉบับ", min_value=1, value=100)
                new_current = c_chap2.number_input("ตอนที่แปลเสร็จแล้ว", min_value=0, value=0)
                if st.form_submit_button("บันทึกนิยายเรื่องใหม่"):
                    if new_title:
                        st.session_state.books_data.append({'ชื่อเรื่อง': new_title, 'หมวดหมู่': new_cat, 'QC': new_qc, 'สถานะ': 'กำลังอัปเดต', 'ตอนปัจจุบัน': new_current, 'เป้าหมาย': new_target, 'ภาพปก': new_cover, 'เรื่องย่อ': '', 'หมายเหตุ': '', 'ลิงก์อ่าน': [], 'ลิงก์ต้นฉบับ': []})
                        save_all(); st.rerun()

        st.markdown("---")
        f_col1, f_col2, f_col3 = st.columns(3)
        search_q = f_col1.text_input("🔍 ค้นหาชื่อเรื่อง...")
        filter_cat = f_col2.selectbox("📂 หมวดหมู่", ["ทั้งหมด"] + st.session_state.app_settings['categories'])
        filter_stat = f_col3.selectbox("📌 สถานะ", ["ทั้งหมด", "กำลังอัปเดต", "จบแล้ว", "พักการแปล"])

        filtered_books = []
        for idx, b in enumerate(st.session_state.books_data):
            if search_q and search_q.lower() not in b['ชื่อเรื่อง'].lower(): continue
            if filter_cat != "ทั้งหมด" and b['หมวดหมู่'] != filter_cat: continue
            if filter_stat != "ทั้งหมด" and b.get('สถานะ') != filter_stat: continue
            b['_orig_idx'] = idx 
            filtered_books.append(b)

        for i in range(0, len(filtered_books), 6):
            cols = st.columns(6)
            for j, col in enumerate(cols):
                if i + j < len(filtered_books):
                    b = filtered_books[i+j]
                    with col:
                        img_url = b.get('ภาพปก') if b.get('ภาพปก') and str(b.get('ภาพปก')).strip() != "" else "https://via.placeholder.com/300x450?text=No+Cover"
                        card = f"<div class='rank-card'><img src='{img_url}' class='rank-img' onerror=\"this.onerror=null;this.src='https://via.placeholder.com/300x450?text=Error';\"><div style='font-size:13px; font-weight:600; line-height:1.3; margin-bottom:5px; height:35px; overflow:hidden;'>{b['ชื่อเรื่อง']}</div>"
                        stat_color = "#28a745" if b.get('สถานะ') == 'จบแล้ว' else ("#ffc107" if b.get('สถานะ') == 'พักการแปล' else "#17a2b8")
                        card += f"<span style='color:{stat_color}; font-size:12px; font-weight:600;'>● {b.get('สถานะ')}</span><br><br></div>"
                        st.markdown(card.replace('\n',''), unsafe_allow_html=True)
                        
                        if st.button("✏️ จัดการ", key=f"edit_{b['_orig_idx']}", use_container_width=True):
                            st.session_state.selected_book_idx = b['_orig_idx']; st.rerun()

# ------------------------------------------
# 📝 หน้า 3: อัปเดตตอนใหม่ & ลิงก์ต้นฉบับ 🚀
# ------------------------------------------
elif menu == "📝 อัปเดตตอนใหม่":
    st.title("📝 อัปเดตตอนใหม่ & วาร์ปต้นฉบับ")
    st.info("💡 ค้นหานิยายที่กำลังแปล กดลิงก์ไปอ่านต้นฉบับภาษาเกาหลี แล้วกลับมาบันทึกยอดการแปลรายวันได้ทันที!")
    
    search_update = st.text_input("🔍 พิมพ์ชื่อเรื่องที่ต้องการอัปเดต...", key="search_update")
    
    filtered_for_update = []
    for idx, b in enumerate(st.session_state.books_data):
        if search_update and search_update.lower() not in b['ชื่อเรื่อง'].lower(): continue
        b['_orig_idx'] = idx 
        filtered_for_update.append(b)

    if not filtered_for_update:
        st.warning("ไม่พบนิยายที่ค้นหาครับ")
    else:
        for b in filtered_for_update:
            idx = b['_orig_idx']
            with st.expander(f"📖 {b['ชื่อเรื่อง']} | สถานะ: {b.get('สถานะ', '')} | ตอนที่แปลเสร็จ: {b.get('ตอนปัจจุบัน', 0)} / {b.get('เป้าหมาย', 1)}"):
                c1, c2 = st.columns([1, 4])
                
                with c1:
                    img_url = b.get('ภาพปก') if b.get('ภาพปก') and str(b.get('ภาพปก')).strip() != "" else "https://via.placeholder.com/150x225?text=No+Cover"
                    st.markdown(f"<img src='{img_url}' style='width:100%; border-radius:8px; box-shadow:0 4px 8px rgba(0,0,0,0.1);' onerror=\"this.onerror=null;this.src='https://via.placeholder.com/150x225?text=Error';\">", unsafe_allow_html=True)
                
                with c2:
                    st.markdown("#### ⚙️ อัปเดตยอดการแปล")
                    c_input, c_btn = st.columns([2, 1])
                    
                    old_chap = int(b.get('ตอนปัจจุบัน', 0))
                    new_chap = c_input.number_input("แก้ไขตอน (ตอนปัจจุบันที่แปลเสร็จ)", value=old_chap, min_value=0, key=f"upd_chap_{idx}")
                    
                    if c_btn.button("💾 บันทึกตอน", key=f"save_chap_{idx}", type="primary", use_container_width=True):
                        # 🚀 ระบบคำนวณและบันทึกความคืบหน้าอัตโนมัติ
                        if new_chap > old_chap:
                            added_chaps = new_chap - old_chap
                            new_log = pd.DataFrame([{
                                'วันที่': datetime.today().strftime('%Y-%m-%d'),
                                'ชื่อเรื่อง': b['ชื่อเรื่อง'],
                                'QC': b.get('QC', 'ตอง'),
                                'จำนวนตอนที่เพิ่ม': added_chaps
                            }])
                            st.session_state.progress_log_db = pd.concat([st.session_state.progress_log_db, new_log], ignore_index=True)
                            
                        st.session_state.books_data[idx]['ตอนปัจจุบัน'] = new_chap
                        save_all()
                        st.rerun()
                        
                    st.markdown("---")
                    st.markdown("#### 🇰🇷 ลิงก์ต้นฉบับ & การจัดการ")
                    c_link, c_manage = st.columns(2)
                    
                    with c_link:
                        orig_links = b.get('ลิงก์ต้นฉบับ', [])
                        has_link = False
                        if isinstance(orig_links, list):
                            for i, link in enumerate(orig_links):
                                url = link.get('url', '')
                                note = link.get('note', '')
                                if url:
                                    has_link = True
                                    # 🚀 แสดงข้อความจากช่องหมายเหตุ ถ้าไม่มีให้แสดงคำเริ่มต้น
                                    btn_label = f"🔗 {note}" if note and str(note).strip() != "" else f"🔗 ไปยังเว็บต้นฉบับ {i+1}"
                                    st.link_button(btn_label, url, use_container_width=True)
                        if not has_link:
                            st.warning("ยังไม่ได้ใส่ข้อมูลลิงก์ต้นฉบับในเรื่องนี้ครับ")
                            
                    with c_manage:
                        if st.button("🛠️ จัดการข้อมูลเต็ม (แก้ไขเรื่องย่อ/ปก)", key=f"go_edit_{idx}", use_container_width=True):
                            st.session_state.selected_book_idx = idx
                            st.session_state.main_menu = "📚 คลังนิยาย"
                            st.rerun()

# ------------------------------------------
# 📈 หน้า 4: ความคืบหน้างานแปล
# ------------------------------------------
elif menu == "📈 ความคืบหน้างานแปล":
    st.title("📈 ติดตามความคืบหน้างานแปล")
    
    if st.session_state.progress_log_db.empty:
        st.info("💡 ยังไม่มีการบันทึกความคืบหน้าครับ (ระบบจะเริ่มบันทึกอัตโนมัติเมื่อกด 'บันทึกตอน' ในหน้าอัปเดตตอนใหม่)")
    else:
        df_prog = st.session_state.progress_log_db.copy()
        df_prog['วันที่'] = pd.to_datetime(df_prog['วันที่'], errors='coerce')
        df_prog['จำนวนตอนที่เพิ่ม'] = pd.to_numeric(df_prog['จำนวนตอนที่เพิ่ม'], errors='coerce').fillna(0)
        
        # คำนวณวันที่สำหรับกรองข้อมูล
        today_date = pd.Timestamp(datetime.today().date())
        start_of_week = today_date - pd.Timedelta(days=today_date.dayofweek) # จันทร์เป็นวันแรกของสัปดาห์
        start_of_month = today_date.replace(day=1)
        
        df_today = df_prog[df_prog['วันที่'] == today_date]
        df_week = df_prog[df_prog['วันที่'] >= start_of_week]
        df_month = df_prog[df_prog['วันที่'] >= start_of_month]
        
        def get_sum(df, qc_name): return int(df[df['QC'] == qc_name]['จำนวนตอนที่เพิ่ม'].sum())
        
        # 🌟 ส่วนที่ 1: การ์ดแสดงผลสรุปยอด
        st.markdown("### 🏆 สรุปยอดจำนวนตอนที่แปลเพิ่ม")
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown("<div class='progress-box'><h4>📅 ผลงานวันนี้</h4>"
                        f"<div style='margin-bottom:10px;'><span style='font-size:1.2rem;'>ตอง: </span><span class='progress-value val-tong'>{get_sum(df_today, 'ตอง')}</span></div>"
                        f"<div><span style='font-size:1.2rem;'>ตาว: </span><span class='progress-value val-tao'>{get_sum(df_today, 'ตาว')}</span></div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='progress-box'><h4>🗓️ ผลงานสัปดาห์นี้</h4>"
                        f"<div style='margin-bottom:10px;'><span style='font-size:1.2rem;'>ตอง: </span><span class='progress-value val-tong'>{get_sum(df_week, 'ตอง')}</span></div>"
                        f"<div><span style='font-size:1.2rem;'>ตาว: </span><span class='progress-value val-tao'>{get_sum(df_week, 'ตาว')}</span></div></div>", unsafe_allow_html=True)
        with c3:
            total_month_tong = get_sum(df_month, 'ตอง')
            total_month_tao = get_sum(df_month, 'ตาว')
            st.markdown("<div class='progress-box'><h4>🌍 ผลงานเดือนนี้</h4>"
                        f"<div style='margin-bottom:10px;'><span style='font-size:1.2rem;'>ตอง: </span><span class='progress-value val-tong'>{total_month_tong}</span></div>"
                        f"<div><span style='font-size:1.2rem;'>ตาว: </span><span class='progress-value val-tao'>{total_month_tao}</span></div></div>", unsafe_allow_html=True)

        st.markdown("---")
        
        # 🌟 ส่วนที่ 2: AI วิเคราะห์และให้คำแนะนำ
        st.markdown("### 🤖 AI Executive Report (วิเคราะห์สปีดงานแปล)")
        
        total_month_all = total_month_tong + total_month_tao
        
        ai_text = f"""
        <div class='ai-main'>
            <h4 style='color:#6C63FF; margin-bottom:10px;'>📊 ภาพรวมการทำงานของทีม</h4>
            <p>ภาพรวมสปีดงานแปลของทีมในเดือนนี้ถือว่าทำยอดรวมไปได้แล้ว <b>{total_month_all} ตอน</b> แบ่งเป็นผลงานของตอง {total_month_tong} ตอน และของตาว {total_month_tao} ตอนครับ</p>
            <p>💡 <b>เป้าหมายโปรเจกต์ใหญ่:</b> เพื่อบริหารจัดการการแปลนิยายระดับมาสเตอร์พีซทั้ง 10 เรื่อง (ความยาวเรื่องละ 150 ตอน) ให้บรรลุเป้าหมายภายในเวลา 1 เดือน เราจะต้องสร้างอัตราการแปลเฉลี่ยให้ได้รวมวันละประมาณ 50 ตอนครับ หากเรารักษาความเร็วการแปลให้สม่ำเสมอในทุกๆ วัน การปิดโปรเจกต์สุดหินนี้ก็อยู่ในกำมือเราแน่นอนครับ สู้ๆ ค๊า!</p>
        </div>
        """
        st.markdown(ai_text.replace('\n', ''), unsafe_allow_html=True)
        
        st.markdown("---")
        with st.expander("📋 ดูประวัติการบันทึกข้อมูลย้อนหลังทั้งหมด"):
            st.dataframe(df_prog.sort_values(by='วันที่', ascending=False), use_container_width=True)

# ------------------------------------------
# ⚡ หน้า 5: แก้ไขด่วน (Quick Edit)
# ------------------------------------------
elif menu == "⚡ แก้ไขด่วน (Quick Edit)":
    st.title("⚡ ระบบแก้ไขด่วนแบบตาราง")
    st.info("💡 แก้ไขข้อมูลในตารางได้อิสระ แล้วกดปุ่ม 'บันทึกการเปลี่ยนแปลงทั้งหมด' ด้านล่างเพื่ออัปเดตพร้อมกัน")
    if not st.session_state.books_data: st.warning("ไม่มีข้อมูลนิยาย")
    else:
        df_quick = pd.DataFrame(st.session_state.books_data)
        edit_cols = ['ชื่อเรื่อง', 'หมวดหมู่', 'สถานะ', 'QC', 'ตอนปัจจุบัน', 'เป้าหมาย']
        edited_df = st.data_editor(
            df_quick[edit_cols],
            column_config={
                "หมวดหมู่": st.column_config.SelectboxColumn("หมวดหมู่", options=st.session_state.app_settings['categories'], required=True),
                "สถานะ": st.column_config.SelectboxColumn("สถานะ", options=["กำลังอัปเดต", "จบแล้ว", "พักการแปล"], required=True),
                "QC": st.column_config.SelectboxColumn("ผู้ดูแล (QC)", options=["ตอง", "ตาว"], required=True),
                "ตอนปัจจุบัน": st.column_config.NumberColumn("แปลแล้ว (ตอน)", min_value=0),
                "เป้าหมาย": st.column_config.NumberColumn("ต้นฉบับ (ตอน)", min_value=1)
            }, use_container_width=True, num_rows="fixed", height=500
        )
        if st.button("💾 บันทึกการเปลี่ยนแปลงทั้งหมด", type="primary"):
            for i in range(len(edited_df)):
                for col in edit_cols: st.session_state.books_data[i][col] = edited_df.iloc[i][col]
            save_all(); st.rerun()

# ------------------------------------------
# 📢 หน้า 6: แนะนำนิยาย (Promo Page)
# ------------------------------------------
elif menu == "📢 แนะนำนิยาย":
    if st.session_state.selected_promo_idx is not None:
        idx = st.session_state.selected_promo_idx
        b = st.session_state.books_data[idx]
        
        if st.button("🔙 กลับหน้าหลัก"): st.session_state.selected_promo_idx = None; st.rerun()
        
        img_url = b.get('ภาพปก') if b.get('ภาพปก') and str(b.get('ภาพปก')).strip() != "" else "https://via.placeholder.com/300x450?text=No+Cover"
        synopsis = str(b.get('เรื่องย่อ', '')).replace('\n', '<br>')
        
        links_html = ""
        for link in b.get('ลิงก์อ่าน', []):
            if link.get('url'):
                links_html += f"<span style='display:inline-block; background: linear-gradient(135deg, #6C63FF 0%, #8A84FF 100%); color:white; padding:8px 20px; border-radius:25px; text-decoration:none; font-weight:600; margin-right:10px; box-shadow: 0 4px 10px rgba(108,99,255,0.2);'>📖 {link.get('note','อ่านเลย')}</span>"

        promo_html = f"""
        <div style="background: #ffffff; padding: 50px; border-radius: 30px; box-shadow: 0 15px 40px rgba(0,0,0,0.06); border: 1px solid #eef2f6; display: flex; flex-wrap: wrap; gap: 40px; align-items: flex-start; max-width: 1000px; margin: 0 auto;">
            <div style="flex: 0 0 320px;">
                <img src="{img_url}" style="width: 100%; aspect-ratio: 2/3; object-fit: cover; border-radius: 20px; box-shadow: 0 12px 30px rgba(0,0,0,0.15);" onerror="this.onerror=null;this.src='https://via.placeholder.com/300x450?text=Error';">
            </div>
            <div style="flex: 1; min-width: 300px;">
                <div style="color: #6C63FF; font-weight: 700; font-size: 14px; letter-spacing: 1px; margin-bottom: 10px; text-transform: uppercase;">Nok-kaew Translation</div>
                <h1 style="color: #1e293b; font-size: 2.4rem; font-weight: 700; margin-top: 0; margin-bottom: 20px; line-height: 1.3;">{b['ชื่อเรื่อง']}</h1>
                
                <div style="margin-bottom: 30px; display: flex; gap: 15px; flex-wrap: wrap;">
                    <div style="background: #e0f2fe; color: #0284c7; padding: 6px 18px; border-radius: 20px; font-weight: 600; font-size: 14px;">📌 สถานะ: {b.get('สถานะ','')}</div>
                    <div style="background: #f3e8ff; color: #7e22ce; padding: 6px 18px; border-radius: 20px; font-weight: 600; font-size: 14px;">📑 {b.get('ตอนปัจจุบัน',0)} / {b.get('เป้าหมาย',0)} ตอน</div>
                    <div style="background: #ffedd5; color: #be185d; padding: 6px 18px; border-radius: 20px; font-weight: 600; font-size: 14px;">📂 {b.get('หมวดหมู่','')}</div>
                </div>
                
                <div style="background: #f8fafc; padding: 25px; border-radius: 20px; border-left: 6px solid #6C63FF;">
                    <h3 style="color: #475569; margin-top: 0; margin-bottom: 15px; font-size: 1.2rem; font-weight: 600;">📝 เรื่องย่อ</h3>
                    <p style="color: #334155; font-size: 1.05rem; line-height: 1.8; margin-bottom: 0;">{synopsis}</p>
                </div>
                
                <div style="margin-top: 35px;">
                    <h4 style="color: #64748b; margin-bottom: 15px; font-size: 1rem; font-weight: 500;">ติดตามผู้แปลได้ที่:</h4>
                    {links_html}
                </div>
            </div>
        </div>
        """
        st.markdown(promo_html.replace('\n', ''), unsafe_allow_html=True)
        st.info("📸 **Tip:** เลื่อนจัดหน้าจอให้สวยงาม แล้วแคปเจอร์เพื่อนำไปโพสต์ได้เลยครับ!")

    else:
        st.title("📢 สร้างภาพโปรโมทนิยาย")
        st.write("เลือกนิยายที่ต้องการ เพื่อสร้างภาพพร้อมเรื่องย่อสำหรับแคปหน้าจอไปโปรโมท")
        st.markdown("---")
        
        for i in range(0, len(st.session_state.books_data), 6):
            cols = st.columns(6)
            for j, col in enumerate(cols):
                if i + j < len(st.session_state.books_data):
                    b = st.session_state.books_data[i+j]
                    with col:
                        img_url = b.get('ภาพปก') if b.get('ภาพปก') and str(b.get('ภาพปก')).strip() != "" else "https://via.placeholder.com/300x450?text=No+Cover"
                        card = f"<div class='rank-card'><img src='{img_url}' class='rank-img' onerror=\"this.onerror=null;this.src='https://via.placeholder.com/300x450?text=Error';\"><div style='font-size:13px; font-weight:600; line-height:1.2; margin-bottom:10px; height:32px; overflow:hidden;'>{b['ชื่อเรื่อง']}</div></div>"
                        st.markdown(card.replace('\n', ''), unsafe_allow_html=True)
                        if st.button("👁️ สร้างภาพ", key=f"promo_{i+j}", use_container_width=True):
                            st.session_state.selected_promo_idx = i+j; st.rerun()

# ------------------------------------------
# 📰 หน้า 7: จัดการประกาศ
# ------------------------------------------
elif menu == "📰 จัดการประกาศ":
    st.title("📰 จัดการประกาศ (Announcements)")
    st.info("💡 เพิ่ม ลบ หรือแก้ไขประกาศที่จะไปแสดงผลที่หน้าเว็บสาธารณะ (สร้างอัตโนมัติลงชีต 'Announcements')")
    
    with st.form("add_announcement_form"):
        c1, c2 = st.columns([1, 3])
        a_date = c1.date_input("วันที่ประกาศ", value=datetime.today())
        a_status = c1.selectbox("สถานะ", ["แสดง", "ซ่อน"])
        a_title = c2.text_input("หัวข้อประกาศ (จำเป็นต้องใส่)")
        a_content = st.text_area("รายละเอียดประกาศ")
        
        if st.form_submit_button("➕ เพิ่มประกาศใหม่", type="primary"):
            if a_title:
                new_announce = pd.DataFrame([{
                    'วันที่': a_date.strftime("%Y-%m-%d"), 
                    'หัวข้อประกาศ': a_title, 
                    'เนื้อหา': a_content, 
                    'สถานะ': a_status
                }])
                st.session_state.announcements_db = pd.concat([st.session_state.announcements_db, new_announce], ignore_index=True)
                save_all()
                st.rerun()
            else:
                st.warning("⚠️ กรุณาใส่หัวข้อประกาศก่อนบันทึกครับ")
                
    st.markdown("#### ✏️ ตารางแก้ไขและลบประกาศ")
    if st.session_state.announcements_db.empty:
        st.write("ยังไม่มีข้อมูลประกาศในระบบค๊า")
    else:
        edited_announce = st.data_editor(
            st.session_state.announcements_db, 
            num_rows="dynamic", 
            use_container_width=True,
            column_config={
                "วันที่": st.column_config.TextColumn("วันที่ (YYYY-MM-DD)", required=True),
                "สถานะ": st.column_config.SelectboxColumn("สถานะ", options=["แสดง", "ซ่อน"], required=True)
            }
        )
        if st.button("💾 บันทึกการแก้ไขตารางประกาศ", type="primary"):
            st.session_state.announcements_db = edited_announce
            save_all()
            st.rerun()

# ------------------------------------------
# 💰 หน้า 8: บัญชีรายรับ (ปรับปรุงใหม่ ฟีเจอร์เพิ่มรายรับรวดเร็ว)
# ------------------------------------------
elif menu == "💰 บัญชีรายรับ":
    st.title("💰 บันทึกบัญชีรายรับ")
    
    tab1, tab2, tab3 = st.tabs(["⚡ เพิ่มรายรับรวดเร็ว (แบบกลุ่ม)", "📝 เพิ่มรายรับ (ทีละรายการ)", "✏️ แก้ไขข้อมูลทั้งหมด"])
    
    # 🌟 แท็บ 1: ฟีเจอร์เพิ่มรายรับรวดเร็วตามที่คุณขอ 
    with tab1:
        st.info("💡 เลือกระบุวันที่ลงบัญชี, แพลตฟอร์ม และผู้ดูแล (QC) ระบบจะแสดงรายชื่อนิยายทั้งหมดของคนนั้น ให้คุณใส่ยอดรายได้ดิบพร้อมกันได้เลยทีเดียว")
        
        c1, c2, c3 = st.columns(3)
        q_date = c1.date_input("วันที่ลงบัญชี", key="q_date")
        q_plat = c2.selectbox("แพลตฟอร์ม", st.session_state.app_settings['platforms'], key="q_plat")
        q_qc = c3.selectbox("ผู้ดูแล (QC)", ["ตอง", "ตาว"], key="q_qc")
        
        # กรองนิยายเฉพาะที่เป็นของ QC คนที่เลือก
        qc_books = [b['ชื่อเรื่อง'] for b in st.session_state.books_data if b.get('QC') == q_qc]
        
        if not qc_books:
            st.warning(f"⚠️ ไม่พบนิยายที่ดูแลโดย {q_qc} ในระบบครับ")
        else:
            # สร้างตารางจำลองให้กรอกเฉพาะ "ยอดดิบ"
            df_quick_fin = pd.DataFrame({
                "ชื่อเรื่อง": qc_books,
                "ยอดดิบ": [0.0] * len(qc_books)
            })
            
            st.write(f"**กรอกยอดรายรับดิบของ {q_plat} ประจำวันที่ {q_date.strftime('%d/%m/%Y')}**")
            edited_q_fin = st.data_editor(
                df_quick_fin,
                column_config={
                    "ชื่อเรื่อง": st.column_config.TextColumn("ชื่อเรื่อง", disabled=True),
                    "ยอดดิบ": st.column_config.NumberColumn("ยอดรายได้ดิบ (฿)", min_value=0.0, format="%.2f")
                },
                use_container_width=True,
                hide_index=True
            )
            
            if st.button("💾 บันทึกยอดรายรับเข้าสู่ระบบทั้งหมด", type="primary", use_container_width=True):
                new_entries = []
                for _, row in edited_q_fin.iterrows():
                    amt = row["ยอดดิบ"]
                    if amt > 0: # ดึงเฉพาะเรื่องที่มียอดเงินมากกว่า 0
                        new_entries.append({
                            'วันที่': q_date.strftime("%Y-%m-%d"),
                            'ชื่อเรื่อง': row["ชื่อเรื่อง"],
                            'แพลตฟอร์ม': q_plat,
                            'ยอดดิบ': amt,
                            'หักแพลตฟอร์ม (17%)': amt * 0.17,
                            'ยอดสุทธิ': amt * 0.83
                        })
                
                if new_entries:
                    st.session_state.finance_db = pd.concat([st.session_state.finance_db, pd.DataFrame(new_entries)], ignore_index=True)
                    save_all()
                    st.success(f"✅ บันทึกยอดรายรับใหม่จำนวน {len(new_entries)} รายการ ลงฐานข้อมูลเรียบร้อยแล้ว!")
                    st.rerun()
                else:
                    st.warning("⚠️ ไม่มียอดให้บันทึก (คุณยังไม่ได้ใส่ยอดดิบในตารางครับ)")

    # 🌟 แท็บ 2: ฟอร์มแบบเดิม (ทีละรายการ)
    with tab2:
        st.write("#### 📝 ฟอร์มเพิ่มรายได้ทีละเรื่อง")
        with st.form("add_finance"):
            c_f1, c_f2 = st.columns(2)
            d = c_f1.date_input("วันที่")
            b = c_f1.selectbox("ชื่อเรื่อง", [bk['ชื่อเรื่อง'] for bk in st.session_state.books_data] if st.session_state.books_data else ["ไม่มีข้อมูล"])
            p = c_f2.selectbox("แพลตฟอร์ม", st.session_state.app_settings['platforms'])
            amt = c_f2.number_input("ยอดรายได้ดิบ (฿)", min_value=0.0)
            if st.form_submit_button("บันทึกรายได้"):
                if b != "ไม่มีข้อมูล":
                    new_f = pd.DataFrame([{'วันที่':d.strftime("%Y-%m-%d"), 'ชื่อเรื่อง':b, 'แพลตฟอร์ม':p, 'ยอดดิบ':amt, 'หักแพลตฟอร์ม (17%)':amt*0.17, 'ยอดสุทธิ':amt*0.83}])
                    st.session_state.finance_db = pd.concat([st.session_state.finance_db, new_f], ignore_index=True)
                    save_all(); st.rerun()
                    
    # 🌟 แท็บ 3: ตารางแก้ไขข้อมูลดิบ
    with tab3:
        st.write("#### ✏️ ตารางแก้ไข/ลบข้อมูลรายรับ")
        edited_finance = st.data_editor(st.session_state.finance_db, num_rows="dynamic", use_container_width=True)
        if st.button("💾 บันทึกตารางบัญชีล่าสุด"): 
            st.session_state.finance_db = edited_finance; save_all(); st.rerun()

# ------------------------------------------
# 💸 หน้า 9: แบ่งรายได้ (QC)
# ------------------------------------------
elif menu == "💸 สรุปส่วนแบ่ง (QC)":
    st.title("💸 ระบบสรุปส่วนแบ่งรายได้ (QC)")
    if st.session_state.finance_db.empty or not st.session_state.books_data: st.warning("⚠️ ยังไม่มีข้อมูลนิยายหรือรายได้")
    else:
        df_fin = st.session_state.finance_db.copy()
        df_books = pd.DataFrame(st.session_state.books_data)[['ชื่อเรื่อง', 'QC']]
        df_merge = pd.merge(df_fin, df_books, on='ชื่อเรื่อง', how='left')
        df_merge['ยอดสุทธิ'] = pd.to_numeric(df_merge['ยอดสุทธิ'], errors='coerce').fillna(0)
        df_merge['วันที่'] = pd.to_datetime(df_merge['วันที่'])
        df_merge['เดือน-ปี'] = df_merge['วันที่'].dt.strftime('%Y-%m')
        
        c_filter1, _ = st.columns(2)
        av_months = sorted(df_merge['เดือน-ปี'].dropna().unique(), reverse=True)
        sel_month = c_filter1.selectbox("📌 เลือกรอบเดือนที่ต้องการดูยอด", av_months if av_months else [datetime.now().strftime('%Y-%m')])
        df_month = df_merge[df_merge['เดือน-ปี'] == sel_month]
        
        st.markdown("---")
        rev_tong = df_month[df_month['QC'] == 'ตอง']['ยอดสุทธิ'].sum()
        rev_tao = df_month[df_month['QC'] == 'ตาว']['ยอดสุทธิ'].sum()
        total_m = df_month['ยอดสุทธิ'].sum()

        col1, col2, col3 = st.columns(3)
        with col1: st.markdown(f"<div class='metric-card'><h3 style='color:#6C63FF;'>💖 ยอดของ ตอง</h3><h2>฿{rev_tong:,.2f}</h2></div>", unsafe_allow_html=True)
        with col2: st.markdown(f"<div class='metric-card'><h3 style='color:#FF6584;'>💙 ยอดของ ตาว</h3><h2>฿{rev_tao:,.2f}</h2></div>", unsafe_allow_html=True)
        with col3: st.markdown(f"<div class='metric-card'><h3>🌍 รวมทั้งเดือน</h3><h2>฿{total_m:,.2f}</h2></div>", unsafe_allow_html=True)

        who = st.multiselect("กรองดูเฉพาะรายชื่อ:", options=['ตอง', 'ตาว'], default=['ตอง', 'ตาว'])
        st.dataframe(df_month[df_month['QC'].isin(who)][['วันที่', 'ชื่อเรื่อง', 'แพลตฟอร์ม', 'QC', 'ยอดสุทธิ']].sort_values('ยอดสุทธิ', ascending=False), use_container_width=True)

# ------------------------------------------
# 🏆 หน้า 10: อันดับนิยายขายดี
# ------------------------------------------
elif menu == "🏆 อันดับนิยายขายดี":
    st.title("🏆 อันดับนิยายขายดี (Leaderboard)")
    if st.session_state.finance_db.empty or not st.session_state.books_data: st.warning("⚠️ ยังไม่มีข้อมูลเพียงพอ")
    else:
        df_fin = st.session_state.finance_db.copy()
        df_books = pd.DataFrame(st.session_state.books_data)[['ชื่อเรื่อง', 'QC', 'ภาพปก']]
        df_merge = pd.merge(df_fin, df_books, on='ชื่อเรื่อง', how='left')
        df_merge['ยอดสุทธิ'] = pd.to_numeric(df_merge['ยอดสุทธิ'], errors='coerce').fillna(0)
        df_merge['วันที่'] = pd.to_datetime(df_merge['วันที่'])
        df_merge['เดือน-ปี'] = df_merge['วันที่'].dt.strftime('%Y-%m')

        st.subheader("📈 กราฟเปรียบเทียบแนวโน้ม (Trend)")
        trend_df = df_merge.groupby(['เดือน-ปี', 'QC'])['ยอดสุทธิ'].sum().reset_index()
        if not trend_df.empty:
            fig_trend = px.line(trend_df, x='เดือน-ปี', y='ยอดสุทธิ', color='QC', markers=True, color_discrete_map={'ตอง':'#6C63FF', 'ตาว':'#FF6584'})
            fig_trend.update_layout(font_family="Kanit", margin=dict(t=20, b=20))
            st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown("---")

        def draw_top_10_html(df_source, title, box_class):
            top_10 = df_source.groupby('ชื่อเรื่อง').agg({'ยอดสุทธิ':'sum', 'ภาพปก':'first'}).reset_index()
            top_10 = top_10.sort_values('ยอดสุทธิ', ascending=False).head(10)
            
            html_content = f"<div class='{box_class}'><h3 style='text-align:center; margin-bottom:25px;'>{title}</h3>"
            if top_10.empty:
                html_content += "<p style='text-align:center; color:#888;'>ยังไม่มีข้อมูล</p></div>"
                st.markdown(html_content, unsafe_allow_html=True); return

            html_content += "<div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;'>"
            for i, row in enumerate(top_10.itertuples()):
                img_url = row.ภาพปก if row.ภาพปก and str(row.ภาพปก).strip() != "" else "https://via.placeholder.com/200x300?text=No+Cover"
                card_html = f"<div class='rank-card' style='padding:10px;'><img src='{img_url}' style='width:100%; aspect-ratio:2/3; object-fit:cover; border-radius:8px; box-shadow:0 4px 8px rgba(0,0,0,0.1); margin-bottom:8px;' onerror=\"this.onerror=null;this.src='https://via.placeholder.com/200x300?text=Error';\"><div style='font-size:12px; line-height:1.2; margin-bottom:4px; font-weight:600; height:28px; overflow:hidden;'><b>#{i+1}</b> {row.ชื่อเรื่อง}</div><div style='color:#6C63FF; font-weight:bold; font-size:14px;'>฿{row.ยอดสุทธิ:,.0f}</div></div>"
                html_content += card_html
            html_content += "</div></div>"
            st.markdown(html_content.replace('\n', ''), unsafe_allow_html=True)

        all_m = sorted(df_merge['เดือน-ปี'].dropna().unique(), reverse=True)
        cur_m = all_m[0] if all_m else None

        st.subheader("🌍 Top 10 ขายดีภาพรวม (ทั้งหมด)")
        col_all1, col_all2 = st.columns(2)
        with col_all1:
            if cur_m: draw_top_10_html(df_merge[df_merge['เดือน-ปี'] == cur_m], f"📅 ประจำเดือน {cur_m}", "split-box-blue")
        with col_all2:
            draw_top_10_html(df_merge, "🌟 ตลอดกาล (All-Time)", "split-box-pink")

# ------------------------------------------
# ⚙️ หน้า 11: ตั้งค่าระบบ
# ------------------------------------------
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
