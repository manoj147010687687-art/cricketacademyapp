"""
🏏 Shree Shyam Cricket Academy — AI Performance & Fitness Suite Pro
Main Streamlit application.

Run with:
    streamlit run app.py

Set your free GroqCloud API key in the sidebar (get one at https://console.groq.com/keys)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime, timedelta
import io
import os

import db
import groq_client as gc
import email_client as ec
import whatsapp_client as wc
import match_heroes as mh
import live_score as lc
from exercise_data import EXERCISES, CATEGORIES, POSITION_CATEGORY_MAP, filter_exercises
from styles import CUSTOM_CSS

# ----------------------------------------------------------------------------
# Page config & global setup
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Shree Shyam Cricket Academy Bahadurgarh AI based",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
db.init_db()
mh.init_mh_tables()
lc.init_lc_tables()


def page_header(emoji, title, sub=None):
    """Consistent, polished page header used across every page in the app."""
    sub_html = f'<p>{sub}</p>' if sub else ""
    st.markdown(
        f'''<div class="section-head">
                <div class="sh-icon">{emoji}</div>
                <div class="sh-text"><h3 style="font-size:26px;">{title}</h3>{sub_html}</div>
            </div>
            <div class="page-divider"></div>''',
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------------
# PUBLIC LIVE SCOREBOARD — no login required at all.
# Open with ...?live=1 in the URL (share this link with anyone).
# ----------------------------------------------------------------------------
if st.query_params.get("live") == "1":
    lc.public_live_page()
    st.stop()

DEFAULT_ADMIN_USER = "admin"
DEFAULT_ADMIN_PASS = "admin123"
COACHES = {
    "Mohit Kumar": {"type": "batting", "password": "coach123", "emoji": "🏏"},
    "Ankush Kumar": {"type": "bowling", "password": "coach123", "emoji": "🎯"},
}

# ----------------------------------------------------------------------------
# Session state defaults
# ----------------------------------------------------------------------------
defaults = {
    "auth_role": None,          # "admin" / "coach" / "student"
    "coach_name": None,
    "student_id": None,
    "groq_api_key": os.environ.get("GROQ_API_KEY", ""),
    "groq_model": gc.DEFAULT_MODEL,
    "smtp_email": os.environ.get("SMTP_EMAIL", ""),
    "smtp_app_password": os.environ.get("SMTP_APP_PASSWORD", ""),
    "page": "Dashboard",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def logout():
    for k in ["auth_role", "coach_name", "student_id"]:
        st.session_state[k] = None
    st.rerun()


# ----------------------------------------------------------------------------
# ACADEMY PHOTO BANNER
# ----------------------------------------------------------------------------
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
ACADEMY_PHOTO_CANDIDATES = [
    os.path.join(ASSETS_DIR, "academy_photo.jpg"),
    os.path.join(ASSETS_DIR, "academy_photo.jpeg"),
    os.path.join(ASSETS_DIR, "academy_photo.png"),
]


def academy_banner():
    """Shows the academy's real photo as a hero banner if present in /assets,
    otherwise falls back to a nice gradient stadium banner."""
    photo_path = next((p for p in ACADEMY_PHOTO_CANDIDATES if os.path.exists(p)), None)
    if photo_path:
        import base64
        with open(photo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        ext = photo_path.split(".")[-1]
        st.markdown(
            f'''<div class="academy-banner">
                    <img src="data:image/{ext};base64,{b64}" />
                    <div class="academy-banner-overlay">
                        <h1>🏏 Shree Shyam Cricket Academy</h1>
                        <p>Bahadurgarh · AI Performance &amp; Fitness Suite Pro</p>
                    </div>
                </div>''',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '''<div class="academy-banner-fallback">
                    <h1>🏏 Shree Shyam Cricket Academy Bahadurgarh</h1>
                    <p>AI Performance &amp; Fitness Suite Pro — add your academy's photo to
                    <code>assets/academy_photo.jpg</code> to instantly show it as the banner.</p>
                </div>''',
            unsafe_allow_html=True,
        )


# ----------------------------------------------------------------------------
# LOGIN SCREEN
# ----------------------------------------------------------------------------
def login_screen():
    academy_banner()
    st.write("")
    lc1, lc2, lc3 = st.columns([1, 1.3, 1])
    with lc2:
        lc.login_teaser()
    st.write("")
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        role = st.selectbox("Login as", ["Student", "Coach", "Admin"])

        if role == "Student":
            students = db.get_students()
            if not students:
                st.info("No students registered yet. Please ask the admin to register you.")
            else:
                sid_input = st.text_input("Student ID", placeholder="Enter your Student ID (get it from Admin/Coach)")
                pin = st.text_input("PIN (default: 1234)", type="password")
                if st.button("Login ▶", use_container_width=True):
                    sid = None
                    if sid_input.strip().isdigit():
                        sid = int(sid_input.strip())
                    student = db.get_student(sid) if sid else None
                    if student and pin == (student.get("pin") or "1234"):
                        st.session_state.auth_role = "student"
                        st.session_state.student_id = sid
                        st.rerun()
                    else:
                        st.error("Incorrect Student ID or PIN.")

        elif role == "Coach":
            coach_name = st.selectbox("Select Coach", list(COACHES.keys()))
            pw = st.text_input("Password", type="password", value="", placeholder="coach123")
            if st.button("Login ▶", use_container_width=True):
                if pw == COACHES[coach_name]["password"]:
                    st.session_state.auth_role = "coach"
                    st.session_state.coach_name = coach_name
                    st.rerun()
                else:
                    st.error("Incorrect password.")

        else:  # Admin
            u = st.text_input("Username", value="")
            p = st.text_input("Password", type="password", value="")
            if st.button("Login ▶", use_container_width=True):
                if u == DEFAULT_ADMIN_USER and p == DEFAULT_ADMIN_PASS:
                    st.session_state.auth_role = "admin"
                    st.rerun()
                else:
                    st.error("Incorrect username/password. (default: admin / admin123)")

        st.caption("Default → Admin: **admin / admin123** · Coach password: **coach123** · Student PIN: **1234**")
        st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------
def sidebar_nav():
    with st.sidebar:
        st.markdown("### 🏏 Shree Shyam Academy")
        role = st.session_state.auth_role
        if role == "admin":
            st.markdown('<span class="badge badge-orange">ADMIN</span>', unsafe_allow_html=True)
            pages = ["Dashboard", "Student Management", "Fees Management", "AI Diet Planner", "AI Fitness & Workout",
                     "Position-Based Training", "Stretching & Recovery", "Exercise Library",
                     "Coach Panel", "AI Chat Assistant", "Injury Prevention",
                     "Match Performance & Analytics", "🦸 SSCA Match Heroes", "🔴 Live Match Center", "Leaderboard", "Announcements",
                     "Attendance", "Reports", "Admin Panel"]
        elif role == "coach":
            st.markdown(f'<span class="badge">COACH · {st.session_state.coach_name}</span>', unsafe_allow_html=True)
            pages = ["Dashboard", "Coach Panel", "Match Performance & Analytics", "🦸 SSCA Match Heroes", "🔴 Live Match Center", "Leaderboard",
                     "Announcements", "Injury Prevention", "Fees Management", "Attendance", "Exercise Library", "AI Chat Assistant"]
        else:
            st.markdown('<span class="badge badge-green">STUDENT</span>', unsafe_allow_html=True)
            pages = ["Dashboard", "AI Diet Planner", "AI Fitness & Workout", "Position-Based Training",
                     "Stretching & Recovery", "Exercise Library", "AI Chat Assistant",
                     "Injury Prevention", "Match Performance & Analytics", "🦸 SSCA Match Heroes", "📡 Live Scores", "Leaderboard",
                     "Announcements", "Fees Management", "Reports"]

        st.session_state.page = st.radio("Navigation", pages, index=pages.index(st.session_state.page) if st.session_state.page in pages else 0, label_visibility="collapsed")

        st.markdown("---")
        with st.expander("⚙️ SSCA AI Settings"):
            st.session_state.groq_api_key = st.text_input(
                "API Key", value=st.session_state.groq_api_key, type="password",
                help="Free key: https://console.groq.com/keys"
            )
            st.session_state.groq_model = st.selectbox(
                "Model", gc.AVAILABLE_MODELS,
                index=gc.AVAILABLE_MODELS.index(st.session_state.groq_model) if st.session_state.groq_model in gc.AVAILABLE_MODELS else 0
            )
        with st.expander("📧 Email Settings (Free Gmail SMTP)"):
            st.session_state.smtp_email = st.text_input(
                "Your Gmail address", value=st.session_state.smtp_email, key="smtp_email_input"
            )
            st.session_state.smtp_app_password = st.text_input(
                "Gmail App Password", value=st.session_state.smtp_app_password, type="password",
                key="smtp_pass_input",
                help="Your normal Gmail password will NOT work. Google Account → Security → "
                     "2-Step Verification → App Passwords, and generate a free 16-digit password."
            )
            st.caption("Diet plans and fees reminder emails will be sent from this Gmail account — completely free, no paid service required.")
        st.markdown("---")
        st.caption(f"🕒 {datetime.now().strftime('%d %b %Y, %I:%M %p')}")
        if st.button("🚪 Logout", use_container_width=True):
            logout()


# ----------------------------------------------------------------------------
# Helper: student picker for coach/admin views
# ----------------------------------------------------------------------------
def pick_student(label="Select Student", role_filter=None, key=None):
    students = db.get_students_by_role(role_filter) if role_filter else db.get_students()
    if not students:
        st.warning("No students are registered yet.")
        return None
    names = {f"{s['name']} (ID {s['id']})": s for s in students}
    choice = st.selectbox(label, list(names.keys()), key=key)
    return names[choice]


def current_student():
    """Resolve the student record depending on role (self for student, chosen one for admin/coach)."""
    if st.session_state.auth_role == "student":
        return db.get_student(st.session_state.student_id)
    return None


def fee_effective_status(fee):
    """Fees status is computed, not just stored: an unpaid fee past its due date shows as Overdue."""
    if fee.get("status") == "Paid":
        return "Paid"
    try:
        due = datetime.strptime(fee["due_date"], "%Y-%m-%d").date()
    except Exception:
        return fee.get("status") or "Pending"
    return "Overdue" if due < date.today() else "Pending"


# ----------------------------------------------------------------------------
# PAGE: Dashboard
# ----------------------------------------------------------------------------
def page_dashboard():
    role = st.session_state.auth_role
    academy_banner()
    page_header("📊", "Dashboard", f"Today: {date.today().strftime('%A, %d %B %Y')}")
    st.write("")

    anns = db.get_announcements(limit=3)
    if anns:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 📢 Latest Announcements")
        for a in anns:
            st.markdown(
                f'''<div class="announcement-item">
                        <div class="a-date">{a["post_date"]} · {a["posted_by"]}</div>
                        <div class="a-title">{a["title"]}</div>
                        <div>{a["message"] or ""}</div>
                    </div>''',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    if role == "student":
        s = current_student()
        if not s:
            st.error("Student record not found.")
            return
        fees = db.get_fees(s["id"])
        pending_fees = [f for f in fees if fee_effective_status(f) != "Paid"]
        if pending_fees:
            overdue_fees = [f for f in pending_fees if fee_effective_status(f) == "Overdue"]
            color = "#e63946" if overdue_fees else "#f4a300"
            label = "OVERDUE" if overdue_fees else "Due Soon"
            st.markdown(
                f'<div class="glass-card" style="border-left:4px solid {color};">'
                f'💰 <b>Fees {label}:</b> {len(pending_fees)} record(s) pending. '
                f'See details on the "Fees Management" page.</div>',
                unsafe_allow_html=True,
            )
            st.write("")

        col1, col2, col3, col4 = st.columns(4)
        bmi = None
        if s.get("height_cm") and s.get("weight_kg"):
            h_m = s["height_cm"] / 100
            bmi = round(s["weight_kg"] / (h_m ** 2), 1)
        with col1:
            st.markdown(f'<div class="metric-card"><h2>{s.get("age","-")}</h2><p>Age</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><h2>{bmi or "-"}</h2><p>BMI</p></div>', unsafe_allow_html=True)
        with col3:
            att = db.attendance_summary(s["id"])
            present = att.get("Present", 0)
            total = sum(att.values()) or 1
            pct = round(100 * present / total)
            st.markdown(f'<div class="metric-card"><h2>{pct}%</h2><p>Attendance</p></div>', unsafe_allow_html=True)
        with col4:
            injuries = db.get_injuries(s["id"])
            active = len([i for i in injuries if i["status"] == "Active"])
            st.markdown(f'<div class="metric-card"><h2>{active}</h2><p>Active Injuries</p></div>', unsafe_allow_html=True)

        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### 👤 Profile")
            st.write(f"**Role:** {s.get('role')}  \n**Batting style:** {s.get('batting_style') or '-'}  \n"
                      f"**Bowling style:** {s.get('bowling_style') or '-'}  \n**Dominant hand:** {s.get('dominant_hand') or '-'}")
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### 💧 Hydration Reminder")
            st.progress(0.6, text="2.4L / 4L water target consumed today (manually tracked)")
            st.caption("Drink at least 4-5 litres of water/electrolytes on match day.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.write("")
        c3, c4 = st.columns(2)
        with c3:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### 🥗 Latest Diet Plan")
            logs = db.get_diet_logs(s["id"])
            if logs:
                st.caption(f"Generated on {logs[0]['log_date']} · {logs[0]['diet_type']} · Goal: {logs[0]['goal']}")
                with st.expander("View"):
                    st.markdown(logs[0]["plan_text"])
            else:
                st.info("No diet plan has been generated yet. Go to the 'AI Diet Planner' page.")
            st.markdown("</div>", unsafe_allow_html=True)
        with c4:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### 💪 Latest Workout Plan")
            wlogs = db.get_workout_logs(s["id"])
            if wlogs:
                st.caption(f"Generated on {wlogs[0]['log_date']} · Goal: {wlogs[0]['goal']}")
                with st.expander("View"):
                    st.markdown(wlogs[0]["plan_text"])
            else:
                st.info("No workout plan has been generated yet. Go to the 'AI Fitness & Workout' page.")
            st.markdown("</div>", unsafe_allow_html=True)

        perf = db.get_performance(s["id"])
        if perf:
            st.write("")
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### 📈 Performance Trend")
            df = pd.DataFrame(perf)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df["match_date"], y=df["runs"], mode="lines+markers", name="Runs", line=dict(color="#FFD166")))
            fig.add_trace(go.Scatter(x=df["match_date"], y=df["wickets"], mode="lines+markers", name="Wickets", line=dict(color="#4facfe")))
            fig.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                               legend=dict(orientation="h"), margin=dict(l=10, r=10, t=10, b=10), height=320)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        students = db.get_students()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card"><h2>{len(students)}</h2><p>Total Students</p></div>', unsafe_allow_html=True)
        with col2:
            bats = len([s for s in students if s["role"] == "Batsman"])
            st.markdown(f'<div class="metric-card"><h2>{bats}</h2><p>Batsmen</p></div>', unsafe_allow_html=True)
        with col3:
            bowl = len([s for s in students if s["role"] == "Bowler"])
            st.markdown(f'<div class="metric-card"><h2>{bowl}</h2><p>Bowlers</p></div>', unsafe_allow_html=True)
        with col4:
            all_inj = db.get_injuries()
            active_inj = len([i for i in all_inj if i["status"] == "Active"])
            st.markdown(f'<div class="metric-card"><h2>{active_inj}</h2><p>Active Injuries</p></div>', unsafe_allow_html=True)

        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### 🧑‍🏫 Coaches")
            for name, info in COACHES.items():
                st.markdown(
                    f'<div class="coach-card"><div class="coach-avatar">{info["emoji"]}</div>'
                    f'<div><b>{name}</b><br><span style="color:#a9b2cc;">'
                    f'{"Batting Coach" if info["type"]=="batting" else "Bowling Coach"}</span></div></div>',
                    unsafe_allow_html=True,
                )
                st.write("")
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### 🏏 Role Distribution")
            if students:
                role_counts = pd.Series([s["role"] for s in students]).value_counts()
                fig = px.pie(values=role_counts.values, names=role_counts.index, hole=0.55,
                             color_discrete_sequence=["#FFD166", "#FF7A50", "#4facfe", "#43e97b"])
                fig.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                   margin=dict(l=10, r=10, t=10, b=10), height=280)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No students yet.")
            st.markdown("</div>", unsafe_allow_html=True)

        all_fees = db.get_all_fees_with_student()
        overdue = [f for f in all_fees if fee_effective_status(f) == "Overdue"]
        pending = [f for f in all_fees if fee_effective_status(f) == "Pending"]
        if overdue or pending:
            st.write("")
            st.markdown('<div class="glass-card" style="border-left:4px solid #e63946;">', unsafe_allow_html=True)
            st.markdown("#### 💰 Fees Alert")
            if overdue:
                names = ", ".join(sorted(set(f["student_name"] for f in overdue))[:10])
                st.write(f"🔴 **{len(overdue)} fee(s) OVERDUE** — {names}")
            if pending:
                st.write(f"🟡 **{len(pending)} fee(s) pending** (due soon)")
            st.caption("Go to the 'Fees Management' page for details, marking as paid, and sending reminder emails.")
            st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# PAGE: Student Management (Admin)
# ----------------------------------------------------------------------------
def page_student_management():
    page_header("👤", "Student Management")
    tab1, tab2 = st.tabs(["➕ Register New Student", "📋 All Students"])

    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        with st.form("add_student_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                name = st.text_input("Full Name *")
                age = st.number_input("Age", 6, 60, 16)
                height_cm = st.number_input("Height (cm)", 100.0, 220.0, 165.0)
                weight_kg = st.number_input("Weight (kg)", 20.0, 150.0, 55.0)
            with c2:
                role = st.selectbox("Playing Role", ["Batsman", "Bowler", "All Rounder", "Wicket Keeper"])
                dominant_hand = st.selectbox("Dominant Hand", ["Right", "Left"])
                batting_style = st.selectbox("Batting Style", ["Right-hand bat", "Left-hand bat", "N/A"])
                bowling_style = st.selectbox("Bowling Style", [
                    "Right-arm fast", "Right-arm medium", "Right-arm off-spin", "Right-arm leg-spin",
                    "Left-arm fast", "Left-arm medium", "Left-arm orthodox", "Left-arm chinaman", "N/A"
                ])
            with c3:
                contact = st.text_input("Contact Number")
                email = st.text_input("Email (for diet plan / fees alerts)")
                injury_history = st.text_area("Injury History (if any)", height=68)
                pin = st.text_input("Login PIN (4 digit)", value="1234")
            submitted = st.form_submit_button("✅ Register Student", use_container_width=True)
            if submitted:
                if not name.strip():
                    st.error("Name is required.")
                else:
                    sid = db.add_student({
                        "name": name.strip(), "age": age, "height_cm": height_cm, "weight_kg": weight_kg,
                        "role": role, "dominant_hand": dominant_hand, "batting_style": batting_style,
                        "bowling_style": bowling_style, "contact": contact, "email": email.strip() if email else None,
                        "injury_history": injury_history,
                        "pin": pin or "1234",
                    })
                    st.success(f"✅ {name} register ho gaya! Student ID: {sid} · PIN: {pin or '1234'}")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        students = db.get_students()
        if not students:
            st.info("No students registered yet.")
        else:
            search = st.text_input("🔍 Search by name")
            filtered = [s for s in students if search.lower() in s["name"].lower()] if search else students
            for s in filtered:
                with st.expander(f"🏏 {s['name']} — {s['role']} (ID {s['id']})"):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.write(f"**Age:** {s['age']}  |  **Height:** {s['height_cm']} cm  |  **Weight:** {s['weight_kg']} kg")
                        st.write(f"**Dominant Hand:** {s['dominant_hand']}  |  **Batting:** {s['batting_style']}  |  **Bowling:** {s['bowling_style']}")
                        st.write(f"**Contact:** {s['contact'] or '-'}  |  **Email:** {s.get('email') or '-'}")
                        st.write(f"**Injury History:** {s['injury_history'] or 'None'}")
                        st.write(f"**Joined:** {s['join_date']}  |  **PIN:** {s['pin']}")
                    with c2:
                        if st.button("🗑️ Delete Student", key=f"del_{s['id']}"):
                            db.delete_student(s["id"])
                            st.rerun()
                        new_pin = st.text_input("Reset PIN", value=s["pin"], key=f"pin_{s['id']}")
                        if st.button("Update PIN", key=f"updatepin_{s['id']}"):
                            db.update_student(s["id"], {"pin": new_pin})
                            st.success("PIN update ho gaya.")
                        new_email = st.text_input("Update Email", value=s.get("email") or "", key=f"email_{s['id']}")
                        if st.button("Update Email", key=f"updateemail_{s['id']}"):
                            db.update_student(s["id"], {"email": new_email.strip()})
                            st.success("Email update ho gaya.")


# ----------------------------------------------------------------------------
# PAGE: AI Diet Planner
# ----------------------------------------------------------------------------
def page_diet_planner():
    page_header("🥗", "AI Diet Planner", "Personalised, India-friendly cricket diet plans generated by SSCA AI.")
    st.write("")

    if st.session_state.auth_role == "student":
        student = current_student()
    else:
        student = pick_student()
    if not student:
        return

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        diet_type = st.selectbox("Diet Type", ["Vegetarian", "Non-Vegetarian", "Jain", "Eggetarian"])
    with c2:
        goal = st.selectbox("Goal", ["Weight Gain (Muscle)", "Weight Loss (Fat Cut)", "High Protein Maintenance",
                                       "Budget-Friendly Diet", "Match Day Diet"])
    with c3:
        st.write("")
        st.write("")
        generate = st.button("🤖 Generate AI Diet Plan", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if generate:
        with st.spinner("SSCA AI is preparing the diet plan..."):
            text, err = gc.generate_diet_plan(st.session_state.groq_api_key, student, diet_type, goal,
                                                model=st.session_state.groq_model)
        if err:
            st.error(err)
        else:
            db.save_diet_log(student["id"], diet_type, goal, text)
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(text)
            st.markdown("</div>", unsafe_allow_html=True)

            if student.get("email"):
                if st.button("📧 Email This Diet Plan to Student", key="email_diet_plan_new"):
                    body = ec.diet_plan_email_body(student, diet_type, goal, text)
                    ok, err2 = ec.send_email(
                        st.session_state.smtp_email, st.session_state.smtp_app_password,
                        student["email"], "Your AI Diet Plan — Shree Shyam Cricket Academy", body
                    )
                    if ok:
                        st.success(f"✅ Diet plan emailed to {student['email']}.")
                    else:
                        st.error(err2)
            else:
                st.info("This student's email is not registered — add it in Student Management so the plan can be emailed.")

    logs = db.get_diet_logs(student["id"])
    if logs:
        st.markdown("#### 📜 Previous Diet Plans")
        for log in logs[:5]:
            with st.expander(f"{log['log_date']} · {log['diet_type']} · {log['goal']}"):
                st.markdown(log["plan_text"])
                if student.get("email"):
                    if st.button("📧 Email this plan", key=f"email_log_{log['id']}"):
                        body = ec.diet_plan_email_body(student, log["diet_type"], log["goal"], log["plan_text"])
                        ok, err2 = ec.send_email(
                            st.session_state.smtp_email, st.session_state.smtp_app_password,
                            student["email"], "Your Diet Plan — Shree Shyam Cricket Academy", body
                        )
                        if ok:
                            st.success("✅ Email sent.")
                        else:
                            st.error(err2)


# ----------------------------------------------------------------------------
# PAGE: AI Fitness & Workout
# ----------------------------------------------------------------------------
def page_fitness_workout():
    page_header("💪", "AI Fitness & Workout Module", "Cricket-specific strength, conditioning & recovery — generated instantly by AI.")
    st.write("")

    if st.session_state.auth_role == "student":
        student = current_student()
    else:
        student = pick_student()
    if not student:
        return

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        goal = st.selectbox("Workout Goal", ["Fat Loss", "Muscle Gain", "General Cricket Fitness",
                                               "Match Day / Pre-Match Activation", "Injury Recovery"])
    with c2:
        st.write("")
        st.write("")
        generate = st.button("🤖 Generate AI Workout Plan", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if generate:
        with st.spinner("SSCA AI is preparing the workout plan..."):
            text, err = gc.generate_workout_plan(st.session_state.groq_api_key, student, goal,
                                                   model=st.session_state.groq_model)
        if err:
            st.error(err)
        else:
            db.save_workout_log(student["id"], goal, text)
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(text)
            st.markdown("</div>", unsafe_allow_html=True)

    logs = db.get_workout_logs(student["id"])
    if logs:
        st.markdown("#### 📜 Previous Workout Plans")
        for log in logs[:5]:
            with st.expander(f"{log['log_date']} · {log['goal']}"):
                st.markdown(log["plan_text"])


# ----------------------------------------------------------------------------
# PAGE: Position-Based Training
# ----------------------------------------------------------------------------
FOCUS_AREAS = {
    "Batsman": ["Bat Speed", "Shadow Practice", "Reaction Drill", "Throwdowns", "Power Hitting",
                "Front Foot Play", "Back Foot Play", "Cover Drive", "Pull Shot", "Hook Shot", "Sweep Shot"],
    "Bowler": ["Yorker", "Bouncer", "Run-up Rhythm", "Release Point", "Hip Rotation", "Shoulder Strength",
               "Core Power", "Spin Variations", "Line & Length"],
    "Wicket Keeper": ["Footwork", "Diving", "Glove Work", "Reaction Drill", "Reflexes", "Explosive Jump"],
    "Fielder": ["Slip Catching", "High Catch", "Boundary Fielding", "Direct Hit", "Throw Accuracy",
                "Reaction Speed", "Sprint", "Agility", "Diving"],
}


def page_position_training():
    page_header("🏏", "Position-Based Training", "Batsman • Bowler • Wicket Keeper • Fielder — AI generated session plans.")
    st.write("")

    if st.session_state.auth_role == "student":
        student = current_student()
        default_position = student["role"] if student["role"] in FOCUS_AREAS else "Batsman"
    else:
        student = pick_student()
        default_position = "Batsman"
    if not student:
        return

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    position = st.selectbox("Position", list(FOCUS_AREAS.keys()),
                             index=list(FOCUS_AREAS.keys()).index(default_position) if default_position in FOCUS_AREAS else 0)
    focus = st.multiselect("Focus Areas (optional — leave blank for a well-rounded session)", FOCUS_AREAS[position])
    generate = st.button("🤖 Generate AI Training Session", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if generate:
        with st.spinner("Preparing the session plan..."):
            text, err = gc.generate_position_training(st.session_state.groq_api_key, student, position, focus,
                                                         model=st.session_state.groq_model)
        if err:
            st.error(err)
        else:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(text)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("#### 📚 Related Drills from Exercise Library")
    cats = POSITION_CATEGORY_MAP.get(position, [])
    related = [e for e in EXERCISES if e["category"] in cats]
    if related:
        df = pd.DataFrame(related)[["name", "category", "muscle_group", "equipment", "difficulty", "duration"]]
        st.dataframe(df, use_container_width=True, hide_index=True)


# ----------------------------------------------------------------------------
# PAGE: Stretching & Recovery
# ----------------------------------------------------------------------------
def page_stretching_recovery():
    page_header("🧘", "Stretching & Recovery Module", "Dynamic • Static • Warm-up • Cool-down • Foam Rolling • Yoga • Mobility")
    st.write("")

    if st.session_state.auth_role == "student":
        student = current_student()
    else:
        student = pick_student()
    if not student:
        return

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    kind = st.selectbox("Routine Type", ["Dynamic Stretch", "Static Stretch", "Warm-up", "Cool-down",
                                           "Foam Rolling", "Yoga", "Mobility"])
    generate = st.button("🤖 Generate AI Routine", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if generate:
        with st.spinner("Preparing the routine..."):
            text, err = gc.generate_stretch_recovery(st.session_state.groq_api_key, student, kind,
                                                        model=st.session_state.groq_model)
        if err:
            st.error(err)
        else:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(text)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("#### 📚 Library Reference")
    cat_map = {
        "Dynamic Stretch": "Dynamic Stretch", "Static Stretch": "Static Stretch", "Warm-up": "Warm-up",
        "Cool-down": "Static Stretch", "Foam Rolling": "Foam Rolling", "Yoga": "Yoga/Mobility", "Mobility": "Yoga/Mobility"
    }
    items = filter_exercises(category=cat_map.get(kind))
    if items:
        df = pd.DataFrame(items)[["name", "muscle_group", "duration", "cues"]]
        st.dataframe(df, use_container_width=True, hide_index=True)


# ----------------------------------------------------------------------------
# PAGE: Exercise Library
# ----------------------------------------------------------------------------
def page_exercise_library():
    page_header("📚", "Exercise Library", "Curated cricket-specific exercises — searchable & filterable.")
    st.write("")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        category = st.selectbox("Category", ["All"] + CATEGORIES)
    with c2:
        difficulty = st.selectbox("Difficulty", ["All", "Easy", "Medium", "Hard"])
    with c3:
        search = st.text_input("🔍 Search exercise / muscle group")
    st.markdown("</div>", unsafe_allow_html=True)

    results = filter_exercises(category=category, difficulty=difficulty, search=search)
    st.caption(f"Showing {len(results)} of {len(EXERCISES)} exercises. Need more? Ask the AI Chat Assistant for a custom drill!")
    if results:
        df = pd.DataFrame(results)[["name", "category", "muscle_group", "equipment", "difficulty", "duration", "calories", "cues"]]
        df.columns = ["Exercise", "Category", "Muscle Group", "Equipment", "Difficulty", "Duration", "Est. Calories", "Coaching Cue"]
        st.dataframe(df, use_container_width=True, hide_index=True, height=500)
    else:
        st.info("No exercises found matching these filters.")


# ----------------------------------------------------------------------------
# PAGE: Coach Panel
# ----------------------------------------------------------------------------
def page_coach_panel():
    page_header("🧑‍🏫", "Coach Panel")

    role = st.session_state.auth_role
    if role == "coach":
        coach_name = st.session_state.coach_name
        coach_type = COACHES[coach_name]["type"]
    else:
        c1, c2 = st.columns(2)
        with c1:
            coach_name = st.selectbox("Coach", list(COACHES.keys()))
        coach_type = COACHES[coach_name]["type"]

    emoji = COACHES[coach_name]["emoji"]
    st.markdown(
        f'<div class="coach-card"><div class="coach-avatar">{emoji}</div>'
        f'<div><b style="font-size:18px;">{coach_name}</b><br>'
        f'<span style="color:#a9b2cc;">{"Batting Coach" if coach_type=="batting" else "Bowling Coach"} · '
        f'Shree Shyam Cricket Academy</span></div></div>',
        unsafe_allow_html=True,
    )
    st.write("")

    relevant_role = "Batsman" if coach_type == "batting" else "Bowler"
    all_students = db.get_students()
    if not all_students:
        st.info("No students registered.")
        return

    student = pick_student(label="Select Student (to give feedback)", key="coach_pick")
    if not student:
        return

    tab1, tab2, tab3 = st.tabs(["📝 Add Coach Note", "📈 Progress History", "🤖 AI Recommendation"])

    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        note = st.text_area("Technique note / observation", height=100)
        rating = st.slider(f"{'Batting' if coach_type=='batting' else 'Bowling'} Rating (out of 10)", 1, 10, 6)
        if st.button("💾 Save Note", use_container_width=True):
            if note.strip():
                db.add_coach_note(student["id"], coach_name, note.strip(), rating)
                st.success("Note save ho gaya.")
            else:
                st.warning("Please write a note first.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        notes = db.get_coach_notes(student_id=student["id"], coach_name=coach_name)
        if notes:
            df = pd.DataFrame(notes)[["note_date", "note", "rating"]]
            df.columns = ["Date", "Note", "Rating"]
            st.dataframe(df, use_container_width=True, hide_index=True)
            fig = px.line(df, x="Date", y="Rating", markers=True, template="plotly_dark")
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=300,
                               margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No notes yet for this student.")

    with tab3:
        notes = db.get_coach_notes(student_id=student["id"], coach_name=coach_name)
        notes_text = "\n".join([f"{n['note_date']} (rating {n['rating']}/10): {n['note']}" for n in notes]) or "No notes yet."
        if st.button("🤖 Generate AI Recommendation", use_container_width=True):
            with st.spinner("Preparing AI recommendation..."):
                text, err = gc.generate_coach_recommendation(st.session_state.groq_api_key, student, coach_type,
                                                                notes_text, model=st.session_state.groq_model)
            if err:
                st.error(err)
            else:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown(text)
                st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# PAGE: AI Chat Assistant
# ----------------------------------------------------------------------------
def page_ai_chat():
    page_header("🤖", "AI Chat Assistant", "Batting, bowling, diet, fitness, recovery — ask anything and SSCA AI will answer instantly.")
    st.write("")

    if st.session_state.auth_role == "student":
        student = current_student()
    else:
        student = pick_student()
    if not student:
        return

    history = db.get_chat_history(student["id"])
    for h in history:
        with st.chat_message("user" if h["sender"] == "user" else "assistant"):
            st.markdown(h["message"])

    prompt = st.chat_input("Type your question... (e.g. How can I improve my batting, coach?)")
    if prompt:
        db.save_chat(student["id"], "user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Soch raha hoon..."):
                reply, err = gc.ai_chat_reply(st.session_state.groq_api_key, student, history, prompt,
                                                model=st.session_state.groq_model)
            if err:
                st.error(err)
            else:
                st.markdown(reply)
                db.save_chat(student["id"], "ai", reply)

    st.caption("💡 Try: \"How do I increase my fast bowling speed?\" · \"What should I eat before a match?\" · \"I have shoulder pain, what should I do?\"")


# ----------------------------------------------------------------------------
# PAGE: Injury Prevention
# ----------------------------------------------------------------------------
def page_injury_prevention():
    page_header("🩹", "Injury Prevention & Recovery")
    st.write("")

    if st.session_state.auth_role == "student":
        student = current_student()
    else:
        student = pick_student()
    if not student:
        return

    tab1, tab2, tab3 = st.tabs(["➕ Log Injury", "📋 Injury History", "🤸 Prevention Routine"])

    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            body_part = st.selectbox("Body Part", ["Shoulder", "Knee", "Back", "Hamstring", "Ankle",
                                                      "Groin", "Elbow", "Wrist", "Other"])
            severity = st.selectbox("Severity", ["Mild", "Moderate", "Severe"])
        with c2:
            injury_date = st.date_input("Injury Date", value=date.today())
            status = st.selectbox("Status", ["Active", "Recovering", "Recovered"])
        recovery_notes = st.text_area("Notes / Treatment", height=80)
        if st.button("💾 Save Injury Record", use_container_width=True):
            db.add_injury({
                "student_id": student["id"], "body_part": body_part, "injury_date": str(injury_date),
                "severity": severity, "status": status, "recovery_notes": recovery_notes,
            })
            st.success("Injury record save ho gaya.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        injuries = db.get_injuries(student["id"])
        if not injuries:
            st.info("No injury records — great!")
        else:
            for inj in injuries:
                badge_class = {"Active": "badge-red", "Recovering": "badge-orange", "Recovered": "badge-green"}[inj["status"]]
                st.markdown(
                    f'<div class="glass-card"><b>{inj["body_part"]}</b> — {inj["severity"]} '
                    f'<span class="badge {badge_class}">{inj["status"]}</span><br>'
                    f'<span style="color:#a9b2cc;">Date: {inj["injury_date"]}</span><br>{inj["recovery_notes"] or ""}</div>',
                    unsafe_allow_html=True,
                )
                new_status = st.selectbox("Update status", ["Active", "Recovering", "Recovered"],
                                            index=["Active", "Recovering", "Recovered"].index(inj["status"]),
                                            key=f"inj_status_{inj['id']}")
                if new_status != inj["status"]:
                    if st.button("Update", key=f"inj_upd_{inj['id']}"):
                        db.update_injury_status(inj["id"], new_status)
                        st.rerun()

    with tab3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        body_part = st.selectbox("Prevention focus area", ["Shoulder", "Knee", "Back", "Hamstring", "Ankle", "Groin"], key="prevention_area")
        if st.button("🤖 Generate AI Injury Prevention Routine", use_container_width=True):
            prompt_student = dict(student)
            prompt_student["injury_history"] = f"Prevention focus: {body_part}. " + (student.get("injury_history") or "")
            with st.spinner("Preparing the routine..."):
                text, err = gc.generate_stretch_recovery(st.session_state.groq_api_key, prompt_student,
                                                            f"{body_part} injury-prevention mobility & strengthening",
                                                            model=st.session_state.groq_model)
            if err:
                st.error(err)
            else:
                st.markdown(text)
        st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# PAGE: Match Performance & Analytics
# ----------------------------------------------------------------------------
def page_analytics():
    page_header("📊", "Match Performance & Analytics")
    st.write("")

    if st.session_state.auth_role == "student":
        student = current_student()
    else:
        student = pick_student()
    if not student:
        return

    if st.session_state.auth_role != "student":
        with st.expander("➕ Add Match Performance"):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                match_date = st.date_input("Match Date", value=date.today())
                runs = st.number_input("Runs", 0, 500, 0)
                balls_faced = st.number_input("Balls Faced", 0, 500, 0)
            with c2:
                fours = st.number_input("Fours", 0, 50, 0)
                sixes = st.number_input("Sixes", 0, 50, 0)
                overs_bowled = st.number_input("Overs Bowled", 0.0, 50.0, 0.0, step=0.1)
            with c3:
                runs_conceded = st.number_input("Runs Conceded", 0, 300, 0)
                wickets = st.number_input("Wickets", 0, 10, 0)
                catches = st.number_input("Catches", 0, 10, 0)
            with c4:
                run_outs = st.number_input("Run Outs", 0, 10, 0)
                notes = st.text_area("Notes", height=100)
            if st.button("💾 Save Match Data", use_container_width=True):
                db.add_performance({
                    "student_id": student["id"], "match_date": str(match_date), "runs": runs,
                    "balls_faced": balls_faced, "fours": fours, "sixes": sixes, "overs_bowled": overs_bowled,
                    "runs_conceded": runs_conceded, "wickets": wickets, "catches": catches,
                    "run_outs": run_outs, "notes": notes,
                })
                st.success("Match data save ho gaya.")
                st.rerun()

    perf = db.get_performance(student["id"])
    if not perf:
        st.info("No match data yet.")
        return

    df = pd.DataFrame(perf)
    df["strike_rate"] = (df["runs"] / df["balls_faced"].replace(0, pd.NA) * 100).fillna(0).round(1)
    df["economy"] = (df["runs_conceded"] / df["overs_bowled"].replace(0, pd.NA)).fillna(0).round(2)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="metric-card"><h2>{df["runs"].sum()}</h2><p>Total Runs</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card"><h2>{round(df["runs"].mean(),1)}</h2><p>Avg Runs</p></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card"><h2>{df["wickets"].sum()}</h2><p>Total Wickets</p></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-card"><h2>{df["catches"].sum()}</h2><p>Total Catches</p></div>', unsafe_allow_html=True)

    st.write("")
    tab1, tab2, tab3 = st.tabs(["📈 Trends", "🕸️ Skill Radar", "🤖 AI Analysis"])

    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["match_date"], y=df["runs"], name="Runs", mode="lines+markers", line=dict(color="#FFD166")))
        fig.add_trace(go.Scatter(x=df["match_date"], y=df["strike_rate"], name="Strike Rate", mode="lines+markers", line=dict(color="#4facfe")))
        fig.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           legend=dict(orientation="h"), height=380)
        st.plotly_chart(fig, use_container_width=True)

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df["match_date"], y=df["wickets"], name="Wickets", marker_color="#FF7A50"))
        fig2.add_trace(go.Scatter(x=df["match_date"], y=df["economy"], name="Economy", mode="lines+markers", yaxis="y2", line=dict(color="#43e97b")))
        fig2.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                            yaxis2=dict(overlaying="y", side="right"), legend=dict(orientation="h"), height=380)
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        categories = ["Batting", "Bowling", "Fielding", "Fitness", "Consistency"]
        bat_score = min(10, (df["runs"].mean() / 5)) if df["runs"].mean() else 3
        bowl_score = min(10, df["wickets"].sum())
        field_score = min(10, df["catches"].sum() + df["run_outs"].sum())
        consistency = min(10, 10 - df["runs"].std() / 10) if len(df) > 1 else 5
        values = [round(bat_score, 1), round(bowl_score, 1), round(field_score, 1), 6, round(max(consistency, 1), 1)]
        fig3 = go.Figure(data=go.Scatterpolar(r=values, theta=categories, fill="toself", line=dict(color="#FFD166")))
        fig3.update_layout(template="plotly_dark", polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                            paper_bgcolor="rgba(0,0,0,0)", height=400)
        st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        if st.button("🤖 Generate AI Performance Analysis", use_container_width=True):
            with st.spinner("Preparing the analysis..."):
                text, err = gc.generate_performance_analysis(st.session_state.groq_api_key, student, perf,
                                                                model=st.session_state.groq_model)
            if err:
                st.error(err)
            else:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown(text)
                st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# PAGE: Attendance
# ----------------------------------------------------------------------------
def page_attendance():
    page_header("✅", "Attendance")
    st.write("")

    students = db.get_students()
    if not students:
        st.info("No students registered.")
        return

    if st.session_state.auth_role in ("admin", "coach"):
        att_date = st.date_input("Date", value=date.today())
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f"#### Mark attendance — {att_date}")
        for s in students:
            existing = db.get_attendance(student_id=s["id"], att_date=str(att_date))
            current_status = existing[0]["status"] if existing else "Present"
            status = st.selectbox(s["name"], ["Present", "Absent", "Leave"],
                                    index=["Present", "Absent", "Leave"].index(current_status),
                                    key=f"att_{s['id']}_{att_date}")
            db.mark_attendance(s["id"], str(att_date), status)
        st.markdown("</div>", unsafe_allow_html=True)
        st.success("Attendance auto-saved ✅")

    st.markdown("#### 📊 Monthly Summary")
    student = pick_student(key="att_summary") if st.session_state.auth_role != "student" else current_student()
    if student:
        summary = db.attendance_summary(student["id"])
        if summary:
            fig = px.pie(values=list(summary.values()), names=list(summary.keys()), hole=0.5,
                         color_discrete_sequence=["#43e97b", "#ff5858", "#FFD166"])
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No attendance records yet.")


# ----------------------------------------------------------------------------
# PAGE: Reports (PDF / Excel)
# ----------------------------------------------------------------------------
def build_pdf_report(student, perf, injuries, diet_logs, workout_logs, coach_notes):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=18*mm, bottomMargin=18*mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleX", parent=styles["Title"], textColor=colors.HexColor("#1a1a2e"))
    h2 = ParagraphStyle("H2X", parent=styles["Heading2"], textColor=colors.HexColor("#c0392b"))
    normal = styles["Normal"]

    story = []
    story.append(Paragraph("🏏 Shree Shyam Cricket Academy", title_style))
    story.append(Paragraph("AI Performance & Fitness Report", styles["Heading3"]))
    story.append(Spacer(1, 10))

    info_data = [
        ["Name", student["name"], "Age", str(student["age"])],
        ["Role", student["role"], "Dominant Hand", student["dominant_hand"] or "-"],
        ["Height", f'{student["height_cm"]} cm', "Weight", f'{student["weight_kg"]} kg'],
        ["Batting Style", student["batting_style"] or "-", "Bowling Style", student["bowling_style"] or "-"],
        ["Contact", student["contact"] or "-", "Joined", student["join_date"]],
    ]
    t = Table(info_data, colWidths=[85, 140, 85, 140])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f0f0")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#f0f0f0")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))

    if perf:
        story.append(Paragraph("Match Performance", h2))
        rows = [["Date", "Runs", "Balls", "4s", "6s", "Overs", "Runs Con.", "Wkts", "Catches"]]
        for p in perf[-10:]:
            rows.append([p["match_date"], p["runs"], p["balls_faced"], p["fours"], p["sixes"],
                         p["overs_bowled"], p["runs_conceded"], p["wickets"], p["catches"]])
        pt = Table(rows, repeatRows=1)
        pt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ]))
        story.append(pt)
        story.append(Spacer(1, 14))

    if injuries:
        story.append(Paragraph("Injury History", h2))
        for inj in injuries[:8]:
            story.append(Paragraph(
                f"• {inj['body_part']} ({inj['severity']}) — {inj['status']} since {inj['injury_date']}: {inj['recovery_notes'] or ''}",
                normal))
        story.append(Spacer(1, 14))

    if diet_logs:
        story.append(Paragraph("Latest Diet Plan", h2))
        clean = diet_logs[0]["plan_text"].replace("#", "").replace("*", "")
        for line in clean.split("\n")[:40]:
            if line.strip():
                story.append(Paragraph(line.strip(), normal))
        story.append(Spacer(1, 14))

    if workout_logs:
        story.append(Paragraph("Latest Workout Plan", h2))
        clean = workout_logs[0]["plan_text"].replace("#", "").replace("*", "")
        for line in clean.split("\n")[:40]:
            if line.strip():
                story.append(Paragraph(line.strip(), normal))
        story.append(Spacer(1, 14))

    if coach_notes:
        story.append(Paragraph("Coach Remarks", h2))
        for n in coach_notes[:8]:
            story.append(Paragraph(f"• [{n['note_date']}] {n['coach_name']} (Rating {n['rating']}/10): {n['note']}", normal))

    doc.build(story)
    buf.seek(0)
    return buf


def page_reports():
    page_header("📄", "Report Generator")
    st.write("")

    if st.session_state.auth_role == "student":
        student = current_student()
    else:
        student = pick_student()
    if not student:
        return

    perf = db.get_performance(student["id"])
    injuries = db.get_injuries(student["id"])
    diet_logs = db.get_diet_logs(student["id"])
    workout_logs = db.get_workout_logs(student["id"])
    coach_notes = db.get_coach_notes(student_id=student["id"])

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write(f"Report ready for **{student['name']}** — includes profile, match performance, injuries, diet & workout plans, coach remarks.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📄 Generate PDF Report", use_container_width=True):
            pdf_buf = build_pdf_report(student, perf, injuries, diet_logs, workout_logs, coach_notes)
            st.download_button("⬇️ Download PDF", data=pdf_buf, file_name=f"{student['name']}_report.pdf",
                                mime="application/pdf", use_container_width=True)
    with c2:
        if st.button("📊 Export Excel (Performance)", use_container_width=True):
            if perf:
                df = pd.DataFrame(perf)
                excel_buf = io.BytesIO()
                with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Performance")
                excel_buf.seek(0)
                st.download_button("⬇️ Download Excel", data=excel_buf, file_name=f"{student['name']}_performance.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True)
            else:
                st.warning("No performance data available to export.")
    st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# PAGE: Leaderboard
# ----------------------------------------------------------------------------
def page_leaderboard():
    page_header("🏆", "Leaderboard", "The academy's top performers — based on match data.")
    st.write("")

    metric_labels = {
        "runs": "🏏 Most Runs", "wickets": "🎯 Most Wickets",
        "catches": "🧤 Most Catches", "fours": "🔥 Most Fours", "sixes": "💥 Most Sixes",
    }
    metric = st.selectbox("Category", list(metric_labels.keys()), format_func=lambda k: metric_labels[k])

    rows = db.get_leaderboard(metric=metric, limit=10)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    if not rows:
        st.info("No match performance data yet. Add it from the 'Match Performance & Analytics' page.")
    else:
        medals = ["🥇", "🥈", "🥉"]
        for i, r in enumerate(rows):
            rank_class = f"rank-{i+1}" if i < 3 else ""
            rank_display = medals[i] if i < 3 else f"#{i+1}"
            st.markdown(
                f'''<div class="leaderboard-row">
                        <div class="leaderboard-rank {rank_class}">{rank_display}</div>
                        <div class="leaderboard-name">{r["name"]} <span style="color:#8fb8a0;font-weight:400;font-size:12px;">({r["role"]})</span></div>
                        <div class="leaderboard-stat">{r["total"]}</div>
                    </div>''',
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# PAGE: Announcements
# ----------------------------------------------------------------------------
def page_announcements():
    page_header("📢", "Announcements", "Academy notices, match dates, and updates.")
    st.write("")

    role = st.session_state.auth_role
    if role in ("admin", "coach"):
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### ➕ Post a New Announcement")
        with st.form("new_announcement", clear_on_submit=True):
            title = st.text_input("Title *")
            message = st.text_area("Message", height=90)
            posted_by = st.session_state.coach_name if role == "coach" else "Admin"
            submitted = st.form_submit_button("📢 Post Announcement", use_container_width=True)
            if submitted:
                if not title.strip():
                    st.error("Title is required.")
                else:
                    db.add_announcement(title.strip(), message.strip(), posted_by)
                    st.success("Announcement post ho gaya!")
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 🗞️ All Announcements")
    anns = db.get_announcements(limit=30)
    if not anns:
        st.info("No announcements yet.")
    else:
        for a in anns:
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(
                    f'''<div class="announcement-item">
                            <div class="a-date">{a["post_date"]} · {a["posted_by"]}</div>
                            <div class="a-title">{a["title"]}</div>
                            <div>{a["message"] or ""}</div>
                        </div>''',
                    unsafe_allow_html=True,
                )
            with c2:
                if role in ("admin", "coach"):
                    if st.button("🗑️", key=f"del_ann_{a['id']}"):
                        db.delete_announcement(a["id"])
                        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# PAGE: Admin Panel
# ----------------------------------------------------------------------------
def page_admin_panel():
    page_header("⚙️", "Admin Panel")
    st.write("")

    tab1, tab2, tab3 = st.tabs(["💾 Backup / Restore", "👥 Users & Roles", "🗑️ Data Management"])

    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Database Backup")
        if os.path.exists(db.backup_path()):
            with open(db.backup_path(), "rb") as f:
                st.download_button("⬇️ Download Full Database Backup (.db)", data=f.read(),
                                    file_name=f"academy_backup_{date.today()}.db", use_container_width=True)
        st.caption("Save the backup file somewhere safe. To restore, rename this file to `academy.db`, replace it in the app folder, and restart the app.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Default Login Credentials")
        st.write(f"**Admin:** `{DEFAULT_ADMIN_USER}` / `{DEFAULT_ADMIN_PASS}`")
        for name, info in COACHES.items():
            st.write(f"**Coach ({name}):** password `{info['password']}`")
        st.write("**Student:** your Student ID (visible in Student Management) + PIN (default `1234`, changeable from there)")
        st.info("Make sure to change these passwords before deploying to production (at the top of `app.py`).")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Danger Zone")
        students = db.get_students()
        st.write(f"Total records: {len(students)} students")
        confirm = st.checkbox("I confirm that I want to delete all data")
        if st.button("🗑️ Reset Entire Database", disabled=not confirm):
            os.remove(db.backup_path())
            db.init_db()
            st.success("Database reset ho gaya.")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# PAGE: Fees Management
# ----------------------------------------------------------------------------
def page_fees_management():
    page_header("💰", "Fees Management")
    role = st.session_state.auth_role
    status_icon = {"Paid": "🟢", "Pending": "🟡", "Overdue": "🔴"}

    # ---------------- Student: read-only view of own fees ----------------
    if role == "student":
        student = current_student()
        if not student:
            return
        fees = db.get_fees(student["id"])
        pending = [f for f in fees if fee_effective_status(f) != "Paid"]
        if pending:
            overdue = [f for f in pending if fee_effective_status(f) == "Overdue"]
            if overdue:
                st.markdown(
                    f'<div class="glass-card" style="border-left:4px solid #e63946;">'
                    f'⚠️ <b>{len(overdue)} fee(s) OVERDUE!</b> Please contact the academy office as soon as possible.</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="glass-card" style="border-left:4px solid #f4a300;">'
                    f'🔔 <b>{len(pending)} fee(s) pending.</b></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.success("✅ No fees are pending. All clear!")

        st.write("")
        if not fees:
            st.info("No fee records yet.")
        else:
            for f in fees:
                eff = fee_effective_status(f)
                with st.expander(f"{status_icon[eff]} {f['month']} — ₹{f['amount']:.0f} — {eff}"):
                    st.write(f"**Due Date:** {f['due_date']}")
                    if f.get("paid_date"):
                        st.write(f"**Paid On:** {f['paid_date']}")
                    if f.get("notes"):
                        st.write(f"**Notes:** {f['notes']}")
        return

    # ---------------- Admin / Coach view ----------------
    is_admin = role == "admin"
    if is_admin:
        tab_all, tab_add, tab_remind = st.tabs(["📋 All Fees", "➕ Add / Generate Fees", "📧 Send Reminders"])
    else:
        (tab_all,) = st.tabs(["📋 All Fees"])

    with tab_all:
        all_fees = db.get_all_fees_with_student()
        if not all_fees:
            st.info("No fee records yet.")
        else:
            total_pending_amt = sum(f["amount"] or 0 for f in all_fees if fee_effective_status(f) != "Paid")
            overdue_cnt = len([f for f in all_fees if fee_effective_status(f) == "Overdue"])
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="metric-card"><h2>{len(all_fees)}</h2><p>Total Fee Records</p></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="metric-card"><h2>{overdue_cnt}</h2><p>Overdue</p></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="metric-card"><h2>₹{total_pending_amt:,.0f}</h2><p>Total Pending Amount</p></div>', unsafe_allow_html=True)

            st.write("")
            status_filter = st.selectbox("Status filter", ["All", "Pending", "Overdue", "Paid"])
            for f in all_fees:
                eff = fee_effective_status(f)
                if status_filter != "All" and eff != status_filter:
                    continue
                with st.expander(f"{status_icon[eff]} {f['student_name']} — {f['month']} — ₹{f['amount']:.0f} — {eff}"):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.write(f"**Due Date:** {f['due_date']}")
                        st.write(f"**Email:** {f.get('student_email') or '-'}  |  **Contact:** {f.get('student_contact') or '-'}")
                        if f.get("paid_date"):
                            st.write(f"**Paid On:** {f['paid_date']}")
                        if f.get("reminder_sent_date"):
                            st.caption(f"Last reminder sent: {f['reminder_sent_date']}")
                    with c2:
                        if is_admin and eff != "Paid":
                            if st.button("✅ Mark Paid", key=f"paid_{f['id']}"):
                                db.mark_fee_paid(f["id"])
                                st.rerun()
                        if eff != "Paid":
                            if st.button("📧 Send Reminder", key=f"remind_{f['id']}"):
                                body = ec.fee_reminder_email_body(
                                    {"name": f["student_name"]}, {**f, "_effective_status": eff}
                                )
                                ok, err = ec.send_email(
                                    st.session_state.smtp_email, st.session_state.smtp_app_password,
                                    f.get("student_email"), "Fees Reminder — Shree Shyam Cricket Academy", body
                                )
                                if ok:
                                    db.mark_reminder_sent(f["id"])
                                    st.success("Reminder email sent.")
                                else:
                                    st.error(err)
                        if eff != "Paid":
                            wa_text = wc.fee_reminder_whatsapp_text(f["student_name"], {**f, "_effective_status": eff})
                            wa_url = wc.wa_link(f.get("student_contact"), wa_text)
                            if wa_url:
                                st.link_button("🟢 WhatsApp Reminder", wa_url, use_container_width=True)
                            else:
                                st.caption("⚠️ Contact number missing/invalid — add it in Student Management.")
                        if is_admin:
                            if st.button("🗑️ Delete Record", key=f"delfee_{f['id']}"):
                                db.delete_fee(f["id"])
                                st.rerun()

    if is_admin:
        with tab_add:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### Single Fee Entry")
            student = pick_student(key="fee_single_student")
            c1, c2, c3 = st.columns(3)
            with c1:
                month = st.text_input("Month/Period (e.g. July 2026)", value=date.today().strftime("%B %Y"), key="fee_month_single")
            with c2:
                amount = st.number_input("Amount (₹)", 0.0, 100000.0, 1500.0, key="fee_amount_single")
            with c3:
                due_date_val = st.date_input("Due Date", value=date.today(), key="fee_due_single")
            if st.button("➕ Add Fee Record", key="add_fee_single") and student:
                db.add_fee({
                    "student_id": student["id"], "month": month, "amount": amount,
                    "due_date": str(due_date_val), "status": "Pending",
                })
                st.success(f"{month} fees added for {student['name']}.")
            st.markdown("</div>", unsafe_allow_html=True)

            st.write("")
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### 🔁 Bulk Generate for All Students (Monthly)")
            c1, c2, c3 = st.columns(3)
            with c1:
                bulk_month = st.text_input("Month/Period", value=date.today().strftime("%B %Y"), key="fee_month_bulk")
            with c2:
                bulk_amount = st.number_input("Amount (₹) per student", 0.0, 100000.0, 1500.0, key="fee_amount_bulk")
            with c3:
                bulk_due = st.date_input("Due Date", value=date.today() + timedelta(days=7), key="fee_due_bulk")
            if st.button("🔁 Generate for All Students", key="bulk_gen_fees"):
                students = db.get_students()
                created, skipped = 0, 0
                for s in students:
                    if db.fee_exists(s["id"], bulk_month):
                        skipped += 1
                        continue
                    db.add_fee({
                        "student_id": s["id"], "month": bulk_month, "amount": bulk_amount,
                        "due_date": str(bulk_due), "status": "Pending",
                    })
                    created += 1
                st.success(f"{bulk_month} fees created for {created} students. ({skipped} already existed.)")
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_remind:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### 📧 Bulk Fee Reminders")
            st.caption("Send reminder emails to all students with Pending/Overdue fees in one click "
                       "(via free Gmail SMTP — set up 'Email Settings' in the sidebar first).")
            all_fees = db.get_all_fees_with_student()
            due_list = [f for f in all_fees if fee_effective_status(f) != "Paid" and f.get("student_email")]
            no_email_list = [f for f in all_fees if fee_effective_status(f) != "Paid" and not f.get("student_email")]
            st.write(f"**{len(due_list)}** students can be emailed (email registered).")
            if no_email_list:
                missing_names = ", ".join(sorted(set(f["student_name"] for f in no_email_list)))
                st.warning(f"{len(no_email_list)} pending fee record(s) have no email registered — "
                           f"add it first in Student Management: {missing_names}")
            if st.button("📧 Send Reminder to All Pending/Overdue", disabled=not due_list):
                sent, failed = 0, 0
                for f in due_list:
                    eff = fee_effective_status(f)
                    body = ec.fee_reminder_email_body({"name": f["student_name"]}, {**f, "_effective_status": eff})
                    ok, err = ec.send_email(
                        st.session_state.smtp_email, st.session_state.smtp_app_password,
                        f.get("student_email"), "Fees Reminder — Shree Shyam Cricket Academy", body
                    )
                    if ok:
                        db.mark_reminder_sent(f["id"])
                        sent += 1
                    else:
                        failed += 1
                st.success(f"✅ {sent} reminder email(s) sent.")
                if failed:
                    st.error(f"❌ {failed} failed to send (check 'Email Settings' in the sidebar).")
            st.markdown("</div>", unsafe_allow_html=True)

            st.write("")
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### 🟢 Bulk WhatsApp Reminders (100% Free)")
            st.caption(
                "A single-click 'send all' is not possible on WhatsApp (WhatsApp itself requires every message to be "
                "sent manually — this is not a paid API/service, it's the fastest free method available). "
                "Below, each student has a 'Send' button — clicking it opens WhatsApp (mobile app / WhatsApp Web) "
                "with the message already typed in, you just need to tap Send."
            )
            wa_due_list = [f for f in all_fees if fee_effective_status(f) != "Paid"]
            wa_ok = [f for f in wa_due_list if wc.normalize_indian_number(f.get("student_contact"))]
            wa_missing = [f for f in wa_due_list if not wc.normalize_indian_number(f.get("student_contact"))]
            if wa_missing:
                missing_names = ", ".join(sorted(set(f["student_name"] for f in wa_missing)))
                st.warning(f"{len(wa_missing)} record(s) have a missing/invalid contact number: {missing_names}")
            if wa_ok:
                sel_names = st.multiselect(
                    "Choose who to send to (default: all)",
                    options=[f"{f['student_name']} — {f['month']} (₹{f['amount']:.0f})" for f in wa_ok],
                    default=[f"{f['student_name']} — {f['month']} (₹{f['amount']:.0f})" for f in wa_ok],
                    key="wa_bulk_select",
                )
                selected = [f for f in wa_ok
                            if f"{f['student_name']} — {f['month']} (₹{f['amount']:.0f})" in sel_names]

                if selected:
                    wa_urls = []
                    for f in selected:
                        eff = fee_effective_status(f)
                        wa_text = wc.fee_reminder_whatsapp_text(f["student_name"], {**f, "_effective_status": eff})
                        wa_urls.append(wc.wa_link(f["student_contact"], wa_text))
                    import json as _json
                    import streamlit.components.v1 as _components
                    urls_json = _json.dumps(wa_urls)
                    _components.html(f"""
                        <div style="font-family:'Poppins',sans-serif;">
                        <button id="wa-open-all" style="width:100%;padding:10px 16px;border:none;border-radius:10px;
                            background:linear-gradient(135deg,#25D366,#128C7E);color:white;font-weight:700;
                            font-size:14px;cursor:pointer;">
                            📲 Open All {len(wa_urls)} WhatsApp Chats (New Tabs)
                        </button>
                        <div id="wa-status" style="color:#7fa892;font-size:12px;margin-top:6px;"></div>
                        </div>
                        <script>
                        const waUrls = {urls_json};
                        document.getElementById('wa-open-all').addEventListener('click', function() {{
                            let i = 0;
                            const statusEl = document.getElementById('wa-status');
                            function openNext() {{
                                if (i >= waUrls.length) {{
                                    statusEl.innerText = 'Done! ' + waUrls.length + ' tab(s) opened — just tap Send in each tab.';
                                    return;
                                }}
                                window.open(waUrls[i], '_blank');
                                statusEl.innerText = 'Opening ' + (i+1) + ' / ' + waUrls.length + ' ... (if blocked, allow popups via the browser\'s popup icon)';
                                i++;
                                setTimeout(openNext, 600);
                            }}
                            openNext();
                        }});
                        </script>
                    """, height=80)
                    st.caption("⚠️ Your browser may block popups — if a popup-blocked icon appears in the address bar the first time, "
                               "choose 'Always allow popups from this site', then click the button again.")

                st.write("")
                for f in selected:
                    eff = fee_effective_status(f)
                    wa_text = wc.fee_reminder_whatsapp_text(f["student_name"], {**f, "_effective_status": eff})
                    wa_url = wc.wa_link(f["student_contact"], wa_text)
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.write(f"{status_icon[eff]} **{f['student_name']}** — {f['month']} — ₹{f['amount']:.0f} ({eff})")
                    with c2:
                        st.link_button("🟢 Send", wa_url, use_container_width=True)
            else:
                st.info("No pending/overdue fee records with a registered WhatsApp number.")
            st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# ROUTER
# ----------------------------------------------------------------------------
def main():
    if not st.session_state.auth_role:
        login_screen()
        return

    sidebar_nav()
    page = st.session_state.page

    page_map = {
        "Dashboard": page_dashboard,
        "Student Management": page_student_management,
        "Fees Management": page_fees_management,
        "AI Diet Planner": page_diet_planner,
        "AI Fitness & Workout": page_fitness_workout,
        "Position-Based Training": page_position_training,
        "Stretching & Recovery": page_stretching_recovery,
        "Exercise Library": page_exercise_library,
        "Coach Panel": page_coach_panel,
        "AI Chat Assistant": page_ai_chat,
        "Injury Prevention": page_injury_prevention,
        "Match Performance & Analytics": page_analytics,
        "🦸 SSCA Match Heroes": mh.page_match_heroes,
        "🔴 Live Match Center": lc.page_live_match_center,
        "📡 Live Scores": lc.page_live_scores_readonly,
        "Leaderboard": page_leaderboard,
        "Announcements": page_announcements,
        "Attendance": page_attendance,
        "Reports": page_reports,
        "Admin Panel": page_admin_panel,
    }
    fn = page_map.get(page, page_dashboard)
    fn()


if __name__ == "__main__":
    main()
