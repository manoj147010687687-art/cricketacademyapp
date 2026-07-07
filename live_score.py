"""
live_score.py — SSCA Live Match Center
------------------------------------------------------------------------------
A CricHeroes-style LIVE, ball-by-ball cricket scoring module for Shree Shyam
Cricket Academy — built to go a step further than CricHeroes:

  • Any two teams — not fixed to "SSCA vs Opponent". Works for academy
    matches, friendlies, tournaments AND corporate/company matches.
  • Admin (or Coach) creates the match and adds players to BOTH teams —
    academy students can be picked directly, or any outside/opponent/
    corporate player can be added by just typing their name.
  • True ball-by-ball live scoring: runs, wides, no-balls, byes, leg-byes,
    wickets (with dismissal type, batsman, fielder), automatic strike
    rotation, over completion, innings transition, target/required-run-rate,
    and final result computation — all done live, ball by ball.
  • A public, read-only Live Scoreboard that ANY user can see — including
    people who are NOT logged in at all (wired up from app.py via a
    ?live=1 URL query flag) — auto-refreshing, CricHeroes-style.

Shares the same academy.db SQLite file (via db.py's get_conn), so it plugs
straight into the existing Student/Coach/Admin system.
------------------------------------------------------------------------------
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime

import db
import weather_client as wx
import sound_fx as sfx

# ==========================================================================
# Constants
# ==========================================================================
MATCH_TYPES = ["Academy Match", "Corporate Match", "Friendly / Practice", "Tournament", "Local Tournament"]
TOSS_DECISIONS = ["Bat", "Bowl"]
EXTRA_TYPE_LABELS = ["Normal", "Wide", "No Ball", "Bye", "Leg Bye"]
DISMISSAL_NORMAL = ["Bowled", "Caught", "LBW", "Run Out", "Stumped", "Hit Wicket"]
DISMISSAL_WIDE = ["Run Out", "Stumped"]
DISMISSAL_RUNOUT_ONLY = ["Run Out"]
TEAM_EMOJIS = ["🏏", "🦁", "🐯", "🐘", "🦅", "🐺", "🔥", "⚡", "🛡️", "👑", "🐉", "🚀", "🏢", "⭐", "🦂", "🐍"]


def _fee_status_for_student(student_id):
    """Lightweight standalone version of app.py's fee_effective_status, kept
    here too so live_score.py doesn't need to import app.py (would be a
    circular import). Returns 'Paid' / 'Pending' / 'Overdue' / None (no fee record)."""
    if not student_id:
        return None
    fees = db.get_fees(student_id)
    if not fees:
        return None
    unpaid = [f for f in fees if f.get("status") != "Paid"]
    if not unpaid:
        return "Paid"
    worst = "Pending"
    for f in unpaid:
        try:
            due = datetime.strptime(f["due_date"], "%Y-%m-%d").date()
        except Exception:
            continue
        if due < date.today():
            worst = "Overdue"
            break
    return worst


def _fee_badge_html(status):
    if status is None:
        return ""
    cls = {"Paid": "fee-badge-paid", "Pending": "fee-badge-pending", "Overdue": "fee-badge-overdue"}.get(status, "")
    icon = {"Paid": "✅", "Pending": "🟡", "Overdue": "🔴"}.get(status, "")
    return f'<span class="fee-badge {cls}">{icon} Fees {status}</span>'


# ==========================================================================
# DB LAYER
# ==========================================================================

def init_lc_tables():
    conn = db.get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS lc_matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_a_name TEXT NOT NULL,
        team_b_name TEXT NOT NULL,
        match_type TEXT DEFAULT 'Academy Match',
        venue TEXT,
        match_date TEXT,
        overs_limit INTEGER DEFAULT 20,
        toss_winner TEXT,          -- 'A' / 'B'
        toss_decision TEXT,        -- 'Bat' / 'Bowl'
        batting_first TEXT,        -- 'A' / 'B'
        status TEXT DEFAULT 'Setup',   -- Setup / Live / Completed
        current_innings INTEGER DEFAULT 0,
        result_text TEXT,
        created_by TEXT,
        created_at TEXT
    )
    """)

    # ---- Migration: team emoji flair for the New Match / scoreboard screens ----
    existing_cols = {row["name"] for row in cur.execute("PRAGMA table_info(lc_matches)").fetchall()}
    for col, default in [("team_a_emoji", "'🏏'"), ("team_b_emoji", "'🏢'")]:
        if col not in existing_cols:
            cur.execute(f"ALTER TABLE lc_matches ADD COLUMN {col} TEXT DEFAULT {default}")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS lc_players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        team TEXT,                 -- 'A' / 'B'
        student_id INTEGER,        -- NULL if an outside/opponent/corporate player
        player_name TEXT NOT NULL,
        FOREIGN KEY(match_id) REFERENCES lc_matches(id) ON DELETE CASCADE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS lc_innings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        innings_no INTEGER,
        batting_team TEXT,          -- 'A' / 'B'
        bowling_team TEXT,
        opening_striker_id INTEGER,
        opening_non_striker_id INTEGER,
        opening_bowler_id INTEGER,
        status TEXT DEFAULT 'In Progress',   -- In Progress / Completed
        target INTEGER,
        FOREIGN KEY(match_id) REFERENCES lc_matches(id) ON DELETE CASCADE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS lc_balls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        innings_id INTEGER,
        bowler_id INTEGER,
        extra_type TEXT DEFAULT '',      -- '' / 'Wide' / 'No Ball' / 'Bye' / 'Leg Bye'
        runs_batsman INTEGER DEFAULT 0,
        extra_runs INTEGER DEFAULT 0,
        is_wicket INTEGER DEFAULT 0,
        wicket_type TEXT,
        out_player_id INTEGER,
        new_batsman_id INTEGER,
        fielder_id INTEGER,
        ts TEXT,
        FOREIGN KEY(innings_id) REFERENCES lc_innings(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()


# ---------------- Matches ----------------

def create_match(data: dict):
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO lc_matches (team_a_name, team_b_name, match_type, venue, match_date,
            overs_limit, status, created_by, created_at, team_a_emoji, team_b_emoji)
        VALUES (?, ?, ?, ?, ?, ?, 'Setup', ?, ?, ?, ?)
    """, (
        data["team_a_name"], data["team_b_name"], data.get("match_type", "Academy Match"),
        data.get("venue", ""), data.get("match_date", str(date.today())),
        data.get("overs_limit", 20), data.get("created_by", ""), datetime.now().isoformat(),
        data.get("team_a_emoji", "🏏"), data.get("team_b_emoji", "🏢"),
    ))
    conn.commit()
    mid = cur.lastrowid
    conn.close()
    return mid


def get_matches(status=None):
    conn = db.get_conn()
    if status:
        rows = conn.execute("SELECT * FROM lc_matches WHERE status = ? ORDER BY id DESC", (status,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM lc_matches ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_match(match_id):
    conn = db.get_conn()
    row = conn.execute("SELECT * FROM lc_matches WHERE id = ?", (match_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_match(match_id, data: dict):
    conn = db.get_conn()
    cur = conn.cursor()
    fields = ", ".join([f"{k} = ?" for k in data.keys()])
    values = list(data.values()) + [match_id]
    cur.execute(f"UPDATE lc_matches SET {fields} WHERE id = ?", values)
    conn.commit()
    conn.close()


def delete_match(match_id):
    conn = db.get_conn()
    inns = conn.execute("SELECT id FROM lc_innings WHERE match_id = ?", (match_id,)).fetchall()
    for i in inns:
        conn.execute("DELETE FROM lc_balls WHERE innings_id = ?", (i["id"],))
    conn.execute("DELETE FROM lc_innings WHERE match_id = ?", (match_id,))
    conn.execute("DELETE FROM lc_players WHERE match_id = ?", (match_id,))
    conn.execute("DELETE FROM lc_matches WHERE id = ?", (match_id,))
    conn.commit()
    conn.close()


# ---------------- Players / Playing XI ----------------

def add_player(match_id, team, player_name, student_id=None):
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO lc_players (match_id, team, student_id, player_name) VALUES (?, ?, ?, ?)",
                (match_id, team, student_id, player_name))
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid


def remove_player(player_id):
    conn = db.get_conn()
    conn.execute("DELETE FROM lc_players WHERE id = ?", (player_id,))
    conn.commit()
    conn.close()


def get_players(match_id, team=None):
    conn = db.get_conn()
    if team:
        rows = conn.execute("SELECT * FROM lc_players WHERE match_id = ? AND team = ? ORDER BY id",
                             (match_id, team)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM lc_players WHERE match_id = ? ORDER BY id", (match_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_players_dict(match_id):
    return {p["id"]: p for p in get_players(match_id)}


# ---------------- Innings ----------------

def start_innings(match_id, innings_no, batting_team, bowling_team,
                   opening_striker_id, opening_non_striker_id, opening_bowler_id, target=None):
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO lc_innings (match_id, innings_no, batting_team, bowling_team,
            opening_striker_id, opening_non_striker_id, opening_bowler_id, status, target)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'In Progress', ?)
    """, (match_id, innings_no, batting_team, bowling_team,
          opening_striker_id, opening_non_striker_id, opening_bowler_id, target))
    conn.commit()
    iid = cur.lastrowid
    conn.close()
    return iid


def get_innings_for_match(match_id):
    conn = db.get_conn()
    rows = conn.execute("SELECT * FROM lc_innings WHERE match_id = ? ORDER BY innings_no", (match_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def current_innings_for_match(match_id):
    inns = get_innings_for_match(match_id)
    for i in reversed(inns):
        if i["status"] == "In Progress":
            return i
    return inns[-1] if inns else None


def set_innings_status(innings_id, status):
    conn = db.get_conn()
    conn.execute("UPDATE lc_innings SET status = ? WHERE id = ?", (status, innings_id))
    conn.commit()
    conn.close()


# ---------------- Ball-by-ball ledger ----------------

def get_balls(innings_id):
    conn = db.get_conn()
    rows = conn.execute("SELECT * FROM lc_balls WHERE innings_id = ? ORDER BY id", (innings_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def record_ball(innings_id, bowler_id, extra_type, runs_batsman, extra_runs,
                 is_wicket, wicket_type=None, out_player_id=None, new_batsman_id=None, fielder_id=None):
    conn = db.get_conn()
    conn.execute("""
        INSERT INTO lc_balls (innings_id, bowler_id, extra_type, runs_batsman, extra_runs,
            is_wicket, wicket_type, out_player_id, new_batsman_id, fielder_id, ts)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (innings_id, bowler_id, extra_type, int(runs_batsman), int(extra_runs), int(is_wicket),
          wicket_type, out_player_id, new_batsman_id, fielder_id, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def undo_last_ball(innings_id):
    conn = db.get_conn()
    row = conn.execute("SELECT id FROM lc_balls WHERE innings_id = ? ORDER BY id DESC LIMIT 1",
                        (innings_id,)).fetchone()
    if row:
        conn.execute("DELETE FROM lc_balls WHERE id = ?", (row["id"],))
        conn.commit()
    conn.close()


# ---------------- The scoring engine: replay balls -> live state ----------------

def _ball_desc(b, et, runs_bat, extra_runs):
    if b["is_wicket"]:
        return "W"
    if et == "Wide":
        return f"Wd+{extra_runs - 1}" if extra_runs > 1 else "Wd"
    if et == "No Ball":
        return f"Nb+{runs_bat}" if runs_bat else "Nb"
    if et == "Bye":
        return f"{extra_runs}B"
    if et == "Leg Bye":
        return f"{extra_runs}LB"
    if runs_bat == 6:
        return "6"
    if runs_bat == 4:
        return "4"
    return str(runs_bat)


def _pill_class(desc):
    if desc == "W":
        return "pill-wicket"
    if desc.startswith("Wd"):
        return "pill-wide"
    if desc.startswith("Nb"):
        return "pill-nb"
    if desc.endswith("LB") or (desc.endswith("B") and desc[:-1].isdigit()):
        return "pill-bye"
    if desc == "6":
        return "pill-six"
    if desc == "4":
        return "pill-four"
    if desc == "0":
        return "pill-dot"
    return "pill-run"


def _render_ball_feed(feed, caption=None):
    """Colourful over-by-over ball pills (4=blue, 6=gold, W=red, dot=grey...)."""
    if caption:
        st.markdown(f"##### {caption}")
    if not feed:
        st.caption("—")
        return
    pills = "".join(f'<span class="ball-pill {_pill_class(d)}">{d}</span>' for d in feed)
    st.markdown(f'<div class="ball-pill-row">{pills}</div>', unsafe_allow_html=True)


def compute_innings_state(innings, players=None):
    """Replays every ball of an innings from the openers onward and derives
    the complete live state — score, overs, current striker/non-striker/
    bowler, batting & bowling cards, extras, fall of wickets. This is the
    single source of truth: nothing is cached, so 'Undo Last Ball' is just
    a delete + re-derive, with zero risk of the score drifting out of sync."""
    if players is None:
        players = get_players_dict(innings["match_id"])
    balls = get_balls(innings["id"])

    striker = innings["opening_striker_id"]
    non_striker = innings["opening_non_striker_id"]
    bowler = innings["opening_bowler_id"]

    balls_this_over = 0
    over_number = 0
    total_runs = 0
    total_wickets = 0
    extras = {"Wide": 0, "No Ball": 0, "Bye": 0, "Leg Bye": 0}
    bat_stats = {}
    bowl_stats = {}
    this_over_feed = []
    fall_of_wickets = []
    prev_over_bowler = None
    legal_count = 0
    last_wkt_runs = 0
    last_wkt_balls = 0

    def ensure_bat(pid):
        if pid not in bat_stats:
            bat_stats[pid] = {"runs": 0, "balls": 0, "fours": 0, "sixes": 0, "out": False, "dismissal": "Not Out"}

    def ensure_bowl(pid):
        if pid not in bowl_stats:
            bowl_stats[pid] = {"balls": 0, "runs": 0, "wickets": 0}

    ensure_bat(striker)
    ensure_bat(non_striker)
    ensure_bowl(bowler)

    for b in balls:
        et = b["extra_type"] or ""
        legal = et not in ("Wide", "No Ball")
        if legal:
            legal_count += 1
        this_bowler = b["bowler_id"] or bowler
        ensure_bowl(this_bowler)
        runs_bat = b["runs_batsman"] or 0
        extra_runs = b["extra_runs"] or 0

        total_runs += runs_bat + extra_runs
        if et in extras:
            extras[et] += extra_runs

        ensure_bat(striker)
        if et in ("", "No Ball"):
            bat_stats[striker]["runs"] += runs_bat
            if runs_bat == 4:
                bat_stats[striker]["fours"] += 1
            if runs_bat == 6:
                bat_stats[striker]["sixes"] += 1
        if et != "Wide":
            bat_stats[striker]["balls"] += 1

        bowl_conceded = runs_bat + (extra_runs if et in ("Wide", "No Ball") else 0)
        bowl_stats[this_bowler]["runs"] += bowl_conceded
        if legal:
            bowl_stats[this_bowler]["balls"] += 1

        this_over_feed.append(_ball_desc(b, et, runs_bat, extra_runs))

        if b["is_wicket"]:
            total_wickets += 1
            if b["wicket_type"] != "Run Out":
                bowl_stats[this_bowler]["wickets"] += 1
            out_id = b["out_player_id"] or striker
            ensure_bat(out_id)
            bat_stats[out_id]["out"] = True
            fielder_name = players.get(b["fielder_id"], {}).get("player_name") if b["fielder_id"] else None
            bowler_name = players.get(this_bowler, {}).get("player_name", "?")
            wt = b["wicket_type"] or "Out"
            if wt == "Run Out":
                how = "Run Out" + (f" ({fielder_name})" if fielder_name else "")
            elif wt == "Caught":
                how = f"c {fielder_name or '?'} b {bowler_name}"
            elif wt == "Stumped":
                how = f"st {fielder_name or '?'} b {bowler_name}"
            else:
                how = f"{wt} b {bowler_name}"
            bat_stats[out_id]["dismissal"] = how
            fall_of_wickets.append({
                "wicket_no": total_wickets, "runs": total_runs,
                "player": players.get(out_id, {}).get("player_name", "?"),
            })
            last_wkt_runs = total_runs
            last_wkt_balls = legal_count
            new_in = b["new_batsman_id"]
            if new_in:
                ensure_bat(new_in)
                if out_id == striker:
                    striker = new_in
                else:
                    non_striker = new_in
        else:
            if et == "":
                odd = runs_bat % 2 == 1
            elif et == "No Ball":
                odd = runs_bat % 2 == 1
            elif et == "Wide":
                odd = (extra_runs - 1) % 2 == 1
            else:  # Bye / Leg Bye
                odd = extra_runs % 2 == 1
            if odd:
                striker, non_striker = non_striker, striker

        bowler = this_bowler
        if legal:
            balls_this_over += 1
            if balls_this_over == 6:
                balls_this_over = 0
                prev_over_bowler = bowler
                over_number += 1
                striker, non_striker = non_striker, striker
                bowler = None
                this_over_feed = []

    legal_balls_total = over_number * 6 + balls_this_over
    run_rate = round(total_runs / (legal_balls_total / 6), 2) if legal_balls_total else 0.0
    partnership_runs = total_runs - last_wkt_runs
    partnership_balls = legal_count - last_wkt_balls

    return {
        "total_runs": total_runs, "total_wickets": total_wickets,
        "overs_display": f"{over_number}.{balls_this_over}",
        "legal_balls_total": legal_balls_total, "run_rate": run_rate,
        "extras": extras, "extras_total": sum(extras.values()),
        "striker": striker, "non_striker": non_striker, "bowler": bowler,
        "prev_over_bowler": prev_over_bowler,
        "bat_stats": bat_stats, "bowl_stats": bowl_stats,
        "this_over_feed": this_over_feed, "fall_of_wickets": fall_of_wickets,
        "partnership_runs": partnership_runs, "partnership_balls": partnership_balls,
        "target": innings.get("target"),
    }


def _finalize_match(match_id):
    match = get_match(match_id)
    inns = get_innings_for_match(match_id)
    players = get_players_dict(match_id)
    result_text = "Match Tied"
    if len(inns) >= 2 and inns[0]["status"] and inns[1]:
        s1 = compute_innings_state(inns[0], players)
        s2 = compute_innings_state(inns[1], players)
        team1_name = match["team_a_name"] if inns[0]["batting_team"] == "A" else match["team_b_name"]
        team2_name = match["team_a_name"] if inns[1]["batting_team"] == "A" else match["team_b_name"]
        xi2 = len(get_players(match_id, inns[1]["batting_team"]))
        if s2["total_runs"] > s1["total_runs"]:
            wickets_in_hand = max(xi2 - 1 - s2["total_wickets"], 0)
            result_text = f"{team2_name} won by {wickets_in_hand} wicket(s)"
        elif s1["total_runs"] > s2["total_runs"]:
            result_text = f"{team1_name} won by {s1['total_runs'] - s2['total_runs']} run(s)"
        else:
            result_text = "Match Tied"
    update_match(match_id, {"status": "Completed", "result_text": result_text})


# ==========================================================================
# UI LAYER
# ==========================================================================

def _section_title(emoji, title, sub=None):
    sub_html = f'<p>{sub}</p>' if sub else ""
    st.markdown(
        f'''<div class="section-head">
                <div class="sh-icon">{emoji}</div>
                <div class="sh-text"><h3>{title}</h3>{sub_html}</div>
            </div>
            <div class="page-divider"></div>''',
        unsafe_allow_html=True,
    )


def _match_label(m):
    tag = "🏢" if m["match_type"] == "Corporate Match" else "🏏"
    return f'{tag} {m["team_a_name"]} vs {m["team_b_name"]} — {m.get("match_date","")} ({m["status"]})'


# ---------------- Tab: New Match ----------------

def _tab_new_match(created_by):
    _section_title("🆕", "Create a New Live Match",
                    "Works between any two teams — academy, opponent, tournament, or corporate match, all supported. "
                    "Pick an emoji/mascot for each team — it will represent the team on the scoreboard 🎨")
    with st.form("lc_new_match_form"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 🅰️ Team A")
            team_a = st.text_input("Team A Name*", placeholder="e.g. Shree Shyam Cricket Academy")
            team_a_emoji = st.selectbox("Team A Mascot", TEAM_EMOJIS, index=0, key="team_a_emoji_pick")
            st.markdown(f'<div class="team-chip"><span class="chip-emoji">{team_a_emoji}</span> '
                        f'{team_a.strip() or "Team A"}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown("##### 🅱️ Team B")
            team_b = st.text_input("Team B Name*", placeholder="e.g. Opponent Academy / Company XYZ")
            team_b_emoji = st.selectbox("Team B Mascot", TEAM_EMOJIS, index=1, key="team_b_emoji_pick")
            st.markdown(f'<div class="team-chip"><span class="chip-emoji">{team_b_emoji}</span> '
                        f'{team_b.strip() or "Team B"}</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            match_type = st.selectbox("Match Type", MATCH_TYPES)
        with c2:
            match_date_val = st.date_input("Match Date", value=date.today())
        with c3:
            overs_limit = st.number_input("Overs (per innings)", min_value=1, max_value=50, value=20)
        venue = st.text_input("📍 Venue / Location", placeholder="e.g. Bahadurgarh, Haryana — used for live weather & map too")
        st.caption("🌦️ Once a venue is entered, its live weather and location will automatically appear on the scoreboard.")
        submitted = st.form_submit_button("✅ Create Match", use_container_width=True, type="primary")
        if submitted:
            if not team_a.strip() or not team_b.strip():
                st.error("Both team names are required.")
            else:
                mid = create_match({
                    "team_a_name": team_a.strip(), "team_b_name": team_b.strip(), "match_type": match_type,
                    "venue": venue.strip(), "match_date": str(match_date_val), "overs_limit": int(overs_limit),
                    "created_by": created_by, "team_a_emoji": team_a_emoji, "team_b_emoji": team_b_emoji,
                })
                st.session_state["lc_active_match"] = mid
                st.success("✅ Match created! Now go to the '👥 Playing XI' tab to add players for both teams.")
                st.rerun()


# ---------------- Tab: Playing XI ----------------

def _tab_playing_xi():
    _section_title("👥", "Playing XI — Both Teams",
                    "Select academy students directly, or add opponent/corporate team players by typing their names.")
    setup_matches = get_matches(status="Setup")
    if not setup_matches:
        st.info("Please create a match first in the '🆕 New Match' tab.")
        return

    labels = {_match_label(m): m["id"] for m in setup_matches}
    keys = list(labels.keys())
    default_mid = st.session_state.get("lc_active_match")
    idx = next((i for i, k in enumerate(keys) if labels[k] == default_mid), 0)
    choice = st.selectbox("Select Match", keys, index=idx)
    match_id = labels[choice]
    st.session_state["lc_active_match"] = match_id
    match = get_match(match_id)

    students = db.get_students()
    student_names = {s["name"]: s["id"] for s in students}

    col_a, col_b = st.columns(2)
    all_pending_names = []
    for col, team_key, team_name, emoji in [
        (col_a, "A", match["team_a_name"], match.get("team_a_emoji") or "🏏"),
        (col_b, "B", match["team_b_name"], match.get("team_b_emoji") or "🏢"),
    ]:
        with col:
            st.markdown(f'<div class="team-chip"><span class="chip-emoji">{emoji}</span> {team_name}</div>',
                        unsafe_allow_html=True)
            roster = get_players(match_id, team_key)
            for p in roster:
                fee_status = _fee_status_for_student(p.get("student_id"))
                if fee_status in ("Pending", "Overdue"):
                    all_pending_names.append(f"{p['player_name']} ({team_name})")
                cc1, cc2 = st.columns([4, 1])
                cc1.markdown(f"• {p['player_name']} {_fee_badge_html(fee_status)}", unsafe_allow_html=True)
                if cc2.button("✕", key=f"rm_{p['id']}"):
                    remove_player(p["id"])
                    st.rerun()
            st.caption(f"Total: {len(roster)} players")

            existing_ids = {p["student_id"] for p in roster if p["student_id"]}
            avail_students = [n for n, sid in student_names.items() if sid not in existing_ids]
            sel = st.multiselect(f"🎓 Add academy students", avail_students, key=f"ms_{team_key}_{match_id}")
            if st.button("➕ Add Selected Students", key=f"addsel_{team_key}_{match_id}", use_container_width=True):
                for n in sel:
                    add_player(match_id, team_key, n, student_id=student_names[n])
                st.rerun()

            custom_name = st.text_input("🌐 Or an outside / opponent / corporate player name", key=f"custom_{team_key}_{match_id}",
                                         placeholder="e.g. Rohit (Opponent) / Amit (Sales Team)")
            if st.button("➕ Add Custom Player", key=f"addcustom_{team_key}_{match_id}", use_container_width=True):
                if custom_name.strip():
                    add_player(match_id, team_key, custom_name.strip())
                    st.rerun()

    if match["match_type"] == "Corporate Match" and all_pending_names:
        st.markdown(
            f'<div class="glass-card" style="border-left:4px solid #e63946;">'
            f'⚠️ <b>Fees pending/overdue for these players:</b> {", ".join(all_pending_names)}. '
            f'Please check "Fees Management" before starting the match.</div>',
            unsafe_allow_html=True,
        )
    elif all_pending_names:
        st.warning(f"⚠️ Fees pending/overdue for these players: {', '.join(all_pending_names)}")

    st.write("")
    a_count, b_count = len(get_players(match_id, "A")), len(get_players(match_id, "B"))
    if a_count >= 2 and b_count >= 2:
        st.success("✅ Both teams are ready — now go to the '🪙 Toss & Start' tab to start the match.")
    else:
        st.warning("⚠️ Add at least 2 players to each team before starting the match.")


# ---------------- Tab: Toss & Start ----------------

def _tab_toss_start():
    _section_title("🪙", "Toss & Match Start", "Set the toss result, choose opening players, and make the match live.")

    # Matches still in Setup (toss not done yet) with full playing XI.
    setup_ready = [m for m in get_matches(status="Setup")
                   if len(get_players(m["id"], "A")) >= 2 and len(get_players(m["id"], "B")) >= 2]
    # Matches where toss is already done (status flipped to Live) but the
    # opening XI (innings 1) hasn't been started yet — these MUST stay
    # visible here too, otherwise they vanish right after toss confirm and
    # the "choose opening players" screen never shows up.
    live_awaiting_start = [m for m in get_matches(status="Live") if not get_innings_for_match(m["id"])]

    ready = setup_ready + live_awaiting_start
    if not ready:
        st.info("No match is ready yet. Please complete '👥 Playing XI' first.")
        return

    labels = {_match_label(m): m for m in ready}
    keys = list(labels.keys())
    default_mid = st.session_state.get("lc_toss_active_match")
    idx = next((i for i, k in enumerate(keys) if labels[k]["id"] == default_mid), 0)
    choice = st.selectbox("Select Match", keys, index=idx, key="lc_toss_match_choice")
    match = labels[choice]
    match_id = match["id"]
    st.session_state["lc_toss_active_match"] = match_id

    if match["status"] == "Setup":
        with st.form(f"lc_toss_form_{match_id}"):
            toss_winner_name = st.selectbox("Toss Jeeta", [match["team_a_name"], match["team_b_name"]])
            toss_decision = st.selectbox("Decision", TOSS_DECISIONS)
            submitted = st.form_submit_button("🚀 Confirm Toss & Proceed", use_container_width=True)
            if submitted:
                toss_winner = "A" if toss_winner_name == match["team_a_name"] else "B"
                batting_first = toss_winner if toss_decision == "Bat" else ("B" if toss_winner == "A" else "A")
                update_match(match_id, {
                    "toss_winner": toss_winner, "toss_decision": toss_decision,
                    "batting_first": batting_first, "status": "Live", "current_innings": 1,
                })
                st.session_state["lc_toss_active_match"] = match_id
                st.rerun()

    match = get_match(match_id)
    if match["status"] == "Live" and not get_innings_for_match(match_id):
        batting_first = match["batting_first"]
        team_a_players = get_players(match_id, "A")
        team_b_players = get_players(match_id, "B")
        batting_players = team_a_players if batting_first == "A" else team_b_players
        bowling_players = team_b_players if batting_first == "A" else team_a_players
        bat_team_name = match["team_a_name"] if batting_first == "A" else match["team_b_name"]

        st.markdown(f"**{bat_team_name}** batting first. Select opening players:")
        p_names = {p["player_name"]: p["id"] for p in batting_players}
        b_names = {p["player_name"]: p["id"] for p in bowling_players}
        c1, c2, c3 = st.columns(3)
        striker_name = c1.selectbox("Striker", list(p_names.keys()), key=f"open_striker_{match_id}")
        ns_opts = [n for n in p_names if n != striker_name]
        non_striker_name = c2.selectbox("Non-Striker", ns_opts, key=f"open_nonstriker_{match_id}")
        bowler_name = c3.selectbox("Opening Bowler", list(b_names.keys()), key=f"open_bowler_{match_id}")
        if st.button("🏏 Begin Innings 1", key=f"begin_inn_{match_id}", use_container_width=True, type="primary"):
            start_innings(match_id, 1, batting_first, "B" if batting_first == "A" else "A",
                          p_names[striker_name], p_names[non_striker_name], b_names[bowler_name])
            st.success("Innings 1 has started! Now go to the '🔴 Live Scoring' tab to add ball-by-ball scores.")
            st.rerun()


# ---------------- Tab: Live Scoring ----------------

def _tab_live_scoring():
    _section_title("🔴", "Live Scoring", "Enter the score ball-by-ball — everyone sees it live instantly, even without logging in.")
    live_matches = get_matches(status="Live")
    if not live_matches:
        st.info("No match is currently live.")
        return

    labels = {_match_label(m): m for m in live_matches}
    choice = st.selectbox("Select Live Match", list(labels.keys()), key="lc_scoring_match_choice")
    match = labels[choice]
    match_id = match["id"]

    innings = current_innings_for_match(match_id)
    if not innings:
        st.warning("This match's innings hasn't started. Check the '🪙 Toss & Start' tab.")
        return

    players = get_players_dict(match_id)
    state = compute_innings_state(innings, players)
    bat_team_name = match["team_a_name"] if innings["batting_team"] == "A" else match["team_b_name"]
    bowl_team_name = match["team_b_name"] if innings["batting_team"] == "A" else match["team_a_name"]
    batting_players = get_players(match_id, innings["batting_team"])
    bowling_players = get_players(match_id, innings["bowling_team"])
    xi_count = len(batting_players)

    _render_scoreboard_header(match, innings, state, players, bat_team_name, bowl_team_name)

    pending_fx_key = f"lc_fx_{innings['id']}"
    pending_event = st.session_state.pop(pending_fx_key, None)
    if pending_event:
        sfx.render_event_fx(pending_event)

    if innings["status"] == "Completed":
        st.info("This innings has already been completed.")
        _innings_transition_controls(match, innings)
        _render_live_scorecards(state, players, batting_players, bowling_players)
        return

    all_out = state["total_wickets"] >= max(xi_count - 1, 1)
    overs_done = state["legal_balls_total"] >= match["overs_limit"] * 6
    target_chased = bool(innings.get("target")) and state["total_runs"] >= innings["target"]
    if all_out or overs_done or target_chased:
        reason = "All Out" if all_out else ("Overs Complete" if overs_done else "🎯 Target Achieved")
        st.success(f"🏁 Innings Over — {reason}!")
        set_innings_status(innings["id"], "Completed")
        _innings_transition_controls(match, innings)
        _render_live_scorecards(state, players, batting_players, bowling_players)
        return

    st.markdown("---")
    st.markdown("##### ⚡ Add a New Ball")

    bowl_names = {p["player_name"]: p["id"] for p in bowling_players}
    ball_key_base = f"ball_{innings['id']}_{len(get_balls(innings['id']))}"

    bowler_default_name = players.get(state["bowler"], {}).get("player_name") if state["bowler"] else None
    bowler_options = list(bowl_names.keys())
    bowler_idx = bowler_options.index(bowler_default_name) if bowler_default_name in bowler_options else 0
    if state["bowler"] is None and state.get("prev_over_bowler"):
        prev_name = players.get(state["prev_over_bowler"], {}).get("player_name")
        st.caption(f"⚠️ New over — {prev_name} bowled the previous over. (The same bowler cannot bowl consecutive overs.)")

    c1, c2 = st.columns(2)
    with c1:
        bowler_name = st.selectbox("Bowler", bowler_options, index=bowler_idx, key=f"{ball_key_base}_bowler")
    with c2:
        extra_type_label = st.selectbox("Ball Type", EXTRA_TYPE_LABELS, key=f"{ball_key_base}_extype")

    extra_type_db = "" if extra_type_label == "Normal" else extra_type_label
    runs_batsman, extra_runs = 0, 0

    c1, c2 = st.columns(2)
    if extra_type_label == "Normal":
        with c1:
            runs_batsman = st.number_input("Runs off bat", min_value=0, max_value=6, value=0, key=f"{ball_key_base}_runs")
    elif extra_type_label == "No Ball":
        with c1:
            runs_batsman = st.number_input("Runs off bat (no ball par)", min_value=0, max_value=6, value=0, key=f"{ball_key_base}_runs")
        with c2:
            st.info("Penalty: +1 run (extra, automatic)")
        extra_runs = 1
    elif extra_type_label == "Wide":
        with c1:
            extra_runs = st.number_input("Total runs is wide par", min_value=1, max_value=7, value=1, key=f"{ball_key_base}_wideruns")
    else:  # Bye / Leg Bye
        with c1:
            extra_runs = st.number_input("Runs taken", min_value=1, max_value=6, value=1, key=f"{ball_key_base}_byeruns")

    is_wicket = st.checkbox("🎯 Is ball par wicket gira?", key=f"{ball_key_base}_wicket")

    wicket_type = out_player_id = new_batsman_id = fielder_id = None
    if is_wicket:
        if extra_type_label == "Normal":
            options = DISMISSAL_NORMAL
        elif extra_type_label == "Wide":
            options = DISMISSAL_WIDE
        else:
            options = DISMISSAL_RUNOUT_ONLY
        wicket_type = st.selectbox("Dismissal Type", options, key=f"{ball_key_base}_wtype")

        striker_name = players.get(state["striker"], {}).get("player_name", "Striker")
        nonstriker_name = players.get(state["non_striker"], {}).get("player_name", "Non-Striker")
        who_out_label = st.selectbox("Who Got Out?", [striker_name, nonstriker_name], key=f"{ball_key_base}_whoout")
        out_player_id = state["striker"] if who_out_label == striker_name else state["non_striker"]

        available_next = [p for p in batting_players
                           if p["id"] not in (state["striker"], state["non_striker"])
                           and not state["bat_stats"].get(p["id"], {}).get("out")]
        if available_next:
            next_bat_name = st.selectbox("New Batsman", [p["player_name"] for p in available_next], key=f"{ball_key_base}_nextbat")
            new_batsman_id = next(p["id"] for p in available_next if p["player_name"] == next_bat_name)
        else:
            st.info("No other batsman is available — this will be the last wicket (All Out).")

        if wicket_type in ("Caught", "Stumped", "Run Out"):
            fielder_name = st.selectbox("Fielder / Keeper (optional)", ["-- None --"] + list(bowl_names.keys()),
                                         key=f"{ball_key_base}_fielder")
            fielder_id = bowl_names.get(fielder_name)

    bc1, bc2, bc3 = st.columns([2, 1, 1])
    with bc1:
        if st.button("✅ Add Ball", type="primary", use_container_width=True, key=f"{ball_key_base}_submit"):
            record_ball(innings["id"], bowl_names[bowler_name], extra_type_db, runs_batsman, extra_runs,
                        is_wicket, wicket_type, out_player_id, new_batsman_id, fielder_id)
            event_key = sfx.classify_ball_event(extra_type_label, runs_batsman, is_wicket)
            st.session_state[f"lc_fx_{innings['id']}"] = event_key
            st.rerun()
    with bc2:
        if st.button("↩️ Undo Last Ball", use_container_width=True, key=f"undo_{innings['id']}"):
            undo_last_ball(innings["id"])
            st.rerun()
    with bc3:
        if st.button("🏁 End Innings", use_container_width=True, key=f"endinn_{innings['id']}"):
            set_innings_status(innings["id"], "Completed")
            st.rerun()

    _render_ball_feed(state["this_over_feed"], caption="📺 This Over")

    _render_live_scorecards(state, players, batting_players, bowling_players)


def _innings_transition_controls(match, innings):
    match_id = match["id"]
    if innings["innings_no"] == 1:
        if st.button("▶️ Start 2nd Innings", type="primary", key=f"start2_{match_id}"):
            st.session_state["lc_start_2nd"] = match_id
        if st.session_state.get("lc_start_2nd") == match_id:
            players = get_players_dict(match_id)
            state = compute_innings_state(innings, players)
            target = state["total_runs"] + 1
            batting_team = innings["bowling_team"]
            bowling_team = innings["batting_team"]
            bat_players = get_players(match_id, batting_team)
            bowl_players = get_players(match_id, bowling_team)
            p_names = {p["player_name"]: p["id"] for p in bat_players}
            b_names = {p["player_name"]: p["id"] for p in bowl_players}
            st.info(f"🎯 Target: **{target}** runs to win")
            c1, c2, c3 = st.columns(3)
            striker_name = c1.selectbox("Striker", list(p_names.keys()), key=f"s2_striker_{match_id}")
            ns_opts = [n for n in p_names if n != striker_name]
            ns_name = c2.selectbox("Non-Striker", ns_opts, key=f"s2_ns_{match_id}")
            bowler_name = c3.selectbox("Opening Bowler", list(b_names.keys()), key=f"s2_bowler_{match_id}")
            if st.button("🏏 Begin Innings 2", key=f"begin2_{match_id}", use_container_width=True, type="primary"):
                start_innings(match_id, 2, batting_team, bowling_team,
                              p_names[striker_name], p_names[ns_name], b_names[bowler_name], target=target)
                update_match(match_id, {"current_innings": 2})
                st.session_state.pop("lc_start_2nd", None)
                st.rerun()
    else:
        if st.button("🏆 Complete Match", type="primary", key=f"complete_{match_id}", use_container_width=True):
            _finalize_match(match_id)
            st.session_state[f"lc_win_fx_{match_id}"] = True
            st.rerun()


# ---------------- Shared scoreboard rendering (used live + public + read-only) ----------------

def _render_scoreboard_header(match, innings, state, players, bat_team_name, bowl_team_name):
    tag = "🏢 Corporate Match" if match["match_type"] == "Corporate Match" else match["match_type"]
    live_dot = '<span class="live-dot"></span>' if match["status"] == "Live" else ""

    prev_line = ""
    if innings["innings_no"] == 2:
        first = next((i for i in get_innings_for_match(match["id"]) if i["innings_no"] == 1), None)
        if first:
            fstate = compute_innings_state(first, players)
            fname = match["team_a_name"] if first["batting_team"] == "A" else match["team_b_name"]
            prev_line = (f'<div class="prev-inns">1st Innings: {fname} {fstate["total_runs"]}/'
                         f'{fstate["total_wickets"]} ({fstate["overs_display"]} ov)</div>')

    target_line = ""
    if innings.get("target"):
        need = max(innings["target"] - state["total_runs"], 0)
        balls_left = match["overs_limit"] * 6 - state["legal_balls_total"]
        rrr = round(need / (balls_left / 6), 2) if balls_left > 0 else 0
        target_line = (f'<div class="subline">🎯 Target {innings["target"]} · Need '
                        f'<b>{need}</b> off <b>{balls_left}</b> balls · RRR <b>{rrr}</b></div>')

    emoji_a = match.get("team_a_emoji") or "🏏"
    emoji_b = match.get("team_b_emoji") or "🏢"
    venue_bits = " · ".join(x for x in [match.get("venue"), match.get("match_date")] if x)
    st.markdown(
        f'''<div class="score-hero">
            <div class="teams">{live_dot}{tag} · {emoji_a} {match["team_a_name"]} vs {emoji_b} {match["team_b_name"]}</div>
            <div class="venue">{venue_bits}</div>
            <p class="bigscore">{bat_team_name} {state["total_runs"]}/{state["total_wickets"]}</p>
            <div class="oversline">({state["overs_display"]} overs) · CRR {state["run_rate"]}</div>
            {target_line}
            {prev_line}
        </div>''',
        unsafe_allow_html=True,
    )
    wx.render_weather_strip(match.get("venue"))

    # ---- Creative progress strip: overs used, and run-chase progress if 2nd innings ----
    overs_limit = match.get("overs_limit") or 1
    balls_total_limit = overs_limit * 6
    overs_pct = min(100, round(state["legal_balls_total"] / balls_total_limit * 100)) if balls_total_limit else 0
    bars_html = f'''<div class="progress-wrap">
        <div class="progress-label"><span>Overs Used</span><span>{state["overs_display"]} / {overs_limit}</span></div>
        <div class="progress-track"><div class="progress-fill" style="width:{overs_pct}%;"></div></div>
    </div>'''
    if innings.get("target"):
        target = innings["target"]
        chase_pct = min(100, round(state["total_runs"] / target * 100)) if target else 0
        need = max(target - state["total_runs"], 0)
        balls_left = balls_total_limit - state["legal_balls_total"]
        fill_cls = "progress-fill-chase"
        if balls_left > 0:
            rrr = need / (balls_left / 6)
            if rrr > (state["run_rate"] or 0) + 3:
                fill_cls = "progress-fill-danger"
        bars_html += f'''<div class="progress-wrap">
            <div class="progress-label"><span>Chase Progress</span><span>{state["total_runs"]} / {target}</span></div>
            <div class="progress-track"><div class="progress-fill {fill_cls}" style="width:{chase_pct}%;"></div></div>
        </div>'''
    st.markdown(bars_html, unsafe_allow_html=True)

    st.write("")
    striker = state["bat_stats"].get(state["striker"], {})
    nons = state["bat_stats"].get(state["non_striker"], {})
    bowl = state["bowl_stats"].get(state["bowler"], {}) if state["bowler"] else {}
    c1, c2, c3 = st.columns(3)
    with c1:
        name = players.get(state["striker"], {}).get("player_name", "-")
        st.markdown(f'<div class="metric-card"><h2>{striker.get("runs",0)} ({striker.get("balls",0)})</h2>'
                    f'<p>🏏 {name} *</p></div>', unsafe_allow_html=True)
    with c2:
        name = players.get(state["non_striker"], {}).get("player_name", "-")
        st.markdown(f'<div class="metric-card"><h2>{nons.get("runs",0)} ({nons.get("balls",0)})</h2>'
                    f'<p>🏏 {name}</p></div>', unsafe_allow_html=True)
    with c3:
        bowler_label = players.get(state["bowler"], {}).get("player_name", "TBD") if state["bowler"] else "TBD"
        ob = bowl.get("balls", 0)
        st.markdown(f'<div class="metric-card"><h2>{bowl.get("wickets",0)}/{bowl.get("runs",0)} ({ob//6}.{ob%6})</h2>'
                    f'<p>🎯 {bowler_label}</p></div>', unsafe_allow_html=True)
    if state.get("partnership_balls", 0) > 0 or state.get("partnership_runs", 0) > 0:
        st.caption(f'🤝 Partnership: **{state["partnership_runs"]}** runs off **{state["partnership_balls"]}** balls')


def _render_live_scorecards(state, players, batting_players, bowling_players):
    st.markdown("##### 🏏 Batting")
    rows = []
    for p in batting_players:
        bs = state["bat_stats"].get(p["id"])
        if not bs:
            continue
        sr = round(bs["runs"] / bs["balls"] * 100, 1) if bs["balls"] else 0
        status = "Not Out" if not bs["out"] else bs["dismissal"]
        marker = " *" if p["id"] in (state["striker"], state["non_striker"]) and not bs["out"] else ""
        rows.append({"Player": p["player_name"] + marker, "R": bs["runs"], "B": bs["balls"],
                     "4s": bs["fours"], "6s": bs["sixes"], "SR": sr, "Status": status})
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.caption("No batsman has come to the crease yet.")

    st.markdown("##### 🎯 Bowling")
    rows = []
    for p in bowling_players:
        bs = state["bowl_stats"].get(p["id"])
        if not bs:
            continue
        econ = round(bs["runs"] / (bs["balls"] / 6), 2) if bs["balls"] else 0
        rows.append({"Bowler": p["player_name"], "O": f'{bs["balls"]//6}.{bs["balls"]%6}',
                     "R": bs["runs"], "W": bs["wickets"], "Econ": econ})
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if state["extras_total"]:
        e = state["extras"]
        st.caption(f'Extras: {state["extras_total"]} (WD {e["Wide"]}, NB {e["No Ball"]}, B {e["Bye"]}, LB {e["Leg Bye"]})')
    if state["fall_of_wickets"]:
        fow = ", ".join(f'{w["wicket_no"]}-{w["runs"]} ({w["player"]})' for w in state["fall_of_wickets"])
        st.caption(f"Fall of Wickets: {fow}")


# ---------------- Public / read-only Live Scoreboard ----------------

def _render_match_public_card(m):
    tag = "🏢 Corporate Match" if m["match_type"] == "Corporate Match" else m["match_type"]
    inns = get_innings_for_match(m["id"])
    players = get_players_dict(m["id"])
    is_live = m["status"] == "Live"
    live_dot = '<span class="live-dot"></span>' if is_live else ""
    header = f'{"🔴 " if is_live else ""}{m["team_a_name"]} vs {m["team_b_name"]} · {tag} · {m.get("venue") or ""}'
    with st.expander(header, expanded=is_live):
        if not inns:
            st.caption("Match hasn't started yet — waiting for the toss.")
            return

        venue_bits = " · ".join(x for x in [m.get("venue"), m.get("match_date")] if x)
        score_lines = ""
        for innings in reversed(inns):
            state = compute_innings_state(innings, players)
            bat_name = m["team_a_name"] if innings["batting_team"] == "A" else m["team_b_name"]
            tgt = f' · Target {innings["target"]}' if innings.get("target") else ""
            cls = "bigscore" if innings["id"] == inns[-1]["id"] else "prev-inns"
            tagname = "p" if cls == "bigscore" else "div"
            score_lines += (f'<{tagname} class="{cls}">{bat_name} {state["total_runs"]}/{state["total_wickets"]} '
                            f'<span style="font-size:14px;">({state["overs_display"]} ov)</span>'
                            f'{"" if cls=="bigscore" else ""}</{tagname}>')
            if cls == "bigscore":
                score_lines += f'<div class="oversline">CRR {state["run_rate"]}{tgt}</div>'

        emoji_a = m.get("team_a_emoji") or "🏏"
        emoji_b = m.get("team_b_emoji") or "🏢"
        st.markdown(f'''<div class="score-hero">
                <div class="teams">{live_dot}{tag} · {emoji_a} {m["team_a_name"]} vs {emoji_b} {m["team_b_name"]}</div>
                <div class="venue">{venue_bits}</div>
                {score_lines}
            </div>''', unsafe_allow_html=True)
        if is_live:
            wx.render_weather_strip(m.get("venue"))

        if m["status"] == "Completed" and m.get("result_text"):
            st.success(f'🏆 {m["result_text"]}')
            if st.session_state.pop(f"lc_win_fx_{m['id']}", None):
                sfx.render_event_fx("win")

        latest = inns[-1]
        state = compute_innings_state(latest, players)
        bat_players = get_players(m["id"], latest["batting_team"])
        bowl_players = get_players(m["id"], latest["bowling_team"])
        if latest["status"] != "Completed":
            _render_ball_feed(state["this_over_feed"], caption="📺 This Over")
        _render_live_scorecards(state, players, bat_players, bowl_players)


def render_public_board(standalone=False):
    """Renders the full live scoreboard. Used both for the true public,
    no-login route (standalone=True, auto-refreshing) and inside the
    logged-in app as a read-only tab."""
    live = get_matches(status="Live")
    completed = get_matches(status="Completed")

    if standalone:
        if live:
            # Auto-refresh only while a match is actually live — no point
            # reloading a static page when nothing is happening. 5s is the
            # closest a plain web page can get to "refresh only when a ball
            # is bowled" without a persistent server connection (websocket),
            # which a simple hosted Streamlit app doesn't have.
            st.markdown('<meta http-equiv="refresh" content="5">', unsafe_allow_html=True)
        st.markdown(f'<div class="hero-title">{"🔴 " if live else ""}SSCA Live Match Center</div>', unsafe_allow_html=True)
        if live:
            st.markdown('<div class="hero-sub">Match is live — the score refreshes automatically every 5 seconds.</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="hero-sub">No match is live right now. It will appear here instantly once a match starts.</div>',
                        unsafe_allow_html=True)
        st.markdown(f'<p class="live-updated-caption">🕐 Last updated: {datetime.now().strftime("%H:%M:%S")}</p>',
                    unsafe_allow_html=True)
        st.write("")
    else:
        if st.button("🔄 Refresh Now", key="lc_manual_refresh"):
            st.rerun()
        st.caption(f'🕐 Last updated: {datetime.now().strftime("%H:%M:%S")}')

    st.markdown("### 🔴 Live Now")
    if live:
        for m in live:
            _render_match_public_card(m)
    else:
        st.info("No match is currently live.")

    if completed:
        st.markdown("### ✅ Recent Results")
        for m in completed[:15]:
            _render_match_public_card(m)

    corp = [m for m in (live + completed) if m["match_type"] == "Corporate Match"]
    if corp:
        with st.expander(f"🏢 Corporate Matches ({len(corp)})"):
            for m in corp:
                _render_match_public_card(m)


# ---------------- History tab ----------------

def _tab_history():
    _section_title("📜", "Match History", "All completed matches — with the full scorecard.")
    completed = get_matches(status="Completed")
    if not completed:
        st.info("No matches have been completed yet.")
        return
    for m in completed:
        _render_match_public_card(m)
        if st.session_state.get("auth_role") == "admin":
            if st.button("🗑️ Delete Match", key=f"del_lc_{m['id']}"):
                delete_match(m["id"])
                st.rerun()


# ---------------- Entry points (called from app.py) ----------------

def page_live_match_center():
    """Full admin/coach control center: create matches, set playing XI,
    toss, live ball-by-ball scoring — plus the same live board everyone sees."""
    created_by = st.session_state.get("coach_name") or "Admin"
    tabs = st.tabs(["📡 Live Scores", "🆕 New Match", "👥 Playing XI", "🪙 Toss & Start", "🔴 Live Scoring", "📜 History"])
    with tabs[0]:
        render_public_board()
    with tabs[1]:
        _tab_new_match(created_by)
    with tabs[2]:
        _tab_playing_xi()
    with tabs[3]:
        _tab_toss_start()
    with tabs[4]:
        _tab_live_scoring()
    with tabs[5]:
        _tab_history()


def page_live_scores_readonly():
    """Read-only live scores page for students inside the logged-in app."""
    render_public_board()


def login_teaser():
    """A compact, good-looking teaser for the login page — shows a live
    score preview if a match is currently live, otherwise a simple call to
    action. Clicking always jumps straight to the public board, no login."""
    live = get_matches(status="Live")
    if live:
        m = live[0]
        inns = get_innings_for_match(m["id"])
        extra = f" +{len(live)-1} more live" if len(live) > 1 else ""
        if inns:
            players = get_players_dict(m["id"])
            state = compute_innings_state(inns[-1], players)
            bat_name = m["team_a_name"] if inns[-1]["batting_team"] == "A" else m["team_b_name"]
            score_html = f'{bat_name} {state["total_runs"]}/{state["total_wickets"]} ({state["overs_display"]} ov)'
        else:
            score_html = "Toss is done — match is about to begin"
        st.markdown(
            f'''<div class="live-mini-card">
                <div class="teams"><span class="live-dot"></span>{m["team_a_name"]} vs {m["team_b_name"]}{extra}</div>
                <div class="score">{score_html}</div>
            </div>''',
            unsafe_allow_html=True,
        )
        label = "🔴 View Full Live Scorecard"
    else:
        label = "📡 View Live Match Center (No Login Required)"

    if st.button(label, use_container_width=True, type="primary", key="login_live_teaser_btn"):
        st.query_params["live"] = "1"
        st.rerun()
    #st.caption("Or simply share this URL with anyone: **your-app-url** + `?live=1`")


def public_live_page():
    """The true no-login public page — wired up in app.py via a ?live=1 URL flag."""
    if st.button("⬅ Login Page par Wapas Jaayein"):
        st.query_params.clear()
        st.rerun()
    render_public_board(standalone=True)
