# 📝 วิธีการแก้ไข app.py - ทีละขั้นตอน

## 📌 Overview
ไฟล์นี้อธิบายวิธีการรวม ReadToon module เข้าไปใน app.py ของคุณ อย่างละเอียด

---

## 🔧 ขั้นตอนที่ 1: เพิ่ม Imports

**ตำแหน่ง:** บรรทัดที่ 1-8 (ส่วน imports ทั่วไป)

**ก่อนแก้ไข (บรรทัด 1-7):**
```python
import streamlit as st
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection
import json
import plotly.express as px
from datetime import datetime
```

**หลังแก้ไข (เพิ่มเข้าไป):**
```python
import streamlit as st
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection
import json
import plotly.express as px
from datetime import datetime
import os  # ✅ เพิ่มบรรทัดนี้
from dotenv import load_dotenv  # ✅ เพิ่มบรรทัดนี้
load_dotenv()  # ✅ เพิ่มบรรทัดนี้

# ✅ เพิ่ม import ReadToon module
from readtoon_scraper import fetch_readtoon_data
```

---

## 🔧 ขั้นตอนที่ 2: เพิ่ม Session State สำหรับ ReadToon

**ตำแหน่ง:** บรรทัดที่ 30-35 (ส่วน session state initialization)

**เดิม (บรรทัด 30-35):**
```python
if 'selected_book_idx' not in st.session_state: st.session_state.selected_book_idx = None
if 'selected_promo_idx' not in st.session_state: st.session_state.selected_promo_idx = None
```

**เพิ่มเข้าไป:**
```python
if 'selected_book_idx' not in st.session_state: st.session_state.selected_book_idx = None
if 'selected_promo_idx' not in st.session_state: st.session_state.selected_promo_idx = None
if 'readtoon_cache' not in st.session_state: st.session_state.readtoon_cache = None  # ✅ เพิ่มบรรทัดนี้
```

---

## 🔧 ขั้นตอนที่ 3: เปลี่ยน Menu เพิ่มเมนู ReadToon Creator

**ตำแหน่ง:** บรรทัดที่ 220-237 (ส่วน `st.sidebar.radio()`)

**เดิม:**
```python
menu = st.sidebar.radio(
    "📌 เลือกหน้าที่ต้องการ",
    [
        "🏠 หน้าหลัก",
        "📚 จัดการนิยาย",
        "👥 จัดการผู้เขียน",
        "📖 จัดการตอน",
        "⭐ จัดการความเห็น",
        "🎁 จัดการส่วนลด",
        "📣 ประกาศ",
        "💰 บัญชีรายรับ",
        "💸 สรุปส่วนแบ่ง (QC)",
        "🏆 อันดับนิยายขายดี",
        "⚙️ ตั้งค่าระบบ"
    ]
)
```

**แก้ไขเป็น:**
```python
menu = st.sidebar.radio(
    "📌 เลือกหน้าที่ต้องการ",
    [
        "🏠 หน้าหลัก",
        "📚 จัดการนิยาย",
        "👥 จัดการผู้เขียน",
        "📖 จัดการตอน",
        "⭐ จัดการความเห็น",
        "🎁 จัดการส่วนลด",
        "📣 ประกาศ",
        "💰 บัญชีรายรับ",
        "💸 สรุปส่วนแบ่ง (QC)",
        "🏆 อันดับนิยายขายดี",
        "🎯 ReadToon Creator",  # ✅ เพิ่มบรรทัดนี้
        "⚙️ ตั้งค่าระบบ"
    ]
)
```

---

## 🔧 ขั้นตอนที่ 4: เพิ่มหน้า ReadToon Creator

**ตำแหน่ง:** ก่อน `elif menu == "⚙️ ตั้งค่าระบบ":` (ประมาณบรรทัด 820)

**เพิ่มโค้ดต่อไปนี้:**

```python
# ------------------------------------------
# 🎯 หน้า: ReadToon Creator Dashboard
# ------------------------------------------
elif menu == "🎯 ReadToon Creator":
    st.title("🎯 ReadToon Creator Dashboard")
    st.markdown("---")
    
    # Tabs สำหรับแบ่งการแสดงผล
    tab1, tab2, tab3, tab4 = st.tabs(["📊 สรุปยอด", "📈 รายละเอียด", "💹 เทรนด์", "⚙️ ตั้งค่า"])
    
    # ========== TAB 1: สรุปยอด ==========
    with tab1:
        st.subheader("📊 สรุปข้อมูลจากเว็บ ReadToon")
        
        # ปุ่มดึงข้อมูลใหม่
        if st.button("🔄 ดึงข้อมูลใหม่จาก ReadToon", type="primary"):
            email = os.getenv("READTOON_EMAIL")
            password = os.getenv("READTOON_PASSWORD")
            
            if not email or not password:
                st.error("❌ ยังไม่ได้ตั้งค่า READTOON_EMAIL และ READTOON_PASSWORD")
            else:
                with st.spinner("🔄 กำลังดึงข้อมูล..."):
                    readtoon_data = fetch_readtoon_data(email, password)
                    
                    if "error" in readtoon_data:
                        st.error(f"❌ {readtoon_data['error']}")
                    else:
                        st.session_state.readtoon_cache = readtoon_data
                        st.rerun()
        
        # ดึงข้อมูลจาก cache
        if "readtoon_cache" in st.session_state and st.session_state.readtoon_cache:
            data = st.session_state.readtoon_cache
            revenue = data.get("revenue", {})
            
            # แสดงไฟล์ข้อมูลหลัก
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_revenue = revenue.get("total_revenue", 0)
                st.markdown(f"""
                <div class='metric-card'>
                    <h3 style='color:#6C63FF;'>💰 รายได้รวม</h3>
                    <h2>฿{total_revenue:,.2f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                net_revenue = revenue.get("net_revenue", 0)
                st.markdown(f"""
                <div class='metric-card'>
                    <h3 style='color:#FF6584;'>💸 รายได้สุทธิ</h3>
                    <h2>฿{net_revenue:,.2f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                commission = revenue.get("commission", 0)
                st.markdown(f"""
                <div class='metric-card'>
                    <h3 style='color:#38bdf8;'>📊 หักค่าแพลตฟอร์ม</h3>
                    <h2>฿{commission:,.2f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # แสดงข้อมูลอื่นๆ
            if "monthly" in revenue:
                st.subheader("📅 รายได้รายเดือน")
                monthly_data = revenue.get("monthly", [])
                
                if monthly_data:
                    df_monthly = pd.DataFrame(monthly_data)
                    
                    # สร้างกราฟ
                    if not df_monthly.empty and 'month' in df_monthly.columns:
                        fig = px.bar(
                            df_monthly, 
                            x="month", 
                            y="amount",
                            title="รายได้รายเดือน",
                            color_discrete_sequence=["#6C63FF"]
                        )
                        fig.update_layout(font_family="Kanit")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # แสดงตาราง
                    st.dataframe(df_monthly, use_container_width=True)
        else:
            st.info("🔍 กดปุ่มดึงข้อมูลเพื่อโหลดข้อมูลจาก ReadToon Creator")
    
    # ========== TAB 2: รายละเอียด ==========
    with tab2:
        st.subheader("📈 รายละเอียดการขายและรายได้")
        
        if "readtoon_cache" in st.session_state and st.session_state.readtoon_cache:
            data = st.session_state.readtoon_cache
            sales = data.get("sales", [])
            
            if sales:
                df_sales = pd.DataFrame(sales)
                st.dataframe(df_sales, use_container_width=True)
                
                # ปุ่มดาวน์โหลด
                csv = df_sales.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 ดาวน์โหลด CSV",
                    data=csv,
                    file_name=f"readtoon_sales_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("❌ ไม่มีข้อมูลการขาย")
        else:
            st.info("🔍 โปรดดึงข้อมูลจาก Tab แรก")
    
    # ========== TAB 3: เทรนด์ ==========
    with tab3:
        st.subheader("💹 วิเคราะห์เทรนด์")
        
        if "readtoon_cache" in st.session_state and st.session_state.readtoon_cache:
            data = st.session_state.readtoon_cache
            revenue = data.get("revenue", {})
            
            if "daily" in revenue:
                daily_data = revenue.get("daily", [])
                if daily_data:
                    df_daily = pd.DataFrame(daily_data)
                    
                    # กราฟเส้น
                    if not df_daily.empty and 'date' in df_daily.columns:
                        fig = px.line(
                            df_daily,
                            x="date",
                            y="amount",
                            title="เทรนด์รายได้รายวัน",
                            markers=True,
                            color_discrete_sequence=["#6C63FF"]
                        )
                        fig.update_layout(font_family="Kanit")
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("❌ ไม่มีข้อมูลรายวัน")
        else:
            st.info("🔍 โปรดดึงข้อมูลจาก Tab แรก")
    
    # ========== TAB 4: ตั้งค่า ==========
    with tab4:
        st.subheader("⚙️ ตั้งค่า ReadToon Integration")
        
        st.info("""
        **วิธีการตั้งค่า Credentials:**
        
        1. **Local Development:**
           - สร้างไฟล์ `.env`
           - เพิ่ม: READTOON_EMAIL=email@example.com
           - เพิ่ม: READTOON_PASSWORD=password
        
        2. **Streamlit Cloud:**
           - Settings → Secrets
           - เพิ่ม READTOON_EMAIL และ READTOON_PASSWORD
        """)
        
        # ตรวจสอบสถานะการตั้งค่า
        email_status = "✅" if os.getenv("READTOON_EMAIL") else "❌"
        password_status = "✅" if os.getenv("READTOON_PASSWORD") else "❌"
        
        st.write(f"**สถานะการตั้งค่า:**")
        st.write(f"  {email_status} READTOON_EMAIL: {os.getenv('READTOON_EMAIL', 'ไม่ได้ตั้งค่า')}")
        st.write(f"  {password_status} READTOON_PASSWORD: {'ตั้งค่าแล้ว' if os.getenv('READTOON_PASSWORD') else 'ไม่ได้ตั้งค่า'}")
```

---

## 📋 Summary ของการแก้ไข

| ขั้นตอน | ตำแหน่ง | การกระทำ |
|--------|--------|---------|
| 1 | บรรทัด 1-7 | เพิ่ม `import os`, `load_dotenv()`, import ReadToon module |
| 2 | บรรทัด 30-35 | เพิ่ม `st.session_state.readtoon_cache` |
| 3 | บรรทัด 220-237 | เพิ่มเมนู "🎯 ReadToon Creator" |
| 4 | ก่อนบรรทัด 820 | เพิ่มหน้า ReadToon Creator ที่สมบูรณ์ |

---

## ✅ Verification Checklist

หลังจากแก้ไข ให้ตรวจสอบ:

- [ ] ไม่มี syntax errors
- [ ] สามารถ import modules ได้ทั้งหมด
- [ ] เมนู "🎯 ReadToon Creator" ปรากฎ
- [ ] สามารถดึงข้อมูลได้
- [ ] ไม่มีข้อความ error สีแดง

---

## 🚀 ทดสอบ

```bash
# 1. ติดตั้ง dependencies
pip install -r requirements_readtoon.txt

# 2. สร้างไฟล์ .env
cp .env.example .env
# แก้ไข .env ใส่ credentials จริง

# 3. รัน app
streamlit run app.py

# 4. ทดสอบโดยคลิกปุ่ม "🎄 ดึงข้อมูลใหม่จาก ReadToon"
```

---

## ❓ FAQ

**Q: หากฉันแก้ไขผิด ทำไง?**
A: ให้ยกเลิกการแก้ไข (Ctrl+Z) หรือ revert ไฟล์เดิม

**Q: ReadToon module ติดตั้งยังไง?**
A: ไม่ต้องติดตั้ง เพียงวางไฟล์ `readtoon_scraper.py` ในโฟลเดอร์เดียวกับ `app.py`

**Q: credentials จะเก็บที่ไหน?**
A: เก็บใน environment variables ผ่านไฟล์ `.env` (local) หรือ Streamlit Secrets (cloud)

---

**✅ เสร็จแล้ว! ไปลองเลย!**
