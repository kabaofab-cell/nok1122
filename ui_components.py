import streamlit as st


APP_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap');
:root {
    --bg: #f6f7fb;
    --panel: rgba(255, 255, 255, 0.82);
    --panel-strong: #ffffff;
    --text: #0f172a;
    --muted: #64748b;
    --border: rgba(148, 163, 184, 0.22);
    --primary: #6d7cff;
    --primary-2: #9b7bff;
    --success: #10b981;
    --danger: #ef4444;
    --shadow: 0 18px 60px rgba(15, 23, 42, 0.08);
    --radius: 22px;
}
html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, input, button {
    font-family: 'Kanit', sans-serif !important;
}
.stApp {
    background:
        radial-gradient(circle at top left, rgba(109, 124, 255, 0.14), transparent 28%),
        radial-gradient(circle at top right, rgba(155, 123, 255, 0.12), transparent 26%),
        linear-gradient(180deg, #f8faff 0%, var(--bg) 100%);
    color: var(--text);
}
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(245,247,255,0.98));
    border-right: 1px solid var(--border);
    box-shadow: 6px 0 28px rgba(15, 23, 42, 0.05);
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: var(--text) !important;
    font-weight: 600 !important;
    font-size: 15px !important;
}
[data-testid="stSidebar"] .stRadio > div { gap: 0.35rem; }
@media (prefers-color-scheme: dark) {
    .stApp { background: linear-gradient(180deg, #0f172a 0%, #111827 100%); color: #e2e8f0; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0b1220, #111827); }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: #e2e8f0 !important; }
    .metric-card, .rank-card, .soft-panel { background: rgba(15, 23, 42, 0.88) !important; border-color: rgba(148, 163, 184, 0.18) !important; }
}
h1, h2, h3 { letter-spacing: -0.02em; }
p, li { color: var(--muted); }
div[role="radiogroup"] > label {
    padding: 12px 16px;
    background: rgba(255,255,255,0.72);
    border: 1px solid transparent;
    border-radius: 16px;
    transition: 0.25s ease;
    cursor: pointer;
    margin-bottom: 8px;
    box-shadow: 0 6px 22px rgba(15, 23, 42, 0.04);
}
div[role="radiogroup"] > label:hover {
    background: rgba(109, 124, 255, 0.08);
    border-color: rgba(109, 124, 255, 0.24);
    transform: translateX(4px);
}
.stButton > button, .stDownloadButton > button {
    border-radius: 16px !important;
    border: 1px solid rgba(109, 124, 255, 0.18) !important;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-2) 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 10px 25px rgba(109, 124, 255, 0.25);
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 18px 30px rgba(109, 124, 255, 0.28);
    color: white !important;
}
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div, .stMultiSelect div[data-baseweb="select"] > div, .stDateInput input {
    border-radius: 14px !important;
    border-color: rgba(148, 163, 184, 0.2) !important;
    background: rgba(255,255,255,0.88) !important;
}
.soft-panel, .metric-card, .rank-card {
    background: var(--panel);
    backdrop-filter: blur(18px);
    border-radius: var(--radius);
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
}
.metric-card {
    padding: 22px 18px;
    text-align: center;
    margin-bottom: 18px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover, .rank-card:hover { transform: translateY(-2px); box-shadow: 0 22px 50px rgba(15, 23, 42, 0.10); }
.metric-card h2 { color: var(--primary); font-size: 2.15rem; font-weight: 700; margin-top: 8px; margin-bottom: 0; }
.metric-card h3 { color: var(--text); font-size: 0.98rem; margin-bottom: 0.25rem; }
.rank-card { padding: 12px; text-align: center; margin-bottom: 18px; }
.rank-img {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
    border-radius: 14px;
    box-shadow: 0 14px 24px rgba(15, 23, 42, 0.14);
    margin-bottom: 10px;
    border: 1px solid rgba(148, 163, 184, 0.12);
}
.btn-delete>div>button { background: linear-gradient(135deg, var(--danger) 0%, #fb7185 100%) !important; color: white !important; }
.btn-secondary>div>button { background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%) !important; color: #0f172a !important; }
.hero {
    background: linear-gradient(135deg, rgba(109,124,255,0.16), rgba(155,123,255,0.10));
    border: 1px solid rgba(109,124,255,0.16);
    border-radius: 28px;
    padding: 24px 26px;
    box-shadow: var(--shadow);
    margin-bottom: 18px;
}
.hero-kicker {
    color: var(--primary);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.78rem;
}
.hero-title { margin: 0.25rem 0 0.45rem 0; font-size: 2rem; font-weight: 800; color: var(--text); }
.hero-subtitle { margin: 0; color: var(--muted); font-size: 1rem; line-height: 1.6; max-width: 58rem; }
.section-title { margin: 1.2rem 0 0.75rem; font-size: 1.1rem; font-weight: 700; color: var(--text); }
.section-note { color: var(--muted); margin-top: -0.35rem; margin-bottom: 0.9rem; }
.compact-pill {
    display: inline-block;
    padding: 0.35rem 0.7rem;
    border-radius: 999px;
    background: rgba(109,124,255,0.10);
    color: var(--primary);
    font-size: 0.82rem;
    font-weight: 700;
    margin-right: 0.5rem;
    margin-bottom: 0.4rem;
}
.fc-daygrid-day-frame { min-height: 110px !important; height: 100% !important; }
.fc-event { border-radius: 8px !important; border: none !important; padding: 3px 8px !important; font-weight: 500 !important; font-size: 0.84em !important; margin: 2px 0 !important; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.fc-daygrid-day-number { font-size: 0.9em !important; color: #64748b !important; padding: 8px !important; text-decoration: none !important; font-weight: 600 !important; }
.fc-daygrid-more-link { color: #6d7cff !important; font-weight: 700 !important; font-size: 0.82em !important; padding-left: 5px !important; }
</style>
"""


def render_app_style():
    st.markdown(APP_STYLE, unsafe_allow_html=True)


def render_sidebar_brand():
    st.sidebar.markdown(
        """
        <div style="padding: 1rem 0.9rem 0.35rem 0.9rem;">
          <div class="hero-kicker">Admin Suite</div>
          <div style="font-size:1.35rem; font-weight:800; color:#0f172a; line-height:1.1; margin-top:0.25rem;">Nok-kaew Admin</div>
          <div style="color:#64748b; font-size:0.92rem; margin-top:0.45rem;">จัดการนิยาย คิวงาน และรายรับในที่เดียว</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero(kicker: str, title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-kicker">{kicker}</div>
            <div class="hero-title">{title}</div>
            <p class="hero-subtitle">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
