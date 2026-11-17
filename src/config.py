from urllib.parse import urlencode


APP_BASE_URL = "https://snap-class-07.streamlit.app/"


def build_class_join_url(subject_code: str) -> str:
    return f"{APP_BASE_URL}?{urlencode({'join-code': subject_code})}"
