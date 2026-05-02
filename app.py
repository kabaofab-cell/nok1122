import streamlit as st
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection
import json
import plotly.express as px
from datetime import datetime
from streamlit_calendar import calendar

# ==========================================
# 🔑 0. การตั้งค่าความลับ (Secrets & Settings)
# ==========================================
IMGBB_API_KEY = "c2632e406b68246bd02423be8f9bf384"

st.set_page_config(page_title="Nok-kaew Admin Pro", layout="wide", page_icon="💎")

# ==========================================
# 🎨 1. ตั้งค่าและดีไซน์ (Modern Soft UI & Smart Flex)
# ==========================================
if 'selected_book_idx' not in st.session_state: 
    st.session_state.selected_book_idx = None

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, input, button { 
        font-family: 'Kanit', sans-serif !important; 
    }
    
    .stApp { background-color: #fcfcfd; }
    
    [data-testid="stSidebar"] { background-color: #ffffff; box-shadow: 4px 0 15px rgba(0,0,0,0.03); }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: #1e293b !important; font-weight: 600 !important; font-size: 15px !important; }
    @media (prefers-color-scheme: dark) {
        [data-testid="stSidebar"] { background-color: #0f172a; }
        [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: #f8fafc !important; }
        .stApp { background-color: #1e293b; }
    }
    
    div[role="radiogroup"] > label { padding: 10px 20px; background: transparent; border-radius: 12px; transition: 0.3s ease; cursor: pointer; margin-bottom: 5px; }
    div[role="radiogroup"] > label:hover { background: rgba(108, 99, 255, 0.1); transform: translateX(5px); }

    .stButton > button { border-radius: 20px; border: none; background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%); color: white; font-weight: 500; transition: all 0.3s ease; }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(129, 140, 248, 0.35); color: white; }
    
    .metric-card { background: white; padding: 25px 20px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); text-align: center; margin-bottom: 20px; border: 1px solid #e2e8f0; transition: 0.3s ease; }
    @media (prefers-color-scheme: dark) { .metric-card { background: #1e293b; border-color: #334155; } }
    .metric-card h2 { color: #818cf8; font-size: 2.2rem; font-weight: 700; margin-top: 10px; }
    
    .rank-card { background: white; padding: 15px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); transition: 0.3s ease; text-align: center; border: 1px solid #e2e8f0; margin-bottom: 20px; }
    @media (prefers-color-scheme: dark) { .rank-card { background: #1e293b; border-color: #334155; } }
    .rank-img { width: 100%; aspect-ratio: 2/3; object-fit: cover; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 12px; }
    
    .btn-delete>div>button { background: linear-gradient(135deg, #FF4B4B 0%, #ff7676 100%) !important; color: white !important; }
    
    .progress-box { background: white; border-radius: 16px; padding: 20px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.03); border: 1px solid #e2e8f0; height: 100%; }
    @media (prefers-color-scheme: dark) { .progress-box { background: #1e293b; border-color: #334155; } }
    .progress-box h4 { color: #475569; font-size: 1.1rem; margin-bottom: 15px; }
    @media (prefers-color-scheme: dark) { .progress-box h4 { color: #cbd5e1; } }
    .progress-value { font-size: 2.5rem; font-weight: 700; }
    .val-tong { color: #f87171; }
    .val-tao { color: #60a5fa; }

    /* Smart Flex Calendar CSS */
    .fc-daygrid-day-frame { min-height: 110px !important; height: 100% !important; }
    .fc-event { border-radius: 6px !important; border: none !important; padding: 2px 6px !important; font-weight: 400 !important; font-size: 0.85em !important; margin: 2px 0 !important; }
    .fc-daygrid-day-number { font-size: 0.9em !important; color: #64748b !important; padding: 8px !important; text-decoration: none !important; }
    .fc-daygrid-more-link { color: #818cf8 !important; font-weight: 500 !important; font-size: 0.85em !important; padding-left: 5px !important; }
    </style>
    """, unsafe_allow_html=True)

def safe_image(url, img_class="rank-img"):
    if url and str(url).strip() != "": 
        st.markdown(f'<img src="{url}" class="{img_class}" onerror=\"this.onerror=null;this.src=\'https://via.placeholder.com/300x450?text=Error\';\">', unsafe_allow_html=True)
    else: 
        st.markdown(f'<img src="https://via.placeholder.com/300x450?text=No+Cover" class="{img_class}">', unsafe_allow_html=True)

def get_thai_date(raw_date_str):
    try:
        if "T" in str(raw_date_str):
            dt = pd.to_datetime(raw_date_str)
            if dt.tzinfo is not None:
                dt = dt.tz_convert('Asia/Bangkok')
            else:
                dt = dt + pd.Timedelta(hours=7)
            return dt.strftime("%Y-%m-%d")
        return str(raw_date_str)[:10]
    except:
        return str(raw_date_str)[:10]

# ==========================================
# 💾 2. ระบบฐานข้อมูล & โหลดข้อมูลอย่างปลอดภัย
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

def upload_to_imgbb(file):
    with st.spinner("กำลังอัปโหลดรูปภาพไปยัง ImgBB..."):
        try:
            res = requests.post("https://api.imgbb.com/1/upload", data={"key": IMGBB_API_KEY}, files={"image": file.getvalue()})
            if res.status_code == 200: 
                return res.json()["data"]["url"]
            else: 
                st.error("เกิดข้อผิดพลาดจาก ImgBB")
                return None
        except Exception as e: 
            st.error(f"Upload Failed: {e}")
            return None

@st.cache_data(ttl=300)
def fetch_all_google_sheets():
    try:
        b_df = conn.read(worksheet="Books", ttl=0)
        f_df = conn.read(worksheet="Finance", ttl=0)
        c_df = conn.read(worksheet="Calendar", ttl=0)
        s_df = conn.read(worksheet="Settings", ttl=0)
        p_df = conn.read(worksheet="ProgressLog", ttl=0)
        return b_df, f_df, c_df, s_df, p_df
    except Exception as e:
        return None, None, None, None, None

def initialize_data():
    b_df, f_df, c_df, s_df, p_df = fetch_all_google_sheets()
    
    if b_df is None:
        st.error("🚨 ไม่สามารถเชื่อมต่อกับ Google Sheets ได้ กรุณาตรวจสอบชื่อแผ่นงานให้ถูกต้อง")
        st.stop()
        
    books = b_df.to_dict('records')
    for b in books:
        def clean_str(val): 
            return str(val) if pd.notna(val) and str(val).lower() != 'nan' else ''
        
        b['ภาพปก'] = clean_str(b.get('ภาพปก'))
        b['เรื่องย่อ'] = clean_str(b.get('เรื่องย่อ'))
        b['หมายเหตุ'] = clean_str(b.get('หมายเหตุ'))
        
        for key in ['ลิงก์อ่าน', 'ลิงก์ต้นฉบับ']:
            try: 
                l_data = b.get(key)
                b[key] = json.loads(l_data) if pd.notna(l_data) and str(l_data).strip() not in ['', 'nan'] else []
            except: 
                b[key] = []
            if not isinstance(b[key], list): 
                b[key] = []
            
        b['สถานะ'] = b.get('สถานะ', 'กำลังอัปเดต')
        b['หมวดหมู่'] = b.get('หมวดหมู่', 'ทั่วไป')
        b['QC'] = b.get('QC', 'ตอง')
        b['ตอนปัจจุบัน'] = int(b.get('ตอนปัจจุบัน', 0)) if pd.notna(b.get('ตอนปัจจุบัน')) else 0
        b['เป้าหมาย'] = int(b.get('เป้าหมาย', 1)) if pd.notna(b.get('เป้าหมาย')) else 1
    st.session_state.books_data = books

    st.session_state.finance_db = f_df if not f_df.empty else pd.DataFrame(columns=['วันที่', 'ชื่อเรื่อง', 'แพลตฟอร์ม', 'ยอดดิบ', 'หักแพลตฟอร์ม (17%)', 'ยอดสุทธิ'])
    
    # 🛠️ โหลดและล้างค่าว่างใน Calendar ทันที
    if not c_df.empty:
        st.session_state.calendar_db = c_df.dropna(how='all').dropna(subset=['วันที่', 'ชื่อเรื่อง']).reset_index(drop=True)
    else:
        st.session_state.calendar_db = pd.DataFrame(columns=['วันที่', 'ชื่อเรื่อง', 'ตอนที่'])
    
    if not s_df.empty:
        st.session_state.app_settings = {"categories": s_df['categories'].dropna().tolist(), "platforms": s_df['platforms'].dropna().tolist()}
    else:
        st.session_state.app_settings = {"categories": ["นิยายรัก", "แฟนตาซี", "นิยายวาย (BL)", "ทั่วไป"], "platforms": ["ReadToon", "KAIREW", "Facebook", "Meb", "Dek-D"]}
        
    st.session_state.progress_log_db = p_df if not p_df.empty else pd.DataFrame(columns=['วันที่', 'ชื่อเรื่อง', 'QC', 'จำนวนตอนที่เพิ่ม'])

if 'books_data' not in st.session_state:
    initialize_data()

def save_all():
    try:
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
        conn.update(worksheet="Finance", data=st.session_state.finance_db)
        
        set_df = pd.DataFrame({"categories": pd.Series(st.session_state.app_settings['categories']), "platforms": pd.Series(st.session_state.app_settings['platforms'])})
        conn.update(worksheet="Settings", data=set_df)
        
        df_prog = st.session_state.progress_log_db if not st.session_state.progress_log_db.empty else pd.DataFrame(columns=['วันที่', 'ชื่อเรื่อง', 'QC', 'จำนวนตอนที่เพิ่ม'])
        conn.update(worksheet="ProgressLog", data=df_prog)

        # 🛠️ กรองแถวว่างทิ้งก่อนบันทึกลง Calendar
        df_cal = st.session_state.calendar_db.copy()
        if not df_cal.empty:
            df_cal = df_cal.dropna(subset=['วันที่', 'ชื่อเรื่อง']).reset_index(drop=True)
        else:
            df_cal = pd.DataFrame(columns=['วันที่', 'ชื่อเรื่อง', 'ตอนที่'])
        conn.update(worksheet="Calendar", data=df_cal)
            
        st.cache_data.clear()
        st.toast("✅ บันทึกข้อมูลลงฐานข้อมูลเรียบร้อยแล้ว!")
    except Exception as e: 
        st.error(f"Error saving: {e}")

# ==========================================
# 🌟 ระบบป๊อปอัปจัดการรายวัน (เสถียร 100%)
# ==========================================
@st.dialog("📅 บันทึกคิวงานรายวัน")
def daily_manager_dialog(selected_date, unique_novels):
    st.markdown(f"**ตารางงานของวันที่:** `{selected_date}`")
    
    day_events = st.session_state.calendar_db[st.session_state.calendar_db['วันที่'] == selected_date].copy()
    options = unique_novels if unique_novels else ["ยังไม่มีข้อมูลนิยาย"]

    if day_events.empty:
        day_events = pd.DataFrame([{'ชื่อเรื่อง': options[0], 'ตอนที่': ''}])
    else:
        day_events = day_events[['ชื่อเรื่อง', 'ตอนที่']]
        day_events['ชื่อเรื่อง'] = day_events['ชื่อเรื่อง'].fillna(options[0])
        day_events['ตอนที่'] = day_events['ตอนที่'].fillna("").astype(str)
        day_events['ชื่อเรื่อง'] = day_events['ชื่อเรื่อง'].astype(str).str.strip()
        day_events['ชื่อเรื่อง'] = day_events['ชื่อเรื่อง'].apply(lambda x: x if x in options else options[0])

    try:
        edited_df = st.data_editor(
            day_events, 
            column_config={
                "ชื่อเรื่อง": st.column_config.SelectboxColumn("ชื่อเรื่อง", options=options, required=True),
                "ตอนที่": st.column_config.TextColumn("ช่วงตอนที่อัป", required=False) # อนุญาตให้เว้นว่างได้เวลาพิมพ์
            },
            num_rows="dynamic",
            use_container_width=True,
            key=f"editor_stable_{selected_date}" 
        )
        
        if st.button("💾 บันทึกตารางคิวงาน", type="primary", use_container_width=True):
            # กรองเฉพาะแถวที่มีชื่อเรื่อง
            valid_df = edited_df.dropna(subset=['ชื่อเรื่อง'])
            valid_df = valid_df[valid_df['ชื่อเรื่อง'].astype(str).str.strip() != '']
            valid_df['วันที่'] = selected_date
            
            st.session_state.calendar_db = st.session_state.calendar_db[st.session_state.calendar_db['วันที่'] != selected_date]
            if not valid_df.empty:
                st.session_state.calendar_db = pd.concat([st.session_state.calendar_db, valid_df], ignore_index=True)
            
            st.session_state.last_processed_state = None
            save_all()
            st.rerun()

    except Exception as e:
        st.error("พบข้อมูลขัดข้องในระบบ กรุณากดปุ่มเพื่อรีเซ็ตงานของวันนี้")
        if st.button("🗑️ ล้างข้อมูลและเริ่มใหม่"):
            st.session_state.calendar_db = st.session_state.calendar_db[st.session_state.calendar_db['วันที่'] != selected_date]
            save_all()
            st.rerun()

# ==========================================
# 📱 3. ระบบนำทาง (Sidebar)
# ==========================================
st.sidebar.markdown("<h2 style='text-align: center; color: #818cf8; font-weight: 700; margin-bottom: 20px;'>💎 Nok-kaew Admin</h2>", unsafe_allow_html=True)

menu_options = [
    "📊 สรุปภาพรวม", 
    "📅 ปฏิทินคิวงาน", 
    "📚 จัดการนิยาย & ไฟล์", 
    "📝 บันทึกงานแปลรายวัน", 
    "💰 บัญชี & ค่าตอบแทน", 
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
    st.title("📊 สรุปภาพรวม (Dashboard)")
    
    if st.button("🔄 โหลดข้อมูลใหม่ (Clear Cache)", type="primary"): 
        st.cache_data.clear()
        st.session_state.pop('books_data', None)
        st.rerun()
    
    total_books = len(st.session_state.books_data)
    active_books = sum(1 for b in st.session_state.books_data if b.get('สถานะ') == 'กำลังอัปเดต')
    finished_books = sum(1 for b in st.session_state.books_data if b.get('สถานะ') == 'จบแล้ว')
    
    df_finance = st.session_state.finance_db.copy()
    total_revenue = pd.to_numeric(df_finance['ยอดสุทธิ'], errors='coerce').sum() if not df_finance.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1: 
        st.markdown(f"<div class='metric-card'><h3>📚 นิยายทั้งหมด</h3><h2>{total_books}</h2></div>", unsafe_allow_html=True)
    with col2: 
        st.markdown(f"<div class='metric-card'><h3>🔥 กำลังแปล</h3><h2>{active_books}</h2></div>", unsafe_allow_html=True)
    with col3: 
        st.markdown(f"<div class='metric-card'><h3>🎉 จบแล้ว</h3><h2>{finished_books}</h2></div>", unsafe_allow_html=True)
    with col4: 
        st.markdown(f"<div class='metric-card'><h3>💰 ยอดสุทธิรวม</h3><h2 style='color:#818cf8;'>฿{total_revenue:,.0f}</h2></div>", unsafe_allow_html=True)

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
# 📅 หน้า 2: ปฏิทินคิวงาน (Smart Flex)
# ------------------------------------------
elif menu == "📅 ปฏิทินคิวงาน":
    st.title("📅 ปฏิทินจดคิวงาน")
    st.info("💡 คลิกที่ช่องวันที่เพื่อเพิ่มหรือแก้ไขคิวงานของวันนั้นๆ (ระบบรองรับงานจำนวนมากโดยไม่ทำให้ตารางเสียทรง)")
    
    unique_novels = [b['ชื่อเรื่อง'] for b in st.session_state.books_data] if st.session_state.books_data else []
    
    # โทนสีละมุนตาสำหรับป้ายชื่อเรื่อง
    colors = ["#fca5a5", "#93c5fd", "#86efac", "#fcd34d", "#d8b4fe", "#5eead4", "#f9a8d4", "#bef264", "#fdba74", "#94a3b8"]
    color_map = {novel: colors[i % len(colors)] for i, novel in enumerate(unique_novels)}

    events = []
    if not st.session_state.calendar_db.empty:
        for idx, row in st.session_state.calendar_db.iterrows():
            novel_name = str(row.get('ชื่อเรื่อง', ''))
            chap = str(row.get('ตอนที่', ''))
            
            # การดึงวันที่อย่างปลอดภัย
            raw_date = str(row.get('วันที่', ''))
            date_val = raw_date.split(" ")[0][:10] if raw_date else ""
            
            if date_val and date_val.lower() not in ['nan', 'nat', 'none', '']:
                display_title = f"[{chap}] {novel_name}" if chap and chap.lower() != 'nan' else novel_name
                events.append({
                    "id": str(idx),
                    "title": display_title,
                    "start": date_val,
                    "color": color_map.get(novel_name, "#cbd5e1"),
                    "textColor": "#1e293b",
                    "allDay": True
                })
    
    # 🛠️ ตั้งค่า Smart Flex Calendar
    calendar_options = {
        "timeZone": "Asia/Bangkok",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek",
        },
        "initialView": "dayGridMonth",
        "selectable": True,
        "height": "auto",            # ขยายความสูงตามเนื้อหา
        "contentHeight": "auto",
        "aspectRatio": 1.5,          # สัดส่วนความกว้างต่อความสูงที่พอดี
        "dayMaxEvents": True,        # ยุบงานที่ล้นเป็น pop-over (+ more)
        "expandRows": True,
        "eventDisplay": "block"
    }
    
    state = calendar(events=events, options=calendar_options, key="novel_calendar_smart")
    
    if state is not None and state.get("callback") in ["dateClick", "eventClick"]:
        current_state_str = str(state)
        
        if st.session_state.get("last_processed_state") != current_state_str:
            if state["callback"] == "dateClick":
                raw_date = state["dateClick"]["date"]
                clicked_date = get_thai_date(raw_date)
                daily_manager_dialog(clicked_date, unique_novels)
                
            elif state["callback"] == "eventClick":
                raw_date = state["eventClick"]["event"]["start"]
                clicked_date = get_thai_date(raw_date)
                daily_manager_dialog(clicked_date, unique_novels)

    st.markdown("---")
    st.subheader("⚡ ตารางตรวจสอบรายเดือน")
    st.write("ตารางสำหรับตรวจสอบความถูกต้องหรือลบข้อมูลอย่างรวดเร็ว (อัปเดตอัตโนมัติ)")
    edited_cal = st.data_editor(st.session_state.calendar_db, num_rows="dynamic", use_container_width=True, height=250)
    if st.button("💾 บันทึกตารางส่วนนี้", type="secondary"):
        st.session_state.calendar_db = edited_cal
        save_all()
        st.rerun()

# ------------------------------------------
# 📚 หน้า 3: จัดการนิยาย & ไฟล์
# ------------------------------------------
elif menu == "📚 จัดการนิยาย & ไฟล์":
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
                    save_all()
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
                save_all()
                st.session_state.selected_book_idx = None
                st.rerun()
            
            st.markdown("<div class='btn-delete'>", unsafe_allow_html=True)
            if del_col.button("🗑️ ลบนิยายเรื่องนี้", use_container_width=True):
                st.session_state.books_data.pop(idx)
                save_all()
                st.session_state.selected_book_idx = None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.title("📚 จัดการนิยาย & ไฟล์")
        tab1, tab2 = st.tabs(["🖼️ แกลลอรี่นิยาย", "⚡ แก้ไขข้อมูลด่วน (ตาราง)"])
        
        with tab1:
            with st.expander("✨ เพิ่มนิยายเรื่องใหม่"):
                with st.form("add_book_form"):
                    c_new1, c_new2 = st.columns(2)
                    new_title = c_new1.text_input("ชื่อเรื่องนิยาย")
                    new_cat = c_new1.selectbox("หมวดหมู่", st.session_state.app_settings['categories'])
                    new_cover = c_new2.text_input("ลิงก์รูปปก")
                    new_qc = c_new2.radio("ผู้ดูแล (QC)", ["ตอง", "ตาว"], horizontal=True)
                    
                    if st.form_submit_button("เพิ่มนิยาย"):
                        if new_title:
                            st.session_state.books_data.append({'ชื่อเรื่อง': new_title, 'หมวดหมู่': new_cat, 'QC': new_qc, 'สถานะ': 'กำลังอัปเดต', 'ตอนปัจจุบัน': 0, 'เป้าหมาย': 100, 'ภาพปก': new_cover, 'เรื่องย่อ': '', 'ลิงก์อ่าน': [], 'ลิงก์ต้นฉบับ': []})
                            save_all()
                            st.rerun()

            for i in range(0, len(st.session_state.books_data), 6):
                cols = st.columns(6)
                for j, col in enumerate(cols):
                    if i + j < len(st.session_state.books_data):
                        b = st.session_state.books_data[i+j]
                        b['_orig_idx'] = i+j
                        with col:
                            img_url = b.get('ภาพปก') if b.get('ภาพปก') and str(b.get('ภาพปก')).strip() != "" else "https://via.placeholder.com/300x450"
                            card = f"<div class='rank-card'><img src='{img_url}' class='rank-img' onerror=\"this.onerror=null;this.src='https://via.placeholder.com/300x450';\"><div style='font-size:13px; font-weight:600; line-height:1.3; margin-bottom:5px; height:35px; overflow:hidden;'>{b['ชื่อเรื่อง']}</div></div>"
                            st.markdown(card.replace('\n',''), unsafe_allow_html=True)
                            
                            if st.button("✏️ แก้ไข", key=f"edit_{b['_orig_idx']}", use_container_width=True):
                                st.session_state.selected_book_idx = b['_orig_idx']
                                st.rerun()
                                
        with tab2:
            st.info("💡 แก้ไขสถานะและจำนวนตอนรวดเร็วผ่านตารางนี้ได้เลยครับ")
            if st.session_state.books_data:
                df_quick = pd.DataFrame(st.session_state.books_data)
                edit_cols = ['ชื่อเรื่อง', 'สถานะ', 'ตอนปัจจุบัน']
                edited_df = st.data_editor(
                    df_quick[edit_cols],
                    column_config={"สถานะ": st.column_config.SelectboxColumn("สถานะ", options=["กำลังอัปเดต", "จบแล้ว", "พักการแปล"], required=True)},
                    use_container_width=True, num_rows="fixed", height=400
                )
                
                if st.button("💾 บันทึกตาราง", type="primary"):
                    for i in range(len(edited_df)):
                        for col in edit_cols: 
                            st.session_state.books_data[i][col] = edited_df.iloc[i][col]
                    save_all()
                    st.rerun()

# ------------------------------------------
# 📝 หน้า 4: บันทึกงานแปลรายวัน
# ------------------------------------------
elif menu == "📝 บันทึกงานแปลรายวัน":
    st.title("📝 บันทึกงานแปล & ความคืบหน้า")
    
    tab1, tab2 = st.tabs(["⚙️ อัปเดตตอน & ต้นฉบับ", "📈 สรุปสปีดการแปล"])
    with tab1:
        search_update = st.text_input("🔍 ค้นหาชื่อเรื่องที่ต้องการอัปเดตยอด...")
        for idx, b in enumerate(st.session_state.books_data):
            if search_update and search_update.lower() not in b['ชื่อเรื่อง'].lower(): 
                continue
                
            with st.expander(f"📖 {b['ชื่อเรื่อง']} | ตอนที่แปล: {b.get('ตอนปัจจุบัน', 0)} / {b.get('เป้าหมาย', 1)}"):
                c1, c2 = st.columns([1, 3])
                with c1: 
                    safe_image(b.get('ภาพปก'), "rank-img")
                with c2:
                    c_in, c_btn = st.columns([2, 1])
                    old_chap = int(b.get('ตอนปัจจุบัน', 0))
                    new_chap = c_in.number_input("อัปเดตยอดที่แปลเสร็จ", value=old_chap, min_value=0, key=f"ch_{idx}")
                    
                    if c_btn.button("💾 บันทึกยอด", key=f"sv_{idx}", type="primary"):
                        if new_chap > old_chap:
                            new_log = pd.DataFrame([{'วันที่': datetime.today().strftime('%Y-%m-%d'), 'ชื่อเรื่อง': b['ชื่อเรื่อง'], 'QC': b.get('QC', 'ตอง'), 'จำนวนตอนที่เพิ่ม': new_chap - old_chap}])
                            st.session_state.progress_log_db = pd.concat([st.session_state.progress_log_db, new_log], ignore_index=True)
                        st.session_state.books_data[idx]['ตอนปัจจุบัน'] = new_chap
                        save_all()
                        st.rerun()
                        
                    orig_data = pd.DataFrame(b.get('ลิงก์ต้นฉบับ', [{"url":"", "note":""}]))
                    st.write("**🇰🇷 ลิงก์ต้นฉบับเกาหลี**")
                    edited_orig = st.data_editor(orig_data, num_rows="dynamic", use_container_width=True, key=f"orig_{idx}")
                    
                    if st.button("💾 บันทึกลิงก์ต้นฉบับ", key=f"svo_{idx}"):
                        st.session_state.books_data[idx]['ลิงก์ต้นฉบับ'] = [r for r in edited_orig.to_dict('records') if r.get('url')]
                        save_all()
                        st.rerun()

    with tab2:
        df_prog = st.session_state.progress_log_db.copy()
        if not df_prog.empty:
            df_prog['วันที่'] = pd.to_datetime(df_prog['วันที่'])
            df_prog['จำนวนตอนที่เพิ่ม'] = pd.to_numeric(df_prog['จำนวนตอนที่เพิ่ม']).fillna(0)
            today_date = pd.Timestamp(datetime.today().date())
            start_month = today_date.replace(day=1)
            
            tong_m = df_prog[(df_prog['วันที่'] >= start_month) & (df_prog['QC'] == 'ตอง')]['จำนวนตอนที่เพิ่ม'].sum()
            tao_m = df_prog[(df_prog['วันที่'] >= start_month) & (df_prog['QC'] == 'ตาว')]['จำนวนตอนที่เพิ่ม'].sum()
            
            c1, c2, c3 = st.columns(3)
            with c1: 
                st.markdown(f"<div class='progress-box'><h4>💖 ตอง (เดือนนี้)</h4><div class='progress-value val-tong'>{int(tong_m)}</div></div>", unsafe_allow_html=True)
            with c2: 
                st.markdown(f"<div class='progress-box'><h4>💙 ตาว (เดือนนี้)</h4><div class='progress-value val-tao'>{int(tao_m)}</div></div>", unsafe_allow_html=True)
            with c3: 
                st.markdown(f"<div class='progress-box'><h4>🌍 รวมทีม (เดือนนี้)</h4><div class='progress-value' style='color:#818cf8;'>{int(tong_m + tao_m)}</div></div>", unsafe_allow_html=True)
            
            st.dataframe(df_prog.sort_values(by='วันที่', ascending=False), use_container_width=True)
        else: 
            st.write("ยังไม่มีบันทึกความคืบหน้าครับ")

# ------------------------------------------
# 💰 หน้า 5: บัญชี & ค่าตอบแทน
# ------------------------------------------
elif menu == "💰 บัญชี & ค่าตอบแทน":
    st.title("💰 จัดการบัญชี & ส่วนแบ่ง (QC)")
    
    tab1, tab2, tab3 = st.tabs(["⚡ ลงบัญชีด่วนรายคน", "📝 ฐานข้อมูลรายรับ", "💸 สรุปยอดส่วนแบ่ง"])
    
    with tab1:
        st.info("💡 เลือกระบุวันที่, แพลตฟอร์ม และผู้ดูแล (QC) ระบบจะดึงนิยายของคนนั้นมาให้กรอกยอดพร้อมกันครับ")
        c1, c2, c3 = st.columns(3)
        q_date = c1.date_input("วันที่ลงบัญชี")
        q_plat = c2.selectbox("แพลตฟอร์ม", st.session_state.app_settings['platforms'])
        q_qc = c3.selectbox("กรองตามผู้ดูแล (QC)", ["ตอง", "ตาว"])
        
        qc_books = [b['ชื่อเรื่อง'] for b in st.session_state.books_data if b.get('QC') == q_qc]
        
        if qc_books:
            df_quick_fin = pd.DataFrame({"ชื่อเรื่อง": qc_books, "ยอดดิบ": [0.0] * len(qc_books)})
            edited_q_fin = st.data_editor(df_quick_fin, column_config={"ชื่อเรื่อง": st.column_config.TextColumn("ชื่อเรื่อง", disabled=True), "ยอดดิบ": st.column_config.NumberColumn("ยอดดิบ (฿)", min_value=0.0)}, use_container_width=True, hide_index=True)
            
            if st.button("💾 บันทึกยอดรายรับทั้งหมด", type="primary"):
                new_entries = [{'วันที่': q_date.strftime("%Y-%m-%d"), 'ชื่อเรื่อง': row["ชื่อเรื่อง"], 'แพลตฟอร์ม': q_plat, 'ยอดดิบ': row["ยอดดิบ"], 'หักแพลตฟอร์ม (17%)': row["ยอดดิบ"] * 0.17, 'ยอดสุทธิ': row["ยอดดิบ"] * 0.83} for _, row in edited_q_fin.iterrows() if row["ยอดดิบ"] > 0]
                
                if new_entries:
                    st.session_state.finance_db = pd.concat([st.session_state.finance_db, pd.DataFrame(new_entries)], ignore_index=True)
                    save_all()
                    st.rerun()
                else: 
                    st.warning("ไม่มียอดให้บันทึกครับ")
        else: 
            st.warning("ไม่พบนิยายของ QC ท่านนี้")

    with tab2:
        edited_finance = st.data_editor(st.session_state.finance_db, num_rows="dynamic", use_container_width=True)
        if st.button("💾 บันทึกตารางฐานข้อมูล"): 
            st.session_state.finance_db = edited_finance
            save_all()
            st.rerun()

    with tab3:
        if not st.session_state.finance_db.empty:
            df_merge = pd.merge(st.session_state.finance_db, pd.DataFrame(st.session_state.books_data)[['ชื่อเรื่อง', 'QC']], on='ชื่อเรื่อง', how='left')
            df_merge['ยอดสุทธิ'] = pd.to_numeric(df_merge['ยอดสุทธิ']).fillna(0)
            df_merge['เดือน-ปี'] = pd.to_datetime(df_merge['วันที่']).dt.strftime('%Y-%m')
            
            sel_month = st.selectbox("📌 เลือกรอบเดือนที่ต้องการดู", sorted(df_merge['เดือน-ปี'].dropna().unique(), reverse=True))
            df_m = df_merge[df_merge['เดือน-ปี'] == sel_month]
            
            col_t, col_a, col_all = st.columns(3)
            col_t.markdown(f"<div class='metric-card'><h3 style='color:#f87171;'>💖 ยอดของ ตอง</h3><h2>฿{df_m[df_m['QC']=='ตอง']['ยอดสุทธิ'].sum():,.2f}</h2></div>", unsafe_allow_html=True)
            col_a.markdown(f"<div class='metric-card'><h3 style='color:#60a5fa;'>💙 ยอดของ ตาว</h3><h2>฿{df_m[df_m['QC']=='ตาว']['ยอดสุทธิ'].sum():,.2f}</h2></div>", unsafe_allow_html=True)
            col_all.markdown(f"<div class='metric-card'><h3>🌍 รวมสุทธิ</h3><h2>฿{df_m['ยอดสุทธิ'].sum():,.2f}</h2></div>", unsafe_allow_html=True)
            
            st.dataframe(df_m[['วันที่', 'ชื่อเรื่อง', 'แพลตฟอร์ม', 'QC', 'ยอดสุทธิ']].sort_values('ยอดสุทธิ', ascending=False), use_container_width=True)

# ------------------------------------------
# ⚙️ หน้า 6: ตั้งค่าระบบ
# ------------------------------------------
elif menu == "⚙️ ตั้งค่าระบบ":
    st.title("⚙️ ตั้งค่าหมวดหมู่และแพลตฟอร์ม")
    
    c1, c2 = st.columns(2)
    with c1: 
        st.subheader("📚 หมวดหมู่นิยาย")
        ed_c = st.data_editor(pd.DataFrame(st.session_state.app_settings['categories'], columns=['ชื่อหมวดหมู่']), num_rows="dynamic", use_container_width=True)
    with c2: 
        st.subheader("🌐 แพลตฟอร์มเผยแพร่")
        ed_p = st.data_editor(pd.DataFrame(st.session_state.app_settings['platforms'], columns=['ชื่อแพลตฟอร์ม']), num_rows="dynamic", use_container_width=True)
        
    if st.button("💾 บันทึกการตั้งค่า", type="primary"):
        st.session_state.app_settings['categories'] = ed_c['ชื่อหมวดหมู่'].replace('', pd.NA).dropna().tolist()
        st.session_state.app_settings['platforms'] = ed_p['ชื่อแพลตฟอร์ม'].replace('', pd.NA).dropna().tolist()
        save_all()
        st.rerun()
