"""
styles.py — Premium "Stadium Night" cricket theme for the Streamlit app.
Emerald pitch green + floodlight gold + sky blue accents.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"]  {
    font-family: 'Poppins', sans-serif;
}

:root {
    --pitch-green: #0a7a4a;
    --pitch-green-dark: #04381f;
    --gold: #FFC53D;
    --gold-deep: #FF8A00;
    --sky: #38bdf8;
    --ink: #eef6f0;
}

.stApp {
    background:
        radial-gradient(circle at 15% 0%, rgba(10,122,74,0.35) 0%, transparent 45%),
        radial-gradient(circle at 90% 10%, rgba(56,189,248,0.12) 0%, transparent 40%),
        linear-gradient(180deg, #04150e 0%, #03100c 45%, #020a08 100%);
    color: var(--ink);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #06261a 0%, #031810 100%);
    border-right: 1px solid rgba(255,255,255,0.07);
}

section[data-testid="stSidebar"] * {
    color: var(--ink) !important;
}

/* ---------- Academy photo banner ---------- */
.academy-banner {
    position: relative;
    width: 100%;
    border-radius: 22px;
    overflow: hidden;
    margin-bottom: 18px;
    border: 1px solid rgba(255,197,61,0.25);
    box-shadow: 0 10px 40px rgba(0,0,0,0.45);
}

.academy-banner img {
    width: 100%;
    max-height: 260px;
    object-fit: cover;
    display: block;
    filter: brightness(0.72) saturate(1.15);
}

.academy-banner-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, rgba(3,16,10,0.15) 0%, rgba(3,16,10,0.85) 100%);
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    padding: 22px 26px;
}

.academy-banner-overlay h1 {
    margin: 0;
    font-size: 30px;
    font-weight: 900;
    color: #fff;
    text-shadow: 0 2px 12px rgba(0,0,0,0.6);
}

.academy-banner-overlay p {
    margin: 4px 0 0 0;
    color: #ffe9b0;
    font-size: 14px;
    font-weight: 500;
}

.academy-banner-fallback {
    width: 100%;
    padding: 34px 26px;
    border-radius: 22px;
    margin-bottom: 18px;
    background:
        repeating-linear-gradient(90deg, rgba(255,255,255,0.035) 0px, rgba(255,255,255,0.035) 2px, transparent 2px, transparent 40px),
        linear-gradient(135deg, var(--pitch-green) 0%, var(--pitch-green-dark) 65%, #021a10 100%);
    border: 1px solid rgba(255,197,61,0.25);
    box-shadow: 0 10px 40px rgba(0,0,0,0.4);
    text-align: center;
}

.academy-banner-fallback h1 {
    margin: 0;
    font-size: 30px;
    font-weight: 900;
    background: linear-gradient(90deg, #FFC53D, #FF8A00 55%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.academy-banner-fallback p {
    margin: 6px 0 0 0;
    color: #cdeede;
    font-size: 14px;
}

/* Glass card */
.glass-card {
    background: rgba(255, 255, 255, 0.045);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 18px;
    padding: 20px 22px;
    margin-bottom: 16px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
}

.metric-card {
    background: linear-gradient(135deg, rgba(255,197,61,0.16), rgba(10,122,74,0.18));
    border: 1px solid rgba(255,197,61,0.28);
    border-radius: 16px;
    padding: 16px 18px;
    text-align: center;
}

.metric-card h2 {
    margin: 0;
    font-size: 26px;
    background: linear-gradient(90deg, #FFC53D, #FF8A00);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.metric-card p {
    margin: 4px 0 0 0;
    color: #b9d6c6;
    font-size: 13px;
    letter-spacing: 0.4px;
    text-transform: uppercase;
}

.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    background: linear-gradient(90deg, #38bdf8 0%, #22d3ee 100%);
    color: #04121b;
}

.badge-orange {
    background: linear-gradient(90deg, #FFC53D, #FF8A00);
    color: #2b1500;
}

.badge-green {
    background: linear-gradient(90deg, #43e97b 0%, #16a34a 100%);
    color: #04231a;
}

.badge-red {
    background: linear-gradient(90deg, #ff5858 0%, #f857a6 100%);
    color: #2b0000;
}

h1, h2, h3 {
    font-weight: 700 !important;
}

.hero-title {
    font-size: 34px;
    font-weight: 800;
    background: linear-gradient(90deg, #FFC53D, #FF8A00 40%, #38bdf8 80%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0px;
}

.hero-sub {
    color: #b9d6c6;
    font-size: 15px;
    margin-top: 2px;
}

div.stButton > button {
    background: linear-gradient(90deg, #FFC53D, #FF8A00);
    color: #241200;
    border: none;
    border-radius: 12px;
    font-weight: 700;
    padding: 0.55em 1.4em;
    transition: transform 0.15s ease;
}

div.stButton > button:hover {
    transform: translateY(-2px) scale(1.02);
    color: #241200;
}

[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.05);
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.08);
}

hr {
    border-color: rgba(255,255,255,0.08);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.04);
    border-radius: 10px 10px 0 0;
    padding: 8px 16px;
}

.coach-card {
    display: flex;
    align-items: center;
    gap: 14px;
    background: rgba(255,255,255,0.05);
    border-radius: 16px;
    padding: 14px 18px;
    border: 1px solid rgba(255,255,255,0.10);
}

.coach-avatar {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: linear-gradient(135deg, #38bdf8, #22d3ee);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    font-weight: 800;
    color: #04121b;
}

/* ---------- Announcement board ---------- */
.announcement-item {
    background: linear-gradient(135deg, rgba(255,197,61,0.10), rgba(56,189,248,0.06));
    border-left: 4px solid var(--gold);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 10px;
}

.announcement-item .a-date {
    color: #ffe9b0;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.announcement-item .a-title {
    font-weight: 700;
    font-size: 15px;
    margin: 2px 0 4px 0;
    color: #fff;
}

/* ---------- Leaderboard ---------- */
.leaderboard-row {
    display: flex;
    align-items: center;
    gap: 14px;
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 12px 16px;
    margin-bottom: 8px;
}

.leaderboard-rank {
    font-size: 20px;
    font-weight: 900;
    width: 34px;
    text-align: center;
    color: #FFC53D;
}

.leaderboard-rank.rank-1 { color: #FFD700; font-size: 26px; }
.leaderboard-rank.rank-2 { color: #C6C9D2; font-size: 23px; }
.leaderboard-rank.rank-3 { color: #CD7F32; font-size: 21px; }

.leaderboard-name {
    font-weight: 700;
    font-size: 15px;
    flex-grow: 1;
    color: #fff;
}

.leaderboard-stat {
    font-weight: 800;
    font-size: 15px;
    background: linear-gradient(90deg, #FFC53D, #FF8A00);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
/* ---------- Live Scoreboard ---------- */
.live-dot {
    display:inline-block; width:9px; height:9px; border-radius:50%;
    background:#ff3b3b; margin-right:7px; vertical-align:middle;
    box-shadow:0 0 0 0 rgba(255,59,59,0.7);
    animation:live-pulse 1.4s infinite;
}
@keyframes live-pulse {
    0%   { box-shadow:0 0 0 0 rgba(255,59,59,0.55); }
    70%  { box-shadow:0 0 0 9px rgba(255,59,59,0); }
    100% { box-shadow:0 0 0 0 rgba(255,59,59,0); }
}

.score-hero {
    /* Compact, phone-card sized scoreboard (CricHeroes-style mini widget) */
    background: linear-gradient(135deg, rgba(10,122,74,0.42), rgba(3,16,10,0.78));
    border: 1px solid rgba(255,197,61,0.30);
    border-radius: 18px;
    padding: 14px 18px;
    margin: 0 auto 14px auto;
    max-width: 460px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.45);
}
.score-hero .teams {
    font-size:11px; letter-spacing:.4px; color:#cdeede;
    text-transform:uppercase; font-weight:600;
}
.score-hero .venue { font-size:11px; color:#8fb3a0; margin:2px 0 8px 0; }
.score-hero .bigscore {
    font-size:28px; font-weight:900; margin:0; line-height:1.15;
    background: linear-gradient(90deg, #fff, #ffe9b0 60%, #FFC53D 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.score-hero .oversline { font-size:12px; color:#e5f3ea; margin-top:3px; }
.score-hero .subline { font-size:12px; color:#9fd6bb; margin-top:6px; }
.score-hero .prev-inns { font-size:11px; color:#7fa892; margin-top:5px; }

/* ---------- Weather + Location strip (compact, sits under the score card) ---------- */
.wx-strip {
    display:flex; align-items:center; justify-content:center; gap:14px;
    max-width:460px; margin:0 auto 14px auto;
    background: rgba(56,189,248,0.08);
    border: 1px solid rgba(56,189,248,0.22);
    border-radius: 14px;
    padding: 8px 14px;
    font-size: 12px;
    color:#dff3ff;
    flex-wrap: wrap;
}
.wx-strip .wx-item { display:flex; align-items:center; gap:5px; }
.wx-strip .wx-emoji { font-size:16px; }

/* ---------- Team chips (New Match / Playing XI creative touch) ---------- */
.team-chip {
    display:inline-flex; align-items:center; gap:8px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,197,61,0.25);
    border-radius: 14px;
    padding: 8px 14px;
    font-weight:700; font-size:14px; color:#fff;
    margin-bottom: 8px;
}
.team-chip .chip-emoji { font-size:20px; }

.fee-badge {
    display:inline-block; font-size:11px; font-weight:700;
    padding:2px 8px; border-radius:8px; margin-left:6px;
}
.fee-badge-paid    { background: rgba(34,197,94,0.18); color:#86efac; }
.fee-badge-pending { background: rgba(250,204,21,0.18); color:#fde68a; }
.fee-badge-overdue { background: rgba(239,68,68,0.20); color:#fca5a5; }

.ball-pill-row { display:flex; flex-wrap:wrap; gap:6px; margin: 4px 0 16px 0; }
.ball-pill {
    display:inline-flex; align-items:center; justify-content:center;
    min-width:30px; height:30px; padding:0 7px; border-radius:9px;
    font-weight:800; font-size:13px;
    background: rgba(255,255,255,0.10); color:#dfeee6;
    border: 1px solid rgba(255,255,255,0.14);
}
.pill-dot   { background: rgba(255,255,255,0.05); color:#7fa892; }
.pill-run   { background: rgba(56,189,248,0.16); color:#c9f0ff; border-color: rgba(56,189,248,0.3); }
.pill-four  { background: linear-gradient(135deg,#38bdf8,#22d3ee); color:#04121b; border:none; }
.pill-six   { background: linear-gradient(135deg,#FFC53D,#FF8A00); color:#2b1500; border:none; }
.pill-wicket{ background: linear-gradient(135deg,#ff5858,#f857a6); color:#2b0000; border:none; }
.pill-wide, .pill-nb { background: rgba(255,197,61,0.22); color:#ffe9b0; border-color: rgba(255,197,61,0.35); }
.pill-bye   { background: rgba(148,163,184,0.22); color:#e2e8f0; }

.live-mini-card {
    background: linear-gradient(135deg, rgba(10,122,74,0.42), rgba(3,16,10,0.75));
    border: 1px solid rgba(255,197,61,0.32);
    border-radius: 18px;
    padding: 16px 20px;
    margin-bottom: 12px;
    text-align: center;
}
.live-mini-card .teams { font-weight:700; font-size:15px; color:#fff; }
.live-mini-card .score {
    font-size:24px; font-weight:900; margin:6px 0 0 0;
    color:#FFC53D;
}

.live-updated-caption { color:#7fa892; font-size:12px; }

/* ---------- Progress bars (overs / run-chase) ---------- */
.progress-wrap { max-width:460px; margin:0 auto 14px auto; }
.progress-label {
    display:flex; justify-content:space-between; font-size:11px;
    color:#9fd6bb; margin-bottom:4px; text-transform:uppercase; letter-spacing:.4px;
}
.progress-track {
    width:100%; height:8px; border-radius:99px;
    background: rgba(255,255,255,0.08);
    overflow:hidden;
    border: 1px solid rgba(255,255,255,0.06);
}
.progress-fill {
    height:100%; border-radius:99px;
    background: linear-gradient(90deg, #38bdf8, #22d3ee);
    transition: width 0.6s cubic-bezier(.4,0,.2,1);
}
.progress-fill-chase { background: linear-gradient(90deg, #FFC53D, #FF8A00); }
.progress-fill-danger { background: linear-gradient(90deg, #ff5858, #f857a6); }

/* ---------- Polished section header w/ underline accent ---------- */
.section-head { display:flex; align-items:center; gap:10px; margin: 4px 0 14px 0; }
.section-head .sh-icon {
    width:38px; height:38px; border-radius:12px; flex-shrink:0;
    display:flex; align-items:center; justify-content:center; font-size:18px;
    background: linear-gradient(135deg, rgba(255,197,61,0.22), rgba(56,189,248,0.16));
    border: 1px solid rgba(255,197,61,0.28);
}
.section-head .sh-text h3 { margin:0; font-size:19px; font-weight:800; color:#fff; letter-spacing:.2px; }
.section-head .sh-text p { margin:1px 0 0 0; font-size:12.5px; color:#9fd6bb; }

/* ---------- Stat pill row (compact KPI strip) ---------- */
.stat-strip { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:14px; }
.stat-pill {
    flex:1; min-width:110px;
    background: linear-gradient(160deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 14px; padding: 12px 14px;
}
.stat-pill .sp-val {
    font-size:22px; font-weight:900; line-height:1.1;
    background: linear-gradient(90deg, #FFC53D, #38bdf8);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.stat-pill .sp-lbl { font-size:11px; color:#9fd6bb; text-transform:uppercase; letter-spacing:.4px; margin-top:3px; }

/* ---------- Global input / select polish ---------- */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div, .stDateInput input {
    background: rgba(255,255,255,0.045) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 10px !important;
    color: var(--ink) !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
    border-color: rgba(255,197,61,0.55) !important;
    box-shadow: 0 0 0 3px rgba(255,197,61,0.14) !important;
}
.stSlider [data-baseweb="slider"] > div > div { background: linear-gradient(90deg, #FFC53D, #38bdf8) !important; }

/* Dataframes / tables */
[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; border: 1px solid rgba(255,255,255,0.10); }

/* Metric widget (native st.metric) polish */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 14px;
    padding: 12px 16px;
}
[data-testid="stMetricValue"] {
    background: linear-gradient(90deg, #FFC53D, #FF8A00);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

/* Sidebar nav radio -> pill-style nav list */
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    border-radius: 10px !important;
    padding: 6px 10px !important;
    margin-bottom: 2px !important;
    transition: background 0.15s ease;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background: rgba(255,197,61,0.10); }

/* Expander polish */
.streamlit-expanderHeader, [data-testid="stExpander"] {
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}

/* Tab underline accent */
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(255,197,61,0.16), rgba(56,189,248,0.10)) !important;
    border-bottom: 2px solid #FFC53D !important;
}

/* Ball pill pop-in animation */
@keyframes pill-pop {
    0% { transform: scale(0.4); opacity: 0; }
    70% { transform: scale(1.12); opacity: 1; }
    100% { transform: scale(1); }
}
.ball-pill { animation: pill-pop 0.35s ease-out; }

/* Emoji burst for boundary/wicket events */
@keyframes burst-float {
    0% { transform: translateY(0) scale(0.6); opacity: 0; }
    30% { opacity: 1; }
    100% { transform: translateY(-46px) scale(1.5); opacity: 0; }
}
.emoji-burst { text-align:center; font-size:34px; margin: -6px 0 6px 0; animation: burst-float 0.9s ease-out; }

/* Top strip divider used under page titles */
.page-divider {
    height:1px; margin: 6px 0 18px 0;
    background: linear-gradient(90deg, rgba(255,197,61,0.4), rgba(56,189,248,0.25), transparent);
}

</style>
"""
