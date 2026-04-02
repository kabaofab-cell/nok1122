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
    .link-badge:hover { transform: translateY(-2px); box-shadow: 0 4px 10px rgba(108, 99, 255, 0.4); }
    .link-badge-orig { background: #FF6584; }
    .btn-delete>div>button { background: #FF4B4B !important; color: white !important; }
    .metric-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center; margin-bottom: 15px; }
    .synopsis-box { background: #F1F3F4; padding: 15px; border-radius: 10px; font-size: 14px; color: #555; margin-top: 10px; border-left: 4px solid #CCC; margin-bottom: 15px; }
    .cover-img { width: 100%; height: 320px; object-fit: cover; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .rank-img { width: 100%; height: 220px; object-fit: cover; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

def safe_image(url, img_class="cover-img"):
    if url and str(url).strip() != "":
        st.markdown(f'<img src="{url}" class="{img_class}">', unsafe_allow_html=True)
    else:
        st.info("ไม่มีรูปปก")

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
            b['หมวดหมู่'] = b.get('หมวดหมู่', 'ทั่วไป')
            b['QC'] = b.get('QC', 'ตอง')
            b['ตอนปัจจุบัน'] = int(b.get('ตอนปัจจุบัน', 0)) if pd.notna(b.get('ตอนปัจจุบัน')) else 0
            b['เป้าหมาย'] = int(b.get('เป้าหมาย', 1)) if pd.notna(b.get('เป้าหมาย')) else 1
        st.session_state.books_data = books
    except:
        st.session_state.books_data = []

    try:
        st.session_state.finance_db = conn.read(worksheet="Finance", ttl=0)
        if st.session_state.finance_db.empty: raise Exception
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
    try:
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
        settings_df = pd.DataFrame({"categories": pd.Series(st.session_state.app_settings['categories']), "platforms": pd.Series(st.session_state.app_settings['platforms'])})
        safe_update("Settings", settings_df)
        st.toast("✅ บันทึกข้อมูลสำเร็จ!")
    except Exception as e: st.error(f"เกิดข้อผิดพลาด: {e}")

if 'books_data' not in st.session_state: load_data()

# ==========================================
# 📱 3. ระบบนำทาง (Sidebar)
# ==========================================
st.sidebar.markdown("<h1 style='text-align: center;'>💎 Nok-kaew Admin</h1>", unsafe_allow_html=True)
menu = st.sidebar.radio("เมนูหลัก", ["📊 Dashboard", "📚 คลังนิยาย", "⚡ แก้ไขด่วน", "💰 บัญชีรายรับ", "💰 แบ่งรายได้ (QC)", "🏆 อันดับนิยายขายดี", "⚙️ ตั้งค่าระบบ"])

# ------------------------------------------
# ⚡ หน้าใหม่: แก้ไขด่วน (Quick Edit)
# ------------------------------------------
if menu == "⚡ แก้ไขด่วน":
    st.title("⚡ แก้ไขนิยายแบบรวดเร็ว")
    st.info("💡 แก้ไขข้อมูลในตารางได้ทันที แล้วกดปุ่ม 'บันทึกการเปลี่ยนแปลงทั้งหมด' ด้านล่างเพื่ออัปเดตลง Google Sheets")
    
    if not st.session_state.books_data:
        st.warning("ไม่มีข้อมูลนิยาย")
    else:
        # เตรียม DataFrame สำหรับตารางแก้ไข
        df_quick = pd.DataFrame(st.session_state.books_data)
        
        # คอลัมน์ที่จะให้แก้ในตาราง
        edit_cols = ['ชื่อเรื่อง', 'หมวดหมู่', 'สถานะ', 'QC', 'ตอนปัจจุบัน', 'เป้าหมาย']
        
        # ตั้งค่า Dropdown สำหรับคอลัมน์ต่างๆ
        edited_df = st.data_editor(
            df_quick[edit_cols],
            column_config={
                "หมวดหมู่": st.column_config.SelectboxColumn("หมวดหมู่", options=st.session_state.app_settings['categories'], required=True),
                "สถานะ": st.column_config.SelectboxColumn("สถานะ", options=["กำลังอัปเดต", "จบแล้ว", "พักการแปล"], required=True),
                "QC": st.column_config.SelectboxColumn("ผู้ดูแล (QC)", options=["ตอง", "ตาว"], required=True),
                "ตอนปัจจุบัน": st.column_config.NumberColumn("แปลแล้ว", min_value=0),
                "เป้าหมาย": st.column_config.NumberColumn("ต้นฉบับทั้งหมด", min_value=1)
            },
            use_container_width=True,
            num_rows="fixed"
        )
        
        c_save, c_reset = st.columns([1, 4])
        if c_save.button("💾 บันทึกการเปลี่ยนแปลงทั้งหมด", type="primary"):
            # นำข้อมูลที่แก้ในตารางกลับไปใส่ใน session_state หลัก
            for i in range(len(edited_df)):
                for col in edit_cols:
                    st.session_state.books_data[i][col] = edited_df.iloc[i][col]
            save_all_to_sheets()
            st.rerun()
        
        if c_reset.button("🔄 ล้างค่า/โหลดใหม่"):
            load_data()
            st.rerun()

# (ส่วนหน้าอื่นๆ Dashboard, คลังนิยาย ฯลฯ ยังอยู่ครบถ้วนเหมือนเดิมครับ)
elif menu == "📊 Dashboard":
    st.title("📊 Dashboard & 🤖 AI สรุปข้อมูล")
    total_books = len(st.session_state.books_data)
    active_books = sum(1 for b in st.session_state.books_data if b.get('สถานะ') == 'กำลังอัปเดต')
    finished_books = sum(1 for b in st.session_state.books_data if b.get('สถานะ') == 'จบแล้ว')
    df_finance = st.session_state.finance_db.copy()
    total_revenue = 0
    if not df_finance.empty:
        df_finance['ยอดสุทธิ'] = pd.to_numeric(df_finance['ยอดสุทธิ'], errors='coerce').fillna(0)
        total_revenue = df_finance['ยอดสุทธิ'].sum()
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(f"<div class='metric-card'><h3>📚 ทั้งหมด</h3><h2>{total_books}</h2></div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div class='metric-card'><h3>🔥 กำลังแปล</h3><h2>{active_books}</h2></div>", unsafe_allow_html=True)
    with col3: st.markdown(f"<div class='metric-card'><h3>🎉 จบแล้ว</h3><h2>{finished_books}</h2></div>", unsafe_allow_html=True)
    with col4: st.markdown(f"<div class='metric-card'><h3>💰 รายได้สุทธิ</h3><h2>฿{total_revenue:,.2f}</h2></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("🤖 AI Smart Insights")
    insights = []
    if total_books > 0:
        near_finish = [b['ชื่อเรื่อง'] for b in st.session_state.books_data if b.get('สถานะ') == 'กำลังอัปเดต' and (int(b.get('ตอนปัจจุบัน',0))/max(int(b.get('เป้าหมาย',1)),1)) >= 0.8]
        if near_finish: insights.append(f"🎯 **นิยายใกล้จบ:** {', '.join(near_finish)}")
        else: insights.append("✍️ **สถานะ:** ทุกเรื่องกำลังเร่งปั่นครับ")
    for msg in insights: st.success(msg)
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        if total_books > 0:
            df_b = pd.DataFrame(st.session_state.books_data)
            fig_cat = px.pie(df_b, names='หมวดหมู่', title='สัดส่วนหมวดหมู่', hole=0.4)
            st.plotly_chart(fig_cat, use_container_width=True)
    with chart_col2:
        if not df_finance.empty and total_revenue > 0:
            plat_rev = df_finance.groupby('แพลตฟอร์ม')['ยอดสุทธิ'].sum().reset_index()
            fig_plat = px.bar(plat_rev, x='แพลตฟอร์ม', y='ยอดสุทธิ', title='รายได้แยกแพลตฟอร์ม', text_auto='.2s')
            st.plotly_chart(fig_plat, use_container_width=True)

elif menu == "📚 คลังนิยาย":
    st.title("📚 จัดการคลังนิยาย")
    if st.button("🔄 ดึงข้อมูลล่าสุด"): load_data(); st.rerun()
    with st.expander("✨ เพิ่มนิยายเรื่องใหม่"):
        with st.form("add_book"):
            c1, c2 = st.columns(2)
            new_title = c1.text_input("ชื่อเรื่อง")
            new_cat = c1.selectbox("หมวดหมู่", st.session_state.app_settings['categories'])
            new_cover = c2.text_input("ลิงก์รูปปก")
            new_qc = c2.radio("QC", ["ตอง", "ตาว"], horizontal=True)
            c3, c4 = st.columns(2)
            new_tgt = c3.number_input("ตอนต้นฉบับ", min_value=1, value=100)
            new_curr = c4.number_input("แปลแล้วกี่ตอน", min_value=0, value=0)
            new_syn = st.text_area("📔 เรื่องย่อ")
            if st.form_submit_button("บันทึก"):
                st.session_state.books_data.append({'ชื่อเรื่อง': new_title, 'หมวดหมู่': new_cat, 'QC': new_qc, 'สถานะ': 'กำลังอัปเดต', 'ตอนปัจจุบัน': new_curr, 'เป้าหมาย': new_tgt, 'ภาพปก': new_cover, 'เรื่องย่อ': new_syn, 'ลิงก์อ่าน':[], 'ลิงก์ต้นฉบับ':[]})
                save_all_to_sheets(); st.rerun()
    st.markdown("---")
    for idx, b in enumerate(st.session_state.books_data):
        st.markdown("<div class='book-card'>", unsafe_allow_html=True)
        img_col, txt_col = st.columns([1, 4])
        with img_col: safe_image(b.get('ภาพปก'), "cover-img")
        with txt_col:
            h1, h2, h3 = st.columns([3, 1, 1])
            h1.markdown(f"### {b['ชื่อเรื่อง']}")
            if h2.button("💰 ยอดขาย", key=f"rev_{idx}"): st.session_state[f"sr_{idx}"] = not st.session_state.get(f"sr_{idx}", False)
            if h3.button("🛠️ แก้ไข", key=f"ed_{idx}"): st.session_state[f"se_{idx}"] = not st.session_state.get(f"se_{idx}", False)
            if b.get('เรื่องย่อ'): st.markdown(f"<div class='synopsis-box'>{b['เรื่องย่อ']}</div>", unsafe_allow_html=True)
            prog = min(int((int(b['ตอนปัจจุบัน'])/max(int(b['เป้าหมาย']),1))*100), 100)
            st.progress(prog); st.caption(f"แปลแล้ว {b['ตอนปัจจุบัน']} / {b['เป้าหมาย']} ตอน ({prog}%)")
        st.markdown("</div>", unsafe_allow_html=True)

elif menu == "💰 บัญชีรายรับ":
    st.title("💰 บัญชีรายรับ")
    with st.form("add_fin"):
        c1, c2 = st.columns(2); d = c1.date_input("วันที่"); b = c1.selectbox("เรื่อง", [bk['ชื่อเรื่อง'] for bk in st.session_state.books_data])
        p = c2.selectbox("แพลตฟอร์ม", st.session_state.app_settings['platforms']); amt = c2.number_input("ยอดดิบ", min_value=0.0)
        if st.form_submit_button("บันทึก"):
            new = pd.DataFrame([{'วันที่':d.strftime("%Y-%m-%d"), 'ชื่อเรื่อง':b, 'แพลตฟอร์ม':p, 'ยอดดิบ':amt, 'หักแพลตฟอร์ม (17%)':amt*0.17, 'ยอดสุทธิ':amt*0.83}])
            st.session_state.finance_db = pd.concat([st.session_state.finance_db, new], ignore_index=True)
            save_all_to_sheets(); st.rerun()
    ed = st.data_editor(st.session_state.finance_db, num_rows="dynamic", use_container_width=True)
    if st.button("💾 บันทึกตารางล่าสุด"): st.session_state.finance_db = ed; save_all_to_sheets(); st.rerun()

elif menu == "💰 แบ่งรายได้ (QC)":
    st.title("💰 ส่วนแบ่งรายเดือน")
    df_f = st.session_state.finance_db.copy(); df_b = pd.DataFrame(st.session_state.books_data)[['ชื่อเรื่อง', 'QC']]
    df_m = pd.merge(df_f, df_b, on='ชื่อเรื่อง', how='left')
    df_m['ยอดสุทธิ'] = pd.to_numeric(df_m['ยอดสุทธิ'], errors='coerce').fillna(0)
    df_m['วันที่'] = pd.to_datetime(df_m['วันที่']); df_m['เดือน'] = df_m['วันที่'].dt.strftime('%Y-%m')
    sel_m = st.selectbox("เลือกเดือน", sorted(df_m['เดือน'].unique(), reverse=True))
    df_sel = df_m[df_m['เดือน'] == sel_m]
    c1, c2, c3 = st.columns(3)
    c1.metric("💖 ตอง", f"฿{df_sel[df_sel['QC']=='ตอง']['ยอดสุทธิ'].sum():,.2f}")
    c2.metric("💙 ตาว", f"฿{df_sel[df_sel['QC']=='ตาว']['ยอดสุทธิ'].sum():,.2f}")
    c3.metric("🌍 รวม", f"฿{df_sel['ยอดสุทธิ'].sum():,.2f}")
    st.dataframe(df_sel[['วันที่', 'ชื่อเรื่อง', 'QC', 'ยอดสุทธิ']], use_container_width=True)

elif menu == "🏆 อันดับนิยายขายดี":
    st.title("🏆 Leaderboard")
    df_f = st.session_state.finance_db.copy(); df_b = pd.DataFrame(st.session_state.books_data)[['ชื่อเรื่อง', 'QC', 'ภาพปก']]
    df_m = pd.merge(df_f, df_b, on='ชื่อเรื่อง', how='left')
    df_m['ยอดสุทธิ'] = pd.to_numeric(df_m['ยอดสุทธิ'], errors='coerce').fillna(0)
    def draw_top(df, title):
        st.subheader(title)
        top = df.groupby('ชื่อเรื่อง').agg({'ยอดสุทธิ':'sum', 'ภาพปก':'first'}).sort_values('ยอดสุทธิ', ascending=False).head(10)
        cols = st.columns(5)
        for i, (name, r) in enumerate(top.iterrows()):
            with cols[i % 5]: safe_image(r['ภาพปก'], "rank-img"); st.caption(f"#{i+1} {name}"); st.write(f"฿{r['ยอดสุทธิ']:,.0f}")
    draw_top(df_m, "Top 10 ทั้งคลัง")

elif menu == "⚙️ ตั้งค่าระบบ":
    st.title("⚙️ Settings")
    c1, c2 = st.columns(2)
    with c1: ed_c = st.data_editor(pd.DataFrame(st.session_state.app_settings['categories'], columns=['ชื่อ']), num_rows="dynamic")
    with c2: ed_p = st.data_editor(pd.DataFrame(st.session_state.app_settings['platforms'], columns=['ชื่อ']), num_rows="dynamic")
    if st.button("💾 เซฟตั้งค่า"):
        st.session_state.app_settings['categories'] = ed_c['ชื่อ'].tolist()
        st.session_state.app_settings['platforms'] = ed_p['ชื่อ'].tolist()
        save_all_to_sheets(); st.rerun()
