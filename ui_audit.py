import streamlit as st

from ui_panels import render_audit_log_viewer


def render_audit_page():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Audit</div>
            <div class="hero-title">ประวัติการแก้ไข</div>
            <p class="hero-subtitle">ดูว่ามีการเปลี่ยนแปลงอะไร เมื่อไหร่ และโดยใคร เพื่อให้ตามงานและตรวจสอบย้อนหลังได้ง่าย</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_audit_log_viewer()
