import logging
import gspread
import streamlit as st
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# ==========================================
# 🔑 1. ดึงค่าจาก Streamlit Secrets
# ==========================================
# วิธีตั้งค่า: ไปที่ Streamlit Cloud > Settings > Secrets แล้ววางค่า JSON และ Token ลงไป
BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
GOOGLE_CREDS = st.secrets["gspread_credentials"] # ใส่เนื้อหาในไฟล์ JSON ทั้งหมดลงในนี้
SHEET_NAME = "ชื่อไฟล์ Google Sheets ของพี่นกแก้ว" 

# เชื่อมต่อ Google Sheets
gc = gspread.service_account_from_dict(GOOGLE_CREDS)
sh = gc.open(SHEET_NAME)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ==========================================
# 🛠️ 2. ระบบดึงข้อมูลจาก Sheets
# ==========================================

def check_permission(user_id):
    """เช็คสิทธิ์จากหน้า UserPermissions"""
    worksheet = sh.worksheet("UserPermissions")
    records = worksheet.get_all_records()
    return [r['ชื่อเรื่อง'] for r in records if str(r['Telegram ID']) == str(user_id) and r['สถานะ'] == 'ใช้งานได้']

def get_chapters(story_name):
    """ดึงรายชื่อตอนจากหน้า Chapters"""
    worksheet = sh.worksheet("Chapters")
    records = worksheet.get_all_records()
    return [r for r in records if r['ชื่อเรื่อง'] == story_name]

# ==========================================
# 🤖 3. ฟังก์ชันบอท
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    permissions = check_permission(user_id)
    
    if permissions:
        keyboard = [[InlineKeyboardButton(f"📖 {story}", callback_data=f"list_{story}")] for story in permissions]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"ยินดีต้อนรับครับพี่นกแก้ว! (ID: {user_id})\nเลือกนิยายที่ต้องการอ่านได้เลยครับ:", reply_markup=reply_markup)
    else:
        await update.message.reply_text(f"สวัสดีครับ ID: {user_id}\nยังไม่พบสิทธิ์การเข้าถึงนิยาย รบกวนแจ้งแอดมินนะครับ")

async def list_ch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    story_name = query.data.replace("list_", "")
    chapters = get_chapters(story_name)
    
    if not chapters:
        await query.edit_message_text(text="ขออภัยครับ ยังไม่มีตอนอัปเดต")
        return

    keyboard = []
    for ch in chapters:
        # 🚀 ลิงก์ Web App Reader (ต้องเป็น URL ที่พี่นกแก้วเอาไปโฮสต์ไฟล์ reader.html ไว้)
        # เราส่งลิงก์ PDF และ User ID ไปด้วยเพื่อทำลายน้ำ
        reader_base_url = "https://nokkaew-reader.pages.dev" 
        full_url = f"{reader_base_url}?pdf={ch['ลิงก์ไฟล์ PDF']}&uid={update.effective_user.id}"
        
        btn_text = f"ตอนที่ {ch['ตอนที่']}: {ch['ชื่อตอน']}"
        keyboard.append([InlineKeyboardButton(text=btn_text, web_app=WebAppInfo(url=full_url))])
    
    keyboard.append([InlineKeyboardButton("🔙 กลับ", callback_data="home")])
    await query.edit_message_text(text=f"📚 {story_name}\nเลือกตอนที่ต้องการอ่าน:", reply_markup=InlineKeyboardMarkup(keyboard))

if __name__ == '__main__':
    # สำหรับ Streamlit Cloud เรามักจะรันบอทแยกหรือใช้ Thread 
    # แต่ถ้าจะทดสอบ ให้รันไฟล์นี้แยกในเครื่องได้เลยครับ
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(list_ch, pattern="^list_"))
    app.run_polling()
