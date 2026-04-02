import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
from datetime import datetime

# ==========================================
# 🎨 1. ระบบดีไซน์ระดับ Premium (Modern UI)
# ==========================================
st.set_page_config(page_title="Nok-kaew Admin Pro", layout="wide", page_icon="💎")

PRIMARY_COLOR = "#6C63FF"
SECONDARY_COLOR = "#FF6584"
BG_COLOR = "#F0F2F6"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Sarabun', sans-serif;
        background-color: {BG_COLOR};
    }}

    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #2C3E50 0%, #000000 100%);
        color: white;
    }}
    
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}

    .stMetric {{
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }}

    .book-card {{
        background: white;
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        border-left: 8px solid {PRIMARY_COLOR};
    }}

    .stButton>button {{
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(90deg, {PRIMARY_COLOR} 0%, #8A84FF 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
    }}
    
    .btn-delete>div>button {{
        background: linear-gradient(90deg, #FF4B4B 0%, #FF8F8F 100%) !important;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3) !important;
    }}

    .link-badge {{
        display: inline-block;
        background: {PRIMARY_COLOR};
        color: white !important;
        padding: 5px 15px;
        border-radius: 20px;
        text-decoration: none;
        font-size: 14px;
        margin-right: 10px;
        margin-bottom: 10px;
        transition: transform 0.2s;
    }}
    .link-badge:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(108, 99, 255, 0.4);
    }}
    .link-badge-orig {{
        background: {SECONDARY_COLOR};
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 💾 2. ระบบจัดการข้อมูล (Persistent Data)
# ==========================================
BOOKS_JSON = 'nokkaew_books.json'
FINANCE_FILE = 'nokkaew_finance.csv'
SETTINGS_FILE = 'nokkaew_settings.json'

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    return {"categories": ["นิยายรัก", "แฟนตาซี", "นิยายวาย (BL)", "ทั่วไป"], "platforms": ["Meb", "ReadAWrite", "Dek-D", "Pintobook"]}

def load_data():
    if os.path.exists(BOOKS_JSON):
        with open(BOOKS_JSON, 'r', encoding='utf-8') as f: st.session_state.books_data = json.load(f)
    else: st.session_state.books_data = []

    st.session_state.finance_db = pd.read_csv(FINANCE_FILE) if os.path.exists(FINANCE_FILE) else pd.DataFrame(columns=['วันที่', 'ชื่อเรื่อง', 'แพลตฟอร์ม', 'ยอดดิบ', 'หักแพลตฟอร์ม (17%)', 'ยอดสุทธิ'])
    if 'app_settings' not in st.session_state: st.session_state.app_settings = load_settings()

def save_data():
    with open(BOOKS_JSON, 'w', encoding='utf-8') as f: json.dump(st.session_state.books_data, f, ensure_ascii=False, indent=4)
    st.session_state.finance_db.to_csv(FINANCE_FILE, index=False)
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f: json.dump(st.session_state.app_settings, f, ensure_ascii=False, indent=4)

if 'books_data' not in st.session_state: load_data()

# ==========================================
# 📱 3. เมนูนำทาง
# ==========================================
st.sidebar.markdown("<h1 style='text-align: center;'>💎 Nok-kaew</h1>", unsafe_allow_html=True)
st.sidebar.markdown("---")
menu = st.sidebar.radio("เมนูหลัก", ["📊 Dashboard", "📚 คลังนิยาย", "💰 บัญชีรายรับ", "🏆 อันดับเรื่องขายดี", "⚙️ ตั้งค่าระบบ", "🤖 AI Insights"])

df_books = pd.DataFrame(st.session_state.books_data) if st.session_state.books_data else pd.DataFrame()

# ==========================================
# 📊 หน้าที่ 1: Dashboard
# ==========================================
if menu == "📊 Dashboard":
    st.title("📊 สรุปภาพรวมรายได้")
    df_f = st.session_state.finance_db.copy()
    if not df_f.empty and not df_books.empty:
        df_f['วันที่'] = pd.to_datetime(df_f['วันที่'])
        df_f['Year'], df_f['Month'] = df_f['วันที่'].dt.year, df_f['วันที่'].dt.month
        qc_map = dict(zip(df_books['ชื่อเรื่อง'], df_books['QC']))
        df_f['QC'] = df_f['ชื่อเรื่อง'].map(qc_map).fillna('N/A')

        c1, c2, c3 = st.columns(3)
        with c1: sel_year = st.selectbox("ปี", sorted(df_f['Year'].unique(), reverse=True))
        with c2: sel_month = st.selectbox("เดือน", ["รวมทั้งปี"] + ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"])
        with c3: sel_qc = st.selectbox("ผู้ดูแล (QC)", ["ทั้งหมด", "ตอง", "ตาว"])

        df_filt = df_f[df_f['Year'] == sel_year]
        if sel_month != "รวมทั้งปี":
            m_idx = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"].index(sel_month) + 1
            df_filt = df_filt[df_filt['Month'] == m_idx]
        if sel_qc != "ทั้งหมด": df_filt = df_filt[df_filt['QC'] == sel_qc]

        m_col1, m_col2 = st.columns(2)
        m_col1.metric("รายได้ดิบทั้งหมด", f"฿ {df_filt['ยอดดิบ'].sum():,.2f}")
        m_col2.metric("รายได้สุทธิ (หลังหัก 17%)", f"฿ {df_filt['ยอดสุทธิ'].sum():,.2f}")
        
        if sel_month == "รวมทั้งปี":
            st.subheader("🗓️ ผลประกอบการตลอด 12 เดือน")
            m_names = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
            summary = pd.DataFrame({'เดือน': m_names, 'ตอง': 0.0, 'ตาว': 0.0})
            for m in range(1, 13):
                summary.at[m-1, 'ตอง'] = df_f[(df_f['Year']==sel_year) & (df_f['Month']==m) & (df_f['QC']=='ตอง')]['ยอดสุทธิ'].sum()
                summary.at[m-1, 'ตาว'] = df_f[(df_f['Year']==sel_year) & (df_f['Month']==m) & (df_f['QC']=='ตาว')]['ยอดสุทธิ'].sum()
            
            # แสดงตารางแบบปกติเพื่อลดโอกาสเกิด Error ถ้าลืมลง matplotlib
            st.dataframe(summary.set_index('เดือน').T, use_container_width=True)
            fig = px.area(summary, x='เดือน', y=['ตอง', 'ตาว'], color_discrete_sequence=[PRIMARY_COLOR, SECONDARY_COLOR], title="แนวโน้มรายได้")
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = px.bar(df_filt, x='ชื่อเรื่อง', y='ยอดสุทธิ', color='แพลตฟอร์ม', barmode='group')
            st.plotly_chart(fig, use_container_width=True)
    else: st.info("ยังไม่มีข้อมูลในระบบ")

# ==========================================
# 📚 หน้าที่ 2: คลังนิยาย
# ==========================================
elif menu == "📚 คลังนิยาย":
    st.title("📚 จัดการคลังนิยาย")
    with st.expander("✨ เพิ่มนิยายเรื่องใหม่"):
        with st.form("new_book"):
            c1, c2 = st.columns(2)
            t = c1.text_input("ชื่อเรื่อง:")
            g = c1.selectbox("หมวดหมู่:", st.session_state.app_settings['categories'])
            c = c1.text_input("ลิงก์รูปปก:")
            q = c2.radio("QC:", ["ตอง", "ตาว"], horizontal=True)
            p = c2.multiselect("แพลตฟอร์ม:", st.session_state.app_settings['platforms'])
            gl = c2.number_input("เป้าหมายจำนวนตอน:", value=150)
            if st.form_submit_button("บันทึก"):
                new_dict = {'ภาพปก':c if c else "https://via.placeholder.com/150x200", 'ชื่อเรื่อง':t, 'หมวดหมู่':g, 'แพลตฟอร์ม':", ".join(p), 'QC':q, 'สถานะ':'กำลังอัปเดต', 'ตอนปัจจุบัน':0, 'เป้าหมาย':gl, 'หมายเหตุ': "", 'ลิงก์อ่าน': [], 'ลิงก์ต้นฉบับ': []}
                st.session_state.books_data.append(new_dict)
                save_data(); st.rerun()

    st.markdown("---")
    sc1, sc2, sc3, sc4 = st.columns(4)
    sq = sc1.text_input("ค้นหา...")
    fc = sc2.selectbox("หมวดหมู่", ["ทั้งหมด"] + st.session_state.app_settings['categories'])
    fq = sc3.selectbox("ผู้ดูแล", ["ทั้งหมด", "ตอง", "ตาว"])
    fs = sc4.selectbox("สถานะ", ["ทั้งหมด", "กำลังอัปเดต", "จบแล้ว", "พักการแปล"])

    # กรองข้อมูลและแสดงผล
    for idx, b in enumerate(st.session_state.books_data):
        if sq and sq.lower() not in b['ชื่อเรื่อง'].lower(): continue
        if fc != "ทั้งหมด" and b['หมวดหมู่'] != fc: continue
        if fq != "ทั้งหมด" and b['QC'] != fq: continue
        if fs != "ทั้งหมด" and b['สถานะ'] != fs: continue
        
        st.markdown(f"<div class='book-card'>", unsafe_allow_html=True)
        ic, tc = st.columns([1, 4])
        with ic: st.image(b.get('ภาพปก', ''), use_container_width=True)
        with tc:
            c_title, c_btn = st.columns([4, 1])
            c_title.markdown(f"### {b['ชื่อเรื่อง']}")
            if c_btn.button("🛠️ แก้ไข", key=f"ed_{idx}"): st.session_state[f"edit_{idx}"] = not st.session_state.get(f"edit_{idx}", False)
            
            prog = min(int(b['ตอนปัจจุบัน']/b['เป้าหมาย']*100), 100) if b['เป้าหมาย'] > 0 else 0
            st.progress(prog)
            st.write(f"**QC:** {b['QC']} | **ตอน:** {b['ตอนปัจจุบัน']} / {b['เป้าหมาย']} | **สถานะ:** {b['สถานะ']}")
            
            if b.get('ลิงก์อ่าน'):
                links_html = "".join([f"<a href='{l['url']}' target='_blank' class='link-badge'>🔗 {l['note']}</a>" for l in b['ลิงก์อ่าน'] if l.get('url')])
                st.markdown(links_html, unsafe_allow_html=True)
            if b.get('ลิงก์ต้นฉบับ'):
                orig_html = "".join([f"<a href='{l['url']}' target='_blank' class='link-badge link-badge-orig'>🇰🇷 {l['note']}</a>" for l in b['ลิงก์ต้นฉบับ'] if l.get('url')])
                st.markdown(orig_html, unsafe_allow_html=True)

        if st.session_state.get(f"edit_{idx}", False):
            with st.form(f"f_ed_{idx}"):
                c1, c2 = st.columns(2)
                e_t = c1.text_input("ชื่อเรื่อง", value=b['ชื่อเรื่อง'])
                e_c = c1.text_input("รูปปก", value=b['ภาพปก'])
                e_s = c2.selectbox("สถานะ", ["กำลังอัปเดต", "จบแล้ว", "พักการแปล"], index=0)
                e_curr = c2.number_input("ตอนปัจจุบัน", value=int(b['ตอนปัจจุบัน']))
                
                st.write("🔗 **คลังลิงก์ (URL และ หมายเหตุ)**")
                dr = st.data_editor(pd.DataFrame(b.get('ลิงก์อ่าน', [{"url":"", "note":""}])), num_rows="dynamic", key=f"dr_{idx}")
                do = st.data_editor(pd.DataFrame(b.get('ลิงก์ต้นฉบับ', [{"url":"", "note":""}])), num_rows="dynamic", key=f"do_{idx}")
                e_n = st.text_area("หมายเหตุ", value=b.get('หมายเหตุ', ''))
                
                if st.form_submit_button("บันทึกการแก้ไข"):
                    b.update({'ชื่อเรื่อง':e_t, 'ภาพปก':e_c, 'สถานะ':e_s, 'ตอนปัจจุบัน':e_curr, 'หมายเหตุ':e_n, 'ลิงก์อ่าน':dr.to_dict('records'), 'ลิงก์ต้นฉบับ':do.to_dict('records')})
                    save_data(); st.rerun()
                st.markdown("<div class='btn-delete'>", unsafe_allow_html=True)
                if st.form_submit_button("🗑️ ลบเรื่องนี้"):
                    st.session_state.books_data.pop(idx); save_data(); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 💰 บัญชี / 🏆 อันดับ / ⚙️ ตั้งค่า (รวมโค้ดเดิม)
# ==========================================
elif menu == "💰 บัญชีรายรับ":
    st.title("💰 บันทึกรายได้")
    with st.form("add_rev"):
        c1, c2 = st.columns(2)
        d = c1.date_input("วันที่:")
        b_list = df_books['ชื่อเรื่อง'].tolist() if not df_books.empty else ["N/A"]
        b = c1.selectbox("เรื่อง:", b_list)
        p = c2.selectbox("แพลตฟอร์ม:", st.session_state.app_settings['platforms'])
        g = c2.number_input("ยอดดิบ (฿):", min_value=0.0)
        if st.form_submit_button("บันทึก"):
            new_f = pd.DataFrame([{'วันที่':d.strftime("%Y-%m-%d"), 'ชื่อเรื่อง':b, 'แพลตฟอร์ม':p, 'ยอดดิบ':g, 'หักแพลตฟอร์ม (17%)':g*0.17, 'ยอดสุทธิ':g*0.83}])
            st.session_state.finance_db = pd.concat([st.session_state.finance_db, new_f], ignore_index=True)
            save_data(); st.rerun()
    st.data_editor(st.session_state.finance_db, num_rows="dynamic", use_container_width=True)

elif menu == "🏆 อันดับเรื่องขายดี":
    st.title("🏆 อันดับความนิยม")
    df = st.session_state.finance_db.copy()
    if not df.empty:
        rank = df.groupby('ชื่อเรื่อง')['ยอดสุทธิ'].sum().reset_index().sort_values(by='ยอดสุทธิ', ascending=False)
        st.plotly_chart(px.bar(rank, x='ยอดสุทธิ', y='ชื่อเรื่อง', orientation='h', color='ยอดสุทธิ'), use_container_width=True)

elif menu == "⚙️ ตั้งค่าระบบ":
    st.title("⚙️ การตั้งค่า")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("หมวดหมู่")
        nc = st.text_input("เพิ่มหมวดหมู่:")
        if st.button("➕ เพิ่ม"):
            st.session_state.app_settings['categories'].append(nc); save_data(); st.rerun()
    with c2:
        st.subheader("แพลตฟอร์ม")
        np = st.text_input("เพิ่มแพลตฟอร์ม:")
        if st.button("➕ เพิ่มแพลตฟอร์ม"):
            st.session_state.app_settings['platforms'].append(np); save_data(); st.rerun()

elif menu == "🤖 AI Insights":
    st.title("🤖 AI Insights")
    if not st.session_state.finance_db.empty:
        st.markdown("<div class='book-card'>### 📜 จดหมายจากเลขา AI<br>กำลังวิเคราะห์ข้อมูล...</div>", unsafe_allow_html=True)
        st.info("AI วิเคราะห์: นิยายเรื่องที่ทำกำไรสูงสุดคือ " + st.session_state.finance_db.groupby('ชื่อเรื่อง')['ยอดสุทธิ'].sum().idxmax())