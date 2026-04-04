# 🎯 ReadToon Creator Integration Guide

## 📋 สรุป
ไฟล์นี้อธิบายวิธีการรวม ReadToon Creator Dashboard เข้าไปใน Streamlit app ของคุณ

---

## 🚀 ขั้นตอนการติดตั้ง

### 1️⃣ **ติดตั้ง Dependencies**
```bash
pip install beautifulsoup4 python-dotenv
```

### 2️⃣ **สร้างไฟล์ `.env` (สำหรับ Local Development)**
สร้างไฟล์ชื่อ `.env` ในโฟลเดอร์เดียวกับ `app.py`:

```env
READTOON_EMAIL=kabaofab@gmail.com
READTOON_PASSWORD=Ip11220473
```

⚠️ **สำคัญ**: 
- **ห้าม** commit ไฟล์ `.env` ขึ้น GitHub
- เพิ่ม `.env` ลงใน `.gitignore`

### 3️⃣ **ไฟล์ที่ต้องทำ**

#### ไฟล์ที่สร้างให้แล้ว:
- ✅ `readtoon_scraper.py` - ตัวสกราป ReadToon
- ✅ `readtoon_streamlit_integration.py` - UI ของ Streamlit

#### ต้องปรับปรุง `app.py`:

**เพิ่มบรรทัดเหล่านี้ที่ด้านบนของไฟล์ (หลัง import ปกติ):**

```python
import os
from dotenv import load_dotenv
load_dotenv()  # โหลด environment variables จาก .env

# นำเข้า ReadToon module
from readtoon_scraper import fetch_readtoon_data
```

**เพิ่มเข้าไปในส่วน initialization (ประมาณบรรทัด 30-35):**

```python
# สำหรับ cache ReadToon data
if 'readtoon_cache' not in st.session_state:
    st.session_state.readtoon_cache = None
```

**เพิ่มเมนูใหม่ (บรรทัด ~220-235):**

```python
menu = st.sidebar.radio(
    "📌 เลือกหน้าที่ต้องการ",
    [
        "🏠 หน้าหลัก",
        "📚 จัดการนิยาย",
        # ... เมนูอื่นๆ ...
        "🎯 ReadToon Creator",  # ← เพิ่มบรรทัดนี้
        "⚙️ ตั้งค่าระบบ"
    ]
)
```

**เพิ่มหน้าใหม่ (ก่อน `elif menu == "⚙️ ตั้งค่าระบบ"` ประมาณบรรทัด 818):**

```python
# วางโค้ดจากไฟล์ readtoon_streamlit_integration.py ที่นี่
```

---

## ⚙️ วิธีการตั้งค่า Credentials

### 🏠 Local Development
```bash
# 1. สร้างไฟล์ .env
echo "READTOON_EMAIL=kabaofab@gmail.com" > .env
echo "READTOON_PASSWORD=Ip11220473" >> .env

# 2. รัน Streamlit
streamlit run app.py
```

### ☁️ Streamlit Cloud (https://share.streamlit.io)
1. ไปที่ app ของคุณ
2. กด **⋮ (menu)** → **Settings**
3. ไปที่ tab **Secrets**
4. เพิ่มข้อมูล:
```toml
READTOON_EMAIL = "kabaofab@gmail.com"
READTOON_PASSWORD = "Ip11220473"
```

### 🖥️ Server/VPS
```bash
# ตั้ง environment variables
export READTOON_EMAIL="kabaofab@gmail.com"
export READTOON_PASSWORD="Ip11220473"

# รัน app
python -m streamlit run app.py
```

### Docker
เพิ่มเข้าไปใน `Dockerfile`:
```dockerfile
ENV READTOON_EMAIL="kabaofab@gmail.com"
ENV READTOON_PASSWORD="Ip11220473"
```

---

## 📊 ฟีเจอร์ที่ได้

### 📋 Tab 1: สรุปยอด
- ✅ รายได้รวมทั้งสิ้น
- ✅ รายได้สุทธิ
- ✅ ค่าที่หักของแพลตฟอร์ม
- ✅ กราฟรายได้รายเดือน
- ✅ ตาราง 6 เดือนล่าสุด

### 📈 Tab 2: รายละเอียด
- ✅ ตารางรายละเอียดการขาย
- ✅ ดาวน์โหลด CSV

### 💹 Tab 3: เทรนด์
- ✅ กราฟเทรนด์ 14 วันล่าสุด
- ✅ วิเคราะห์รายได้รายวัน

### ⚙️ Tab 4: ตั้งค่า
- ✅ วิธีการตั้งค่า Credentials
- ✅ ตรวจสอบสถานะการเชื่อมต่อ

---

## 🔒 ความปลอดภัย

### ✅ ทำให้ปลอดภัย
```python
# ✅ ถูก - ใช้ environment variables
email = os.getenv("READTOON_EMAIL")
password = os.getenv("READTOON_PASSWORD")
```

### ❌ อันตรายสูง
```python
# ❌ ผิด - วางรหัสผ่านในโค้ด
email = "kabaofab@gmail.com"
password = "Ip11220473"  # ❌ ห้ามทำแบบนี้!
```

### 📝 ตั้ง .gitignore
```
.env
*.pyc
__pycache__/
.streamlit/secrets.toml
```

---

## 🐛 Troubleshooting

### ❌ "ข้อผิดพลาด: เข้าสู่ระบบล้มเหลว"
- ✅ ตรวจสอบ email และ password ถูกต้องหรือไม่
- ✅ ดูว่า ReadToon เว็บปกติหรือไม่ (ลองเข้า web browser)
- ✅ ตรวจสอบการเชื่อมต่อ internet

### ❌ "ModuleNotFoundError: No module named 'readtoon_scraper'"
```bash
# สร้างไฟล์ readtoon_scraper.py ในโฟลเดอร์เดียวกับ app.py
ls -la readtoon_scraper.py
```

### ❌ "READTOON_PASSWORD is None"
- ✅ ตรวจสอบว่าตั้ง environment variables ถูกต้องหรือไม่
- ✅ สำหรับ Local: สร้างไฟล์ `.env`
- ✅ สำหรับ Streamlit Cloud: ไปที่ Secrets

### ❌ "Rate Limit - Request Too Frequently"
- ↔️ ลดความถี่ของการเรียก API
- ⏱️ เพิ่มเวลา delay: `time.sleep(2)` ระหว่างการเรียก

---

## 📦 Requirements

```txt
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.0.0
requests>=2.31.0
beautifulsoup4>=4.12.0
python-dotenv>=1.0.0
streamlit-gsheets>=0.0.7
```

---

## 🔄 อัปเดตข้อมูลอัตโนมัติ

หากต้องการให้ข้อมูล refresh โดยอัตโนมัติ:

```python
import streamlit_autorefresh from streamlit_extras.stateful_buttons import button

# เพิ่มเข้าไปใน ReadToon section
if "readtoon_refresh" not in st.session_state:
    st.session_state.readtoon_refresh = 0

# Auto refresh ทุก 5 นาที
streamlit_autorefresh(interval=5 * 60 * 1000, key="readtoon_auto_refresh")
```

ติดตั้ง:
```bash
pip install streamlit-extras
```

---

## 📞 ติดต่อ & Support

หากมีปัญหา:
1. ตรวจสอบ logs
2. ลองสร้าง issue บน GitHub
3. ตรวจสอบ network/firewall

---

## ✅ Checklist การตั้งค่า

- [ ] ติดตั้ง dependencies (`pip install -r requirements.txt`)
- [ ] สร้างไฟล์ `readtoon_scraper.py`
- [ ] เพิ่มโค้ดใน `app.py`
- [ ] สร้างไฟล์ `.env` (local) หรือตั้ง Secrets (cloud)
- [ ] ทดสอบการเข้าสู่ระบบ
- [ ] ตรวจสอบ `.gitignore` มี `.env` หรือไม่
- [ ] ทดสอบฟีเจอร์ทั้งหมด
- [ ] Deploy ขึ้นระบบจริง

---

**🎉 เสร็จแล้ว! Enjoy! 🎉**
