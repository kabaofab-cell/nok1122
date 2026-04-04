"""
🎯 ตัวอย่างการใช้งาน ReadToon Scraper
สามารถรันไฟล์นี้ได้โดยตรง:
    python example_readtoon_usage.py
"""

import os
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# โหลด environment variables จาก .env
load_dotenv()

# นำเข้า ReadToon module
from readtoon_scraper import ReadToonScraper, fetch_readtoon_data

# ==========================================
# ตัวอย่างที่ 1: ใช้ fetch_readtoon_data (ง่ายที่สุด)
# ==========================================
def example_1_simple():
    """ตัวอย่างการใช้งานง่ายๆ"""
    print("=" * 50)
    print("📚 ตัวอย่างที่ 1: ใช้งานง่ายๆ")
    print("=" * 50)
    
    # ดึง credentials จาก environment variables
    email = os.getenv("READTOON_EMAIL")
    password = os.getenv("READTOON_PASSWORD")
    
    if not email or not password:
        print("❌ ยังไม่ได้ตั้งค่า READTOON_EMAIL และ READTOON_PASSWORD")
        print("💡 สร้างไฟล์ .env และเพิ่ม:")
        print("   READTOON_EMAIL=your_email@example.com")
        print("   READTOON_PASSWORD=your_password")
        return
    
    # เรียก fetch function
    data = fetch_readtoon_data(email, password)
    
    # แสดงผล
    if "error" not in data:
        print("\n✅ ดึงข้อมูลสำเร็จ!")
        print(f"⏰ เวลา: {data.get('timestamp')}")
        print(f"📊 จำนวนการขาย: {len(data.get('sales', []))}")
        print(f"💰 ข้อมูลรายได้: {json.dumps(data.get('revenue', {}), indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ ข้อผิดพลาด: {data['error']}")


# ==========================================
# ตัวอย่างที่ 2: ใช้ ReadToonScraper class (ขั้นสูง)
# ==========================================
def example_2_advanced():
    """ตัวอย่างการใช้งาน class โดยตรง"""
    print("\n" + "=" * 50)
    print("🎯 ตัวอย่างที่ 2: การใช้ class โดยตรง")
    print("=" * 50)
    
    email = os.getenv("READTOON_EMAIL")
    password = os.getenv("READTOON_PASSWORD")
    
    if not email or not password:
        print("❌ ยังไม่ได้ตั้งค่า credentials")
        return
    
    # สร้าง scraper instance
    scraper = ReadToonScraper(email, password)
    
    # เข้าสู่ระบบ
    if scraper.login():
        print("\n✅ เข้าสู่ระบบสำเร็จ!")
        
        # ดึงข้อมูลการขาย
        print("\n📊 ดึงข้อมูลการขาย...")
        df_sales = scraper.get_sales_data()
        if not df_sales.empty:
            print(f"✅ ได้รับ {len(df_sales)} รายการ")
            print("\n📋 ข้อมูล 5 รายการแรก:")
            print(df_sales.head())
        
        # ดึงข้อมูลรายได้
        print("\n💰 ดึงข้อมูลรายได้...")
        revenue = scraper.get_revenue_summary()
        print(json.dumps(revenue, indent=2, ensure_ascii=False))
        
        # ดึงข้อมูลรายเดือน
        print("\n📅 ดึงข้อมูลเดือนปัจจุบัน...")
        df_monthly = scraper.get_monthly_breakdown()
        if not df_monthly.empty:
            print(f"✅ ได้รับ {len(df_monthly)} รายการ")
            print(df_monthly)
    else:
        print("❌ เข้าสู่ระบบล้มเหลว")


# ==========================================
# ตัวอย่างที่ 3: บันทึกข้อมูลลงไฟล์ CSV
# ==========================================
def example_3_export_csv():
    """บันทึกข้อมูลเป็น CSV"""
    print("\n" + "=" * 50)
    print("💾 ตัวอย่างที่ 3: บันทึกข้อมูลเป็น CSV")
    print("=" * 50)
    
    email = os.getenv("READTOON_EMAIL")
    password = os.getenv("READTOON_PASSWORD")
    
    if not email or not password:
        print("❌ ยังไม่ได้ตั้งค่า credentials")
        return
    
    # ดึงข้อมูล
    scraper = ReadToonScraper(email, password)
    if scraper.login():
        df_sales = scraper.get_sales_data()
        
        if not df_sales.empty:
            # บันทึกเป็น CSV
            filename = f"readtoon_sales_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df_sales.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"✅ บันทึกสำเร็จ: {filename}")
        else:
            print("❌ ไม่มีข้อมูล")
    else:
        print("❌ เข้าสู่ระบบล้มเหลว")


# ==========================================
# ตัวอย่างที่ 4: วิเคราะห์ข้อมูล
# ==========================================
def example_4_analysis():
    """วิเคราะห์ข้อมูลรายได้"""
    print("\n" + "=" * 50)
    print("📊 ตัวอย่างที่ 4: วิเคราะห์ข้อมูล")
    print("=" * 50)
    
    email = os.getenv("READTOON_EMAIL")
    password = os.getenv("READTOON_PASSWORD")
    
    if not email or not password:
        print("❌ ยังไม่ได้ตั้งค่า credentials")
        return
    
    scraper = ReadToonScraper(email, password)
    if scraper.login():
        df_sales = scraper.get_sales_data()
        
        if not df_sales.empty:
            print("\n📊 สรุปวิเคราะห์:")
            print(f"  • จำนวนรายการขายทั้งหมด: {len(df_sales)}")
            
            # หากมีคอลัมน์ amount
            if 'amount' in df_sales.columns:
                total = df_sales['amount'].sum()
                avg = df_sales['amount'].mean()
                max_sale = df_sales['amount'].max()
                min_sale = df_sales['amount'].min()
                
                print(f"  • รายได้รวม: ฿{total:,.2f}")
                print(f"  • รายได้เฉลี่ย: ฿{avg:,.2f}")
                print(f"  • การขายสูงสุด: ฿{max_sale:,.2f}")
                print(f"  • การขายต่ำสุด: ฿{min_sale:,.2f}")
            
            # หากมีข้อมูลตามวัน
            if 'date' in df_sales.columns:
                df_sales['date'] = pd.to_datetime(df_sales['date'])
                daily = df_sales.groupby('date')['amount'].sum()
                print(f"\n  📅 รายได้รายวัน:")
                print(daily.tail(7))  # 7 วันล่าสุด
        else:
            print("❌ ไม่มีข้อมูล")
    else:
        print("❌ เข้าสู่ระบบล้มเหลว")


# ==========================================
# Main
# ==========================================
if __name__ == "__main__":
    print("\n")
    print("🎯 ตัวอย่างการใช้งาน ReadToon Scraper")
    print("=" * 50)
    
    # เลือกตัวอย่างที่ต้องการ
    print("\n📌 เลือกตัวอย่าง:")
    print("  1. ใช้งานง่ายๆ (ดึงข้อมูลทั้งหมด)")
    print("  2. ใช้ class โดยตรง (ขั้นสูง)")
    print("  3. บันทึกข้อมูลเป็น CSV")
    print("  4. วิเคราะห์ข้อมูล")
    print("  0. รัน ทั้งหมด")
    
    choice = input("\nเลือก (0-4): ").strip()
    
    if choice == "1":
        example_1_simple()
    elif choice == "2":
        example_2_advanced()
    elif choice == "3":
        example_3_export_csv()
    elif choice == "4":
        example_4_analysis()
    elif choice == "0":
        example_1_simple()
        example_2_advanced()
        example_3_export_csv()
        example_4_analysis()
    else:
        print("❌ เลือกตัวเลือกที่ถูกต้อง")
    
    print("\n" + "=" * 50)
    print("✅ เสร็จสิ้น")
    print("=" * 50 + "\n")
