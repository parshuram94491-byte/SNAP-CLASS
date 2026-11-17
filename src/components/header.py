import streamlit as st
import os
import base64

def _get_logo_data_uri():
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
    return ""


def header_home():
    logo_uri = _get_logo_data_uri()
    st.markdown(f"""
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:25px; margin-top:10px">
            <div style="background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(12px); padding: 12px; border-radius: 28px; box-shadow: 0 10px 25px rgba(0,0,0,0.18); margin-bottom: 12px; display: inline-flex; align-items: center; justify-content: center;">
                <img src='{logo_uri}' style='height:90px; width:90px; object-fit:contain;' />
            </div>
            <h1 style='text-align:center; color:#FFFFFF !important; font-family:"Outfit", sans-serif !important; font-weight:900; font-size: 3.2rem; letter-spacing: 2px; margin: 0; line-height: 1.1;'>SNAPCLASS</h1>
            <p style='text-align:center; color:#E0E3FF !important; font-family:"Outfit", sans-serif !important; font-size:1.1rem; font-weight:500; margin-top:6px; margin-bottom:0;'>AI-Powered Attendance System</p>
        </div>   
    """, unsafe_allow_html=True)


def header_dashboard():
    logo_uri = _get_logo_data_uri()
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:16px;">
            <div style="background: white; padding: 6px; border-radius: 18px; box-shadow: 0 4px 15px rgba(88, 101, 242, 0.15); display: inline-flex; align-items: center; justify-content: center;">
                <img src='{logo_uri}' style='height:60px; width:60px; object-fit:contain;' />
            </div>
            <div style="display:flex; flex-direction:column;">
                <h2 style='text-align:left; color:#5865F2 !important; font-family:"Outfit", sans-serif !important; font-weight:900; font-size: 2rem; margin:0; line-height:1.1;'>SNAPCLASS</h2>
                <span style='color:#64748B; font-family:"Outfit", sans-serif; font-size:0.85rem; font-weight:600; letter-spacing:0.5px;'>AI ATTENDANCE SYSTEM</span>
            </div>
        </div>   
    """, unsafe_allow_html=True)
