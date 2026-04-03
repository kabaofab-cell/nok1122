import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import json
from datetime import datetime
import urllib.parse
import random

# ==========================================
# 🎨 1. ตั้งค่าดีไซน์ & CSS (ฉบับซ่อน Toolbar)
# ==========================================
st.set_page_config(page_title="Nok-kaew Library", layout="wide", page_icon="✨")

if 'view_idx' not in st.session_state: st.session_state.view_idx = None

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700;800&display=swap');
    
    html, body, .stApp, .main { scroll-behavior: smooth !important; }
    
    .stApp { 
        font-family: 'Kanit', sans-serif !important; 
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #eff6ff 100%); 
        color: #0f172a;
    }
    
    /* 🚫 🔐 จุดสำคัญ: สั่งซ่อน Toolbar, Footer และปุ่มโปรไฟล์ทั้งหมด */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    .stDeployButton {display:none !important;}
    #viewer-badge {display: none !important;}
    
    /* ซ่อนปุ่มล่างขวา (Streamlit Profile) */
    div[data-testid="stStatusWidget"] { display: none !important; }
    button[title="View profile in Streamlit Community Cloud"] { display: none !important; }

    /* ============ 🌟 HEADER โฉมใหม่ ============ */
    .header-container { text-align: center; padding: 40px 20px 30px; position: relative; }
    .header-title {
        font-size: 4.5rem; font-weight: 800; margin: 0; padding-bottom: 10px;
        background: linear-gradient(-45deg, #0ea5e9, #6366f1, #0284c7, #8b5cf6);
        background-size: 300% auto; color: transparent; -webkit-background-clip: text; background-clip: text;
        animation: shine 4s linear infinite; text-shadow: 0 10px 30px rgba(14,165,233,0.2);
    }
    .header-subtitle { font-size: 1.2rem; color: #475569; font-weight: 500; letter-spacing: 2px; margin-top: -10px; }
    @keyframes shine { to { background-position: 300% center; } }
    
    .floating-gem { font-size: 2rem; position: absolute; top: 20px; animation: float 3s ease-in-out infinite; }
    .gem-left { left: 30%; } .gem-right { right: 30%; animation-delay: 1.5s; }
    @keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-15px); } 100% { transform: translateY(0px); } }

    /* ============ 📚 CARD แบบ HTML LINK ============ */
    a.card-link { text-decoration: none !important; display: block; }
    
    .y-card { background: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #bae6fd; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); margin-bottom: 15px; position: relative; box-shadow: 0 4px 10px rgba(14,165,233,0.08); cursor: pointer; }
    .y-card:hover { transform: translateY(-8px) scale(1.02); border-color: #38bdf8; box-shadow: 0 15px 25px rgba(14,165,233,0.25); }
    .y-img-wrapper { position: relative; width: 100%; aspect-ratio: 2/3; overflow: hidden; }
    .y-img { width: 100%; height: 100%; object-fit: cover; transition: 0.5s ease; }
    .y-card:hover .y-img { transform: scale(1.08); } 
    
    .y-info { padding: 8px 6px; text-align: center; background: white; position: relative; z-index: 2; border-top: 1px solid #f0f9ff; }
    .y-name { font-size: 11px; font-weight: 600; color: #1e293b; height: 32px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; line-height:1.4; }
    
    /* Badges */
    .rank-badge { position: absolute; top: 6px; left: 6px; background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%); color: white; padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 11px; z-index: 5; box-shadow: 0 2px 5px rgba(0,0,0,0.2); border: 1px solid #fbbf24; }
    .rank-badge-all { background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%); border-color: #a78bfa; }
    .status-badge { position: absolute; bottom: 6px; right: 6px; background: rgba(255,255,255,0.95); color: #0284c7; padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: 700; z-index: 5; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    
    .section-title { color: #0369a1; font-weight: 800; margin-top: 30px; font-size: 1.6rem; display: flex; align-items: center; gap: 10px; }
    .section-title::after { content: ''; flex: 1; height: 2px; background: linear-gradient(90deg, #bae6fd, transparent); margin-left: 15px; }
    
    .nav-link { flex: 1; text-align: center; padding: 12px 10px; border-radius: 20px; background: rgba(255,255,255,0.7); color: #0284c7; border: 1px solid #7dd3fc; font-weight: 600; font-size: 15px; text-decoration: none; transition: 0.3s; backdrop-filter: blur(5px); }
    .nav-link:hover { background: #0ea5e9; color: #ffffff; transform: translateY(-3px); box-shadow: 0 8px 15px rgba(14,165,233,0.3); }

    /* Promo Page */
    .promo-container { background: white; padding: 40px; border-radius: 30px; display: flex; gap: 40px; flex-wrap: wrap; max-width: 1050px; margin: 0 auto; border: 1px solid #e0f2fe; box-shadow: 0 20px 50px rgba(14,165,233,0.1); }
    .promo-title { color: #0f172a; font-size: 2.5rem; margin-top: 0; font-weight: 800; line-height: 1.2; }
    .promo-synopsis-box { background: linear-gradient(180deg, #f0f9ff 0%, #ffffff 100%); padding: 25px; border-radius: 16px; border-left: 6px solid #38bdf8; margin: 25px 0; border-top: 1px solid #e0f2fe; border-right: 1px solid #e0f2fe; border-bottom: 1px solid #e0f2fe; }
    
    .btn-read { background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%); color: white !important; padding: 12px 25px; border-radius: 30px; text-decoration: none; font-weight: 600; font-size: 15px; display: inline-block; transition: 0.3s; box-shadow: 0 5px 15px rgba(14,165,233,0.3); }
    .btn-read:hover { transform: translateY(-3px) scale(1.05); box-shadow: 0 8px 20px rgba(14,165,233,0.4); }
    
    .fb-link { display: inline-flex; align-items: center; background: #eff6ff; color: #1d4ed8; padding: 12px 25px; border-radius: 30px; font-weight: 600; text-decoration: none; font-size: 15px; transition: 0.3s; border: 1px solid #bfdbfe; }
    .fb-link:hover { background: #dbeafe; transform: translateX(5px); box-shadow: 0 4px 10px rgba(29,78,216,0.1); }
    
    .anchor-offset { position: relative; top: -50px; visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 💾 2. เชื่อมต่อข้อมูล
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=600)
def load_public_data():
    try:
        df_b = conn.read(worksheet="Books", ttl=0)
        df_f = conn.read(worksheet="Finance", ttl=0)
        books = df_b.to_dict('records')
        for b in books:
            try: b['ลิงก์อ่าน'] = json.loads(b.get('ลิงก์อ่าน', '[]')) if pd.notna(b.get('ลิงก์อ่าน')) else []
            except: b['ลิงก์อ่าน'] = []
            b['เรื่องย่อ'] = str(b.get('เรื่องย่อ', '')).replace('\n', '<br>') if pd.notna(b.get('เรื่องย่อ')) and str(b.get('เรื่องย่อ')).lower() != 'nan' else 'รอติดตามความสนุกเร็วๆ นี้ค๊า!'
            b['ตอนปัจจุบัน'] = int(b.get('ตอนปัจจุบัน', 0)) if pd.notna(b.get('ตอนปัจจุบัน')) else 0
        
        df_f['ยอดสุทธิ'] = pd.to_numeric(df_f['ยอดสุทธิ'], errors='coerce').fillna(0)
        df_f['วันที่'] = pd.to_datetime(df_f['วันที่'], errors='coerce')
        df_f['เดือน-ปี'] = df_f['วันที่'].dt.strftime('%Y-%m')
        
        return books, df_f
    except: return [], pd.DataFrame()

books_data, finance_df = load_public_data()

# ตรวจจับการคลิกรูปจาก URL
if "book" in st.query_params:
    target_book = st.query_params["book"]
    found = [i for i, b in enumerate(books_data) if b['ชื่อเรื่อง'] == target_book]
    if found: st.session_state.view_idx = found[0]
    st.query_params.clear()

# หาเดือนที่แล้ว
today = datetime.now()
first_day_this_month = today.replace(day=1)
last_month_date = first_day_this_month - pd.Timedelta(days=1)
last_month_str = last_month_date.strftime('%Y-%m')

# ==========================================
# 🏠 ส่วนแสดงผล
# ==========================================
if st.session_state.view_idx is None:
    
    # --- 🌟 HEADER ---
    st.markdown("""
    <div class="header-container">
        <div class="floating-gem gem-left">✨</div>
        <h1 class="header-title">Nok-kaew Library</h1>
        <p class="header-subtitle">คลังแสงนิยายแปลและมังฮวาสุดพรีเมียม</p>
        <div class="floating-gem gem-right">💎</div>
    </div>
    """, unsafe_allow_html=True)
    
    c_search1, c_search2, c_search3 = st.columns([1, 2, 1])
    search_query = c_search2.text_input("🔍", placeholder="พิมพ์ชื่อนิยายเพื่อค้นหา...", label_visibility="collapsed")
    
    navbar_html = """
    <div style="display: flex; gap: 12px; margin: 30px auto 40px; justify-content: center; max-width: 900px; flex-wrap: wrap;">
        <a href="#latest-updates" class="nav-link">🆕 อัปเดตล่าสุด</a>
        <a href="#top-month" class="nav-link">🔥 ขายดีประจำเดือนที่แล้ว</a>
        <a href="#top-alltime" class="nav-link">🏆 ขายดีตลอดกาล</a>
        <a href="#full-library" class="nav-link">📚 คลังนิยายทั้งหมด</a>
    </div>
    """
    st.markdown(navbar_html, unsafe_allow_html=True)

    filtered_books = [b for b in books_data if search_query.lower() in b['ชื่อเรื่อง'].lower()]

    if filtered_books:
        # --- 🆕 อัปเดตล่าสุด ---
        st.markdown("<div id='latest-updates' class='anchor-offset'></div><h3 class='section-title'>🆕 นิยายอัปเดตล่าสุด</h3>", unsafe_allow_html=True)
        latest_books = filtered_books[::-1][:10]
        cols = st.columns(10)
        for i, b in enumerate(latest_books):
            with cols[i]:
                img = b.get('ภาพปก') if b.get('ภาพปก') and str(b.get('ภาพปก')).strip() != "" else "https://via.placeholder.com/300x450/e0f2fe/0284c7?text=No+Cover"
                card = f"<a href='/?book={urllib.parse.quote(b['ชื่อเรื่อง'])}' target='_self' class='card-link'><div class='y-card'><div class='y-img-wrapper'><div class='status-badge'>ตอน {b.get('ตอนปัจจุบัน',0)}</div><img src='{img}' class='y-img'></div><div class='y-info'><div class='y-name'>{b['ชื่อเรื่อง']}</div></div></div></a>"
                st.markdown(card.replace('\n', ''), unsafe_allow_html=True)

        # --- 🔥 อันดับขายดีเดือนที่แล้ว ---
        st.markdown("<div id='top-month' class='anchor-offset'></div><h3 class='section-title'>🔥 10 อันดับขายดี ประจำเดือน " + last_month_str + "</h3>", unsafe_allow_html=True)
        df_month = finance_df[finance_df['เดือน-ปี'] == last_month_str]
        if not df_month.empty:
            top_month = df_month.groupby('ชื่อเรื่อง')['ยอดสุทธิ'].sum().sort_values(ascending=False).index.tolist()
            display_top_m = [b for title in top_month for b in filtered_books if b['ชื่อเรื่อง'] == title][:10]
            cols_top_m = st.columns(10)
            for i, b in enumerate(display_top_m):
                with cols_top_m[i]:
                    img = b.get('ภาพปก') if b.get('ภาพปก') and str(b.get('ภาพปก')).strip() != "" else "https://via.placeholder.com/300x450/e0f2fe/0284c7?text=No+Cover"
                    card = f"<a href='/?book={urllib.parse.quote(b['ชื่อเรื่อง'])}' target='_self' class='card-link'><div class='y-card'><div class='y-img-wrapper'><div class='rank-badge'>Top {i+1}</div><img src='{img}' class='y-img'></div><div class='y-info'><div class='y-name'>{b['ชื่อเรื่อง']}</div></div></div></a>"
                    st.markdown(card.replace('\n', ''), unsafe_allow_html=True)

        # --- 🏆 ขายดีตลอดกาล ---
        st.markdown("<div id='top-alltime' class='anchor-offset'></div><h3 class='section-title'>🏆 10 อันดับขายดี ตลอดกาล</h3>", unsafe_allow_html=True)
        if not finance_df.empty:
            top_all = finance_df.groupby('ชื่อเรื่อง')['ยอดสุทธิ'].sum().sort_values(ascending=False).index.tolist()
            display_top_a = [b for title in top_all for b in filtered_books if b['ชื่อเรื่อง'] == title][:10]
            cols_top_a = st.columns(10)
            for i, b in enumerate(display_top_a):
                with cols_top_a[i]:
                    img = b.get('ภาพปก') if b.get('ภาพปก') and str(b.get('ภาพปก')).strip() != "" else "https://via.placeholder.com/300x450/e0f2fe/0284c7?text=No+Cover"
                    card = f"<a href='/?book={urllib.parse.quote(b['ชื่อเรื่อง'])}' target='_self' class='card-link'><div class='y-card'><div class='y-img-wrapper'><div class='rank-badge rank-badge-all'>#{i+1}</div><img src='{img}' class='y-img'></div><div class='y-info'><div class='y-name'>{b['ชื่อเรื่อง']}</div></div></div></a>"
                    st.markdown(card.replace('\n', ''), unsafe_allow_html=True)

        # --- 📚 คลังนิยายทั้งหมด ---
        st.markdown("<div id='full-library' class='anchor-offset'></div><h3 class='section-title'>📚 คลังนิยายทั้งหมด</h3>", unsafe_allow_html=True)
        for i in range(0, len(filtered_books), 10):
            cols = st.columns(10)
            for j, col in enumerate(cols):
                if i + j < len(filtered_books):
                    b = filtered_books[i+j]
                    with col:
                        img = b.get('ภาพปก') if b.get('ภาพปก') and str(b.get('ภาพปก')).strip() != "" else "https://via.placeholder.com/300x450/e0f2fe/0284c7?text=No+Cover"
                        card = f"<a href='/?book={urllib.parse.quote(b['ชื่อเรื่อง'])}' target='_self' class='card-link'><div class='y-card'><div class='y-img-wrapper'><div class='status-badge'>{b.get('สถานะ','')}</div><img src='{img}' class='y-img'></div><div class='y-info'><div class='y-name'>{b['ชื่อเรื่อง']}</div></div></div></a>"
                        st.markdown(card.replace('\n', ''), unsafe_allow_html=True)

# --- 📢 รายละเอียดนิยาย ---
else:
    b = books_data[st.session_state.view_idx]
    if st.button("🔙 กลับไปคลังนิยาย", type="primary"): st.session_state.view_idx = None; st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    
    links_html = "".join([f"<a href='{l['url']}' target='_blank' class='btn-read' style='margin-right:12px; margin-bottom:12px;'>📖 อ่านที่ {l['note']}</a>" for l in b['ลิงก์อ่าน'] if l.get('url')])
    
    html = f"""<div class='promo-container'><div style='flex:0 0 280px;'><img src='{b.get('ภาพปก')}' style='width:100%; border-radius:18px; box-shadow:0 15px 35px rgba(14,165,233,0.15);'></div><div style='flex:1; min-width:300px;'><div style='color: #0ea5e9; font-weight: 700; margin-bottom: 5px; font-size: 13px;'>💎 NOK-KAEW TRANSLATION</div><h1 class='promo-title'>{b['ชื่อเรื่อง']}</h1><div style='display:flex; gap:10px; margin-bottom:25px; flex-wrap:wrap;'><span style='background:#dcfce7; color:#166534; padding:6px 15px; border-radius:20px; font-size:13px; font-weight:600;'>สถานะ: {b.get('สถานะ','')}</span><span style='background:#e0f2fe; color:#0369a1; padding:6px 15px; border-radius:20px; font-size:13px; font-weight:600;'>ตอนที่ {b.get('ตอนปัจจุบัน',0)}</span><span style='background:#fef3c7; color:#b45309; padding:6px 15px; border-radius:20px; font-size:13px; font-weight:600;'>หมวด: {b.get('หมวดหมู่','')}</span></div><div class='promo-synopsis-box'><h3 style='color:#0284c7; margin-top:0; font-size:1.3rem;'>✨ เรื่องย่อ</h3><p class='promo-synopsis-text'>{b['เรื่องย่อ']}</p></div><div style='margin-top:30px;'><h4 style='color:#475569; font-size:16px; margin-bottom:15px;'>พุ่งตัวไปอ่านได้ที่:</h4><div style='display:flex; flex-wrap:wrap;'>{links_html}</div></div><div style='margin-top:40px; border-top:2px dashed #e2e8f0; padding-top:25px;'><a href='https://www.facebook.com/people/%E0%B8%99%E0%B8%81%E0%B9%81%E0%B8%81%E0%B9%89%E0%B8%A7%E0%B8%AD%E0%B8%B9%E0%B9%89%E0%B8%87%E0%B8%B2%E0%B8%99/61582115332999/' target='_blank' class='fb-link'>ติดตามข่าวสารที่: เพจนกแก้วอู้งาน</a></div></div></div>"""
    st.markdown(html.replace('\n',''), unsafe_allow_html=True)
    
    # ระบบป้ายยา
    st.markdown("<br><hr style='border-color:#bae6fd;'><h3 style='color:#0369a1; text-align:center; margin-bottom:30px;'>💖 เรื่องที่คุณน่าจะชอบ</h3>", unsafe_allow_html=True)
    other_books = [book for book in books_data if book['ชื่อเรื่อง'] != b['ชื่อเรื่อง']]
    if len(other_books) >= 2:
        recommended = random.Random(b['ชื่อเรื่อง']).sample(other_books, 2)
        _, c_rec1, c_rec2, _ = st.columns([3, 2, 2, 3])
        for i, rec_b in enumerate(recommended):
            with (c_rec1 if i == 0 else c_rec2):
                img = rec_b.get('ภาพปก') if rec_b.get('ภาพปก') else "https://via.placeholder.com/300x450"
                st.markdown(f"<a href='/?book={urllib.parse.quote(rec_b['ชื่อเรื่อง'])}' target='_self' class='card-link'><div class='y-card' style='max-width:200px; margin:0 auto;'><div class='y-img-wrapper'><img src='{img}' class='y-img'></div><div class='y-info'><div class='y-name'>{rec_b['ชื่อเรื่อง']}</div></div></div></a>", unsafe_allow_html=True)
