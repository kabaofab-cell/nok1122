import pandas as pd
import streamlit as st


def render_books_page(safe_image, upload_to_imgbb, append_audit_log, save_data, validate_book_editor_df):
    st.title("📚 จัดการนิยาย & ไฟล์")
    tab1, tab2 = st.tabs(["🖼️ แกลลอรี่นิยาย (ทั้งหมด)", "⚡ แก้ไขข้อมูลด่วน (ตาราง)"])

    with tab1:
        with st.expander("✨ เพิ่มนิยายเรื่องใหม่"):
            with st.form("add_book_form"):
                c_new1, c_new2 = st.columns(2)
                new_title = c_new1.text_input("ชื่อเรื่องนิยาย")
                new_cat = c_new1.selectbox("หมวดหมู่", st.session_state.app_settings['categories'])
                new_cover = c_new2.text_input("ลิงก์รูปปก")
                new_qc = c_new2.radio("ผู้ดูแล (QC)", ["ตอง", "ตาว"], horizontal=True)
            
                if st.form_submit_button("เพิ่มนิยาย"):
                    if not new_title:
                        st.error("❌ กรุณาใส่ชื่อเรื่องนิยาย")
                    elif any(b.get('ชื่อเรื่อง') == new_title for b in st.session_state.books_data):
                        st.error(f"❌ นิยาย '{new_title}' มีอยู่ในระบบแล้ว")
                    else:
                        try:
                            st.session_state.books_data.append({
                                'ชื่อเรื่อง': new_title,
                                'หมวดหมู่': new_cat,
                                'QC': new_qc,
                                'สถานะ': 'กำลังอัปเดต',
                                'ตอนปัจจุบัน': 0,
                                'เป้าหมาย': 100,
                                'ภาพปก': new_cover,
                                'เรื่องย่อ': '',
                                'ลิงก์อ่าน': [],
                                'ลิงก์ต้นฉบับ': []
                            })
                            append_audit_log("เพิ่มนิยาย", new_title)
                            save_data(["Books", "AuditLog"])
                            st.success(f"✅ เพิ่มนิยาย '{new_title}' สำเร็จ")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ เพิ่มนิยายล้มเหลว: {str(e)}")

        st.markdown('---')
        st.subheader('🔎 ค้นหาและกรองนิยาย')
        f1, f2, f3, f4 = st.columns(4)
        q_text = f1.text_input('ค้นหาชื่อเรื่อง')
        q_status = f2.selectbox('สถานะ', ['ทั้งหมด', 'กำลังอัปเดต', 'จบแล้ว', 'พักการแปล'])
        q_qc = f3.selectbox('QC', ['ทั้งหมด', 'ตอง', 'ตาว'])
        q_cat = f4.selectbox('หมวดหมู่', ['ทั้งหมด'] + st.session_state.app_settings['categories'])

        books_with_idx = [{'data': b, 'orig_idx': idx} for idx, b in enumerate(st.session_state.books_data)]
        filtered_books = []
        for item in books_with_idx:
            b = item['data']
            if q_text.strip() and q_text.strip().lower() not in str(b.get('ชื่อเรื่อง', '')).lower():
                continue
            if q_status != 'ทั้งหมด' and b.get('สถานะ') != q_status:
                continue
            if q_qc != 'ทั้งหมด' and b.get('QC') != q_qc:
                continue
            if q_cat != 'ทั้งหมด' and b.get('หมวดหมู่') != q_cat:
                continue
            filtered_books.append(item)

        all_books = filtered_books[::-1] 
        st.caption(f"ผลลัพธ์ {len(all_books)} เรื่อง")
    
        for i in range(0, len(all_books), 10):
            cols = st.columns(10)
            for j, col in enumerate(cols):
                if i + j < len(all_books):
                    item = all_books[i+j]
                    b = item['data']
                    real_idx = item['orig_idx']
                
                    with col:
                        img_url = b.get('ภาพปก') if b.get('ภาพปก') and str(b.get('ภาพปก')).strip() != "" else "https://via.placeholder.com/300x450"
                        card = f"<div class='rank-card' style='padding: 8px;'><img src='{img_url}' class='rank-img' onerror=\"this.onerror=null;this.src='https://via.placeholder.com/300x450';\"><div style='font-size:11px; font-weight:600; line-height:1.2; margin-bottom:5px; height:28px; overflow:hidden;'>{b['ชื่อเรื่อง']}</div></div>"
                        st.markdown(card.replace('\n',''), unsafe_allow_html=True)
                    
                        if st.button("✏️ แก้ไข", key=f"edit_{real_idx}", use_container_width=True):
                            st.session_state.selected_book_idx = real_idx
                            st.rerun()
                        
                        if st.button("🗑️ ลบ", key=f"delete_{real_idx}", use_container_width=True):
                            st.session_state.book_to_delete = real_idx
                            st.session_state.show_delete_confirm = True
                            st.rerun()
        
        # ลบนิยาย - ขั้นตอนยืนยัน
        if st.session_state.get('show_delete_confirm', False):
            delete_idx = st.session_state.get('book_to_delete')
            if delete_idx is not None and delete_idx < len(st.session_state.books_data):
                book_title = st.session_state.books_data[delete_idx].get('ชื่อเรื่อง', 'Unknown')
                st.warning(f"⚠️ คุณต้องการลบนิยาย '{book_title}' หรือไม่? (ไม่สามารถกู้คืนได้)")
                
                del_col1, del_col2, del_col3 = st.columns(3)
                
                with del_col1:
                    if st.button("✅ ยืนยันลบ", key="confirm_delete"):
                        try:
                            deleted_title = st.session_state.books_data[delete_idx].get('ชื่อเรื่อง', 'Unknown')
                            st.session_state.books_data.pop(delete_idx)
                            append_audit_log("ลบนิยาย", deleted_title)
                            save_data(["Books", "AuditLog"])
                            st.session_state.show_delete_confirm = False
                            st.session_state.book_to_delete = None
                            st.success(f"✅ ลบนิยาย '{deleted_title}' สำเร็จ")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ ลบนิยายล้มเหลว: {str(e)}")
                            st.session_state.show_delete_confirm = False
                
                with del_col2:
                    if st.button("❌ ยกเลิก", key="cancel_delete"):
                        st.session_state.show_delete_confirm = False
                        st.session_state.book_to_delete = None
                        st.rerun()
                        
    with tab2:
        st.info("💡 แก้ไขหมวดหมู่ สถานะ จำนวนตอน และ QC รวดเร็วผ่านตารางนี้ (แสดงผลทั้งหมด)")
        if st.session_state.books_data:
            df_quick = pd.DataFrame(st.session_state.books_data)
            df_quick['_orig_idx'] = df_quick.index
            df_show = df_quick.iloc[::-1].copy()
        
            edit_cols = ['ชื่อเรื่อง', 'หมวดหมู่', 'สถานะ', 'ตอนปัจจุบัน', 'QC']
        
            edited_df = st.data_editor(
                df_show[edit_cols],
                column_config={
                    "หมวดหมู่": st.column_config.SelectboxColumn("หมวดหมู่", options=st.session_state.app_settings['categories'], required=True),
                    "สถานะ": st.column_config.SelectboxColumn("สถานะ", options=["กำลังอัปเดต", "จบแล้ว", "พักการแปล"], required=True),
                    "QC": st.column_config.SelectboxColumn("QC", options=["ตอง", "ตาว"], required=True)
                },
                use_container_width=True, num_rows="fixed", height=500
            )
        
            if st.button("💾 บันทึกตาราง", type="primary"):
                try:
                    book_errors = validate_book_editor_df(edited_df)
                    if book_errors:
                        for err in book_errors[:5]:
                            st.warning(err)
                        st.stop()
                    for i in range(len(edited_df)):
                        real_idx = df_show.iloc[i]['_orig_idx']
                        for col in edit_cols: 
                            st.session_state.books_data[real_idx][col] = edited_df.iloc[i][col]
                    append_audit_log("แก้ไขตารางนิยาย", f"จำนวน {len(edited_df)} แถว")
                    save_data(["Books", "AuditLog"])
                    st.success("✅ บันทึกข้อมูลสำเร็จ")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ บันทึกข้อมูลล้มเหลว: {str(e)}")
