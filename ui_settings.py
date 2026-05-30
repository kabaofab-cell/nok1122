import pandas as pd
import streamlit as st

from app_utils import export_section_csv


def render_settings_page(save_data):
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Settings</div>
            <div class="hero-title">ตั้งค่าระบบ</div>
            <p class="hero-subtitle">จัดการหมวดหมู่ แพลตฟอร์ม และสำรองข้อมูลได้จากหน้าเดียว</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.title("ตั้งค่าหมวดหมู่และแพลตฟอร์ม")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("หมวดหมู่นิยาย")
        ed_c = st.data_editor(
            pd.DataFrame(st.session_state.app_settings["categories"], columns=["ชื่อหมวดหมู่"]),
            num_rows="dynamic",
            use_container_width=True,
        )
    with c2:
        st.subheader("แพลตฟอร์มเผยแพร่")
        ed_p = st.data_editor(
            pd.DataFrame(st.session_state.app_settings["platforms"], columns=["ชื่อแพลตฟอร์ม"]),
            num_rows="dynamic",
            use_container_width=True,
        )

    st.markdown("---")
    st.subheader("สำรองข้อมูล (Backup CSV)")
    e1, e2, e3 = st.columns(3)
    with e1:
        export_section_csv("Books", pd.DataFrame(st.session_state.books_data), "books_backup.csv")
    with e2:
        export_section_csv("Finance", st.session_state.finance_db, "finance_backup.csv")
    with e3:
        export_section_csv("Calendar", st.session_state.calendar_db, "calendar_backup.csv")

    if st.button("บันทึกการตั้งค่า", type="primary"):
        st.session_state.app_settings["categories"] = ed_c["ชื่อหมวดหมู่"].replace("", pd.NA).dropna().tolist()
        st.session_state.app_settings["platforms"] = ed_p["ชื่อแพลตฟอร์ม"].replace("", pd.NA).dropna().tolist()
        save_data(["Settings"])
        st.rerun()
