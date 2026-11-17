import streamlit as st



def style_background_home():

    st.markdown("""
        <style>

                .stApp {
                    background: #5865F2 !important;
                }

                .stApp div[data-testid="stColumn"]{
                    background-color:#E0E3FF !important;
                    padding:2.5rem !important;
                    border-radius: 2.5rem !important;
                    text-align: center;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
                }
        </style>  

                """
            ,unsafe_allow_html=True)
    

def style_background_dashboard():

    st.markdown("""
        <style>

                .stApp {
                    background: #E0E3FF !important;
                }

        </style>  

                """
            ,unsafe_allow_html=True)
    

    

def style_base_layout():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1979&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap');

        /* Hide Top Bar of streamlit */
        #MainMenu, footer, header {
            visibility: hidden;
        }
            
        .block-container {
            padding-top:1.5rem !important;    
        }

        /* Headings */
        h1 {
            font-family: 'Climate Crisis', sans-serif !important;
            font-size: 3.5rem !important;
            line-height: 1.1 !important;
            margin-bottom: 0rem !important;
            color: #1E293B !important;
        }

        h2 {
            font-family: 'Climate Crisis', sans-serif !important;
            font-size: 2rem !important;
            line-height: 1.1 !important;
            margin-bottom: 0rem !important;
            color: #1E293B !important;
        }
            
        h3 {
            font-family: 'Outfit', sans-serif !important;
            color: #1E293B !important;
            font-weight: 700 !important;
        }

        h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            color: #1E293B !important;
        }
            
        p, span {
            font-family: 'Outfit', sans-serif;
            color: #1E293B;
        }

        /* Streamlit markdown containers */
        div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stMarkdownContainer"] span {
            color: #1E293B;
        }

        /* Widget Labels (inputs, selectboxes, camera, file uploaders) */
        label,
        div[data-testid="stWidgetLabel"] label,
        div[data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] * {
            color: #1E293B !important;
            font-weight: 600 !important;
            font-family: 'Outfit', sans-serif !important;
            font-size: 1rem !important;
        }

        /* Input fields and selectboxes */
        div[data-baseweb="input"],
        div[data-baseweb="select"] > div,
        div[data-baseweb="base-input"] {
            background-color: #FFFFFF !important;
            border-radius: 12px !important;
            border: 1px solid #CBD5E1 !important;
            color: #1E293B !important;
        }

        div[data-baseweb="input"] input,
        div[data-baseweb="select"] input,
        div[data-baseweb="select"] div,
        div[data-baseweb="base-input"] input {
            color: #1E293B !important;
            background-color: transparent !important;
        }

        div[data-baseweb="select"] svg {
            fill: #1E293B !important;
        }

        ul[data-baseweb="menu"] {
            background-color: #FFFFFF !important;
        }

        ul[data-baseweb="menu"] li,
        ul[data-baseweb="menu"] li div {
            color: #1E293B !important;
        }

        /* Camera input label and helper text */
        [data-testid="stCameraInput"] p,
        [data-testid="stCameraInput"] span {
            color: #1E293B;
        }

        /* Buttons */
        button {
            border-radius: 1.5rem !important;
            background-color: #5865F2 !important;
            color: white !important;
            padding: 10px 20px !important;
            border: none !important;
            transition: transform 180ms ease, box-shadow 180ms ease, background-color 220ms ease, color 220ms ease, border-color 220ms ease, filter 180ms ease !important;
            will-change: transform;
        }

        button p,
        button span,
        button div {
            color: white !important;
        }

        button[kind="primary"] {
            background-color: #5865F2 !important;
            color: white !important;
        }

        button[kind="secondary"] {
            border-radius: 1.5rem !important;
            background-color: #EB459E !important;
            color: white !important;
            padding: 10px 20px !important;
            border: none !important;
        }

        button[kind="secondary"] p,
        button[kind="secondary"] span,
        button[kind="secondary"] div {
            color: white !important;
        }

        button[kind="tertiary"] {
            border-radius: 1.5rem !important;
            background-color: #111827 !important;
            color: white !important;
            padding: 10px 20px !important;
            border: none !important;
        }

        button[kind="tertiary"] p,
        button[kind="tertiary"] span,
        button[kind="tertiary"] div {
            color: white !important;
        }

        button:not(:disabled):hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(30, 41, 59, 0.18);
            filter: brightness(1.04);
        }

        button:not(:disabled):active {
            transform: translateY(0) scale(0.98);
            box-shadow: 0 2px 6px rgba(30, 41, 59, 0.16);
        }

        button:focus-visible {
            outline: 3px solid rgba(88, 101, 242, 0.55) !important;
            outline-offset: 3px;
        }

        button:disabled {
            cursor: not-allowed;
            opacity: 0.58;
            will-change: auto;
        }

        @keyframes snapclass-content-enter {
            from {
                opacity: 0;
                transform: translateY(12px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes snapclass-dialog-fade {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }

        @keyframes snapclass-dialog-content-enter {
            from {
                transform: translateY(8px) scale(0.985);
            }
            to {
                transform: translateY(0) scale(1);
            }
        }

        div[class*="st-key-teacher-tab-content-"] {
            animation: snapclass-content-enter 380ms cubic-bezier(0.2, 0.75, 0.25, 1) both;
        }

        .snapclass-card {
            border-radius: 20px;
            animation: snapclass-content-enter 420ms cubic-bezier(0.2, 0.75, 0.25, 1) both;
            animation-delay: var(--snapclass-card-delay, 0ms);
            transition: transform 220ms ease, box-shadow 220ms ease, border-color 220ms ease;
        }

        .snapclass-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 14px 28px rgba(30, 41, 59, 0.12);
            border-color: rgba(88, 101, 242, 0.45) !important;
        }

        div[role="dialog"] {
            animation: snapclass-dialog-fade 240ms ease-out both;
        }

        div[role="dialog"] > div {
            animation: snapclass-dialog-content-enter 240ms cubic-bezier(0.2, 0.75, 0.25, 1) both;
            transform-origin: center;
        }

        div[data-testid="stSpinner"] {
            animation: snapclass-content-enter 180ms ease-out both;
        }

        @media (prefers-reduced-motion: reduce) {
            *,
            *::before,
            *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                scroll-behavior: auto !important;
                transition-duration: 0.01ms !important;
            }

            button,
            .snapclass-card {
                transition-duration: 0.01ms !important;
            }

            .snapclass-card {
                animation-delay: 0ms !important;
            }

            div[class*="st-key-teacher-tab-content-"],
            div[role="dialog"],
            div[role="dialog"] > div,
            div[data-testid="stSpinner"] {
                animation-duration: 0.01ms !important;
            }
        }
        </style>  
        """,
      unsafe_allow_html=True)