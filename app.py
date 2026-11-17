
import streamlit as st

from src.screens.home_screen import home_screen

from src.components.dialog_auto_enroll import auto_enroll_dialog

def main():
    st.set_page_config(
        page_title='SnapClass - Making Attendance faster using AI',
        page_icon= "src/assets/logo.png"
    )
    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None

    join_code = st.query_params.get('join-code')
    if join_code:
        st.session_state['login_type'] = 'student'

    match st.session_state['login_type']:
        case 'teacher':
            from src.screens.teacher_screen import teacher_screen

            teacher_screen()

        case 'student':
            from src.screens.student_screen import student_screen

            student_screen()
        
        case None:
            home_screen()


    if join_code:
        if st.session_state.get('is_logged_in') and st.session_state.get('user_role') == 'student':
            auto_enroll_dialog(join_code)
main()