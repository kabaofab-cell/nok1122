import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import json
import plotly.express as px
from datetime import datetime

# ==========================================
# 🎨 1. ตั้งค่าและดีไซน์ (Modern Premium UI)
# ==========================================
st.set_page_config(page_title="Nok-kaew Admin Pro", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, input, button { 
        font-family: 'Prompt', sans-serif !important; 
    }
    
    .stApp { background-color: #f7f9fc; }
    
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        box-shadow: 4px 0 15px rgba(0,0,0,0.03);
    }
    div[role="radiogroup"] > label {
        padding: 10px 20px;
        background: transparent;
        border-radius: 12px;
        transition: 0.3s ease;
        cursor: pointer;
        margin-bottom: 5px;
    }
    div[role="radiogroup"] > label:hover { background: #f0f4f8; transform: translateX(5px); }

    .stButton > button {
        border-radius: 25px;
        border: none;
        background: linear-gradient(135deg, #6C63FF 0%, #8A84FF 100%);
        color: white;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(108, 99, 255, 0.2);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(108, 99, 255, 0.35);
        color: white;
    }
    
    .book-card { 
        background: white; border-radius: 24px; padding: 30px; margin-bottom: 25px; 
        box-shadow: 0 8px 20px rgba(0,0,0,0.04); border-left: 8px solid #6C63FF; transition: all 0.4s ease;
    }
    .book-card:hover { transform: translateY(-5px); box-shadow: 0 15px 30px rgba(108,99,255,0.1); }
    
    .metric-card { 
        background: white; padding: 25px 20px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); 
        text-align: center; margin-bottom: 20px; border: 1px solid #f0f4f8; transition: 0.3s ease;
    }
    .metric-card:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.06); }
    .metric-card h2 { color: #2C3E50; font-size: 2.2rem; font-weight: 700; margin-top: 10px; }
    .metric-card h3 { color: #7F8C8D; font-size: 1rem; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; }

    .link-badge { 
        display: inline-block; background: #6C63FF; color: white !important; 
        padding: 6px 16px; border-radius: 20px; text-decoration: none; font-size: 13px; font-weight: 500;
        margin-right: 10px; margin-bottom: 10px; transition: 0.3s; box-shadow: 0 3px 8px rgba(108,99,255,0.2);
    }
    .link-badge:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(108, 99, 255, 0.4); }
    .link-badge-orig { background: linear-gradient(135deg, #FF6584 0%, #ff8ea4 100%); box-shadow: 0 3px 8px rgba(255,101,132,0.2); }
    
    .synopsis-box { 
        background: #f8fafc; padding: 18px; border-radius: 12px; font-size: 14px; 
        color: #4a5568; margin-top: 15px; margin-bottom: 15px; border-left: 4px solid #cbd5e0; line-height: 1.6;
    }
    
    .split-box-blue { background: linear-gradient(180deg, #e0f2fe 0%, #ffffff 100%); border: 1px solid #bae6fd; border-radius: 24px; padding: 25px; box-shadow: 0 6px 20px rgba(14, 165, 233, 0.08); margin-bottom: 20px; height: 100%; }
    .split-box-pink { background: linear-gradient(180deg, #fce7f3 0%, #ffffff 100%); border: 1px solid #fbcfe8; border-radius: 24px; padding: 25px; box-shadow: 0 6px 20px rgba(236, 72, 153, 0.08); margin-bottom: 20px; height: 100%; }
    
    /* 🤖 AI Report Boxes */
    .ai-main { background: linear-gradient(135deg, #f3f0ff 0%, #ffffff 100%); border-left: 6px solid #6C63FF; padding: 20px; border-radius: 16px; box-shadow: 0 4px 15px rgba(108,99,255,0.1); margin-bottom: 15px; }
    .ai-tong { background: linear-gradient(135deg, #fff0f3 0%, #ffffff 100%); border-left: 6px solid #FF6584; padding: 20px; border-radius: 16px; box-shadow: 0 4px 15px rgba(255,101,132,0.1); margin-bottom: 15px; }
    .ai-tao { background: linear-gradient(135deg, #f0f7ff 0%, #ffffff 100%); border-left: 6px solid #38bdf8; padding: 20px; border-radius: 16px; box-shadow: 0 4px 15px rgba(56,189,248,0.1); margin-bottom: 15px; }
    
    .cover-img { width: 100%; aspect-ratio: 2/3; object-fit: cover; border-radius: 16px; box-shadow: 0 6px 15px rgba(0,0,0,0.08); }
    .rank-card { transition: 0.3s ease; text-align: center; }
    .rank-card:hover { transform: scale(1.03); }
    </style>
    """, unsafe_allow_html=True)

def safe_image(url, img_class="cover-img"):
    if url and str(url).strip() != "": st.markdown(f'<img src="{url}" class="{img_class}">', unsafe_allow_html=True)
    else: st.info("ไม่มีรูปปก")

# ==========================================
# 💾 2. ระบบฐานข้อมูล Google Sheets
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

def safe_update(sheet_name, df):
    try: conn.update(worksheet=sheet_name, data=df)
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
            b['หมายเหตุ'] = b.get('หมายเหตุ', '')
            b['เรื่องย่อ'] = b.get('เรื่องย่อ', '')
            b['ภาพปก'] = b.get('ภาพปก', '')
            b['ตอนปัจจุบัน'] = int(b.get('ตอนปัจจุบัน', 0)) if pd.notna(b.get('ตอนปัจจุบัน')) else 0
            b['เป้าหมาย'] = int(b.get('เป้าหมาย', 1)) if pd.notna(b.get('เป้าหมาย')) else 1
        st.session_state.books_data = books
    except: st.session_state.books_data = []

    try:
        st.session_state.finance_db = conn.read(worksheet="Finance", ttl=0)
        if st.session_state.finance_db.empty: raise Exception
    except: st.session_state.finance_db = pd.DataFrame(columns=['วันที่', 'ชื่อเรื่อง', 'แพลตฟอร์ม', 'ยอดดิบ', 'หักแพลตฟอร์ม (17%)', 'ยอดสุทธิ'])

    try:
        df_settings = conn.read(worksheet="Settings", ttl=0)
        st.session_state.app_settings = {"categories": df_settings['categories'].dropna().tolist(), "platforms": df_settings['platforms'].dropna().tolist()}
    except: st.session_state.app_settings = {"categories": ["นิยายรัก", "แฟนตาซี", "นิยายวาย (BL)", "ทั่วไป"], "platforms": ["Meb", "ReadAWrite", "Dek-D"]}

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
        if df_books_save.empty: df_books_save = pd.DataFrame(columns=['ชื่อเรื่อง', 'หมวดหมู่', 'QC', 'สถานะ', 'ตอนปัจจุบัน', 'เป้าหมาย', 'ภาพปก', 'หมายเหตุ', 'เรื่องย่อ', 'ลิงก์อ่าน', 'ลิงก์ต้นฉบับ'])
        
        safe_update("Books", df_books_save)
        safe_update("Finance", st.session_state.finance_db)
        settings_df = pd.DataFrame({"categories": pd.Series(st.session_state.app_settings['categories']), "platforms": pd.Series(st.session_state.app_settings['platforms'])})
        safe_update("Settings", settings_df)
        st.toast("✅ อัปเดตข้อมูลสำเร็จ!", icon="💎")
    except Exception as e: st.error(f"เกิดข้อผิดพลาด: {e}")

if 'books_data' not in st.session_state: load_data()

# ==========================================
# 📱 3. ระบบนำทาง (Sidebar)
# ==========================================
st.sidebar.markdown("<h2 style='text-align: center; color: #6C63FF; font-weight: 700; margin-bottom: 20px;'>💎 Nok-kaew Admin</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("Navigation Menu", ["📊 Dashboard", "📚 คลังนิยาย", "⚡ แก้ไขด่วน (Quick Edit)", "💰 บัญชีรายรับ", "💸 สรุปส่วนแบ่ง (QC)", "🏆 อันดับนิยายขายดี", "⚙️ ตั้งค่าระบบ"])

# ------------------------------------------
# 📊 หน้า 1: Dashboard & AI Insights
# ------------------------------------------
if menu == "📊 Dashboard":
    st.title("📊 ภาพรวมระบบ (Dashboard)")
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
        
        # --- 1. สรุปภาพรวมและอนาคต ---
        top_cat = df_merge.groupby('หมวดหมู่')['ยอดสุทธิ'].sum().idxmax() if 'หมวดหมู่' in df_merge else "ไม่มีข้อมูล"
        top_book = df_merge.groupby('ชื่อเรื่อง')['ยอดสุทธิ'].sum().idxmax()
        near_finish = [b['ชื่อเรื่อง'] for b in st.session_state.books_data if b.get('สถานะ') == 'กำลังอัปเดต' and (int(b.get('ตอนปัจจุบัน',0))/max(int(b.get('เป้าหมาย',1)),1)) >= 0.8]
        
        main_insight = f"""
        <div class="ai-main">
            <h4 style="color:#6C63FF; margin-bottom:10px;">🌟 ภาพรวมและทิศทางอนาคต (Overall Trends)</h4>
            <p><b>นิยายชูโรงของเรา:</b> ตอนนี้เรื่อง <b>"{top_book}"</b> ยืนหนึ่งเรื่องการสร้างรายได้ครับ ในขณะที่หมวดหมู่ที่นักอ่านเปย์หนักที่สุดตกเป็นของ <b>"{top_cat}"</b></p>
            <p><b>💡 AI ขอแนะนำ:</b> ในการซื้อลิขสิทธิ์เรื่องต่อไป แนะนำให้เล็งหมวด <b>"{top_cat}"</b> เพิ่มเติมครับ เพราะฐานคนอ่านของเราชอบแนวนี้เป็นพิเศษ</p>
        """
        if near_finish:
            main_insight += f"<p><b>🚀 โอกาสทอง:</b> มีนิยายที่แปลไปแล้วเกิน 80% คือ <b>{', '.join(near_finish)}</b> เตรียมจัดแพ็กเกจ E-Book หรือติดเหรียญโปรโมทตอนจบได้เลยครับ คาดว่ายอดจะพุ่งกระฉูดแน่นอน!</p>"
        main_insight += "</div>"
        st.markdown(main_insight, unsafe_allow_html=True)
        
        # --- 2. สรุปผลงาน แยก ตอง & ตาว ---
        col_qc1, col_qc2 = st.columns(2)
        
        with col_qc1:
            df_tong = df_merge[df_merge['QC'] == 'ตอง']
            if not df_tong.empty and df_tong['ยอดสุทธิ'].sum() > 0:
                tong_top = df_tong.groupby('ชื่อเรื่อง')['ยอดสุทธิ'].sum().idxmax()
                tong_rev = df_tong['ยอดสุทธิ'].sum()
                st.markdown(f"""
                <div class="ai-tong">
                    <h4 style="color:#FF6584; margin-bottom:10px;">💖 ผลงานของ ตอง (Tong)</h4>
                    <p><b>ยอดเงินที่ทำได้รวม:</b> ฿{tong_rev:,.0f}</p>
                    <p><b>ลูกรักทำเงิน:</b> เรื่อง <b>"{tong_top}"</b> ทำยอดทะลุเป้าได้อย่างสวยงามครับ</p>
                    <p><b>💡 คำแนะนำ:</b> ตองมีฝีมือในการดึงอารมณ์เรื่อง <b>"{tong_top}"</b> ได้ดีมาก แนะนำให้ดึงนิยายแนวคล้ายๆ กันมาให้ตองดูแลเพิ่ม เพื่อรักษาโมเมนตัมยอดขายไว้ครับ!</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="ai-tong"><h4>💖 ตอง (Tong)</h4><p>กำลังรอสร้างผลงานยอดขายแรกอยู่ครับ สู้ๆ!</p></div>', unsafe_allow_html=True)
                
        with col_qc2:
            df_tao = df_merge[df_merge['QC'] == 'ตาว']
            if not df_tao.empty and df_tao['ยอดสุทธิ'].sum() > 0:
                tao_top = df_tao.groupby('ชื่อเรื่อง')['ยอดสุทธิ'].sum().idxmax()
                tao_rev = df_tao['ยอดสุทธิ'].sum()
                st.markdown(f"""
                <div class="ai-tao">
                    <h4 style="color:#38bdf8; margin-bottom:10px;">💙 ผลงานของ ตาว (Tao)</h4>
                    <p><b>ยอดเงินที่ทำได้รวม:</b> ฿{tao_rev:,.0f}</p>
                    <p><b>ลูกรักทำเงิน:</b> เรื่อง <b>"{tao_top}"</b> คือตัวท็อปในมือตาวตอนนี้เลยครับ</p>
                    <p><b>💡 คำแนะนำ:</b> หากตาวอัปเดตตอนของ <b>"{tao_top}"</b> อย่างสม่ำเสมอ หรือจัดกิจกรรมเล็กๆ ให้นักอ่าน จะช่วยบูสต์ยอดในเดือนหน้าให้ก้าวกระโดดได้อีกครับ!</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="ai-tao"><h4>💙 ตาว (Tao)</h4><p>รอเปิดตัวยอดขายสุดปังอยู่ครับ เป็นกำลังใจให้!</p></div>', unsafe_allow_html=True)

    else:
        st.info("⚠️ ระบบ AI กำลังรอข้อมูลนิยายและยอดขายเพื่อทำการวิเคราะห์ให้พี่นกแก้วอยู่นะครับ")

    st.markdown("---")
    st.subheader("📈 กราฟสรุปภาพรวม")
    c_c1, c_c2 = st.columns(2)
    with c_c1:
        if total_books > 0:
            df_b = pd.DataFrame(st.session_state.books_data)
            fig_cat = px.pie(df_b, names='หมวดหมู่', title='สัดส่วนนิยายแยกตามหมวดหมู่', hole=0.45, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_cat.update_layout(font_family="Prompt")
            st.plotly_chart(fig_cat, use_container_width=True)
    with c_c2:
        if not df_finance.empty and total_revenue > 0:
            plat_rev = df_finance.groupby('แพลตฟอร์ม')['ยอดสุทธิ'].sum().reset_index()
            fig_plat = px.bar(plat_rev, x='แพลตฟอร์ม', y='ยอดสุทธิ', title='รายได้สุทธิแยกตามแพลตฟอร์ม', text_auto='.2s', color='แพลตฟอร์ม', color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_plat.update_layout(font_family="Prompt", showlegend=False)
            st.plotly_chart(fig_plat, use_container_width=True)

# ------------------------------------------
# 📚 หน้า 2: คลังนิยาย
# ------------------------------------------
elif menu == "📚 คลังนิยาย":
    st.title("📚 จัดการคลังนิยาย")
    if st.button("🔄 ดึงข้อมูลล่าสุด / รีเฟรชหน้าจอ"): load_data(); st.rerun()

    with st.expander("✨ เพิ่มนิยายเรื่องใหม่"):
        with st.form("add_book_form"):
            c_new1, c_new2 = st.columns(2)
            new_title = c_new1.text_input("ชื่อเรื่องนิยาย")
            new_cat = c_new1.selectbox("หมวดหมู่", st.session_state.app_settings['categories'])
            new_cover = c_new2.text_input("ลิงก์รูปปก (ถ้ามี)")
            new_qc = c_new2.radio("ผู้ดูแล (QC)", ["ตอง", "ตาว"], horizontal=True)
            
            c_chap1, c_chap2 = st.columns(2)
            new_target = c_chap1.number_input("จำนวนตอนต้นฉบับ (ทั้งหมด)", min_value=1, value=100)
            new_current = c_chap2.number_input("จำนวนตอนที่แปลเสร็จแล้ว", min_value=0, value=0)
            new_synopsis = st.text_area("📔 เรื่องย่อ")
            
            if st.form_submit_button("บันทึกนิยายเรื่องใหม่"):
                if new_title:
                    st.session_state.books_data.append({
                        'ชื่อเรื่อง': new_title, 'หมวดหมู่': new_cat, 'QC': new_qc, 'สถานะ': 'กำลังอัปเดต', 
                        'ตอนปัจจุบัน': new_current, 'เป้าหมาย': new_target, 'ภาพปก': new_cover, 'หมายเหตุ': '', 
                        'เรื่องย่อ': new_synopsis, 'ลิงก์อ่าน': [], 'ลิงก์ต้นฉบับ': []
                    })
                    save_all_to_sheets(); st.rerun()

    st.markdown("---")
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    search_q = f_col1.text_input("🔍 ค้นหาชื่อเรื่อง...")
    filter_cat = f_col2.selectbox("📂 หมวดหมู่", ["ทั้งหมด"] + st.session_state.app_settings['categories'])
    filter_qc = f_col3.selectbox("👥 ผู้ดูแล (QC)", ["ทั้งหมด", "ตอง", "ตาว"])
    filter_stat = f_col4.selectbox("📌 สถานะ", ["ทั้งหมด", "กำลังอัปเดต", "จบแล้ว", "พักการแปล"])

    filtered_books = []
    for idx, b in enumerate(st.session_state.books_data):
        if search_q and search_q.lower() not in b['ชื่อเรื่อง'].lower(): continue
        if filter_cat != "ทั้งหมด" and b['หมวดหมู่'] != filter_cat: continue
        if filter_qc != "ทั้งหมด" and b.get('QC') != filter_qc: continue
        if filter_stat != "ทั้งหมด" and b.get('สถานะ') != filter_stat: continue
        b['_orig_idx'] = idx 
        filtered_books.append(b)

    for b in filtered_books:
        idx = b['_orig_idx']
        st.markdown("<div class='book-card'>", unsafe_allow_html=True)
        img_col, txt_col = st.columns([1, 4])
        
        with img_col: safe_image(b.get('ภาพปก'), "cover-img")
            
        with txt_col:
            h_col1, h_col2, h_col3 = st.columns([3, 1, 1])
            h_col1.markdown(f"<h2>{b['ชื่อเรื่อง']}</h2>", unsafe_allow_html=True)
            if h_col2.button("💰 ดูยอดขาย", key=f"rev_btn_{idx}"): st.session_state[f"show_rev_{idx}"] = not st.session_state.get(f"show_rev_{idx}", False)
            if h_col3.button("🛠️ แก้ไข", key=f"edit_btn_{idx}"): st.session_state[f"show_edit_{idx}"] = not st.session_state.get(f"show_edit_{idx}", False)

            st.write(f"**หมวดหมู่:** {b['หมวดหมู่']} | **QC:** {b.get('QC','-')} | **สถานะ:** {b.get('สถานะ', 'กำลังอัปเดต')}")
            if b.get('เรื่องย่อ'): st.markdown(f"<div class='synopsis-box'><b>เรื่องย่อ:</b><br>{b['เรื่องย่อ']}</div>", unsafe_allow_html=True)
            
            c_chap = int(b.get('ตอนปัจจุบัน', 0))
            t_chap = max(int(b.get('เป้าหมาย', 1)), 1)
            prog_val = min(int((c_chap / t_chap) * 100), 100)
            
            st.progress(prog_val)
            st.caption(f"ความคืบหน้า: แปลแล้ว {c_chap} / ต้นฉบับ {t_chap} ตอน ({prog_val}%)")

            if b.get('ลิงก์อ่าน'):
                l_h = "".join([f"<a href='{l.get('url','')}' target='_blank' class='link-badge'>🔗 {l.get('note','ลิงก์อ่าน')}</a>" for l in b['ลิงก์อ่าน'] if l.get('url')])
                st.markdown(f"**📖 อ่านนิยาย:** {l_h}", unsafe_allow_html=True)
            if b.get('ลิงก์ต้นฉบับ'):
                o_h = "".join([f"<a href='{l.get('url','')}' target='_blank' class='link-badge link-badge-orig'>🇰🇷 {l.get('note','ต้นฉบับ')}</a>" for l in b['ลิงก์ต้นฉบับ'] if l.get('url')])
                st.markdown(f"**ต้นฉบับ:** {o_h}", unsafe_allow_html=True)
            if b.get('หมายเหตุ'): st.info(f"**📝 หมายเหตุ:** {b['หมายเหตุ']}")

        if st.session_state.get(f"show_rev_{idx}", False):
            st.markdown("#### 💵 สรุปยอดขายเรื่องนี้")
            df_this = st.session_state.finance_db[st.session_state.finance_db['ชื่อเรื่อง'] == b['ชื่อเรื่อง']]
            if not df_this.empty:
                df_this['ยอดสุทธิ'] = pd.to_numeric(df_this['ยอดสุทธิ'])
                st.success(f"💰 **รายได้สุทธิรวมจากเรื่องนี้:** ฿{df_this['ยอดสุทธิ'].sum():,.2f}")
                st.dataframe(df_this[['วันที่', 'แพลตฟอร์ม', 'ยอดสุทธิ']].sort_values('วันที่', ascending=False), use_container_width=True)
            else: st.warning("ยังไม่มีการบันทึกรายได้ของเรื่องนี้ครับ")

        if st.session_state.get(f"show_edit_{idx}", False):
            st.markdown("---")
            e1, e2 = st.columns(2)
            e_title = e1.text_input("ชื่อเรื่อง", value=b['ชื่อเรื่อง'], key=f"t_{idx}")
            e_cover = e1.text_input("ภาพปก", value=b.get('ภาพปก',''), key=f"c_{idx}")
            e_stat = e2.selectbox("สถานะ", ["กำลังอัปเดต", "จบแล้ว", "พักการแปล"], index=["กำลังอัปเดต", "จบแล้ว", "พักการแปล"].index(b.get('สถานะ','กำลังอัปเดต')) if b.get('สถานะ') in ["กำลังอัปเดต", "จบแล้ว", "พักการแปล"] else 0, key=f"s_{idx}")
            e_tgt = e2.number_input("จำนวนตอนต้นฉบับ", value=int(b.get('เป้าหมาย',1)), key=f"tgt_{idx}")
            e_curr = e2.number_input("จำนวนตอนที่แปลเสร็จแล้ว", value=int(b.get('ตอนปัจจุบัน',0)), key=f"curr_{idx}")
            e_synopsis = st.text_area("📔 เรื่องย่อ", value=b.get('เรื่องย่อ',''), key=f"syn_{idx}")
            e_note = st.text_area("📝 หมายเหตุ (Note)", value=b.get('หมายเหตุ',''), key=f"n_{idx}")
            
            l1, l2 = st.columns(2)
            with l1:
                st.write("**📖 ลิงก์อ่าน**")
                df_read = pd.DataFrame(b.get('ลิงก์อ่าน', [{"url":"", "note":""}]))
                if df_read.empty: df_read = pd.DataFrame([{"url":"", "note":""}])
                edited_read = st.data_editor(df_read, num_rows="dynamic", key=f"dr_{idx}", use_container_width=True)
            with l2:
                st.write("**🇰🇷 ลิงก์ต้นฉบับ**")
                df_orig = pd.DataFrame(b.get('ลิงก์ต้นฉบับ', [{"url":"", "note":""}]))
                if df_orig.empty: df_orig = pd.DataFrame([{"url":"", "note":""}])
                edited_orig = st.data_editor(df_orig, num_rows="dynamic", key=f"do_{idx}", use_container_width=True)

            sv_col, del_col = st.columns(2)
            if sv_col.button("💾 บันทึกการแก้ไข", key=f"save_{idx}"):
                st.session_state.books_data[idx].update({'ชื่อเรื่อง': e_title, 'ภาพปก': e_cover, 'สถานะ': e_stat, 'ตอนปัจจุบัน': e_curr, 'เป้าหมาย': e_tgt, 'เรื่องย่อ': e_synopsis, 'หมายเหตุ': e_note, 'ลิงก์อ่าน': [r for r in edited_read.to_dict('records') if r.get('url')], 'ลิงก์ต้นฉบับ': [r for r in edited_orig.to_dict('records') if r.get('url')]})
                st.session_state[f"show_edit_{idx}"] = False
                save_all_to_sheets(); st.rerun()
            st.markdown("<div class='btn-delete'>", unsafe_allow_html=True)
            if del_col.button("🗑️ ลบนิยายเรื่องนี้", key=f"delete_{idx}"):
                st.session_state.books_data.pop(idx); save_all_to_sheets(); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# ⚡ หน้า 3: แก้ไขด่วน (Quick Edit)
# ------------------------------------------
elif menu == "⚡ แก้ไขด่วน (Quick Edit)":
    st.title("⚡ ระบบแก้ไขด่วนแบบตาราง (Quick Edit)")
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
        c_save, c_reset = st.columns([1, 4])
        if c_save.button("💾 บันทึกการเปลี่ยนแปลงทั้งหมด", type="primary"):
            for i in range(len(edited_df)):
                for col in edit_cols: st.session_state.books_data[i][col] = edited_df.iloc[i][col]
            save_all_to_sheets(); st.rerun()
        if c_reset.button("🔄 ล้างค่า/โหลดใหม่"): load_data(); st.rerun()

# ------------------------------------------
# 💰 หน้า 4: บัญชีรายรับ
# ------------------------------------------
elif menu == "💰 บัญชีรายรับ":
    st.title("💰 บันทึกบัญชีรายรับ")
    st.info("กรอกรายได้ดิบ ระบบจะหัก 17% ให้โดยอัตโนมัติ")
    with st.form("add_finance"):
        c1, c2 = st.columns(2)
        d = c1.date_input("วันที่")
        b = c1.selectbox("ชื่อเรื่อง", [bk['ชื่อเรื่อง'] for bk in st.session_state.books_data] if st.session_state.books_data else ["ไม่มีข้อมูล"])
        p = c2.selectbox("แพลตฟอร์ม", st.session_state.app_settings['platforms'])
        amt = c2.number_input("ยอดรายได้ดิบ (฿)", min_value=0.0)
        if st.form_submit_button("บันทึกรายได้"):
            if b != "ไม่มีข้อมูล":
                new_f = pd.DataFrame([{'วันที่':d.strftime("%Y-%m-%d"), 'ชื่อเรื่อง':b, 'แพลตฟอร์ม':p, 'ยอดดิบ':amt, 'หักแพลตฟอร์ม (17%)':amt*0.17, 'ยอดสุทธิ':amt*0.83}])
                st.session_state.finance_db = pd.concat([st.session_state.finance_db, new_f], ignore_index=True)
                save_all_to_sheets(); st.rerun()
                
    st.write("#### ✏️ ตารางแก้ไข/ลบข้อมูลรายรับ")
    edited_finance = st.data_editor(st.session_state.finance_db, num_rows="dynamic", use_container_width=True)
    if st.button("💾 บันทึกตารางบัญชีล่าสุด"): 
        st.session_state.finance_db = edited_finance; save_all_to_sheets(); st.rerun()

# ------------------------------------------
# 💸 หน้า 5: แบ่งรายได้ (QC)
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

        st.markdown("---")
        who = st.multiselect("กรองดูเฉพาะรายชื่อ:", options=['ตอง', 'ตาว'], default=['ตอง', 'ตาว'])
        st.dataframe(df_month[df_month['QC'].isin(who)][['วันที่', 'ชื่อเรื่อง', 'แพลตฟอร์ม', 'QC', 'ยอดสุทธิ']].sort_values('ยอดสุทธิ', ascending=False), use_container_width=True)

# ------------------------------------------
# 🏆 หน้า 6: อันดับนิยายขายดี (กล่องเรียบเนียน ไม่ทะลุ)
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
            fig_trend.update_layout(font_family="Prompt", margin=dict(t=20, b=20))
            st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown("---")

        def draw_top_10_html(df_source, title, box_class):
            top_10 = df_source.groupby('ชื่อเรื่อง').agg({'ยอดสุทธิ':'sum', 'ภาพปก':'first'}).reset_index()
            top_10 = top_10.sort_values('ยอดสุทธิ', ascending=False).head(10)
            
            html_content = f"<div class='{box_class}'><h3 style='text-align:center; color:#2C3E50; margin-bottom:25px;'>{title}</h3>"
            
            if top_10.empty:
                html_content += "<p style='text-align:center; color:#888;'>ยังไม่มีข้อมูล</p></div>"
                st.markdown(html_content, unsafe_allow_html=True)
                return

            html_content += "<div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;'>"
            for i, row in enumerate(top_10.itertuples()):
                img_url = row.ภาพปก if row.ภาพปก and str(row.ภาพปก).strip() else "https://via.placeholder.com/200x300?text=No+Cover"
                card_html = f"<div class='rank-card'><img src='{img_url}' style='width:100%; aspect-ratio:2/3; object-fit:cover; border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.1); margin-bottom:8px;' onerror=\"this.onerror=null;this.src='https://via.placeholder.com/200x300?text=Error';\"><div style='font-size:13px; line-height:1.2; margin-bottom:4px; font-weight:600; color:#333;'><b>#{i+1}</b> {row.ชื่อเรื่อง}</div><div style='color:#6C63FF; font-weight:bold; font-size:15px;'>฿{row.ยอดสุทธิ:,.0f}</div></div>"
                html_content += card_html
            
            html_content += "</div></div>"
            st.markdown(html_content, unsafe_allow_html=True)

        all_m = sorted(df_merge['เดือน-ปี'].dropna().unique(), reverse=True)
        cur_m = all_m[0] if all_m else None

        st.subheader("🌍 Top 10 ขายดีภาพรวม (ทั้งหมด)")
        col_all1, col_all2 = st.columns(2)
        with col_all1:
            if cur_m: draw_top_10_html(df_merge[df_merge['เดือน-ปี'] == cur_m], f"📅 ประจำเดือน {cur_m}", "split-box-blue")
        with col_all2:
            draw_top_10_html(df_merge, "🌟 ตลอดกาล (All-Time)", "split-box-pink")

        st.markdown("---")
        st.subheader("👥 Top 10 แยกตามผู้ดูแล (QC)")
        t3, t4 = st.tabs(["💖 ผลงานของ ตอง", "💙 ผลงานของ ตาว"])
        with t3:
            df_tong = df_merge[df_merge['QC'] == 'ตอง']
            c_tong1, c_tong2 = st.columns(2)
            with c_tong1: 
                if cur_m: draw_top_10_html(df_tong[df_tong['เดือน-ปี'] == cur_m], "📅 ประจำเดือนล่าสุด", "split-box-blue")
            with c_tong2: 
                draw_top_10_html(df_tong, "🌟 ตลอดกาล", "split-box-pink")
                
        with t4:
            df_tao = df_merge[df_merge['QC'] == 'ตาว']
            c_tao1, c_tao2 = st.columns(2)
            with c_tao1: 
                if cur_m: draw_top_10_html(df_tao[df_tao['เดือน-ปี'] == cur_m], "📅 ประจำเดือนล่าสุด", "split-box-blue")
            with c_tao2: 
                draw_top_10_html(df_tao, "🌟 ตลอดกาล", "split-box-pink")

# ------------------------------------------
# ⚙️ หน้า 7: ตั้งค่าระบบ
# ------------------------------------------
elif menu == "⚙️ ตั้งค่าระบบ":
    st.title("⚙️ ตั้งค่าระบบ")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📚 หมวดหมู่นิยาย")
        ed_c = st.data_editor(pd.DataFrame(st.session_state.app_settings['categories'], columns=['ชื่อหมวดหมู่']), num_rows="dynamic", use_container_width=True)
    with c2:
        st.subheader("🌐 แพลตฟอร์มรายได้")
        ed_p = st.data_editor(pd.DataFrame(st.session_state.app_settings['platforms'], columns=['ชื่อแพลตฟอร์ม']), num_rows="dynamic", use_container_width=True)
    st.markdown("---")
    if st.button("💾 บันทึกการตั้งค่าทั้งหมด"):
        st.session_state.app_settings['categories'] = ed_c['ชื่อหมวดหมู่'].replace('', pd.NA).dropna().tolist()
        st.session_state.app_settings['platforms'] = ed_p['ชื่อแพลตฟอร์ม'].replace('', pd.NA).dropna().tolist()
        save_all_to_sheets(); st.rerun()
