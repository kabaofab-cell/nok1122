import json
from datetime import datetime

import pandas as pd
import requests
import streamlit as st


def safe_image(url, img_class="rank-img"):
    if url and str(url).strip() != "":
        st.markdown(
            f'<img src="{url}" class="{img_class}" onerror="this.onerror=null;this.src=\'https://via.placeholder.com/300x450?text=Error\';">',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<img src="https://via.placeholder.com/300x450?text=No+Cover" class="{img_class}">',
            unsafe_allow_html=True,
        )


def get_thai_date(raw_date_str):
    try:
        if "T" in str(raw_date_str):
            dt = pd.to_datetime(raw_date_str)
            if dt.tzinfo is not None:
                dt = dt.tz_convert("Asia/Bangkok")
            else:
                dt = dt + pd.Timedelta(hours=7)
            return dt.strftime("%Y-%m-%d")
        return str(raw_date_str)[:10]
    except (ValueError, TypeError):
        return str(raw_date_str)[:10]


def get_imgbb_api_key():
    key = ""
    if hasattr(st, "secrets"):
        key = (
            st.secrets.get("IMGBB_API_KEY", "")
            or st.secrets.get("imgbb_api_key", "")
            or st.secrets.get("IMGBB_KEY", "")
        )
    if not key:
        import os

        key = os.getenv("IMGBB_API_KEY", "") or os.getenv("IMGBB_KEY", "")
    if not key:
        st.error("🚨 ไม่พบ IMGBB_API_KEY ใน secrets/env กรุณาตั้งค่าใน Streamlit Secrets")
        st.info('ตัวอย่าง: `IMGBB_API_KEY = "your_imgbb_key"`')
        return None
    return key


def clean_str(val):
    return str(val) if pd.notna(val) and str(val).lower() != "nan" else ""


def log_error(context, error):
    st.error(f"❌ {context}: {type(error).__name__} - {error}")


def check_required_secrets():
    required_keys = ["IMGBB_API_KEY"]
    missing = [k for k in required_keys if not st.secrets.get(k)]
    if missing:
        st.warning(
            f"⚠️ ยังไม่ได้ตั้งค่า secrets: {', '.join(missing)} (ฟีเจอร์อัปโหลดรูปจะใช้งานไม่ได้)"
        )


def safe_parse_date(value):
    try:
        dt = pd.to_datetime(value, errors="raise")
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def deduplicate_dataframe(df, subset_cols):
    if df.empty:
        return df
    return df.drop_duplicates(subset=subset_cols, keep="last").reset_index(drop=True)


def validate_book_editor_df(df):
    errors = []
    for i, row in df.iterrows():
        if not str(row.get("ชื่อเรื่อง", "")).strip():
            errors.append(f"แถว {i+1}: ชื่อเรื่องห้ามว่าง")
        for ncol in ["ตอนปัจจุบัน"]:
            val = pd.to_numeric(row.get(ncol), errors="coerce")
            if pd.isna(val) or val < 0:
                errors.append(f"แถว {i+1}: {ncol} ต้องเป็นเลข >= 0")
    return errors


def validate_finance_editor_df(df):
    required = ["วันที่", "ชื่อเรื่อง", "แพลตฟอร์ม", "ยอดดิบ", "หักแพลตฟอร์ม (17%)", "ยอดสุทธิ"]
    errors = []
    for col in required:
        if col not in df.columns:
            errors.append(f"ไม่มีคอลัมน์ {col}")
    if errors:
        return errors

    for i, row in df.iterrows():
        if not safe_parse_date(row.get("วันที่")):
            errors.append(f"แถว {i+1}: วันที่ไม่ถูกต้อง")
        if not str(row.get("ชื่อเรื่อง", "")).strip():
            errors.append(f"แถว {i+1}: ชื่อเรื่องห้ามว่าง")
        if not str(row.get("แพลตฟอร์ม", "")).strip():
            errors.append(f"แถว {i+1}: แพลตฟอร์มห้ามว่าง")
    return errors


def append_audit_log(action, detail):
    if "audit_log" not in st.session_state:
        st.session_state.audit_log = pd.DataFrame(columns=["เวลา", "การกระทำ", "รายละเอียด"])
    new_row = pd.DataFrame(
        [
            {
                "เวลา": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "การกระทำ": action,
                "รายละเอียด": detail,
            }
        ]
    )
    st.session_state.audit_log = pd.concat([st.session_state.audit_log, new_row], ignore_index=True)


def export_section_csv(label, df, filename):
    if df is None or df.empty:
        st.caption(f"{label}: ยังไม่มีข้อมูลให้ดาวน์โหลด")
        return
    csv_data = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(f"⬇️ Export {label} (CSV)", data=csv_data, file_name=filename, mime="text/csv")


def upload_to_imgbb(file, timeout=20, retries=2):
    api_key = get_imgbb_api_key()
    if not api_key:
        return None

    with st.spinner("กำลังอัปโหลดรูปภาพไปยัง ImgBB..."):
        for attempt in range(1, retries + 1):
            try:
                res = requests.post(
                    "https://api.imgbb.com/1/upload",
                    data={"key": api_key},
                    files={"image": file.getvalue()},
                    timeout=timeout,
                )
                if res.status_code == 200:
                    return res.json().get("data", {}).get("url")
                st.warning(f"ครั้งที่ {attempt}: ImgBB ตอบกลับด้วยสถานะ {res.status_code}")
            except requests.RequestException as e:
                if attempt == retries:
                    log_error("Upload Failed", e)
                else:
                    st.warning(f"เครือข่ายมีปัญหา กำลังลองใหม่ ({attempt}/{retries})")
    return None


def parse_links(raw_link_data):
    if pd.isna(raw_link_data):
        return []
    text = str(raw_link_data).strip()
    if text in ["", "nan"]:
        return []
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


def normalize_book_record(book):
    book["ภาพปก"] = clean_str(book.get("ภาพปก"))
    book["เรื่องย่อ"] = clean_str(book.get("เรื่องย่อ"))
    book["หมายเหตุ"] = clean_str(book.get("หมายเหตุ"))
    book["ลิงก์อ่าน"] = parse_links(book.get("ลิงก์อ่าน"))
    book["ลิงก์ต้นฉบับ"] = parse_links(book.get("ลิงก์ต้นฉบับ"))
    book["สถานะ"] = book.get("สถานะ", "กำลังอัปเดต")
    book["หมวดหมู่"] = book.get("หมวดหมู่", "ทั่วไป")
    book["QC"] = book.get("QC", "ต้อง")
    book["ตอนปัจจุบัน"] = int(book.get("ตอนปัจจุบัน", 0)) if pd.notna(book.get("ตอนปัจจุบัน")) else 0
    book["เป้าหมาย"] = int(book.get("เป้าหมาย", 1)) if pd.notna(book.get("เป้าหมาย")) else 1
    return book

