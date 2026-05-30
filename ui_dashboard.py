import pandas as pd
import plotly.express as px
import streamlit as st

from ui_components import render_hero
from ui_panels import render_system_health_panel


CHART_COLORS = ["#006d77", "#e95f46", "#1f9d72", "#f2b84b", "#4a8f8a", "#b94f3d"]


def render_dashboard(fetch_all_google_sheets):
    render_hero(
        "Overview",
        "สรุปภาพรวมของระบบ",
        "ดูสถานะนิยาย คิวงาน และรายรับในหน้าเดียว พร้อมรีเฟรชข้อมูลได้ทันที",
    )
    render_system_health_panel()

    if st.button("โหลดข้อมูลใหม่", type="primary"):
        fetch_all_google_sheets.clear()
        st.session_state.pop("books_data", None)
        st.session_state.pop("finance_db", None)
        st.session_state.pop("calendar_db", None)
        st.session_state.pop("app_settings", None)
        st.rerun()

    books = st.session_state.books_data
    total_books = len(books)
    active_books = sum(1 for b in books if b.get("สถานะ") == "กำลังอัปเดต")
    finished_books = sum(1 for b in books if b.get("สถานะ") == "จบแล้ว")

    df_finance = st.session_state.finance_db.copy()
    total_revenue = pd.to_numeric(df_finance["ยอดสุทธิ"], errors="coerce").sum() if not df_finance.empty else 0

    st.markdown('<div class="section-title">ภาพรวมตัวเลขสำคัญ</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><h3>นิยายทั้งหมด</h3><h2>{total_books}</h2></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><h3>กำลังอัปเดต</h3><h2>{active_books}</h2></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><h3>จบแล้ว</h3><h2>{finished_books}</h2></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><h3>ยอดสุทธิรวม</h3><h2>฿{total_revenue:,.0f}</h2></div>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">แนวโน้มรายงาน</div>', unsafe_allow_html=True)
    chart_1, chart_2 = st.columns(2)
    with chart_1:
        if total_books > 0:
            fig_cat = px.pie(
                pd.DataFrame(books),
                names="หมวดหมู่",
                title="สัดส่วนนิยายแยกตามหมวดหมู่",
                hole=0.48,
                color_discrete_sequence=CHART_COLORS,
            )
            fig_cat.update_layout(font_family="Kanit", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("ยังไม่มีข้อมูลนิยาย")
    with chart_2:
        if not df_finance.empty and total_revenue > 0:
            by_platform = df_finance.groupby("แพลตฟอร์ม")["ยอดสุทธิ"].sum().reset_index()
            fig_plat = px.bar(
                by_platform,
                x="แพลตฟอร์ม",
                y="ยอดสุทธิ",
                title="รายได้สุทธิแยกตามแพลตฟอร์ม",
                text_auto=".2s",
                color="แพลตฟอร์ม",
                color_discrete_sequence=CHART_COLORS,
            )
            fig_plat.update_layout(font_family="Kanit", showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_plat, use_container_width=True)
        else:
            st.info("ยังไม่มีข้อมูลรายรับ")

    st.markdown("---")
    st.subheader("10 อันดับนิยายขายดีประจำเดือน")
    if not df_finance.empty:
        df_finance["เดือน-ปี"] = pd.to_datetime(df_finance["วันที่"]).dt.strftime("%Y-%m")
        avail_months = sorted(df_finance["เดือน-ปี"].dropna().unique(), reverse=True)

        if avail_months:
            selected_dash_month = st.selectbox("เลือกเดือนที่ต้องการดูยอดขาย", avail_months, key="dash_month_selector")
            df_month = df_finance[df_finance["เดือน-ปี"] == selected_dash_month]

            if not df_month.empty:
                df_month["ยอดสุทธิ"] = pd.to_numeric(df_month["ยอดสุทธิ"], errors="coerce").fillna(0)
                top10 = df_month.groupby("ชื่อเรื่อง")["ยอดสุทธิ"].sum().reset_index()
                top10 = top10.sort_values(by="ยอดสุทธิ", ascending=False).head(10)
                top10.index = range(1, len(top10) + 1)

                dash_c1, dash_c2 = st.columns([1, 2])
                with dash_c1:
                    st.dataframe(top10.style.format({"ยอดสุทธิ": "฿{:,.2f}"}), use_container_width=True)
                with dash_c2:
                    fig_top10 = px.bar(
                        top10,
                        x="ยอดสุทธิ",
                        y="ชื่อเรื่อง",
                        orientation="h",
                        title=f"Top 10 Bestsellers ({selected_dash_month})",
                        text="ยอดสุทธิ",
                        color="ยอดสุทธิ",
                        color_continuous_scale=["#d9eee8", "#006d77", "#073b3f"],
                    )
                    fig_top10.update_traces(texttemplate="฿%{text:,.0f}", textposition="outside")
                    fig_top10.update_layout(
                        yaxis={"categoryorder": "total ascending"},
                        font_family="Kanit",
                        coloraxis_showscale=False,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(fig_top10, use_container_width=True)
            else:
                st.info("ไม่มีข้อมูลยอดขายในเดือนที่เลือก")
