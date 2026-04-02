import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import json

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
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 💾 2. ระบบฐานข้อมูล Google Sheets
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # โหลดคลังนิยาย
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
            # เติมค่าว่างกัน Error
            if 'สถานะ' not in b: b['สถานะ'] = 'กำลังอัปเดต'
            if 'หมายเหตุ' not in b: b['หมายเหตุ'] = ''
        st.session_state.books_data = books
    except:
        st.session_state.books_data = []

    # โหลดบัญชี
    try:
        st.session_state.finance_db = conn.read(worksheet="Finance", ttl=0)
        if st.session_state.finance_db.empty: raise Exception
    except:
        st.session_state.finance_db = pd.DataFrame(columns=['วันที่', 'ชื่อเรื่อง', 'แพลตฟอร์ม', 'ยอดดิบ', 'หักแพลตฟอร์ม (17%)', 'ยอดสุทธิ'])

    # โหลดการตั้งค่า
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
        # 1. บันทึก Books
        books_to_save = []
        for b in st.session_state.books_data:
            temp = b.copy()
            temp['ลิงก์อ่าน'] = json.dumps(b.get('ลิงก์อ่าน', []))
            temp['ลิงก์ต้นฉบับ'] = json.dumps(b.get('ลิงก์ต้นฉบับ', []))
            books_to_save.append(temp)
        
        df_books_save = pd.DataFrame(books_to_save)
        if df_books_save.empty:
            df_books_save = pd.DataFrame(columns=['ชื่อเรื่อง', 'หมวดหมู่', 'QC', 'สถานะ', 'ตอนปัจจุบัน', 'เป้าหมาย', 'ภาพปก', 'หมายเหตุ', 'ลิงก์อ่าน', 'ลิงก์ต้นฉบับ'])
        conn.update(worksheet="Books", data=df_books_save)
        
        # 2. บันทึก Finance
        conn.update(worksheet="Finance", data=st.session_state.finance_db)
        
        # 3. บันทึก Settings
        settings_df = pd.DataFrame({
            "categories": pd.Series(st.session_state.app_settings['categories']),
            "platforms": pd.Series(st.session_state.app_settings['platforms'])
        })
        conn.update(worksheet="Settings", data=settings_df)
        
        st.toast("✅ ซิงค์ข้อมูลกับ Google Sheets สำเร็จ!")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการบันทึก: {e} \n\nโปรดตรวจสอบว่าสร้าง Tab ชื่อ 'Books', 'Finance', 'Settings' ครบถ้วนและแชร์สิทธิ์ Editor แล้ว")

if 'books_data' not in st.session_state: load_data()

# ==========================================
# 📱 3. ระบบนำทางและหน้าจอหลัก
# ==========================================
st.sidebar.markdown("<h1 style='text-align: center;'>💎 Nok-kaew Admin</h1>", unsafe_allow_html=True)
st.sidebar.markdown("---")
menu = st.sidebar.radio("เมนูหลัก", ["📚 คลังนิยาย", "💰 บัญชีรายรับ", "⚙️ ตั้งค่าระบบ"])

# ------------------------------------------
# หน้า: คลังนิยาย
# ------------------------------------------
if menu == "📚 คลังนิยาย":
    st.title("📚 จัดการคลังนิยาย")
    
    col_ref, _ = st.columns([1, 4])
    if col_ref.button("🔄 ดึงข้อมูลล่าสุด"): load_data(); st.rerun()

    # --- ฟอร์มเพิ่มนิยาย ---
    with st.expander("✨ เพิ่มนิยายเรื่องใหม่"):
        with st.form("add_book_form"):
            c1, c2 = st.columns(2)
            new_title = c1.text_input("ชื่อเรื่องนิยาย")
            new_cat = c1.selectbox("หมวดหมู่", st.session_state.app_settings['categories'])
            new_cover = c2.text_input("ลิงก์รูปปก (ถ้ามี)")
            new_qc = c2.radio("ผู้ดูแล (QC)", ["ตอง", "ตาว"], horizontal=True)
            
            if st.form_submit_button("บันทึกนิยายเรื่องใหม่"):
                if new_title:
                    new_entry = {'ชื่อเรื่อง': new_title, 'หมวดหมู่': new_cat, 'QC': new_qc, 'สถานะ': 'กำลังอัปเดต', 'ตอนปัจจุบัน': 0, 'เป้าหมาย': 150, 'ภาพปก': new_cover, 'หมายเหตุ': '', 'ลิงก์อ่าน': [], 'ลิงก์ต้นฉบับ': []}
                    st.session_state.books_data.append(new_entry)
                    save_all_to_sheets(); st.rerun()

    st.markdown("---")
    
    # --- ระบบค้นหาและฟิลเตอร์ ---
    st.subheader("🔍 ค้นหาและคัดกรอง")
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    search_q = f_col1.text_input("ค้นหาชื่อเรื่อง...")
    filter_cat = f_col2.selectbox("หมวดหมู่", ["ทั้งหมด"] + st.session_state.app_settings['categories'])
    filter_qc = f_col3.selectbox("ผู้ดูแล (QC)", ["ทั้งหมด", "ตอง", "ตาว"])
    filter_stat = f_col4.selectbox("สถานะ", ["ทั้งหมด", "กำลังอัปเดต", "จบแล้ว", "พักการแปล"])

    # กรองข้อมูล
    filtered_books = []
    for idx, b in enumerate(st.session_state.books_data):
        if search_q and search_q.lower() not in b['ชื่อเรื่อง'].lower(): continue
        if filter_cat != "ทั้งหมด" and b['หมวดหมู่'] != filter_cat: continue
        if filter_qc != "ทั้งหมด" and b.get('QC') != filter_qc: continue
        if filter_stat != "ทั้งหมด" and b.get('สถานะ') != filter_stat: continue
        b['_orig_idx'] = idx 
        filtered_books.append(b)

    # --- แสดงการ์ดนิยาย ---
    for b in filtered_books:
        idx = b['_orig_idx']
        st.markdown("<div class='book-card'>", unsafe_allow_html=True)
        img_col, txt_col = st.columns([1, 4])
        
        with img_col:
            if b.get('ภาพปก'): st.image(b['ภาพปก'], use_container_width=True)
            else: st.info("ไม่มีรูปปก")
            
        with txt_col:
            header_col, btn_col = st.columns([4, 1])
            header_col.markdown(f"### {b['ชื่อเรื่อง']}")
            if btn_col.button("🛠️ แก้ไข", key=f"edit_{idx}"):
                st.session_state[f"show_edit_{idx}"] = not st.session_state.get(f"show_edit_{idx}", False)

            st.write(f"**หมวดหมู่:** {b['หมวดหมู่']} | **QC:** {b.get('QC','-')} | **สถานะ:** {b.get('สถานะ', 'กำลังอัปเดต')}")
            st.progress(min(int(b.get('ตอนปัจจุบัน',0)/max(b.get('เป้าหมาย',1),1)*100), 100))
            st.caption(f"ตอนที่: {b.get('ตอนปัจจุบัน',0)} / {b.get('เป้าหมาย',150)}")

            # แสดงปุ่มลิงก์
            if b.get('ลิงก์อ่าน'):
                links_html = "".join([f"<a href='{l.get('url','')}' target='_blank' class='link-badge'>🔗 {l.get('note','ลิงก์อ่าน')}</a>" for l in b['ลิงก์อ่าน'] if l.get('url')])
                st.markdown(f"**📖 อ่านนิยาย:** {links_html}", unsafe_allow_html=True)
            if b.get('ลิงก์ต้นฉบับ'):
                orig_html = "".join([f"<a href='{l.get('url','')}' target='_blank' class='link-badge link-badge-orig'>🇰🇷 {l.get('note','ต้นฉบับ')}</a>" for l in b['ลิงก์ต้นฉบับ'] if l.get('url')])
                st.markdown(f"**ต้นฉบับ:** {orig_html}", unsafe_allow_html=True)
            if b.get('หมายเหตุ'):
                st.info(f"**📝 หมายเหตุ:** {b['หมายเหตุ']}")

        # --- หน้าต่างแก้ไขข้อมูล (ซ่อน/แสดง) ---
        if st.session_state.get(f"show_edit_{idx}", False):
            st.markdown("---")
            st.write("#### 🛠️ แก้ไขรายละเอียด")
            e1, e2 = st.columns(2)
            e_title = e1.text_input("ชื่อเรื่อง", value=b['ชื่อเรื่อง'], key=f"t_{idx}")
            e_cover = e1.text_input("ภาพปก", value=b.get('ภาพปก',''), key=f"c_{idx}")
            e_stat = e2.selectbox("สถานะ", ["กำลังอัปเดต", "จบแล้ว", "พักการแปล"], index=["กำลังอัปเดต", "จบแล้ว", "พักการแปล"].index(b.get('สถานะ','กำลังอัปเดต')) if b.get('สถานะ') in ["กำลังอัปเดต", "จบแล้ว", "พักการแปล"] else 0, key=f"s_{idx}")
            e_curr = e2.number_input("ตอนปัจจุบัน", value=int(b.get('ตอนปัจจุบัน',0)), key=f"curr_{idx}")
            e_note = st.text_area("📝 หมายเหตุ (Note)", value=b.get('หมายเหตุ',''), key=f"n_{idx}")
            
            st.write("#### 🔗 จัดการลิงก์ (กดช่องว่างบรรทัดล่างสุดเพื่อเพิ่มลิงก์ใหม่)")
            l1, l2 = st.columns(2)
            with l1:
                st.write("**📖 ลิงก์อ่าน (URL & ชื่อปุ่ม)**")
                df_read = pd.DataFrame(b.get('ลิงก์อ่าน', [{"url":"", "note":""}]))
                if df_read.empty: df_read = pd.DataFrame([{"url":"", "note":""}])
                edited_read = st.data_editor(df_read, num_rows="dynamic", key=f"dr_{idx}", use_container_width=True)
            with l2:
                st.write("**🇰🇷 ลิงก์ต้นฉบับ (URL & ชื่อปุ่ม)**")
                df_orig = pd.DataFrame(b.get('ลิงก์ต้นฉบับ', [{"url":"", "note":""}]))
                if df_orig.empty: df_orig = pd.DataFrame([{"url":"", "note":""}])
                edited_orig = st.data_editor(df_orig, num_rows="dynamic", key=f"do_{idx}", use_container_width=True)

            sv_col, del_col = st.columns(2)
            if sv_col.button("💾 บันทึกการแก้ไข", key=f"save_{idx}"):
                st.session_state.books_data[idx].update({
                    'ชื่อเรื่อง': e_title, 'ภาพปก': e_cover, 'สถานะ': e_stat, 'ตอนปัจจุบัน': e_curr, 'หมายเหตุ': e_note,
                    'ลิงก์อ่าน': [r for r in edited_read.to_dict('records') if r.get('url')],
                    'ลิงก์ต้นฉบับ': [r for r in edited_orig.to_dict('records') if r.get('url')]
                })
                st.session_state[f"show_edit_{idx}"] = False
                save_all_to_sheets(); st.rerun()
                
            st.markdown("<div class='btn-delete'>", unsafe_allow_html=True)
            if del_col.button("🗑️ ลบนิยายเรื่องนี้", key=f"delete_{idx}"):
                st.session_state.books_data.pop(idx)
                save_all_to_sheets(); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# หน้า: บัญชีรายรับ (อย่างย่อ)
# ------------------------------------------
elif menu == "💰 บัญชีรายรับ":
    st.title("💰 บัญชีรายรับ")
    st.info("ระบบบัญชีพร้อมใช้งานแล้ว กรุณาบันทึกข้อมูลได้เลยครับ")
    with st.form("add_finance"):
        c1, c2 = st.columns(2)
        d = c1.date_input("วันที่")
        b = c1.selectbox("ชื่อเรื่อง", [bk['ชื่อเรื่อง'] for bk in st.session_state.books_data] if st.session_state.books_data else ["N/A"])
        p = c2.selectbox("แพลตฟอร์ม", st.session_state.app_settings['platforms'])
        amt = c2.number_input("ยอดรายได้ดิบ (฿)", min_value=0.0)
        
        if st.form_submit_button("บันทึกรายได้"):
            if b != "N/A":
                new_f = pd.DataFrame([{'วันที่':d.strftime("%Y-%m-%d"), 'ชื่อเรื่อง':b, 'แพลตฟอร์ม':p, 'ยอดดิบ':amt, 'หักแพลตฟอร์ม (17%)':amt*0.17, 'ยอดสุทธิ':amt*0.83}])
                st.session_state.finance_db = pd.concat([st.session_state.finance_db, new_f], ignore_index=True)
                save_all_to_sheets(); st.rerun()
                
    st.data_editor(st.session_state.finance_db, num_rows="dynamic", use_container_width=True)
    if st.button("💾 บันทึกตารางบัญชี"): save_all_to_sheets()

# ------------------------------------------
# หน้า: ตั้งค่า
# ------------------------------------------
elif menu == "⚙️ ตั้งค่าระบบ":
    st.title("⚙️ ตั้งค่าระบบ")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("เพิ่มหมวดหมู่นิยาย")
        new_cat = st.text_input("ชื่อหมวดหมู่ใหม่")
        if st.button("เพิ่มหมวดหมู่"):
            if new_cat and new_cat not in st.session_state.app_settings['categories']:
                st.session_state.app_settings['categories'].append(new_cat)
                save_all_to_sheets(); st.rerun()
    with c2:
        st.subheader("เพิ่มแพลตฟอร์ม")
        new_plat = st.text_input("ชื่อแพลตฟอร์มใหม่")
        if st.button("เพิ่มแพลตฟอร์ม"):
            if new_plat and new_plat not in st.session_state.app_settings['platforms']:
                st.session_state.app_settings['platforms'].append(new_plat)
                save_all_to_sheets(); st.rerun()
