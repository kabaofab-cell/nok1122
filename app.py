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
    
    .rank-card { background: white; padding: 10px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); transition: 0.3s ease; text-align: center; border: 1px solid #e2e8f0; margin-bottom: 20px; }
    @media (prefers-color-scheme: dark) { .rank-card { background: #1e293b; border-color: #334155; } }
    .rank-img { width: 100%; aspect-ratio: 2/3; object-fit: cover; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 8px; }
    
    .btn-delete>div>button { background: linear-gradient(135deg, #FF4B4B 0%, #ff7676 100%) !important; color: white !important; }
    
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
    except (ValueError, TypeError):
        return str(raw_date_str)[:10]

# ==========================================
# 💾 2. ระบบฐานข้อมูล & โหลดข้อมูลอย่างปลอดภัย
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

# helpers draft

def get_imgbb_api_key():
    """ดึง API key จาก Streamlit secrets/env แบบปลอดภัย"""
    key = ""
    if hasattr(st, "secrets"):
        key = (
            st.secrets.get("IMGBB_API_KEY", "")
            or st.secrets.get("imgbb_api_key", "")
            or st.secrets.get("IMGBB_KEY", "")
        )

    if not key:
        import os
        key = os.getenv("IMGBB_API_KEY", "") or os.getenv("IMGBB_KEY", "")

    if not key:
        st.error("🚨 ไม่พบ IMGBB_API_KEY ใน secrets/env กรุณาตั้งค่าใน Streamlit Secrets")
        st.info('ตัวอย่าง: `IMGBB_API_KEY = "your_imgbb_key"`')
        return None
    return key


def clean_str(val):
    """แปลงค่าว่าง/NaN ให้เป็นสตริงว่าง"""
    return str(val) if pd.notna(val) and str(val).lower() != 'nan' else ''


def log_error(context, error):
    """แสดงข้อความ error มาตรฐานให้อ่านง่ายและ debug ได้"""
    st.error(f"❌ {context}: {type(error).__name__} - {error}")




def check_required_secrets():
    """ตรวจสอบความพร้อมของ secrets ที่จำเป็นตั้งแต่เริ่มแอป"""
    required_keys = ["IMGBB_API_KEY"]
    missing = [k for k in required_keys if not st.secrets.get(k)]
    if missing:
        st.warning(f"⚠️ ยังไม่ได้ตั้งค่า secrets: {', '.join(missing)} (ฟีเจอร์อัปโหลดรูปจะใช้งานไม่ได้)")


def safe_parse_date(value):
    """คืนค่าวันที่รูปแบบ YYYY-MM-DD ถ้าแปลงไม่ได้คืน None"""
    try:
        dt = pd.to_datetime(value, errors='raise')
        return dt.strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        return None


def deduplicate_dataframe(df, subset_cols):
    """ลบข้อมูลซ้ำโดยยึดแถวล่าสุด"""
    if df.empty:
        return df
    return df.drop_duplicates(subset=subset_cols, keep='last').reset_index(drop=True)


def validate_book_editor_df(df):
    """ตรวจสอบข้อมูลจาก data_editor ของหนังสือ"""
    errors = []
    for i, row in df.iterrows():
        if not str(row.get('ชื่อเรื่อง', '')).strip():
            errors.append(f"แถว {i+1}: ชื่อเรื่องห้ามว่าง")
        for ncol in ['ตอนปัจจุบัน']:
            val = pd.to_numeric(row.get(ncol), errors='coerce')
            if pd.isna(val) or val < 0:
                errors.append(f"แถว {i+1}: {ncol} ต้องเป็นเลข >= 0")
    return errors


def validate_finance_editor_df(df):
    """ตรวจสอบตารางการเงินก่อนบันทึก"""
    required = ['วันที่', 'ชื่อเรื่อง', 'แพลตฟอร์ม', 'ยอดดิบ', 'หักแพลตฟอร์ม (17%)', 'ยอดสุทธิ']
    errors = []
    for col in required:
        if col not in df.columns:
            errors.append(f"ไม่มีคอลัมน์ {col}")
    if errors:
        return errors

    for i, row in df.iterrows():
        if not safe_parse_date(row.get('วันที่')):
            errors.append(f"แถว {i+1}: วันที่ไม่ถูกต้อง")
        if not str(row.get('ชื่อเรื่อง', '')).strip():
            errors.append(f"แถว {i+1}: ชื่อเรื่องห้ามว่าง")
        if not str(row.get('แพลตฟอร์ม', '')).strip():
            errors.append(f"แถว {i+1}: แพลตฟอร์มห้ามว่าง")
    return errors


def append_audit_log(action, detail):
    """บันทึกกิจกรรมสำคัญลง session เพื่อนำไปบันทึกชีต AuditLog"""
    if 'audit_log' not in st.session_state:
        st.session_state.audit_log = pd.DataFrame(columns=['เวลา', 'การกระทำ', 'รายละเอียด'])
    new_row = pd.DataFrame([{
        'เวลา': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'การกระทำ': action,
        'รายละเอียด': detail
    }])
    st.session_state.audit_log = pd.concat([st.session_state.audit_log, new_row], ignore_index=True)


def export_section_csv(label, df, filename):
    """แสดงปุ่มดาวน์โหลด CSV"""
    if df is None or df.empty:
        st.caption(f"{label}: ยังไม่มีข้อมูลให้ดาวน์โหลด")
        return
    csv_data = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(f"⬇️ Export {label} (CSV)", data=csv_data, file_name=filename, mime='text/csv')


def upload_to_imgbb(file, timeout=20, retries=2):
    """อัปโหลดไฟล์รูปไป ImgBB พร้อม timeout/retry"""
    api_key = get_imgbb_api_key()
    if not api_key:
        return None

    with st.spinner("กำลังอัปโหลดรูปภาพไปยัง ImgBB..."):
        for attempt in range(1, retries + 1):
            try:
                res = requests.post(
                    "https://api.imgbb.com/1/upload",
                    data={"key": api_key},
                    files={"image": file.getvalue()},
                    timeout=timeout,
                )
                if res.status_code == 200:
                    return res.json().get("data", {}).get("url")
                st.warning(f"ครั้งที่ {attempt}: ImgBB ตอบกลับด้วยสถานะ {res.status_code}")
            except requests.RequestException as e:
                if attempt == retries:
                    log_error("Upload Failed", e)
                else:
                    st.warning(f"เครือข่ายมีปัญหา กำลังลองใหม่ ({attempt}/{retries})")
    return None


def parse_links(raw_link_data):
    """parse ข้อมูลลิงก์ที่เก็บแบบ JSON string ให้เป็น list เสมอ"""
    if pd.isna(raw_link_data):
        return []

    text = str(raw_link_data).strip()
    if text in ["", "nan"]:
        return []

    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


def normalize_book_record(book):
    """normalize ข้อมูลหนังสือ 1 รายการให้พร้อมใช้งานในแอป"""
    book['ภาพปก'] = clean_str(book.get('ภาพปก'))
    book['เรื่องย่อ'] = clean_str(book.get('เรื่องย่อ'))
    book['หมายเหตุ'] = clean_str(book.get('หมายเหตุ'))
    book['ลิงก์อ่าน'] = parse_links(book.get('ลิงก์อ่าน'))
    book['ลิงก์ต้นฉบับ'] = parse_links(book.get('ลิงก์ต้นฉบับ'))
    book['สถานะ'] = book.get('สถานะ', 'กำลังอัปเดต')
    book['หมวดหมู่'] = book.get('หมวดหมู่', 'ทั่วไป')
    book['QC'] = book.get('QC', 'ตอง')
    book['ตอนปัจจุบัน'] = int(book.get('ตอนปัจจุบัน', 0)) if pd.notna(book.get('ตอนปัจจุบัน')) else 0
    book['เป้าหมาย'] = int(book.get('เป้าหมาย', 1)) if pd.notna(book.get('เป้าหมาย')) else 1
    return book


def validate_books_data(books_data):
    """ตรวจสอบความถูกต้องขั้นพื้นฐานก่อนบันทึกชีต Books"""
    if not isinstance(books_data, list):
        return False, "books_data ต้องเป็น list"

    required_cols = ['ชื่อเรื่อง', 'หมวดหมู่', 'QC', 'สถานะ', 'ตอนปัจจุบัน', 'เป้าหมาย', 'ภาพปก', 'เรื่องย่อ', 'หมายเหตุ', 'ลิงก์อ่าน', 'ลิงก์ต้นฉบับ']
    for idx, book in enumerate(books_data):
        if not isinstance(book, dict):
            return False, f"รายการที่ {idx} ไม่ใช่ dict"
        for field in ['ลิงก์อ่าน', 'ลิงก์ต้นฉบับ']:
            if field in book and not isinstance(book.get(field), list):
                return False, f"{field} ของรายการที่ {idx} ต้องเป็น list"
        for col in required_cols:
            if col not in book:
                book[col] = '' if col not in ['ตอนปัจจุบัน', 'เป้าหมาย', 'ลิงก์อ่าน', 'ลิงก์ต้นฉบับ'] else (0 if col in ['ตอนปัจจุบัน', 'เป้าหมาย'] else [])

    return True, "ok"


def validate_calendar_data(calendar_df):
    """ตรวจสอบความถูกต้องของตารางคิวงานก่อนบันทึก"""
    required_cols = ['วันที่', 'ชื่อเรื่อง', 'ตอนที่']
    if calendar_df is None:
        return False, "calendar_df เป็น None"
    for col in required_cols:
        if col not in calendar_df.columns:
            return False, f"ไม่มีคอลัมน์ {col}"
    return True, "ok"

@st.cache_data(ttl=300)
def fetch_all_google_sheets():
    try:
        b_df = conn.read(worksheet="Books", ttl=0)
        f_df = conn.read(worksheet="Finance", ttl=0)
        c_df = conn.read(worksheet="Calendar", ttl=0)
        s_df = conn.read(worksheet="Settings", ttl=0)
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
            
        st.cache_data.clear()
        st.toast(f"✅ บันทึกข้อมูลเรียบร้อยแล้ว!")
    except Exception as e: 
        log_error("Error saving", e)

# ==========================================
# 🌟 ระบบป๊อปอัปจัดการรายวัน (อุดช่องโหว่พิมพ์ค้างด้วย Form)
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
        day_events['ชื่อเรื่อง'] = day_events['ชื่อเรื่อง'].apply(lambda x: x if x in options else options[0])

    try:
        with st.form(key=f"form_stable_{selected_date}"):
            edited_df = st.data_editor(
                day_events, 
                column_config={
                    "ชื่อเรื่อง": st.column_config.SelectboxColumn("ชื่อเรื่อง", options=options, required=True),
                    "ตอนที่": st.column_config.TextColumn("ช่วงตอนที่อัป", required=False)
                },
                num_rows="dynamic",
                use_container_width=True
            )
            
            submitted = st.form_submit_button("💾 บันทึกตารางคิวงาน", type="primary", use_container_width=True)
            
            if submitted:
                valid_df = edited_df.dropna(subset=['ชื่อเรื่อง'])
                valid_df = valid_df[valid_df['ชื่อเรื่อง'].astype(str).str.strip() != '']
                valid_df['วันที่'] = selected_date
                
                st.session_state.calendar_db = st.session_state.calendar_db[st.session_state.calendar_db['วันที่'] != selected_date]
                if not valid_df.empty:
                    st.session_state.calendar_db = pd.concat([st.session_state.calendar_db, valid_df], ignore_index=True)
                
                st.session_state.last_processed_state = None
                save_data(["Calendar"]) # บันทึกเฉพาะปฏิทิน
                st.rerun()

    except Exception as e:
        st.error("พบข้อมูลขัดข้องในระบบ กรุณากดปุ่มเพื่อรีเซ็ตงานของวันนี้")
        if st.button("🗑️ ล้างข้อมูลและเริ่มใหม่"):
            st.session_state.calendar_db = st.session_state.calendar_db[st.session_state.calendar_db['วันที่'] != selected_date]
            save_data(["Calendar"])
            st.rerun()



def render_system_health_panel():
    """แสดงสถานะความพร้อมของระบบแบบย่อ"""
    st.subheader("🩺 สุขภาพระบบ")
    has_imgbb = bool(get_imgbb_api_key())
    books_rows = len(st.session_state.get('books_data', []))
    finance_rows = len(st.session_state.get('finance_db', pd.DataFrame()))
    calendar_rows = len(st.session_state.get('calendar_db', pd.DataFrame()))
    audit_rows = len(st.session_state.get('audit_log', pd.DataFrame()))

    c1, c2, c3 = st.columns(3)
    c1.metric("ImgBB Key", "พร้อม" if has_imgbb else "ไม่พร้อม")
    c2.metric("Books", books_rows)
    c3.metric("Finance", finance_rows)
    c4, c5 = st.columns(2)
    c4.metric("Calendar", calendar_rows)
    c5.metric("Audit Log", audit_rows)


def render_audit_log_viewer():
    """หน้าแสดงประวัติการแก้ไขพร้อมตัวกรอง"""
    st.title("🧾 ประวัติการแก้ไข")
    audit_df = st.session_state.get('audit_log', pd.DataFrame(columns=['เวลา', 'การกระทำ', 'รายละเอียด']))
    if audit_df.empty:
        st.info("ยังไม่มีประวัติการแก้ไข")
        return

    df = audit_df.copy()
    df['เวลา'] = pd.to_datetime(df['เวลา'], errors='coerce')
    actions = sorted(df['การกระทำ'].dropna().astype(str).unique().tolist())

    c1, c2, c3 = st.columns(3)
    action_filter = c1.multiselect("การกระทำ", actions)
    keyword = c2.text_input("ค้นหา (รายละเอียด)")
    days = c3.selectbox("ช่วงเวลา", [7, 30, 90, 365], index=1)

    since = pd.Timestamp.now() - pd.Timedelta(days=days)
    filtered = df[df['เวลา'] >= since]
    if action_filter:
        filtered = filtered[filtered['การกระทำ'].isin(action_filter)]
    if keyword.strip():
        filtered = filtered[filtered['รายละเอียด'].astype(str).str.contains(keyword.strip(), case=False, na=False)]

    filtered = filtered.sort_values('เวลา', ascending=False)
    st.dataframe(filtered.head(500), use_container_width=True)
    export_section_csv('AuditLog', filtered, 'audit_log_filtered.csv')

# ==========================================
# 📱 3. ระบบนำทาง (Sidebar)
# ==========================================
st.sidebar.markdown("<h2 style='text-align: center; color: #818cf8; font-weight: 700; margin-bottom: 20px;'>💎 Nok-kaew Admin</h2>", unsafe_allow_html=True)

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
    st.title("📊 สรุปภาพรวม (Dashboard)")
    render_system_health_panel()
    
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

    st.markdown("---")
    st.subheader("🏆 10 อันดับนิยายขายดีประจำเดือน")
    if not df_finance.empty:
        df_finance['เดือน-ปี'] = pd.to_datetime(df_finance['วันที่']).dt.strftime('%Y-%m')
        avail_months = sorted(df_finance['เดือน-ปี'].dropna().unique(), reverse=True)
        
        if avail_months:
            selected_dash_month = st.selectbox("📌 เลือกเดือนที่ต้องการดูยอดขาย", avail_months, key="dash_month_selector")
            df_month = df_finance[df_finance['เดือน-ปี'] == selected_dash_month]
            
            if not df_month.empty:
                df_month['ยอดสุทธิ'] = pd.to_numeric(df_month['ยอดสุทธิ'], errors='coerce').fillna(0)
                top10 = df_month.groupby('ชื่อเรื่อง')['ยอดสุทธิ'].sum().reset_index()
                top10 = top10.sort_values(by='ยอดสุทธิ', ascending=False).head(10)
                top10.index = range(1, len(top10) + 1)
                
                dash_c1, dash_c2 = st.columns([1, 2])
                with dash_c1:
                    st.dataframe(top10.style.format({"ยอดสุทธิ": "฿{:,.2f}"}), use_container_width=True)
                with dash_c2:
                    fig_top10 = px.bar(
                        top10, x='ยอดสุทธิ', y='ชื่อเรื่อง', orientation='h', 
                        title=f"Top 10 Bestsellers ({selected_dash_month})", 
                        text='ยอดสุทธิ', color='ยอดสุทธิ', color_continuous_scale="Purp"
                    )
                    fig_top10.update_traces(texttemplate='฿%{text:,.0f}', textposition='outside')
                    fig_top10.update_layout(yaxis={'categoryorder':'total ascending'}, font_family="Kanit", coloraxis_showscale=False)
                    st.plotly_chart(fig_top10, use_container_width=True)
            else:
                st.info("ไม่มีข้อมูลยอดขายในเดือนที่เลือก")

# ------------------------------------------
# 📅 หน้า 2: ปฏิทินคิวงาน (Smart Flex)
# ------------------------------------------
elif menu == "📅 ปฏิทินคิวงาน":
    st.title("📅 ปฏิทินจดคิวงาน")
    st.info("💡 คลิกที่ช่องวันที่เพื่อเพิ่มหรือแก้ไขคิวงานของวันนั้นๆ (ระบบรองรับงานจำนวนมากโดยไม่ทำให้ตารางเสียทรง)")
    
    unique_novels = [b['ชื่อเรื่อง'] for b in st.session_state.books_data] if st.session_state.books_data else []
    
    colors = ["#fca5a5", "#93c5fd", "#86efac", "#fcd34d", "#d8b4fe", "#5eead4", "#f9a8d4", "#bef264", "#fdba74", "#94a3b8"]
    color_map = {novel: colors[i % len(colors)] for i, novel in enumerate(unique_novels)}

    events = []
    if not st.session_state.calendar_db.empty:
        for idx, row in st.session_state.calendar_db.iterrows():
            novel_name = str(row.get('ชื่อเรื่อง', ''))
            chap = str(row.get('ตอนที่', ''))
            
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
    
    calendar_options = {
        "timeZone": "Asia/Bangkok",
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,timeGridWeek"},
        "initialView": "dayGridMonth",
        "selectable": True,
        "height": "auto",
        "contentHeight": "auto",
        "aspectRatio": 1.5,
        "dayMaxEvents": True,
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
        st.session_state.calendar_db = deduplicate_dataframe(edited_cal, ['วันที่', 'ชื่อเรื่อง', 'ตอนที่'])
        append_audit_log('แก้ไขปฏิทิน', f"จำนวน {len(st.session_state.calendar_db)} แถว")
        save_data(["Calendar", "AuditLog"]) # บันทึกเฉพาะปฏิทิน
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
                    append_audit_log('อัปโหลดปก', f"{b['ชื่อเรื่อง']}")
                    save_data(["Books", "AuditLog"]) # บันทึกเฉพาะนิยาย
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
                append_audit_log('แก้ไขนิยาย', e_title)
                save_data(["Books", "AuditLog"]) # บันทึกเฉพาะนิยาย
                st.session_state.selected_book_idx = None
                st.rerun()
            
            st.markdown("<div class='btn-delete'>", unsafe_allow_html=True)
            if del_col.button("🗑️ ลบนิยายเรื่องนี้", use_container_width=True):
                deleted_title = st.session_state.books_data[idx].get('ชื่อเรื่อง', 'ไม่ทราบชื่อ')
                st.session_state.books_data.pop(idx)
                append_audit_log('ลบนิยาย', deleted_title)
                save_data(["Books", "AuditLog"]) # บันทึกเฉพาะนิยาย
                st.session_state.selected_book_idx = None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.title("📚 จัดการนิยาย & ไฟล์")
        tab1, tab2 = st.tabs(["🖼️ แกลลอรี่นิยาย (ทั้งหมด)", "⚡ แก้ไขข้อมูลด่วน (ตาราง)"])
        
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
                            save_data(["Books"]) # บันทึกเฉพาะนิยาย
                            st.rerun()

            st.markdown('---')
            st.subheader('🔎 ค้นหาและกรองนิยาย')
            f1, f2, f3, f4 = st.columns(4)
            q_text = f1.text_input('ค้นหาชื่อเรื่อง')
            q_status = f2.selectbox('สถานะ', ['ทั้งหมด', 'กำลังอัปเดต', 'จบแล้ว', 'พักการแปล'])
            q_qc = f3.selectbox('QC', ['ทั้งหมด', 'ตอง', 'ตาว'])
            q_cat = f4.selectbox('หมวดหมู่', ['ทั้งหมด'] + st.session_state.app_settings['categories'])

            books_with_idx = [{'data': b, 'orig_idx': idx} for idx, b in enumerate(st.session_state.books_data)]
            filtered_books = []
            for item in books_with_idx:
                b = item['data']
                if q_text.strip() and q_text.strip().lower() not in str(b.get('ชื่อเรื่อง', '')).lower():
                    continue
                if q_status != 'ทั้งหมด' and b.get('สถานะ') != q_status:
                    continue
                if q_qc != 'ทั้งหมด' and b.get('QC') != q_qc:
                    continue
                if q_cat != 'ทั้งหมด' and b.get('หมวดหมู่') != q_cat:
                    continue
                filtered_books.append(item)

            all_books = filtered_books[::-1] 
            st.caption(f"ผลลัพธ์ {len(all_books)} เรื่อง")
            
            for i in range(0, len(all_books), 10):
                cols = st.columns(10)
                for j, col in enumerate(cols):
                    if i + j < len(all_books):
                        item = all_books[i+j]
                        b = item['data']
                        real_idx = item['orig_idx']
                        
                        with col:
                            img_url = b.get('ภาพปก') if b.get('ภาพปก') and str(b.get('ภาพปก')).strip() != "" else "https://via.placeholder.com/300x450"
                            card = f"<div class='rank-card' style='padding: 8px;'><img src='{img_url}' class='rank-img' onerror=\"this.onerror=null;this.src='https://via.placeholder.com/300x450';\"><div style='font-size:11px; font-weight:600; line-height:1.2; margin-bottom:5px; height:28px; overflow:hidden;'>{b['ชื่อเรื่อง']}</div></div>"
                            st.markdown(card.replace('\n',''), unsafe_allow_html=True)
                            
                            if st.button("✏️", key=f"edit_{real_idx}", use_container_width=True):
                                st.session_state.selected_book_idx = real_idx
                                st.rerun()
                                
        with tab2:
            st.info("💡 แก้ไขหมวดหมู่ สถานะ จำนวนตอน และ QC รวดเร็วผ่านตารางนี้ (แสดงผลทั้งหมด)")
            if st.session_state.books_data:
                df_quick = pd.DataFrame(st.session_state.books_data)
                df_quick['_orig_idx'] = df_quick.index
                df_show = df_quick.iloc[::-1].copy()
                
                edit_cols = ['ชื่อเรื่อง', 'หมวดหมู่', 'สถานะ', 'ตอนปัจจุบัน', 'QC']
                
                edited_df = st.data_editor(
                    df_show[edit_cols],
                    column_config={
                        "หมวดหมู่": st.column_config.SelectboxColumn("หมวดหมู่", options=st.session_state.app_settings['categories'], required=True),
                        "สถานะ": st.column_config.SelectboxColumn("สถานะ", options=["กำลังอัปเดต", "จบแล้ว", "พักการแปล"], required=True),
                        "QC": st.column_config.SelectboxColumn("QC", options=["ตอง", "ตาว"], required=True)
                    },
                    use_container_width=True, num_rows="fixed", height=500
                )
                
                if st.button("💾 บันทึกตาราง", type="primary"):
                    book_errors = validate_book_editor_df(edited_df)
                    if book_errors:
                        for err in book_errors[:5]:
                            st.warning(err)
                        st.stop()
                    for i in range(len(edited_df)):
                        real_idx = df_show.iloc[i]['_orig_idx']
                        for col in edit_cols: 
                            st.session_state.books_data[real_idx][col] = edited_df.iloc[i][col]
                    save_data(["Books"]) # บันทึกเฉพาะนิยาย
                    st.rerun()

# ------------------------------------------
# 💰 หน้า 4: บัญชี & ค่าตอบแทน
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
                    append_audit_log('เพิ่มรายรับ', f"{q_date.strftime('%Y-%m-%d')} / {q_plat} / {q_qc}")
                    save_data(["Finance", "AuditLog"]) # บันทึกเฉพาะบัญชี
                    st.rerun()
                else: 
                    st.warning("ไม่มียอดให้บันทึกครับ")
        else: 
            st.warning("ไม่พบนิยายของ QC ท่านนี้")

    with tab2:
        edited_finance = st.data_editor(st.session_state.finance_db, num_rows="dynamic", use_container_width=True)
        if st.button("💾 บันทึกตารางฐานข้อมูล"): 
            fin_errors = validate_finance_editor_df(edited_finance)
            if fin_errors:
                for err in fin_errors[:5]:
                    st.warning(err)
                st.stop()
            st.session_state.finance_db = edited_finance
            append_audit_log('แก้ไขฐานข้อมูลการเงิน', f"จำนวน {len(edited_finance)} แถว")
            save_data(["Finance", "AuditLog"]) # บันทึกเฉพาะบัญชี
            st.rerun()

    with tab3:
        if not st.session_state.finance_db.empty:
            df_fin = st.session_state.finance_db.copy()
            df_books = pd.DataFrame(st.session_state.books_data)
            
            if df_books.empty:
                df_books = pd.DataFrame(columns=['ชื่อเรื่อง', 'QC'])
            elif 'ชื่อเรื่อง' not in df_books.columns or 'QC' not in df_books.columns:
                for col in ['ชื่อเรื่อง', 'QC']:
                    if col not in df_books.columns:
                        df_books[col] = ''
                        
            df_merge = pd.merge(df_fin, df_books[['ชื่อเรื่อง', 'QC']], on='ชื่อเรื่อง', how='left')
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
# 🧾 หน้า 5: ประวัติการแก้ไข
# ------------------------------------------
elif menu == "🧾 ประวัติการแก้ไข":
    render_audit_log_viewer()

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
        
    st.markdown('---')
    st.subheader('📦 สำรองข้อมูล (Backup CSV)')
    e1, e2, e3 = st.columns(3)
    with e1:
        export_section_csv('Books', pd.DataFrame(st.session_state.books_data), 'books_backup.csv')
    with e2:
        export_section_csv('Finance', st.session_state.finance_db, 'finance_backup.csv')
    with e3:
        export_section_csv('Calendar', st.session_state.calendar_db, 'calendar_backup.csv')

    if st.button("💾 บันทึกการตั้งค่า", type="primary"):
        st.session_state.app_settings['categories'] = ed_c['ชื่อหมวดหมู่'].replace('', pd.NA).dropna().tolist()
        st.session_state.app_settings['platforms'] = ed_p['ชื่อแพลตฟอร์ม'].replace('', pd.NA).dropna().tolist()
        save_data(["Settings"]) # บันทึกเฉพาะการตั้งค่า
        st.rerun()
