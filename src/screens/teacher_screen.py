import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import check_teacher_exists, create_teacher, teacher_login, get_teacher_subjects, get_attendance_for_teacher
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog

from src.components.dialog_attendance_results import attendance_result_dialog
import numpy as np

from datetime import datetime, date
import io

import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from src.database.config import supabase


def teacher_screen():

    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type=="login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()





def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {teacher_data['name']} """)
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data 
            st.rerun()


    st.space()

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'
    tab1, tab2, tab3 = st.columns(3)


    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == 'take_attendance' else "tertiary"
        if st.button('Take Attendance',type=type1, width='stretch', icon=':material/ar_on_you:'):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == 'manage_subjects' else "tertiary"
        if st.button('Manage Subjects', type=type2, width='stretch', icon=':material/book_ribbon:'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()

    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == 'attendance_records' else "tertiary"
        if st.button('Attendance Records',type=type3, width='stretch', icon=':material/cards_stack:'):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()


    st.divider()

    with st.container(key=f"teacher-tab-content-{st.session_state.current_teacher_tab}"):
        if st.session_state.current_teacher_tab == "take_attendance":
            teacher_tab_take_attendance()
        elif st.session_state.current_teacher_tab == "manage_subjects":
            teacher_tab_manage_subjects()
        elif st.session_state.current_teacher_tab == "attendance_records":
            teacher_tab_attendance_records()

    


    footer_dashboard()

def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.warning('You havent created any subjects yet! Please create one to begin!')
        return
    
    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}

    col1, col2 = st.columns([3,1], vertical_alignment='bottom')

    with col1:
        selected_subject_label = st.selectbox('Select Subject', options=list(subject_options.keys()))

    with col2:
        if st.button('Add Photos', type='primary', icon=':material/photo_prints:', width='stretch'):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.divider()

    if st.session_state.attendance_images:
        st.header('Added Photos')
        gallery_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4 ]:
                st.image(img, width='stretch', caption=f'Photo {idx+1}')
    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button('Clear all photos', width='stretch', type='tertiary', icon=':material/delete:', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()


    with c2:
        
        if st.button('Run Face Analysis', width='stretch', type='secondary', icon=':material/analytics:', disabled=not has_photos):
            from src.pipelines.face_pipeline import predict_attendance

            with st.spinner('Deep scanning classroom photos...'):
                all_detected_ids = {}

                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected, _, _ = predict_attendance(img_np)


                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)

                            all_detected_ids.setdefault(student_id, []).append(f"Photo {idx+1}")

                enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id',selected_subject_id ).execute()
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning('No students enrolled in this course')
                else:

                    results, attendance_to_log  = [], []

                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_ids.get(int(student['student_id']), [])
                        is_present= len(sources) > 0

                        results.append({
                            "Name": student['name'],
                            "ID": student['student_id'],
                            "Source": ", ".join(sources) if is_present else "-",
                            "Status": "✅ Present" if is_present else "❌ Absent"
                        })

                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                        })

                attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button('Use Voice Attendance', type='primary', width='stretch', icon=':material/mic:'):
            from src.components.dialog_voice_attendance import voice_attendance_dialog

            voice_attendance_dialog(selected_subject_id)











def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2)
    with col1:
        st.header('Manage Subjects', width='stretch')

    with col2:
        if st.button('Create New Subject', width='stretch'):
            create_subject_dialog(teacher_id)


    # LIST all SUBJECTS
    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("🫂", "Students", sub['total_students']),
                ("🕰️", "Classes", sub['total_classes']),
            ]
        def share_btn():
            if st.button(f"Share Code: {sub['name']}", key=f"share_{sub['subject_code']}", icon=":material/share:"):
                share_subject_dialog(sub['name'], sub['subject_code'])
            st.space()

        subject_card(
            name = sub['name'],
            code = sub['subject_code'],
            section = sub['section'],
            stats=stats,
            footer_callback=share_btn
        )
    else:
        st.info("NO SUBJECTS FOUND. CREATE ONE ABOVE")


def extract_date_str(ts):
    if not ts:
        return ""
    try:
        ts_str = str(ts).strip()
        if 'T' in ts_str:
            part = ts_str.split('T')[0]
            if len(part) == 10 and part[4] == '-' and part[7] == '-':
                return part
        if ' ' in ts_str:
            part = ts_str.split(' ')[0]
            if len(part) == 10 and part[4] == '-' and part[7] == '-':
                return part
        dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except Exception:
        if len(str(ts)) >= 10:
            return str(ts)[:10]
        return ""


def process_attendance_summary(records):
    """
    Groups attendance records by date, session, subject, subject code, section.
    Deduplicates student entries within the same session and calculates totals accurately.
    """
    if not records:
        return []

    sessions = {}

    for r in records:
        ts = r.get('timestamp') or ''
        date_str = extract_date_str(ts)
        session_key = ts.split(".")[0] if ts else ""

        subj = r.get('subjects') or {}
        subject_name = subj.get('name') or "N/A"
        subject_code = subj.get('subject_code') or "N/A"
        section = subj.get('section') or "N/A"

        student_id = r.get('student_id')
        is_present = bool(r.get('is_present', False))

        group_key = (date_str, session_key, subject_name, subject_code, section)

        if group_key not in sessions:
            sessions[group_key] = {
                "date": date_str,
                "session_key": session_key,
                "subject_name": subject_name,
                "subject_code": subject_code,
                "section": section,
                "students": {}
            }

        if student_id is not None:
            sessions[group_key]["students"][student_id] = is_present

    summary_rows = []
    for key, data in sessions.items():
        students_map = data["students"]
        total_students = len(students_map)
        present_count = sum(1 for p in students_map.values() if p)
        absent_count = total_students - present_count
        attendance_pct = round((present_count / total_students) * 100, 1) if total_students > 0 else 0.0

        summary_rows.append({
            "Date": data["date"],
            "Class / Subject": data["subject_name"],
            "Subject Code": data["subject_code"],
            "Section": data["section"],
            "Total Students": total_students,
            "Present": present_count,
            "Absent": absent_count,
            "Attendance %": attendance_pct,
            "session_key": data["session_key"]
        })

    summary_rows.sort(key=lambda x: x["session_key"], reverse=True)
    return summary_rows


def create_excel_for_summary(summary_rows, sheet_title="Class Summary", detailed_records=None):
    """
    Generates a professionally formatted Excel (.xlsx) file with openpyxl.
    Features:
    - Bold column headers with brand purple fill
    - Freeze header row
    - Proper column widths with padding
    - Native Excel date formatting (yyyy-mm-dd)
    - Native Excel percentage formatting (0.0%)
    - Thin borders and clean row spacing
    - Optional detailed student attendance sheet for full exports
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_title
    ws.views.sheetView[0].showGridLines = True
    ws.freeze_panes = 'A2'

    headers = [
        "Date",
        "Class / Subject",
        "Subject Code",
        "Section",
        "Total Students",
        "Present",
        "Absent",
        "Attendance Percentage"
    ]
    ws.append(headers)

    header_fill = PatternFill(start_color="5865F2", end_color="5865F2", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    thin_side = Side(style="thin", color="CBD5E1")
    cell_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

    ws.row_dimensions[1].height = 28

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
        cell.border = cell_border

    zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

    present_font = Font(name="Calibri", size=11, color="15803D", bold=True)
    absent_font = Font(name="Calibri", size=11, color="B91C1C", bold=True)
    pct_font = Font(name="Calibri", size=11, color="15803D", bold=True)
    regular_font = Font(name="Calibri", size=11, color="1E293B")

    for row_idx, r in enumerate(summary_rows, start=2):
        ws.row_dimensions[row_idx].height = 22
        row_fill = zebra_fill if row_idx % 2 == 0 else white_fill

        date_val = r.get("Date", "")
        if isinstance(date_val, str) and len(date_val) >= 10:
            try:
                date_val = datetime.strptime(date_val[:10], "%Y-%m-%d").date()
            except Exception:
                pass

        total = int(r.get("Total Students", 0))
        present = int(r.get("Present", 0))
        absent = int(r.get("Absent", 0))
        pct = (present / total) if total > 0 else 0.0

        row_data = [
            date_val,
            r.get("Class / Subject", ""),
            r.get("Subject Code", ""),
            r.get("Section", ""),
            total,
            present,
            absent,
            pct
        ]
        ws.append(row_data)

        row_cells = ws[row_idx]
        row_cells[0].alignment = Alignment(horizontal="center", vertical="center")
        row_cells[0].font = regular_font
        row_cells[0].fill = row_fill
        row_cells[0].border = cell_border
        if isinstance(date_val, (datetime, date)):
            row_cells[0].number_format = 'yyyy-mm-dd'

        row_cells[1].alignment = Alignment(horizontal="left", vertical="center")
        row_cells[1].font = regular_font
        row_cells[1].fill = row_fill
        row_cells[1].border = cell_border

        row_cells[2].alignment = Alignment(horizontal="center", vertical="center")
        row_cells[2].font = regular_font
        row_cells[2].fill = row_fill
        row_cells[2].border = cell_border

        row_cells[3].alignment = Alignment(horizontal="center", vertical="center")
        row_cells[3].font = regular_font
        row_cells[3].fill = row_fill
        row_cells[3].border = cell_border

        row_cells[4].alignment = Alignment(horizontal="center", vertical="center")
        row_cells[4].font = regular_font
        row_cells[4].fill = row_fill
        row_cells[4].border = cell_border
        row_cells[4].number_format = '#,##0'

        row_cells[5].alignment = Alignment(horizontal="center", vertical="center")
        row_cells[5].font = present_font
        row_cells[5].fill = row_fill
        row_cells[5].border = cell_border
        row_cells[5].number_format = '#,##0'

        row_cells[6].alignment = Alignment(horizontal="center", vertical="center")
        row_cells[6].font = absent_font
        row_cells[6].fill = row_fill
        row_cells[6].border = cell_border
        row_cells[6].number_format = '#,##0'

        row_cells[7].alignment = Alignment(horizontal="center", vertical="center")
        row_cells[7].font = pct_font
        row_cells[7].fill = row_fill
        row_cells[7].border = cell_border
        row_cells[7].number_format = '0.0%'

    for col in ws.columns:
        max_len = 0
        for cell in col:
            val = str(cell.value or "")
            if len(val) > max_len:
                max_len = len(val)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 15)

    if detailed_records:
        ws2 = wb.create_sheet(title="Detailed Attendance")
        ws2.views.sheetView[0].showGridLines = True
        ws2.freeze_panes = 'A2'
        ws2.row_dimensions[1].height = 28

        det_headers = ["Date & Time", "Student Name", "Student ID", "Class / Subject", "Subject Code", "Section", "Status"]
        ws2.append(det_headers)
        for cell in ws2[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment
            cell.border = cell_border

        for row_idx, d in enumerate(detailed_records, start=2):
            ws2.row_dimensions[row_idx].height = 20
            row_fill = zebra_fill if row_idx % 2 == 0 else white_fill
            is_pres = d.get('is_present', False)

            ws2.append([
                d.get('Date & Time', ''),
                d.get('Student Name', ''),
                d.get('Student ID', ''),
                d.get('Class / Subject', ''),
                d.get('Subject Code', ''),
                d.get('Section', ''),
                'Present' if is_pres else 'Absent'
            ])
            cells = ws2[row_idx]
            for c_idx, cell in enumerate(cells):
                cell.fill = row_fill
                cell.border = cell_border
                cell.alignment = Alignment(horizontal="left" if c_idx in (0, 1, 3) else ("right" if c_idx == 2 else "center"), vertical="center")
                if c_idx == 6:
                    cell.font = present_font if is_pres else absent_font
                else:
                    cell.font = regular_font

        for col in ws2.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws2.column_dimensions[col_letter].width = max(max_len + 4, 15)

        wb.active = wb.index(ws2)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def render_summary_table_html(summary_rows):
    """
    Renders the Class Summary Table matching the SNAPCLASS UI reference design:
    - Rounded card with soft shadow and clean borders
    - Dark navy typography
    - Green pill badge for Present count
    - Red/pink pill badge for Absent count
    - Green percentage badge for Attendance %
    - Responsive horizontal scroll wrapper
    """
    rows_html = []
    for r in summary_rows:
        total = r["Total Students"]
        present = r["Present"]
        absent = r["Absent"]
        pct = r["Attendance %"]

        row_str = f"""
        <tr style="border-bottom: 1px solid #EEF2F6; transition: background-color 0.2s ease;">
            <td style="padding: 16px 20px; font-weight: 500; color: #1E293B; white-space: nowrap;">{r['Date']}</td>
            <td style="padding: 16px 20px; font-weight: 600; color: #0F172A;">{r['Class / Subject']}</td>
            <td style="padding: 16px 20px; color: #475569; font-weight: 500;">{r['Subject Code']}</td>
            <td style="padding: 16px 20px; color: #475569; font-weight: 500;">{r['Section']}</td>
            <td style="padding: 16px 20px; font-weight: 600; color: #1E293B; text-align: center;">{total}</td>
            <td style="padding: 16px 20px; text-align: center;">
                <span style="background-color: #DCFCE7; color: #15803D; font-weight: 700; font-size: 0.88rem; padding: 5px 14px; border-radius: 9999px; display: inline-flex; align-items: center; justify-content: center; border: 1px solid #BBF7D0; min-width: 36px;">
                    {present}
                </span>
            </td>
            <td style="padding: 16px 20px; text-align: center;">
                <span style="background-color: #FEE2E2; color: #B91C1C; font-weight: 700; font-size: 0.88rem; padding: 5px 14px; border-radius: 9999px; display: inline-flex; align-items: center; justify-content: center; border: 1px solid #FECACA; min-width: 36px;">
                    {absent}
                </span>
            </td>
            <td style="padding: 16px 20px; text-align: center;">
                <span style="background-color: #DCFCE7; color: #15803D; font-weight: 700; font-size: 0.88rem; padding: 5px 14px; border-radius: 9999px; display: inline-flex; align-items: center; justify-content: center; border: 1px solid #86EFAC; min-width: 60px;">
                    {pct:.1f}%
                </span>
            </td>
        </tr>
        """
        rows_html.append(row_str)

    table_html = f"""
    <div style="background: #FFFFFF; border-radius: 20px; box-shadow: 0 4px 20px rgba(88, 101, 242, 0.08); border: 1px solid #E2E8F0; overflow: hidden; margin-top: 1.2rem; margin-bottom: 2rem;">
        <div style="overflow-x: auto; width: 100%; -webkit-overflow-scrolling: touch;">
            <table style="width: 100%; border-collapse: collapse; text-align: left; font-family: 'Outfit', sans-serif; font-size: 0.95rem;">
                <thead>
                    <tr style="background-color: #F8FAFC; border-bottom: 2px solid #E2E8F0;">
                        <th style="padding: 16px 20px; font-size: 0.82rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.6px; white-space: nowrap;">Date</th>
                        <th style="padding: 16px 20px; font-size: 0.82rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.6px; white-space: nowrap;">Class / Subject</th>
                        <th style="padding: 16px 20px; font-size: 0.82rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.6px; white-space: nowrap;">Subject Code</th>
                        <th style="padding: 16px 20px; font-size: 0.82rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.6px; white-space: nowrap;">Section</th>
                        <th style="padding: 16px 20px; font-size: 0.82rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.6px; text-align: center; white-space: nowrap;">Total Students</th>
                        <th style="padding: 16px 20px; font-size: 0.82rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.6px; text-align: center; white-space: nowrap;">Present</th>
                        <th style="padding: 16px 20px; font-size: 0.82rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.6px; text-align: center; white-space: nowrap;">Absent</th>
                        <th style="padding: 16px 20px; font-size: 0.82rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.6px; text-align: center; white-space: nowrap;">Attendance %</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(rows_html)}
                </tbody>
            </table>
        </div>
    </div>
    """
    return table_html


def teacher_tab_attendance_records():
    teacher_id = st.session_state.teacher_data['teacher_id']

    all_records = get_attendance_for_teacher(teacher_id) or []

    st.header('Attendance Records')
    date_col, download_col = st.columns([1, 1], vertical_alignment='bottom')
    with date_col:
        selected_date = st.date_input(
            "Select Attendance Date",
            value=datetime.now().date(),
            key="attendance_filter_date"
        )

    selected_date_str = selected_date.strftime("%Y-%m-%d")
    selected_records = [
        r for r in all_records
        if extract_date_str(r.get('timestamp')) == selected_date_str
    ]
    selected_summary_rows = process_attendance_summary(selected_records)

    selected_detailed_data = []
    for r in selected_records:
        ts = r.get('timestamp')
        formatted_time = datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N/A"
        student_obj = r.get('students') or {}
        student_name = student_obj.get('name', '').strip() if student_obj.get('name') else f"Student #{r.get('student_id', '')}"
        subject_obj = r.get('subjects') or {}

        selected_detailed_data.append({
            "Date & Time": formatted_time,
            "Student Name": student_name,
            "Student ID": r.get('student_id'),
            "Class / Subject": subject_obj.get('name', ''),
            "Subject Code": subject_obj.get('subject_code', ''),
            "Section": subject_obj.get('section', ''),
            "is_present": bool(r.get('is_present', False))
        })

    if selected_summary_rows:
        with st.spinner("Preparing attendance report..."):
            selected_excel_bytes = create_excel_for_summary(
                selected_summary_rows,
                sheet_title="Class Summary",
                detailed_records=selected_detailed_data
            )
    else:
        selected_excel_bytes = None

    with download_col:
        if selected_excel_bytes:
            st.download_button(
                label="Download Attendance (.xlsx)",
                data=selected_excel_bytes,
                file_name=f"Attendance_{selected_date_str}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                icon=":material/download:",
                width="stretch",
                key="btn_download_selected_date"
            )
        else:
            st.button(
                "Download Attendance (.xlsx)",
                disabled=True,
                type="primary",
                icon=":material/download:",
                width="stretch",
                key="btn_download_selected_date_disabled"
            )

    if selected_summary_rows:
        st.html(render_summary_table_html(selected_summary_rows))
    else:
        st.info(f"No attendance records found for {selected_date_str}.", icon=":material/info:")


def login_teacher(username, password):
    if not username or not password:
        return False
    
    teacher = teacher_login(username, password)

    if teacher:
        st.session_state.user_role ='teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    

    return False
def teacher_screen_login():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Login using password', text_alignment='center')
    st.space()
    st.space()


    teacher_username = st.text_input("Enter username", placeholder='ananyaroy')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Login', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            with st.spinner("Signing in..."):
                signed_in = login_teacher(teacher_username, teacher_pass)
            if signed_in:
                st.toast("welcome back!", icon="👋")
                st.rerun()
            else:
                st.error("Invalid username and password combo")

    with btnc2:
        if st.button('Register Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'register'

    footer_dashboard()



def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All Fields are required!"
    if check_teacher_exists(teacher_username):
        return False, "Username already taken"
    if teacher_pass != teacher_pass_confirm:
        return False, "Password doesn't match"
    
    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Sucessfully Created! Login Now"
    except Exception as e:
        return False, "Unexpected Error!"
    

def teacher_screen_register():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()



    st.header('Register your teacher profile')

    st.space()
    st.space()

    
    teacher_username = st.text_input("Enter username", placeholder='ananyaroy')

    teacher_name = st.text_input("Enter name", placeholder='Ananya Roy')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    teacher_pass_confirm = st.text_input("Confirm your password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Register now', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            with st.spinner("Creating account..."):
                success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
            if success:
                st.success(message)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)


    with btnc2:
        if st.button('Login Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'login'

    footer_dashboard()