# 🎯 ReadToon Creator Integration for Streamlit

> ระบบเชื่อมต่อข้อมูลการขายจาก https://creator.readtoon.com/ ไปยัง Streamlit Dashboard ของคุณ

---

## 📚 Table of Contents

- [ความสามารถ](#-ความสามารถ)
- [Quick Start](#-quick-start-5-นาที)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 ความสามารถ

✅ **Automatic Data Synchronization**
- ดึงข้อมูลการขายโดยอัตโนมัติจาก ReadToon Creator
- แสดงรายได้รวม รายได้สุทธิ และค่าที่หัก

✅ **Beautiful Dashboard**
- 4 Tabs: สรุปยอด, รายละเอียด, เทรนด์, ตั้งค่า
- กราฟ Plotly ที่สวยงาม
- ตารางข้อมูลแบบ interactive

✅ **Data Export**
- ดาวน์โหลด CSV ได้โดยตรง
- วิเคราะห์ข้อมูลรายวัน รายเดือน

✅ **Security First**
- ใช้ Environment Variables เพื่อความปลอดภัย
- ไม่มี credentials ในโค้ด
- รองรับ Streamlit Cloud Secrets

---

## 🚀 Quick Start (5 นาที)

### 1. ติดตั้ง Dependencies
```bash
pip install -r requirements_readtoon.txt
```

### 2. ตั้งค่า Credentials
```bash
# สร้างไฟล์ .env
cp .env.example .env

# แก้ไขและใส่ credentials จริง
echo "READTOON_EMAIL=kabaofab@gmail.com" >> .env
echo "READTOON_PASSWORD=Ip11220473" >> .env
```

### 3. เพิ่มเข้าไป app.py
ดูไฟล์ `APP_PY_MODIFICATION_GUIDE.md` สำหรับรายละเอียด

### 4. รัน
```bash
streamlit run app.py
```

### 5. ทดสอบ
- เปิด "🎯 ReadToon Creator" จากเมนูด้านข้าง
- คลิก "🔄 ดึงข้อมูลใหม่จาก ReadToon"
- ลองดูแต่ละ Tab

---

## 📦 Installation

### ความต้องการ
- Python 3.8+
- pip
- Streamlit

### ขั้นตอน

**Step 1: Clone/Download ไฟล์**
```bash
# ไฟล์ที่ต้อง:
readtoon_scraper.py
example_readtoon_usage.py
requirements_readtoon.txt
.env.example
```

**Step 2: ติดตั้ง Libraries**
```bash
pip install -r requirements_readtoon.txt
```

**Step 3: ตั้งค่า .env**
```bash
cp .env.example .env
# แก้ไข .env เพิ่มรหัส
```

**Step 4: ตั้งค่า .gitignore**
```bash
# เพิ่ม .env ลงใน .gitignore
echo ".env" >> .gitignore
```

---

## ⚙️ Configuration

### 🏠 Local Development
```bash
# สร้างไฟล์ .env ในโฟลเดอร์เดียวกับ app.py
READTOON_EMAIL=kabaofab@gmail.com
READTOON_PASSWORD=Ip11220473
```

### ☁️ Streamlit Cloud
1. ไปที่ https://share.streamlit.io
2. เลือก App
3. ⋮ (menu) → **Settings**
4. Tab **Secrets**
5. เพิ่ม:
```toml
READTOON_EMAIL = "kabaofab@gmail.com"
READTOON_PASSWORD = "Ip11220473"
```

### 🖥️ Server/VPS
```bash
export READTOON_EMAIL="kabaofab@gmail.com"
export READTOON_PASSWORD="Ip11220473"
streamlit run app.py
```

### 🐳 Docker
```dockerfile
ENV READTOON_EMAIL="kabaofab@gmail.com"
ENV READTOON_PASSWORD="Ip11220473"
```

---

## 💻 Usage

### Option 1: ใช้ใน Streamlit App
```python
# app.py
from readtoon_scraper import fetch_readtoon_data

# ดึงข้อมูล
data = fetch_readtoon_data(
    email="kabaofab@gmail.com",
    password="Ip11220473"
)

# ข้อมูลที่ได้
print(data["sales"])      # รายการขาย
print(data["revenue"])    # สรุปรายได้
print(data["timestamp"])  # เวลา
```

### Option 2: ใช้แบบ Standalone
```bash
# รัน example
python example_readtoon_usage.py

# เลือก option:
# 1. ดึงข้อมูล
# 2. ใช้ class
# 3. บันทึก CSV
# 4. วิเคราะห์
```

### Option 3: ใช้ class ReadToonScraper
```python
from readtoon_scraper import ReadToonScraper

scraper = ReadToonScraper("email", "password")
scraper.login()

sales = scraper.get_sales_data()      # DataFrame
revenue = scraper.get_revenue_summary()  # dict
monthly = scraper.get_monthly_breakdown()  # DataFrame
```

---

## 📊 Dashboard Tabs

### 📊 Tab 1: สรุปยอด
- รายได้รวมทั้งสิ้น
- รายได้สุทธิ
- ค่าที่หักของแพลตฟอร์ม
- กราฟรายได้รายเดือน
- ตาราง 6 เดือนล่าสุด

### 📈 Tab 2: รายละเอียด
- ตารางรายละเอียดการขาย
- ปุ่มดาวน์โหลด CSV
- แก้ไขข้อมูลได้โดยตรง

### 💹 Tab 3: เทรนด์
- กราฟเทรนด์ 14 วันล่าสุด
- วิเคราะห์รายได้รายวัน
- ตารางแสดงข้อมูล

### ⚙️ Tab 4: ตั้งค่า
- วิธีการตั้งค่า Credentials
- ตรวจสอบสถานะการเชื่อมต่อ
- คำแนะนำความปลอดภัย

---

## 🔒 Security Best Practices

### ✅ ทำให้ปลอดภัย

```python
# ✅ ใช้ environment variables
email = os.getenv("READTOON_EMAIL")
password = os.getenv("READTOON_PASSWORD")
```

```bash
# ✅ เก็บใน .env (local)
READTOON_EMAIL=email@example.com
READTOON_PASSWORD=password

# ✅ Streamlit Cloud Secrets
READTOON_EMAIL = "email@example.com"
READTOON_PASSWORD = "password"
```

### ❌ อันตรายสูง

```python
# ❌ ห้ามวางรหัสผ่านในโค้ด!
email = "kabaofab@gmail.com"
password = "Ip11220473"  # ❌ ห้ามทำแบบนี้!
```

```bash
# ❌ ห้าม commit .env ขึ้น GitHub
git add .env  # ❌ ผิด!
```

### 📝 Setup .gitignore

```
.env
.env.local
.streamlit/secrets.toml
*.pyc
__pycache__/
```

---

## 📝 File Structure

```
your-project/
├── app.py                          # ✏️ แก้ไข
├── readtoon_scraper.py            # ✅ ไฟล์ใหม่
├── example_readtoon_usage.py      # ✅ ไฟล์ใหม่
├── .env                            # ✅ สร้างจาก .env.example
├── .env.example                    # ✅ ไฟล์ใหม่
├── .gitignore                      # ✅ ไฟล์ใหม่
├── requirements.txt                # (มีแล้ว)
├── requirements_readtoon.txt      # ✅ ไฟล์ใหม่
├── READTOON_SETUP_GUIDE.md        # 📚 Documentation
├── APP_PY_MODIFICATION_GUIDE.md   # 📚 Documentation
└── IMPLEMENTATION_SUMMARY.md      # 📚 Documentation
```

---

## 🐛 Troubleshooting

### ❌ "No module named 'readtoon_scraper'"
```bash
# ตรวจสอบไฟล์ readtoon_scraper.py
ls -la readtoon_scraper.py

# ตรวจสอบ path
python -c "import sys; print(sys.path)"
```

### ❌ "READTOON_PASSWORD is None"
```bash
# ตรวจสอบ environment variables
echo $READTOON_EMAIL
echo $READTOON_PASSWORD

# หรือตรวจสอบไฟล์ .env
cat .env
```

### ❌ "Invalid credentials"
- ตรวจสอบ email/password ถูกต้องหรือไม่
- ลองเข้า https://creator.readtoon.com ทดสอบ
- เปลี่ยนรหัสผ่านหากจำไม่ได้

### ❌ "Connection timeout"
- ตรวจสอบ internet connection
- ตรวจสอบ ReadToon website ปกติหรือไม่
- ลดความถี่ของการเรียก API

### ❌ "Rate Limited"
```python
# เพิ่ม delay ระหว่างการเรียก
import time
time.sleep(2)  # รอ 2 วินาที
```

---

## 🧪 Testing

### ทดสอบ Scraper
```bash
python example_readtoon_usage.py
```

เลือก:
- 1: ดึงข้อมูลทั้งหมด
- 2: ใช้ class
- 3: บันทึก CSV
- 4: วิเคราะห์ข้อมูล

### ทดสอบ Streamlit
```bash
streamlit run app.py
```

ไปที่ "🎯 ReadToon Creator" และทดสอบแต่ละ Tab

---

## 📚 Documentation Files

| ไฟล์ | วัตถุประสงค์ |
|-----|-----------|
| `READTOON_SETUP_GUIDE.md` | คำแนะนำติดตั้งทั้งหมด |
| `APP_PY_MODIFICATION_GUIDE.md` | วิธีแก้ไข app.py |
| `IMPLEMENTATION_SUMMARY.md` | สรุปการนำไปใช้ |
| `example_readtoon_usage.py` | ตัวอย่างโค้ด |
| `requirements_readtoon.txt` | Dependencies |

---

## 🎓 Learn More

- [ReadToon](https://readtoon.com)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Pandas Documentation](https://pandas.pydata.org)
- [Plotly Documentation](https://plotly.com)

---

## 📞 Support

หากมีปัญหา:

1. **ตรวจสอบ Logs**
   ```bash
   streamlit run app.py --logger.level=debug
   ```

2. **ทดสอบ Scraper**
   ```bash
   python example_readtoon_usage.py
   ```

3. **ตรวจสอบ Network**
   ```bash
   curl https://creator.readtoon.com
   ```

4. **ตรวจสอบ Credentials**
   ```bash
   echo $READTOON_EMAIL
   echo $READTOON_PASSWORD
   ```

---

## ✅ Implementation Checklist

- [ ] ติดตั้ง dependencies
- [ ] สร้างไฟล์ .env
- [ ] เพิ่มโค้ดใน app.py (ตามไฟล์ guide)
- [ ] ทดสอบ scraper
- [ ] ทดสอบ Streamlit
- [ ] ตรวจสอบ .gitignore
- [ ] Commit & Push ขึ้น GitHub
- [ ] Deploy ขึ้น Streamlit Cloud (หากต้อง)

---

## 📄 License

เป็นอิสระใช้งาน

---

## 🙏 Credits

สร้างโดย: Claude AI
วันที่: 2026-04-04

---

## ⭐ Don't Forget!

- ⭐ Star ไฟล์นี้ถ้ามีประโยชน์
- 💬 Share feedback
- 🐛 Report bugs

---

**🎉 Ready to integrate ReadToon with Streamlit! Happy coding! 🎉**
