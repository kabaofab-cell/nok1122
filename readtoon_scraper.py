"""
📚 ReadToon Scraper Module
ใช้สำหรับดึงข้อมูลการขายจาก https://creator.readtoon.com/
"""

import os
import requests
import pandas as pd
from datetime import datetime
import time
from bs4 import BeautifulSoup
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReadToonScraper:
    """ดึงข้อมูลการขายจาก ReadToon Creator Dashboard"""
    
    def __init__(self, email: str, password: str):
        """
        Args:
            email: อีเมลของบัญชี ReadToon
            password: รหัสผ่านของบัญชี ReadToon
        """
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.base_url = "https://creator.readtoon.com"
        self.is_logged_in = False
        
    def login(self) -> bool:
        """เข้าสู่ระบบ ReadToon"""
        try:
            logger.info("🔐 กำลังเข้าสู่ระบบ ReadToon...")
            
            # ทำการเข้าสู่ระบบ
            login_url = f"{self.base_url}/api/auth/login"
            payload = {
                "email": self.email,
                "password": self.password
            }
            
            response = self.session.post(login_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ เข้าสู่ระบบสำเร็จ!")
                self.is_logged_in = True
                return True
            else:
                logger.error(f"❌ เข้าสู่ระบบล้มเหลว: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาดในการเข้าสู่ระบบ: {e}")
            return False
    
    def get_sales_data(self) -> pd.DataFrame:
        """ดึงข้อมูลการขายทั้งหมด"""
        if not self.is_logged_in:
            logger.error("❌ ยังไม่ได้เข้าสู่ระบบ กรุณา login() ก่อน")
            return pd.DataFrame()
        
        try:
            logger.info("📊 กำลังดึงข้อมูลการขาย...")
            
            # เรียก API สำหรับดึงข้อมูลการขาย
            sales_url = f"{self.base_url}/api/dashboard/sales"
            response = self.session.get(sales_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # แปลงเป็น DataFrame
                df = pd.DataFrame(data.get('sales', []))
                logger.info(f"✅ ดึงข้อมูล {len(df)} รายการสำเร็จ")
                return df
            else:
                logger.error(f"❌ ดึงข้อมูลล้มเหลว: {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return pd.DataFrame()
    
    def get_revenue_summary(self) -> dict:
        """ดึงสรุปรายได้"""
        if not self.is_logged_in:
            return {}
        
        try:
            logger.info("💰 กำลังดึงข้อมูลรายได้...")
            
            summary_url = f"{self.base_url}/api/dashboard/revenue"
            response = self.session.get(summary_url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {}
                
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return {}
    
    def get_monthly_breakdown(self, month: str = None) -> pd.DataFrame:
        """ดึงข้อมูลรายได้รายเดือน"""
        if not self.is_logged_in:
            return pd.DataFrame()
        
        try:
            logger.info(f"📅 กำลังดึงข้อมูลเดือน {month or 'ปัจจุบัน'}...")
            
            # ถ้าไม่ระบุเดือน ใช้เดือนปัจจุบัน
            if not month:
                month = datetime.now().strftime("%Y-%m")
            
            monthly_url = f"{self.base_url}/api/dashboard/monthly/{month}"
            response = self.session.get(monthly_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data.get('details', []))
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"❌ ข้อผิดพลาด: {e}")
            return pd.DataFrame()


def fetch_readtoon_data(email: str, password: str) -> dict:
    """
    ฟังก์ชันหลักสำหรับดึงข้อมูลจาก ReadToon
    
    Args:
        email: อีเมล ReadToon Creator
        password: รหัสผ่าน ReadToon Creator
    
    Returns:
        dict: ข้อมูลการขายและรายได้
    """
    scraper = ReadToonScraper(email, password)
    
    # เข้าสู่ระบบ
    if not scraper.login():
        return {"error": "เข้าสู่ระบบล้มเหลว"}
    
    # ดึงข้อมูล
    time.sleep(1)  # รอเล็กน้อยเพื่อหลีกเลี่ยงการถูก rate limit
    
    sales_df = scraper.get_sales_data()
    revenue_summary = scraper.get_revenue_summary()
    
    return {
        "sales": sales_df.to_dict('records') if not sales_df.empty else [],
        "revenue": revenue_summary,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน (ใช้ environment variables)
    email = os.getenv("READTOON_EMAIL")
    password = os.getenv("READTOON_PASSWORD")
    
    if email and password:
        data = fetch_readtoon_data(email, password)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print("❌ ตั้งค่า READTOON_EMAIL และ READTOON_PASSWORD")
