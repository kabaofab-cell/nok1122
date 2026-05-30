import pandas as pd
import streamlit as st


def render_finance_page(append_audit_log, save_data, validate_finance_editor_df):
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Finance</div>
            <div class="hero-title">จัดการบัญชี & ส่วนแบ่ง</div>
            <p class="hero-subtitle">บันทึกรายรับได้เร็วขึ้น ดูสรุปยอดแยกตาม QC และตรวจสอบข้อมูลย้อนหลังได้สะดวก</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.title("💰 จัดการบัญชี & ส่วนแบ่ง (QC)")

    tab1, tab2, tab3 = st.tabs(["⚡ ลงบัญชีด่วนรายคน", "📝 ฐานข้อมูลรายรับ", "💸 สรุปยอดส่วนแบ่ง"])

    with tab1:
        st.info("💡 เลือกวันที่, แพลตฟอร์ม และผู้ดูแล (QC) ระบบจะดึงนิยายของคนนั้นมาให้กรอกยอดพร้อมกันครับ")
        c1, c2, c3 = st.columns(3)
        q_date = c1.date_input("วันที่ลงบัญชี")
        q_plat = c2.selectbox("แพลตฟอร์ม", st.session_state.app_settings["platforms"])
        q_qc = c3.selectbox("กรองตามผู้ดูแล (QC)", ["ตอง", "ตาว"])

        qc_books = [b["ชื่อเรื่อง"] for b in st.session_state.books_data if b.get("QC") == q_qc]
        if qc_books:
            df_quick_fin = pd.DataFrame({"ชื่อเรื่อง": qc_books, "ยอดดิบ": [0.0] * len(qc_books)})
            edited_q_fin = st.data_editor(
                df_quick_fin,
                column_config={
                    "ชื่อเรื่อง": st.column_config.TextColumn("ชื่อเรื่อง", disabled=True),
                    "ยอดดิบ": st.column_config.NumberColumn("ยอดดิบ (฿)", min_value=0.0),
                },
                use_container_width=True,
                hide_index=True,
            )

            if st.button("💾 บันทึกยอดรายรับทั้งหมด", type="primary"):
                new_entries = [
                    {
                        "วันที่": q_date.strftime("%Y-%m-%d"),
                        "ชื่อเรื่อง": row["ชื่อเรื่อง"],
                        "แพลตฟอร์ม": q_plat,
                        "ยอดดิบ": row["ยอดดิบ"],
                        "หักแพลตฟอร์ม (17%)": row["ยอดดิบ"] * 0.17,
                        "ยอดสุทธิ": row["ยอดดิบ"] * 0.83,
                    }
                    for _, row in edited_q_fin.iterrows()
                    if row["ยอดดิบ"] > 0
                ]
                if new_entries:
                    st.session_state.finance_db = pd.concat([st.session_state.finance_db, pd.DataFrame(new_entries)], ignore_index=True)
                    append_audit_log("เพิ่มรายรับ", f"{q_date.strftime('%Y-%m-%d')} / {q_plat} / {q_qc}")
                    save_data(["Finance", "AuditLog"])
                    st.rerun()
                else:
                    st.warning("ไม่มียอดให้บันทึกครับ")
        else:
            st.warning("ไม่พบนิยายของ QC ท่านนี้")

    with tab2:
        edited_finance = st.data_editor(st.session_state.finance_db, num_rows="dynamic", use_container_width=True)
        if st.button("💾 บันทึกตารางฐานข้อมูล"):
            fin_errors = validate_finance_editor_df(edited_finance)
            if fin_errors:
                for err in fin_errors[:5]:
                    st.warning(err)
                st.stop()
            st.session_state.finance_db = edited_finance
            append_audit_log("แก้ไขฐานข้อมูลการเงิน", f"จำนวน {len(edited_finance)} แถว")
            save_data(["Finance", "AuditLog"])
            st.rerun()

    with tab3:
        if not st.session_state.finance_db.empty:
            df_fin = st.session_state.finance_db.copy()
            df_books = pd.DataFrame(st.session_state.books_data)

            if df_books.empty:
                df_books = pd.DataFrame(columns=["ชื่อเรื่อง", "QC"])
            elif "ชื่อเรื่อง" not in df_books.columns or "QC" not in df_books.columns:
                for col in ["ชื่อเรื่อง", "QC"]:
                    if col not in df_books.columns:
                        df_books[col] = ""

            df_merge = pd.merge(df_fin, df_books[["ชื่อเรื่อง", "QC"]], on="ชื่อเรื่อง", how="left")
            df_merge["ยอดสุทธิ"] = pd.to_numeric(df_merge["ยอดสุทธิ"], errors="coerce").fillna(0)
            df_merge["เดือน-ปี"] = pd.to_datetime(df_merge["วันที่"]).dt.strftime("%Y-%m")

            sel_month = st.selectbox("📌 เลือกรอบเดือนที่ต้องการดู", sorted(df_merge["เดือน-ปี"].dropna().unique(), reverse=True))
            df_m = df_merge[df_merge["เดือน-ปี"] == sel_month]

            col_t, col_a, col_all = st.columns(3)
            col_t.markdown(f"<div class='metric-card'><h3 style='color:#f87171;'>💖 ยอดของ ตอง</h3><h2>฿{df_m[df_m['QC']=='ตอง']['ยอดสุทธิ'].sum():,.2f}</h2></div>", unsafe_allow_html=True)
            col_a.markdown(f"<div class='metric-card'><h3 style='color:#60a5fa;'>💙 ยอดของ ตาว</h3><h2>฿{df_m[df_m['QC']=='ตาว']['ยอดสุทธิ'].sum():,.2f}</h2></div>", unsafe_allow_html=True)
            col_all.markdown(f"<div class='metric-card'><h3>🌍 รวมสุทธิ</h3><h2>฿{df_m['ยอดสุทธิ'].sum():,.2f}</h2></div>", unsafe_allow_html=True)

            st.dataframe(df_m[["วันที่", "ชื่อเรื่อง", "แพลตฟอร์ม", "QC", "ยอดสุทธิ"]].sort_values("ยอดสุทธิ", ascending=False), use_container_width=True)
