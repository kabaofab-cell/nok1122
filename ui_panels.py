import pandas as pd
import streamlit as st

from app_utils import (
    append_audit_log,
    deduplicate_dataframe,
    export_section_csv,
    get_imgbb_api_key,
    get_thai_date,
    safe_image,
    upload_to_imgbb,
)


def render_system_health_panel():
    st.subheader("💚 ระบบสุขภาพระบบ")
    has_imgbb = bool(get_imgbb_api_key())
    books_rows = len(st.session_state.get("books_data", []))
    finance_rows = len(st.session_state.get("finance_db", pd.DataFrame()))
    calendar_rows = len(st.session_state.get("calendar_db", pd.DataFrame()))
    audit_rows = len(st.session_state.get("audit_log", pd.DataFrame()))

    c1, c2, c3 = st.columns(3)
    c1.metric("ImgBB Key", "พร้อม" if has_imgbb else "ไม่พร้อม")
    c2.metric("Books", books_rows)
    c3.metric("Finance", finance_rows)
    c4, c5 = st.columns(2)
    c4.metric("Calendar", calendar_rows)
    c5.metric("Audit Log", audit_rows)


def render_audit_log_viewer():
    st.title("🧾 ประวัติการแก้ไข")
    audit_df = st.session_state.get(
        "audit_log", pd.DataFrame(columns=["เวลา", "การกระทำ", "รายละเอียด"])
    )
    if audit_df.empty:
        st.info("ยังไม่มีประวัติการแก้ไข")
        return

    df = audit_df.copy()
    df["เวลา"] = pd.to_datetime(df["เวลา"], errors="coerce")
    actions = sorted(df["การกระทำ"].dropna().astype(str).unique().tolist())

    c1, c2, c3 = st.columns(3)
    action_filter = c1.multiselect("การกระทำ", actions)
    keyword = c2.text_input("ค้นหา (รายละเอียด)")
    days = c3.selectbox("ช่วงเวลา", [7, 30, 90, 365], index=1)

    since = pd.Timestamp.now() - pd.Timedelta(days=days)
    filtered = df[df["เวลา"] >= since]
    if action_filter:
        filtered = filtered[filtered["การกระทำ"].isin(action_filter)]
    if keyword.strip():
        filtered = filtered[
            filtered["รายละเอียด"].astype(str).str.contains(keyword.strip(), case=False, na=False)
        ]

    filtered = filtered.sort_values("เวลา", ascending=False)
    st.dataframe(filtered.head(500), use_container_width=True)
    export_section_csv("AuditLog", filtered, "audit_log_filtered.csv")


@st.dialog("📅 บันทึกคิวงานรายวัน")
def daily_manager_dialog(selected_date, unique_novels, save_data=None):
    st.markdown(f"**ตารางงานของวันที่:** `{selected_date}`")

    day_events = st.session_state.calendar_db[st.session_state.calendar_db["วันที่"] == selected_date].copy()
    options = unique_novels if unique_novels else ["ยังไม่มีข้อมูลนิยาย"]

    if day_events.empty:
        day_events = pd.DataFrame([{"ชื่อเรื่อง": options[0], "ตอนที่": ""}])
    else:
        day_events = day_events[["ชื่อเรื่อง", "ตอนที่"]]
        day_events["ชื่อเรื่อง"] = day_events["ชื่อเรื่อง"].fillna(options[0])
        day_events["ตอนที่"] = day_events["ตอนที่"].fillna("").astype(str)
        day_events["ชื่อเรื่อง"] = day_events["ชื่อเรื่อง"].apply(lambda x: x if x in options else options[0])

    try:
        with st.form(key=f"form_stable_{selected_date}"):
            edited_df = st.data_editor(
                day_events,
                column_config={
                    "ชื่อเรื่อง": st.column_config.SelectboxColumn("ชื่อเรื่อง", options=options, required=True),
                    "ตอนที่": st.column_config.TextColumn("ช่วงตอนที่อัป", required=False),
                },
                num_rows="dynamic",
                use_container_width=True,
            )

            submitted = st.form_submit_button("💾 บันทึกตารางคิวงาน", type="primary", use_container_width=True)

            if submitted:
                valid_df = edited_df.dropna(subset=["ชื่อเรื่อง"])
                valid_df = valid_df[valid_df["ชื่อเรื่อง"].astype(str).str.strip() != ""]
                valid_df["วันที่"] = selected_date

                st.session_state.calendar_db = st.session_state.calendar_db[
                    st.session_state.calendar_db["วันที่"] != selected_date
                ]
                if not valid_df.empty:
                    st.session_state.calendar_db = pd.concat(
                        [st.session_state.calendar_db, valid_df], ignore_index=True
                    )

                st.session_state.last_processed_state = None
                append_audit_log("บันทึกคิวงานรายวัน", selected_date)
                if save_data is not None:
                    save_data(["Calendar", "AuditLog"])
                st.rerun()

    except Exception:
        st.error("พบข้อมูลขัดข้องในระบบ กรุณากดปุ่มเพื่อรีเซ็ตงานของวันนี้")
        if st.button("🔄 ล้างข้อมูลและเริ่มใหม่"):
            st.session_state.calendar_db = st.session_state.calendar_db[
                st.session_state.calendar_db["วันที่"] != selected_date
            ]
            st.rerun()

