"""
🎯 ส่วนของ Streamlit สำหรับแสดงข้อมูล ReadToon Creator
เพิ่มโค้ดนี้เข้าไฟล์ app.py ของคุณ
"""

# ===============================================
# 📊 ส่วนที่ 1: นำเข้า Libraries สำหรับ ReadToon
# ===============================================
# เพิ่มเข้าไปที่ด้านบนของไฟล์ app.py (ประมาณบรรทัดที่ 1-7)
# import os
# from readtoon_scraper import fetch_readtoon_data

# ===============================================
# 📊 ส่วนที่ 2: ตั้งค่า ReadToon Credentials
# ===============================================
# เพิ่มเข้าไปในฟังก์ชัน load_admin_data() หรือสร้าง function ใหม่

def load_readtoon_data():
    """โหลดข้อมูล ReadToon โดยใช้ environment variables"""
    try:
        email = os.getenv("READTOON_EMAIL", "kabaofab@gmail.com")  # ใช้ env variable
        password = os.getenv("READTOON_PASSWORD", "")  # อย่าใส่รหัสผ่านในโค้ด!
        
        if not password:
            st.warning("⚠️ ยังไม่ได้ตั้งค่า READTOON_PASSWORD")
            return None
        
        with st.spinner("🔄 กำลังดึงข้อมูล ReadToon..."):
            data = fetch_readtoon_data(email, password)
            
            if "error" in data:
                st.error(f"❌ {data['error']}")
                return None
            
            return data
    except Exception as e:
        st.error(f"❌ ข้อผิดพลาด: {e}")
        return None


# ===============================================
# 📊 ส่วนที่ 3: เพิ่มหน้า ReadToon Creator ลงในเมนู
# ===============================================
# เพิ่มเข้าไปในส่วน menu selection (ประมาณบรรทัดที่ 220-230)

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
        "🎯 ReadToon Creator",  # <-- เพิ่มบรรทัดนี้
        "⚙️ ตั้งค่าระบบ"
    ]
)


# ===============================================
# 📊 ส่วนที่ 4: สร้างหน้า ReadToon Creator
# ===============================================
# เพิ่มเข้าไปก่อน "⚙️ ตั้งค่าระบบ" (ประมาณบรรทัดที่ 820)

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
            readtoon_data = load_readtoon_data()
            if readtoon_data and "revenue" in readtoon_data:
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
                st.subheader("📅 รายได้รายเดือน (6 เดือนล่าสุด)")
                monthly_data = revenue["monthly"]
                
                df_monthly = pd.DataFrame(monthly_data)
                if not df_monthly.empty:
                    # สร้างกราฟ
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
                df_daily = pd.DataFrame(revenue["daily"])
                
                # กราฟเส้น
                fig = px.line(
                    df_daily,
                    x="date",
                    y="amount",
                    title="เทรนด์รายได้รายวัน (14 วันล่าสุด)",
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
        **วิธีการตั้งค่า Credentials อย่างปลอดภัย:**
        
        1. **สำหรับ Local Development:**
           ```
           สร้างไฟล์ .env ในโฟลเดอร์เดียวกับ app.py:
           READTOON_EMAIL=kabaofab@gmail.com
           READTOON_PASSWORD=รหัสผ่านของคุณ
           ```
        
        2. **สำหรับ Streamlit Cloud:**
           - ไปที่ App Settings (⚙️)
           - Secrets
           - เพิ่ม READTOON_EMAIL และ READTOON_PASSWORD
        
        3. **สำหรับ Server ทั่วไป:**
           ```bash
           export READTOON_EMAIL="email@example.com"
           export READTOON_PASSWORD="password"
           python -m streamlit run app.py
           ```
        """)
        
        # ตรวจสอบสถานะการตั้งค่า
        email_status = "✅" if os.getenv("READTOON_EMAIL") else "❌"
        password_status = "✅" if os.getenv("READTOON_PASSWORD") else "❌"
        
        st.write(f"**สถานะการตั้งค่า:**")
        st.write(f"  {email_status} READTOON_EMAIL")
        st.write(f"  {password_status} READTOON_PASSWORD")
        
        st.markdown("---")
        st.warning("""
        ⚠️ **ข้อควรระวัง:**
        - **ห้าม** วางรหัสผ่านลงในโค้ดหรือ GitHub
        - ใช้ Environment Variables เท่านั้น
        - หากสงสัยว่ารหัสผ่านรั่ว ให้เปลี่ยนเลยทันที
        """)
