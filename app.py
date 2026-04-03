import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import json

# ==========================================
# 🎨 1. ตั้งค่าดีไซน์ One-Page & Auto Dark/Light Mode
# ==========================================
st.set_page_config(page_title="Nok-kaew Library", layout="wide", page_icon="💎")

if 'view_idx' not in st.session_state: st.session_state.view_idx = None

# CSS ฉบับ Responsive + บังคับ Smooth Scroll 100%
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600;700&display=swap');
    
    /* บังคับ Smooth Scroll ทุกองค์ประกอบใน Streamlit */
    html, body, .stApp, .main, div.block-container { 
        scroll-behavior: smooth !important; 
    }
    
    .stApp { font-family: 'Prompt', sans-serif !important; }
    
    /* ซ่อน Sidebar */
    [data-testid="stSidebar"] { display: none; }

    /* ============ LIGHT MODE (ค่าเริ่มต้น) ============ */
    .y-card { background: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; transition: 0.3s; margin-bottom: 15px; position: relative; }
    .y-card:hover { transform: translateY(-5px); border-color: #8b5cf6; box-shadow: 0 10px 20px rgba(0,0,0,0.08); }
    .y-img { width: 100%; aspect-ratio: 2/3; object-fit: cover; }
    .y-info { padding: 10px; text-align: center; }
    .y-name { font-size: 13px; font-weight: 600; color: #1e293b; height: 36px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; line-height:1.3; }
    
    .section-title { color: #1e293b; font-weight: 700; margin-top: 20px; }
    
    /* ปุ่ม Navbar แบบ HTML ล้วน (ไม่ทำให้หน้ากระตุก) */
    .nav-link { flex: 1; text-align: center; padding: 12px 10px; border-radius: 15px; background: #f8fafc; color: #475569; border: 1px solid #cbd5e1; font-weight: 600; text-decoration: none; transition: 0.3s; }
    .nav-link:hover { background: #e0e7ff; color: #8b5cf6; border-color: #8b5cf6; transform: translateY(-2px); }

    /* หน้า Promo */
    .promo-container { background: #ffffff; padding: 40px; border-radius: 30px; display: flex; gap: 40px; flex-wrap: wrap; max-width: 1100px; margin: 0 auto; border: 1px solid #e2e8f0; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
    .promo-title { color: #1e293b; font-size: 2.5rem; margin-top: 0; }
    .promo-synopsis-box { background: #f8fafc; padding: 25px; border-radius: 15px; border-left: 5px solid #8b5cf6; margin: 20px 0; }
    .promo-synopsis-text { color: #334155; line-height: 1.8; }
    
    /* ============ DARK MODE (เมื่อนักอ่านเปิดโหมดมืด) ============ */
    @media (prefers-color-scheme: dark) {
        .y-card { background: #1e293b; border-color: #334155; }
        .y-card:hover { box-shadow: 0 10px 20px rgba(0,0,0,0.4); }
        .y-name { color: #f1f5f9; }
        .section-title { color: #f1f5f9; }
        
        .nav-link { background: #1e293b; color: #cbd5e1; border-color: #334155; }
        .nav-link:hover { background: #0f172a; color: #8b5cf6; border-color: #8b5cf6; }
        
        .promo-container { background: #1e293b; border-color: #334155; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        .promo-title { color: #f1f5f9; }
        .promo-synopsis-box { background: #0f172a; }
        .promo-synopsis-text { color: #cbd5e1; }
    }

    /* Badges & Buttons (ใช้ได้ทั้ง 2 โหมด) */
    .rank-badge { position: absolute; top: 5px; left: 5px; background: #8b5cf6; color: white; padding: 2px 8px; border-radius: 5px; font-weight: 700; font-size: 12px; z-index: 10; }
    .status-badge { position: absolute; bottom: 65px; right: 5px; background: rgba(15,23,42,0.85); color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; z-index: 10; border: 1px solid rgba(255,255,255,0.1); }
    .btn-read { background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%); color: white !important; padding: 12px 25px; border-radius: 30px; text-decoration: none; font-weight: 600; display: inline-block; transition: 0.3s; }
    .btn-read:hover { transform: scale(1.05); box-shadow: 0 5px 15px rgba(139, 92, 246, 0.4); }
    
    /* ตัวชดเชย Anchor เพื่อไม่ให้โดนขอบจอด้านบนบังตอนเลื่อนมาถึง */
    .anchor-offset { position: relative; top: -80px; visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 💾 2. เชื่อมต่อข้อมูล (High Speed Cache)
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=600)
def load_public_data():
    try:
        df_b = conn.read(worksheet="Books", ttl=0)
        df_f = conn.read(worksheet="Finance", ttl=0)
        books = df_b.to_dict('records')
        for b in books:
            if isinstance(b.get('ลิงก์อ่าน'), str):
                try: b['ลิงก์อ่าน'] = json.loads(b['ลิงก์อ่าน'])
                except: b['ลิงก์อ่าน'] = []
            b['เรื่องย่อ'] = str(b.get('เรื่องย่อ', '')).replace('\n', '<br>') if pd.notna(b.get('เรื่องย่อ')) else 'ยังไม่มีการระบุเรื่องย่อสำหรับนิยายเรื่องนี้'
            b['ตอนปัจจุบัน'] = int(b.get('ตอนปัจจุบัน', 0)) if pd.notna(b.get('ตอนปัจจุบัน')) else 0
        df_f['ยอดสุทธิ'] = pd.to_numeric(df_f['ยอดสุทธิ'], errors='coerce').fillna(0)
        return books, df_f
    except: return [], pd.DataFrame()

books_data, finance_df = load_public_data()

# ==========================================
# 🏠 ส่วนแสดงผล (Logic & UI)
# ==========================================
if st.session_state.view_idx is None:
    
    # --- 🔍 ส่วนค้นหาและกรองหมวดหมู่ (อยู่บนสุด) ---
    st.markdown("<h1 style='color:#8b5cf6; text-align:center; margin-bottom: 20px;'>💎 Nok-kaew Library</h1>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([2, 1])
    search_query = c1.text_input("🔍 ค้นหาชื่อเรื่อง...", placeholder="พิมพ์ชื่อนิยายเพื่อค้นหา")
    
    # หาหมวดหมู่ทั้งหมดที่มีในระบบ
    all_categories = sorted(list(set([str(b['หมวดหมู่']) for b in books_data if pd.notna(b.get('หมวดหมู่'))])))
    selected_category = c2.selectbox("📂 หมวดหมู่", ["ทั้งหมด"] + all_categories)
    
    # ระบบกรองข้อมูล
    filtered_books = [
        b for b in books_data 
        if (search_query.lower() in b['ชื่อเรื่อง'].lower()) and 
           (selected_category == "ทั้งหมด" or b.get('หมวดหมู่') == selected_category)
    ]
    
    # --- 🧭 Navbar (HTML แท้ ช่วยให้ Smooth Scroll ทำงาน 100%) ---
    navbar_html = """
    <div style="display: flex; gap: 15px; margin: 30px 0; justify-content: center; width: 100%;">
        <a href="#latest-updates" class="nav-link">🆕 อัปเดตล่าสุด</a>
        <a href="#top-sellers" class="nav-link">🏆 อันดับขายดี</a>
        <a href="#full-library" class="nav-link">📚 คลังนิยายทั้งหมด</a>
    </div>
    <hr style='border-color: #cbd5e1; margin-bottom:30px;'>
    """
    st.markdown(navbar_html, unsafe_allow_html=True)

    if not filtered_books:
        st.warning("❌ ไม่พบชื่อเรื่องหรือหมวดหมู่ที่คุณค้นหาค๊า")
    else:
        # --- 🆕 1. Section: อัปเดตล่าสุด ---
        st.markdown("<div id='latest-updates' class='anchor-offset'></div>", unsafe_allow_html=True)
        st.markdown("<h3 class='section-title'>🆕 นิยายอัปเดตล่าสุด</h3>", unsafe_allow_html=True)
        
        latest_books = filtered_books[::-1][:6] # ดึง 6 เรื่องล่าสุดจากที่กรองมา
        cols = st.columns(6)
        for i, b in enumerate(latest_books):
            with cols[i]:
                img = b.get('ภาพปก') if b.get('ภาพปก') and str(b.get('ภาพปก')).strip() != "" else "https://via.placeholder.com/300x450?text=No+Cover"
                card = f"<div class='y-card'><div class='status-badge'>ตอนที่ {b.get('ตอนปัจจุบัน',0)}</div><img src='{img}' class='y-img' onerror=\"this.onerror=null;this.src='https://via.placeholder.com/300x450?text=Error';\"><div class='y-info'><div class='y-name'>{b['ชื่อเรื่อง']}</div></div></div>"
                st.markdown(card.replace('\n', ''), unsafe_allow_html=True)
                if st.button("ดูข้อมูล", key=f"lat_{b['ชื่อเรื่อง']}_{i}", use_container_width=True): 
                    st.session_state.view_idx = books_data.index(b); st.rerun()

        st.markdown("<br><br>", unsafe_allow_html=True)

        # --- 🏆 2. Section: อันดับขายดีตลอดกาล ---
        st.markdown("<div id='top-sellers' class='anchor-offset'></div>", unsafe_allow_html=True)
        st.markdown("<h3 class='section-title'>🏆 10 อันดับขายดีตลอดกาล</h3>", unsafe_allow_html=True)
        
        if not finance_df.empty:
            # คำนวณอันดับจากยอดเงิน
            top_10 = finance_df.groupby('ชื่อเรื่อง')['ยอดสุทธิ'].sum().sort_values(ascending=False).index.tolist()
            
            # โชว์เฉพาะเรื่องที่อยู่ในกลุ่มที่กรองไว้ (จำกัดไม่เกิน 10 เรื่อง)
            display_top = []
            for title in top_10:
                b_match = next((x for x in filtered_books if x['ชื่อเรื่อง'] == title), None)
                if b_match:
                    display_top.append(b_match)
                if len(display_top) >= 10: break
                
            if display_top:
                cols_top = st.columns(5)
                for i, b in enumerate(display_top):
                    with cols_top[i % 5]:
                        img = b.get('ภาพปก') if b.get('ภาพปก') and str(b.get('ภาพปก')).strip() != "" else "https://via.placeholder.com/300x450?text=No+Cover"
                        card = f"<div class='y-card'><div class='rank-badge'>#{i+1}</div><img src='{img}' class='y-img' onerror=\"this.onerror=null;this.src='https://via.placeholder.com/300x450?text=Error';\"><div class='y-info'><div class='y-name'>{b['ชื่อเรื่อง']}</div></div></div>"
                        st.markdown(card.replace('\n', ''), unsafe_allow_html=True)
                        if st.button("ดูข้อมูล", key=f"top_{b['ชื่อเรื่อง']}_{i}", use_container_width=True):
                            st.session_state.view_idx = books_data.index(b); st.rerun()
            else:
                st.info("ไม่มีข้อมูลอันดับขายดีในหมวดหมู่นี้")

        st.markdown("<br><br>", unsafe_allow_html=True)

        # --- 📚 3. Section: คลังนิยายทั้งหมด ---
        st.markdown("<div id='full-library' class='anchor-offset'></div>", unsafe_allow_html=True)
        st.markdown("<h3 class='section-title'>📚 คลังนิยายทั้งหมด</h3>", unsafe_allow_html=True)
        
        for i in range(0, len(filtered_books), 6):
            cols = st.columns(6)
            for j, col in enumerate(cols):
                if i + j < len(filtered_books):
                    b = filtered_books[i+j]
                    with col:
                        img = b.get('ภาพปก') if b.get('ภาพปก') and str(b.get('ภาพปก')).strip() != "" else "https://via.placeholder.com/300x450?text=No+Cover"
                        card = f"<div class='y-card'><div class='status-badge'>{b.get('สถานะ','')}</div><img src='{img}' class='y-img' onerror=\"this.onerror=null;this.src='https://via.placeholder.com/300x450?text=Error';\"><div class='y-info'><div class='y-name'>{b['ชื่อเรื่อง']}</div></div></div>"
                        st.markdown(card.replace('\n', ''), unsafe_allow_html=True)
                        if st.button("ดูข้อมูล", key=f"all_{b['ชื่อเรื่อง']}_{i+j}", use_container_width=True):
                            st.session_state.view_idx = books_data.index(b); st.rerun()

# --- 📢 4. หน้าใบปลิวโปรโมท (เมื่อกดดูข้อมูล) ---
else:
    b = books_data[st.session_state.view_idx]
    
    # ปุ่มกลับหน้าแรก
    if st.button("🔙 กลับหน้าหลัก"): st.session_state.view_idx = None; st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    
    # จัดการลิงก์ช่องทางการอ่าน
    links_html = ""
    for link in b.get('ลิงก์อ่าน', []):
        if link.get('url'):
            links_html += f"<a href='{link['url']}' target='_blank' class='btn-read' style='margin-right:10px; margin-bottom:10px;'>📖 {link.get('note','อ่านเลย')}</a>"

    # HTML ส่วนโปรโมท (รองรับโหมดมืด/สว่างอัตโนมัติ)
    html = f"""
    <div class='promo-container'>
        <div style='flex:0 0 320px;'>
            <img src='{b.get('ภาพปก', 'https://via.placeholder.com/300x450')}' style='width:100%; border-radius:20px; box-shadow:0 15px 30px rgba(0,0,0,0.2);' onerror=\"this.onerror=null;this.src='https://via.placeholder.com/300x450?text=Error';\">
        </div>
        <div style='flex:1; min-width:300px;'>
            <div style='color: #8b5cf6; font-weight: 600; margin-bottom: 10px; letter-spacing: 1px;'>NOK-KAEW TRANSLATION</div>
            <h1 class='promo-title'>{b['ชื่อเรื่อง']}</h1>
            
            <div style='display:flex; gap:10px; margin-bottom:20px; flex-wrap:wrap;'>
                <span style='background:rgba(16,185,129,0.15); color:#10b981; padding:5px 15px; border-radius:8px; font-weight:600;'>{b.get('สถานะ','กำลังอัปเดต')}</span>
                <span style='background:rgba(139,92,246,0.15); color:#8b5cf6; padding:5px 15px; border-radius:8px; font-weight:600;'>ตอนที่ {b.get('ตอนปัจจุบัน',0)}</span>
                <span style='background:rgba(245,158,11,0.15); color:#d97706; padding:5px 15px; border-radius:8px; font-weight:600;'>{b.get('หมวดหมู่','ทั่วไป')}</span>
            </div>
            
            <div class='promo-synopsis-box'>
                <h3 style='color:#8b5cf6; margin-top:0;'>📝 เรื่องย่อ</h3>
                <p class='promo-synopsis-text'>{b['เรื่องย่อ']}</p>
            </div>
            
            <div style='margin-top:20px;'>{links_html}</div>
            
            <div style='margin-top:30px; border-top:1px solid #cbd5e1; padding-top:20px;'>
                <h4 style='color:#8b5cf6; margin:0;'>✨ ติดตามข่าวสารได้ที่ Facebook: นกแก้วอู้งาน</h4>
            </div>
        </div>
    </div>
    """
    st.markdown(html.replace('\n',''), unsafe_allow_html=True)
