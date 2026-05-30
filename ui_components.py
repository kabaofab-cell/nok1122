import streamlit as st


APP_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap');
:root {
    --bg: #eef7f4;
    --surface: #fffefa;
    --panel: #ffffff;
    --panel-soft: #f4fbf8;
    --text: #173331;
    --muted: #60706c;
    --line: #cfe1dc;
    --primary: #006d77;
    --primary-strong: #084c52;
    --accent: #e95f46;
    --accent-soft: #fff1eb;
    --success: #1f9d72;
    --danger: #d94835;
    --shadow: 0 10px 30px rgba(16, 75, 73, 0.10);
    --radius: 8px;
}
html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, input, button {
    font-family: 'Kanit', sans-serif !important;
}
.stApp {
    background:
        linear-gradient(90deg, rgba(0,109,119,0.055) 1px, transparent 1px),
        linear-gradient(0deg, rgba(0,109,119,0.045) 1px, transparent 1px),
        radial-gradient(circle at 18% 12%, rgba(233,95,70,0.16), transparent 28%),
        linear-gradient(180deg, #f8fffc 0%, var(--bg) 100%);
    background-size: 28px 28px, 28px 28px, auto, auto;
    color: var(--text);
}
.block-container {
    max-width: 1280px;
    padding-top: 1rem;
    padding-bottom: 2rem;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #073b3f 0%, #0d565c 100%);
    border-right: 1px solid rgba(255,255,255,0.14);
    box-shadow: 8px 0 30px rgba(8, 76, 82, 0.18);
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: rgba(255,255,255,0.88) !important;
    font-weight: 600 !important;
    font-size: 15px !important;
}
[data-testid="stSidebar"] .stRadio > div { gap: 0.35rem; }
h1, h2, h3 { letter-spacing: 0; }
p, li { color: var(--muted); }
div[role="radiogroup"] > label {
    padding: 11px 14px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: var(--radius);
    transition: 0.18s ease;
    cursor: pointer;
    margin-bottom: 7px;
    box-shadow: none;
}
div[role="radiogroup"] > label:hover {
    background: rgba(255,255,255,0.16);
    border-color: rgba(255,255,255,0.28);
}
.stButton > button, .stDownloadButton > button {
    border-radius: var(--radius) !important;
    border: 1px solid rgba(0,109,119,0.18) !important;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-strong) 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 8px 18px rgba(0, 109, 119, 0.18);
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 12px 24px rgba(0, 109, 119, 0.22);
    color: white !important;
}
.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div,
.stDateInput input {
    border-radius: var(--radius) !important;
    border-color: var(--line) !important;
    background: var(--surface) !important;
}
.soft-panel, .metric-card, .rank-card {
    background: var(--panel);
    border-radius: var(--radius);
    border: 1px solid var(--line);
    box-shadow: var(--shadow);
}
.metric-card {
    padding: 18px 16px;
    text-align: left;
    margin-bottom: 16px;
    border-left: 5px solid var(--primary);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.metric-card:hover, .rank-card:hover {
    transform: translateY(-1px);
    box-shadow: 0 15px 34px rgba(16, 75, 73, 0.14);
}
.metric-card h2 {
    color: var(--primary-strong);
    font-size: 2rem;
    font-weight: 700;
    margin-top: 6px;
    margin-bottom: 0;
}
.metric-card h3 {
    color: var(--muted);
    font-size: 0.92rem;
    margin-bottom: 0.25rem;
}
.rank-card {
    padding: 10px;
    text-align: center;
    margin-bottom: 14px;
}
.rank-img {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
    border-radius: var(--radius);
    box-shadow: none;
    margin-bottom: 8px;
    border: 1px solid var(--line);
}
.btn-delete>div>button {
    background: linear-gradient(135deg, var(--danger) 0%, #b92d20 100%) !important;
    color: white !important;
}
.btn-secondary>div>button {
    background: linear-gradient(135deg, #d9eee8 0%, #c8e4dd 100%) !important;
    color: var(--text) !important;
}
.hero {
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #073b3f 0%, #0f6c73 62%, #e95f46 100%);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 10px;
    padding: 24px 26px;
    box-shadow: 0 15px 35px rgba(8, 76, 82, 0.18);
    margin-bottom: 18px;
}
.hero:after {
    content: "";
    position: absolute;
    inset: auto -8% -65% 52%;
    height: 170px;
    background: rgba(255,255,255,0.13);
    transform: rotate(-8deg);
}
.hero-kicker {
    color: #b9fff4;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.78rem;
}
.hero-title {
    position: relative;
    margin: 0.25rem 0 0.45rem 0;
    font-size: 2rem;
    font-weight: 800;
    color: #ffffff;
}
.hero-subtitle {
    position: relative;
    margin: 0;
    color: rgba(255,255,255,0.84);
    font-size: 1rem;
    line-height: 1.6;
    max-width: 58rem;
}
.section-title {
    margin: 1.2rem 0 0.75rem;
    font-size: 1.06rem;
    font-weight: 700;
    color: var(--text);
}
.section-note {
    color: var(--muted);
    margin-top: -0.35rem;
    margin-bottom: 0.9rem;
}
.compact-pill {
    display: inline-block;
    padding: 0.35rem 0.7rem;
    border-radius: 999px;
    background: rgba(0,109,119,0.10);
    color: var(--primary);
    font-size: 0.82rem;
    font-weight: 700;
    margin-right: 0.5rem;
    margin-bottom: 0.4rem;
}
.fc-daygrid-day-frame { min-height: 110px !important; height: 100% !important; }
.fc-event {
    border-radius: 6px !important;
    border: none !important;
    padding: 3px 8px !important;
    font-weight: 500 !important;
    font-size: 0.84em !important;
    margin: 2px 0 !important;
    box-shadow: none;
}
.fc-daygrid-day-number {
    font-size: 0.9em !important;
    color: var(--muted) !important;
    padding: 8px !important;
    text-decoration: none !important;
    font-weight: 600 !important;
}
.fc-daygrid-more-link {
    color: var(--primary) !important;
    font-weight: 700 !important;
    font-size: 0.82em !important;
    padding-left: 5px !important;
}
div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {
    border: 1px solid var(--line);
    border-radius: var(--radius);
    overflow: hidden;
}
div[data-testid="stTabs"] button {
    border-radius: var(--radius) var(--radius) 0 0 !important;
}
@media (max-width: 760px) {
    .block-container { padding-left: 1rem; padding-right: 1rem; }
    .hero { padding: 20px 18px; }
    .hero-title { font-size: 1.55rem; }
    .metric-card { padding: 15px 14px; }
}
</style>
"""


def render_app_style():
    st.markdown(APP_STYLE, unsafe_allow_html=True)


def render_sidebar_brand():
    st.sidebar.markdown(
        """
        <div style="padding: 1rem 0.85rem 0.8rem 0.85rem; border-bottom:1px solid rgba(255,255,255,0.14); margin-bottom:0.55rem;">
          <div style="color:#b9fff4; font-weight:800; text-transform:uppercase; letter-spacing:0.08em; font-size:0.75rem;">Story Ops</div>
          <div style="font-size:1.4rem; font-weight:800; color:#ffffff; line-height:1.12; margin-top:0.25rem;">Nok-kaew Admin</div>
          <div style="color:rgba(255,255,255,0.72); font-size:0.9rem; margin-top:0.45rem; line-height:1.5;">จัดการนิยาย คิวงาน และรายรับในที่เดียว</div>
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
