import json

import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import plotly.express as px
from streamlit_calendar import calendar
from app_utils import (
    append_audit_log,
    check_required_secrets,
    deduplicate_dataframe,
    export_section_csv,
    get_imgbb_api_key,
    get_thai_date,
    log_error,
    normalize_book_record,
    parse_links,
    safe_image,
    safe_parse_date,
    upload_to_imgbb,
    validate_book_editor_df,
    validate_books_data,
    validate_calendar_data,
    validate_finance_editor_df,
)
from ui_components import render_app_style, render_hero, render_sidebar_brand
from ui_panels import daily_manager_dialog, render_audit_log_viewer, render_system_health_panel

# ==========================================
# 🔑 0. การตั้งค่าความลับ (Secrets & Settings)
# ==========================================
st.set_page_config(page_title="Nok-kaew Admin Pro", layout="wide", page_icon="💎")

# ==========================================
# 🎨 1. ตั้งค่าและดีไซน์ (Modern Soft UI & Smart Flex)
# ==========================================
if 'selected_book_idx' not in st.session_state: 
    st.session_state.selected_book_idx = None

render_app_style()


@st.cache_data(ttl=300, show_spinner=False)
def fetch_all_google_sheets():
    try:
        b_df = conn.read(worksheet="Books")
        f_df = conn.read(worksheet="Finance")
        c_df = conn.read(worksheet="Calendar")
        s_df = conn.read(worksheet="Settings")
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
            
        fetch_all_google_sheets.clear()
        st.toast(f"✅ บันทึกข้อมูลเรียบร้อยแล้ว!")
    except Exception as e: 
        log_error("Error saving", e)

# ==========================================
# 🌟 ระบบป๊อปอัปจัดการรายวัน (อุดช่องโหว่พิมพ์ค้างด้วย Form)
# ==========================================

# ==========================================
# 📱 3. ระบบนำทาง (Sidebar)
# ==========================================
render_sidebar_brand()

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
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Overview</div>
            <div class="hero-title">สรุปภาพรวมของระบบ</div>
            <p class="hero-subtitle">ดูสถานะนิยาย คิวงาน และรายรับได้ในหน้าเดียว พร้อมปุ่มทางลัดสำหรับรีเฟรชข้อมูลอย่างรวดเร็ว</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_system_health_panel()
    
    if st.button("🔄 โหลดข้อมูลใหม่", type="primary"): 
        fetch_all_google_sheets.clear()
        st.session_state.pop('books_data', None)
        st.session_state.pop('finance_db', None)
        st.session_state.pop('calendar_db', None)
        st.session_state.pop('app_settings', None)
        st.rerun()
    
    total_books = len(st.session_state.books_data)
    active_books = sum(1 for b in st.session_state.books_data if b.get('สถานะ') == 'กำลังอัปเดต')
    finished_books = sum(1 for b in st.session_state.books_data if b.get('สถานะ') == 'จบแล้ว')
    
    df_finance = st.session_state.finance_db.copy()
    total_revenue = pd.to_numeric(df_finance['ยอดสุทธิ'], errors='coerce').sum() if not df_finance.empty else 0

    st.markdown('<div class="section-title">ภาพรวมตัวเลขสำคัญ</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: 
        st.markdown(f"<div class='metric-card'><h3>📚 นิยายทั้งหมด</h3><h2>{total_books}</h2></div>", unsafe_allow_html=True)
    with col2: 
        st.markdown(f"<div class='metric-card'><h3>🔥 กำลังแปล</h3><h2>{active_books}</h2></div>", unsafe_allow_html=True)
    with col3: 
        st.markdown(f"<div class='metric-card'><h3>🎉 จบแล้ว</h3><h2>{finished_books}</h2></div>", unsafe_allow_html=True)
    with col4: 
        st.markdown(f"<div class='metric-card'><h3>💰 ยอดสุทธิรวม</h3><h2 style='color:#818cf8;'>฿{total_revenue:,.0f}</h2></div>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">แนวโน้มรายงาน</div>', unsafe_allow_html=True)
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
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Calendar</div>
            <div class="hero-title">ปฏิทินคิวงาน</div>
            <p class="hero-subtitle">คลิกวันที่เพื่อเพิ่มหรือแก้ไขคิวงานของวันนั้นๆ เหมาะกับการมองภาพรวมรายเดือนและแก้รายการอย่างรวดเร็ว</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info("💡 คลิกที่ช่องวันที่เพื่อเพิ่มหรือแก้ไขคิวงานของวันนั้นๆ")
    
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
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Library</div>
            <div class="hero-title">จัดการนิยาย & ไฟล์</div>
            <p class="hero-subtitle">เพิ่ม แก้ไข ลบ และอัปโหลดปกได้ในหน้าเดียว พร้อมโหมดแกลลอรี่และตารางเพื่อเลือกวิธีทำงานที่ถนัด</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
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
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Finance</div>
            <div class="hero-title">จัดการบัญชี & ส่วนแบ่ง</div>
            <p class="hero-subtitle">บันทึกรายรับได้เร็วขึ้น ดูสรุปยอดแยกตาม QC และตรวจสอบข้อมูลย้อนหลังได้สะดวก</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
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
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Audit</div>
            <div class="hero-title">ประวัติการแก้ไข</div>
            <p class="hero-subtitle">ดูว่ามีการเปลี่ยนแปลงอะไร เมื่อไหร่ และโดยใคร เพื่อให้ตามงานและตรวจสอบย้อนหลังได้ง่าย</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_audit_log_viewer()

# ------------------------------------------
# ⚙️ หน้า 6: ตั้งค่าระบบ
# ------------------------------------------
elif menu == "⚙️ ตั้งค่าระบบ":
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Settings</div>
            <div class="hero-title">ตั้งค่าระบบ</div>
            <p class="hero-subtitle">จัดการหมวดหมู่ แพลตฟอร์ม และสำรองข้อมูลได้จากหน้าเดียว</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
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
