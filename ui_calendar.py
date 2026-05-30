import pandas as pd
import streamlit as st
from streamlit_calendar import calendar


def render_calendar_page(get_thai_date, daily_manager_dialog, append_audit_log, deduplicate_dataframe, save_data):
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Calendar</div>
            <div class="hero-title">ปฏิทินคิวงาน</div>
            <p class="hero-subtitle">คลิกวันที่เพื่อเพิ่มหรือแก้ไขคิวงานของวันนั้นๆ เหมาะกับการมองภาพรวมรายเดือนและแก้รายการอย่างรวดเร็ว</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info("💡 คลิกที่ช่องวันที่เพื่อเพิ่มหรือแก้ไขคิวงานของวันนั้นๆ")

    unique_novels = [b["ชื่อเรื่อง"] for b in st.session_state.books_data] if st.session_state.books_data else []

    colors = ["#fca5a5", "#93c5fd", "#86efac", "#fcd34d", "#d8b4fe", "#5eead4", "#f9a8d4", "#bef264", "#fdba74", "#94a3b8"]
    color_map = {novel: colors[i % len(colors)] for i, novel in enumerate(unique_novels)}

    events = []
    if not st.session_state.calendar_db.empty:
        for idx, row in st.session_state.calendar_db.iterrows():
            novel_name = str(row.get("ชื่อเรื่อง", ""))
            chap = str(row.get("ตอนที่", ""))
            raw_date = str(row.get("วันที่", ""))
            date_val = raw_date.split(" ")[0][:10] if raw_date else ""

            if date_val and date_val.lower() not in ["nan", "nat", "none", ""]:
                display_title = f"[{chap}] {novel_name}" if chap and chap.lower() != "nan" else novel_name
                events.append(
                    {
                        "id": str(idx),
                        "title": display_title,
                        "start": date_val,
                        "color": color_map.get(novel_name, "#cbd5e1"),
                        "textColor": "#1e293b",
                        "allDay": True,
                    }
                )

    calendar_options = {
        "timeZone": "Asia/Bangkok",
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,timeGridWeek"},
        "initialView": "dayGridMonth",
        "selectable": True,
        "height": "auto",
        "contentHeight": "auto",
        "aspectRatio": 1.5,
        "dayMaxEvents": True,
        "expandRows": True,
        "eventDisplay": "block",
    }

    state = calendar(events=events, options=calendar_options, key="novel_calendar_smart")

    if state is not None and state.get("callback") in ["dateClick", "eventClick"]:
        current_state_str = str(state)

        if st.session_state.get("last_processed_state") != current_state_str:
            if state["callback"] == "dateClick":
                raw_date = state["dateClick"]["date"]
                clicked_date = get_thai_date(raw_date)
                daily_manager_dialog(clicked_date, unique_novels)
            elif state["callback"] == "eventClick":
                raw_date = state["eventClick"]["event"]["start"]
                clicked_date = get_thai_date(raw_date)
                daily_manager_dialog(clicked_date, unique_novels)

    st.markdown("---")
    st.subheader("⚡ ตารางตรวจสอบรายเดือน")
    st.write("ตารางสำหรับตรวจสอบความถูกต้องหรือลบข้อมูลอย่างรวดเร็ว (อัปเดตอัตโนมัติ)")
    edited_cal = st.data_editor(st.session_state.calendar_db, num_rows="dynamic", use_container_width=True, height=250)
    if st.button("💾 บันทึกตารางส่วนนี้", type="secondary"):
        st.session_state.calendar_db = deduplicate_dataframe(edited_cal, ["วันที่", "ชื่อเรื่อง", "ตอนที่"])
        append_audit_log("แก้ไขปฏิทิน", f"จำนวน {len(st.session_state.calendar_db)} แถว")
        save_data(["Calendar", "AuditLog"])
        st.rerun()
