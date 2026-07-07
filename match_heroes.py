"""
match_heroes.py — SSCA Match Heroes
------------------------------------------------------------------------------
A full match-centric cricket module for Shree Shyam Cricket Academy, built in
the spirit of CricHeroes but tailored + extended for the academy:

  • Full match creation (opponent, venue, format, toss, result)
  • Ball-park scorecards — batting / bowling / fielding entry per player
  • Auto-computed career stats: average, strike rate, economy, best figures
  • "Hero Points" — a transparent, auto-calculated all-rounder rating engine
    that also auto-suggests the Player of the Match (CricHeroes doesn't show
    you the formula — we do, and it's editable by the coach)
  • Milestones Wall — centuries / fifties / 5-wicket hauls, auto-detected
  • Multi-metric leaderboard (runs, wickets, average, SR, economy, MOM, points)
  • Player profile card — a CricHeroes-style career summary

It shares the same academy.db SQLite file as the rest of the app (via db.py's
get_conn helper), so it plugs straight into the existing Student/Coach/Admin
system — no separate login, no separate database.
------------------------------------------------------------------------------
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date

import db

# ------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------
DISMISSALS = ["Not Out", "Bowled", "Caught", "LBW", "Run Out", "Stumped",
              "Hit Wicket", "Retired Hurt", "Did Not Bat"]
FORMATS = ["T20", "ODI (50 overs)", "T10", "Practice Match", "Multi-day"]
RESULTS = ["Won", "Lost", "Tied", "No Result", "Not Decided Yet"]
TOSS_DECISIONS = ["Bat", "Bowl"]


# ==========================================================================
# DB LAYER
# ==========================================================================

def init_mh_tables():
    """Creates the SSCA Match Heroes tables if they don't already exist."""
    conn = db.get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS mh_matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        opponent TEXT NOT NULL,
        venue TEXT,
        match_date TEXT,
        match_format TEXT,
        overs REAL,
        toss_winner TEXT,          -- 'SSCA' / 'Opponent'
        toss_decision TEXT,        -- 'Bat' / 'Bowl'
        our_score INTEGER DEFAULT 0,
        our_wickets INTEGER DEFAULT 0,
        opponent_score INTEGER DEFAULT 0,
        opponent_wickets INTEGER DEFAULT 0,
        result TEXT,
        margin TEXT,
        player_of_match_id INTEGER,
        notes TEXT,
        created_by TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS mh_batting (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        student_id INTEGER,
        position INTEGER DEFAULT 0,
        runs INTEGER DEFAULT 0,
        balls INTEGER DEFAULT 0,
        fours INTEGER DEFAULT 0,
        sixes INTEGER DEFAULT 0,
        dismissal TEXT DEFAULT 'Not Out',
        FOREIGN KEY(match_id) REFERENCES mh_matches(id) ON DELETE CASCADE,
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS mh_bowling (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        student_id INTEGER,
        overs REAL DEFAULT 0,
        maidens INTEGER DEFAULT 0,
        runs_conceded INTEGER DEFAULT 0,
        wickets INTEGER DEFAULT 0,
        FOREIGN KEY(match_id) REFERENCES mh_matches(id) ON DELETE CASCADE,
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS mh_fielding (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        student_id INTEGER,
        catches INTEGER DEFAULT 0,
        stumpings INTEGER DEFAULT 0,
        run_outs INTEGER DEFAULT 0,
        FOREIGN KEY(match_id) REFERENCES mh_matches(id) ON DELETE CASCADE,
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()


# ---------------- Matches ----------------

def add_match(data: dict):
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO mh_matches (opponent, venue, match_date, match_format, overs,
            toss_winner, toss_decision, our_score, our_wickets, opponent_score,
            opponent_wickets, result, margin, player_of_match_id, notes, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("opponent"), data.get("venue"), data.get("match_date", str(date.today())),
        data.get("match_format"), data.get("overs", 0), data.get("toss_winner"),
        data.get("toss_decision"), data.get("our_score", 0), data.get("our_wickets", 0),
        data.get("opponent_score", 0), data.get("opponent_wickets", 0),
        data.get("result"), data.get("margin", ""), data.get("player_of_match_id"),
        data.get("notes", ""), data.get("created_by", ""),
    ))
    conn.commit()
    mid = cur.lastrowid
    conn.close()
    return mid


def update_match(match_id, data: dict):
    conn = db.get_conn()
    cur = conn.cursor()
    fields = ", ".join([f"{k} = ?" for k in data.keys()])
    values = list(data.values()) + [match_id]
    cur.execute(f"UPDATE mh_matches SET {fields} WHERE id = ?", values)
    conn.commit()
    conn.close()


def delete_match(match_id):
    conn = db.get_conn()
    conn.execute("DELETE FROM mh_batting WHERE match_id = ?", (match_id,))
    conn.execute("DELETE FROM mh_bowling WHERE match_id = ?", (match_id,))
    conn.execute("DELETE FROM mh_fielding WHERE match_id = ?", (match_id,))
    conn.execute("DELETE FROM mh_matches WHERE id = ?", (match_id,))
    conn.commit()
    conn.close()


def get_matches():
    conn = db.get_conn()
    rows = conn.execute("SELECT * FROM mh_matches ORDER BY match_date DESC, id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_match(match_id):
    conn = db.get_conn()
    row = conn.execute("SELECT * FROM mh_matches WHERE id = ?", (match_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ---------------- Scorecard entries ----------------

def clear_scorecard(match_id):
    conn = db.get_conn()
    conn.execute("DELETE FROM mh_batting WHERE match_id = ?", (match_id,))
    conn.execute("DELETE FROM mh_bowling WHERE match_id = ?", (match_id,))
    conn.execute("DELETE FROM mh_fielding WHERE match_id = ?", (match_id,))
    conn.commit()
    conn.close()


def save_batting_row(match_id, student_id, position, runs, balls, fours, sixes, dismissal):
    conn = db.get_conn()
    conn.execute("""
        INSERT INTO mh_batting (match_id, student_id, position, runs, balls, fours, sixes, dismissal)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (match_id, student_id, position, runs, balls, fours, sixes, dismissal))
    conn.commit()
    conn.close()


def save_bowling_row(match_id, student_id, overs, maidens, runs_conceded, wickets):
    conn = db.get_conn()
    conn.execute("""
        INSERT INTO mh_bowling (match_id, student_id, overs, maidens, runs_conceded, wickets)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (match_id, student_id, overs, maidens, runs_conceded, wickets))
    conn.commit()
    conn.close()


def save_fielding_row(match_id, student_id, catches, stumpings, run_outs):
    conn = db.get_conn()
    conn.execute("""
        INSERT INTO mh_fielding (match_id, student_id, catches, stumpings, run_outs)
        VALUES (?, ?, ?, ?, ?)
    """, (match_id, student_id, catches, stumpings, run_outs))
    conn.commit()
    conn.close()


def get_scorecard(match_id):
    conn = db.get_conn()
    bat = conn.execute("""
        SELECT b.*, s.name FROM mh_batting b JOIN students s ON s.id = b.student_id
        WHERE b.match_id = ? ORDER BY b.position
    """, (match_id,)).fetchall()
    bowl = conn.execute("""
        SELECT bw.*, s.name FROM mh_bowling bw JOIN students s ON s.id = bw.student_id
        WHERE bw.match_id = ?
    """, (match_id,)).fetchall()
    field = conn.execute("""
        SELECT f.*, s.name FROM mh_fielding f JOIN students s ON s.id = f.student_id
        WHERE f.match_id = ?
    """, (match_id,)).fetchall()
    conn.close()
    return {
        "batting": [dict(r) for r in bat],
        "bowling": [dict(r) for r in bowl],
        "fielding": [dict(r) for r in field],
    }


# ---------------- Hero Points rating engine ----------------

def batting_points(runs, balls, dismissal):
    pts = runs * 1.0
    if runs >= 100:
        pts += 24
    elif runs >= 50:
        pts += 8
    if dismissal not in ("Not Out", "Did Not Bat") and runs == 0 and balls > 0:
        pts -= 4
    if balls >= 10:
        sr = runs / balls * 100
        if sr >= 150:
            pts += 6
        elif sr >= 130:
            pts += 4
        elif sr < 70:
            pts -= 4
    return round(pts, 1)


def bowling_points(overs, maidens, runs_conceded, wickets):
    pts = wickets * 20.0 + maidens * 4.0
    if wickets >= 5:
        pts += 20
    elif wickets >= 4:
        pts += 12
    elif wickets >= 3:
        pts += 8
    if overs and overs >= 2:
        econ = runs_conceded / overs
        if econ < 6:
            pts += 6
        elif econ > 10:
            pts -= 4
    return round(pts, 1)


def fielding_points(catches, stumpings, run_outs):
    return round(catches * 10 + stumpings * 12 + run_outs * 10, 1)


def match_hero_points(bat_row=None, bowl_row=None, field_row=None, is_mom=False):
    total = 0.0
    if bat_row:
        total += batting_points(bat_row.get("runs", 0), bat_row.get("balls", 0), bat_row.get("dismissal", "Not Out"))
    if bowl_row:
        total += bowling_points(bowl_row.get("overs", 0), bowl_row.get("maidens", 0),
                                 bowl_row.get("runs_conceded", 0), bowl_row.get("wickets", 0))
    if field_row:
        total += fielding_points(field_row.get("catches", 0), field_row.get("stumpings", 0), field_row.get("run_outs", 0))
    if is_mom:
        total += 25
    return round(total, 1)


def suggest_player_of_match(match_id):
    """Auto-suggests a Player of the Match based on Hero Points across all
    batting/bowling/fielding contributions in that match (coach can override)."""
    sc = get_scorecard(match_id)
    totals = {}
    for r in sc["batting"]:
        totals.setdefault(r["student_id"], {"name": r["name"], "pts": 0})
        totals[r["student_id"]]["pts"] += batting_points(r["runs"], r["balls"], r["dismissal"])
    for r in sc["bowling"]:
        totals.setdefault(r["student_id"], {"name": r["name"], "pts": 0})
        totals[r["student_id"]]["pts"] += bowling_points(r["overs"], r["maidens"], r["runs_conceded"], r["wickets"])
    for r in sc["fielding"]:
        totals.setdefault(r["student_id"], {"name": r["name"], "pts": 0})
        totals[r["student_id"]]["pts"] += fielding_points(r["catches"], r["stumpings"], r["run_outs"])
    if not totals:
        return None
    best_id = max(totals, key=lambda k: totals[k]["pts"])
    return {"student_id": best_id, "name": totals[best_id]["name"], "points": round(totals[best_id]["pts"], 1)}


# ---------------- Career stats & aggregation ----------------

def get_career_stats(student_id):
    conn = db.get_conn()
    bat_rows = [dict(r) for r in conn.execute(
        "SELECT * FROM mh_batting WHERE student_id = ?", (student_id,)).fetchall()]
    bowl_rows = [dict(r) for r in conn.execute(
        "SELECT * FROM mh_bowling WHERE student_id = ?", (student_id,)).fetchall()]
    field_rows = [dict(r) for r in conn.execute(
        "SELECT * FROM mh_fielding WHERE student_id = ?", (student_id,)).fetchall()]
    mom_count = conn.execute(
        "SELECT COUNT(*) as c FROM mh_matches WHERE player_of_match_id = ?", (student_id,)).fetchone()["c"]
    conn.close()

    match_ids = set(r["match_id"] for r in bat_rows) | set(r["match_id"] for r in bowl_rows) | \
        set(r["match_id"] for r in field_rows)

    innings = len(bat_rows)
    not_outs = sum(1 for r in bat_rows if r["dismissal"] in ("Not Out", "Retired Hurt"))
    total_runs = sum(r["runs"] for r in bat_rows)
    total_balls = sum(r["balls"] for r in bat_rows)
    highest_score = max([r["runs"] for r in bat_rows], default=0)
    hundreds = sum(1 for r in bat_rows if r["runs"] >= 100)
    fifties = sum(1 for r in bat_rows if 50 <= r["runs"] < 100)
    ducks = sum(1 for r in bat_rows if r["runs"] == 0 and r["dismissal"] not in ("Not Out", "Did Not Bat"))
    fours = sum(r["fours"] for r in bat_rows)
    sixes = sum(r["sixes"] for r in bat_rows)
    dismissals = innings - not_outs
    batting_avg = round(total_runs / dismissals, 2) if dismissals else (float(total_runs) if innings else 0)
    strike_rate = round(total_runs / total_balls * 100, 1) if total_balls else 0

    bowl_innings = len(bowl_rows)
    total_overs = sum(r["overs"] for r in bowl_rows)
    total_conceded = sum(r["runs_conceded"] for r in bowl_rows)
    total_wickets = sum(r["wickets"] for r in bowl_rows)
    best_bowling = max(bowl_rows, key=lambda r: (r["wickets"], -r["runs_conceded"]), default=None)
    best_bowling_str = f'{best_bowling["wickets"]}/{best_bowling["runs_conceded"]}' if best_bowling else "-"
    economy = round(total_conceded / total_overs, 2) if total_overs else 0
    bowling_avg = round(total_conceded / total_wickets, 2) if total_wickets else 0

    catches = sum(r["catches"] for r in field_rows)
    stumpings = sum(r["stumpings"] for r in field_rows)
    run_outs = sum(r["run_outs"] for r in field_rows)

    hero_points = 0.0
    for r in bat_rows:
        hero_points += batting_points(r["runs"], r["balls"], r["dismissal"])
    for r in bowl_rows:
        hero_points += bowling_points(r["overs"], r["maidens"], r["runs_conceded"], r["wickets"])
    for r in field_rows:
        hero_points += fielding_points(r["catches"], r["stumpings"], r["run_outs"])
    hero_points += mom_count * 25

    return {
        "matches": len(match_ids),
        "innings": innings, "not_outs": not_outs, "runs": total_runs, "highest_score": highest_score,
        "hundreds": hundreds, "fifties": fifties, "ducks": ducks, "fours": fours, "sixes": sixes,
        "batting_average": batting_avg, "strike_rate": strike_rate,
        "bowling_innings": bowl_innings, "overs": round(total_overs, 1), "wickets": total_wickets,
        "best_bowling": best_bowling_str, "economy": economy, "bowling_average": bowling_avg,
        "catches": catches, "stumpings": stumpings, "run_outs": run_outs,
        "mom_awards": mom_count, "hero_points": round(hero_points, 1),
    }


def get_all_players_leaderboard():
    """Returns career stats for every student that has at least one Match Heroes entry."""
    conn = db.get_conn()
    ids = set(r["student_id"] for r in conn.execute("SELECT DISTINCT student_id FROM mh_batting").fetchall())
    ids |= set(r["student_id"] for r in conn.execute("SELECT DISTINCT student_id FROM mh_bowling").fetchall())
    ids |= set(r["student_id"] for r in conn.execute("SELECT DISTINCT student_id FROM mh_fielding").fetchall())
    conn.close()
    rows = []
    for sid in ids:
        student = db.get_student(sid)
        if not student:
            continue
        stats = get_career_stats(sid)
        stats["student_id"] = sid
        stats["name"] = student["name"]
        stats["role"] = student.get("role", "")
        rows.append(stats)
    return rows


def get_milestones():
    """Wall of Fame: every century, fifty and 5-wicket haul, newest first."""
    conn = db.get_conn()
    centuries = conn.execute("""
        SELECT b.runs, b.balls, s.name, m.opponent, m.match_date, m.id as match_id
        FROM mh_batting b JOIN students s ON s.id = b.student_id
        JOIN mh_matches m ON m.id = b.match_id
        WHERE b.runs >= 100 ORDER BY m.match_date DESC
    """).fetchall()
    fifties = conn.execute("""
        SELECT b.runs, b.balls, s.name, m.opponent, m.match_date, m.id as match_id
        FROM mh_batting b JOIN students s ON s.id = b.student_id
        JOIN mh_matches m ON m.id = b.match_id
        WHERE b.runs >= 50 AND b.runs < 100 ORDER BY m.match_date DESC
    """).fetchall()
    five_wkts = conn.execute("""
        SELECT bw.wickets, bw.runs_conceded, bw.overs, s.name, m.opponent, m.match_date, m.id as match_id
        FROM mh_bowling bw JOIN students s ON s.id = bw.student_id
        JOIN mh_matches m ON m.id = bw.match_id
        WHERE bw.wickets >= 5 ORDER BY m.match_date DESC
    """).fetchall()
    conn.close()
    return {
        "centuries": [dict(r) for r in centuries],
        "fifties": [dict(r) for r in fifties],
        "five_wicket_hauls": [dict(r) for r in five_wkts],
    }


# ==========================================================================
# UI LAYER
# ==========================================================================

def _metric_card(value, label):
    st.markdown(f'<div class="metric-card"><h2>{value}</h2><p>{label}</p></div>', unsafe_allow_html=True)


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


def _player_card_html(rank, name, role, value, suffix=""):
    medals = ["🥇", "🥈", "🥉"]
    rank_class = f"rank-{rank}" if rank <= 3 else ""
    rank_display = medals[rank - 1] if rank <= 3 else f"#{rank}"
    return f'''<div class="leaderboard-row">
        <div class="leaderboard-rank {rank_class}">{rank_display}</div>
        <div class="leaderboard-name">{name} <span style="color:#8fb8a0;font-weight:400;font-size:12px;">({role})</span></div>
        <div class="leaderboard-stat">{value}{suffix}</div>
    </div>'''


# ---------------- Dashboard ----------------

def _tab_dashboard():
    _section_title("🦸", "SSCA Match Heroes", "Every match, every player's career-defining moment — auto-tracked.")

    matches = get_matches()
    players = get_all_players_leaderboard()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        _metric_card(len(matches), "Matches Recorded")
    with c2:
        top_scorer = max(players, key=lambda p: p["runs"], default=None)
        _metric_card(top_scorer["name"] if top_scorer else "-", "🏏 Top Run Scorer")
    with c3:
        top_bowler = max(players, key=lambda p: p["wickets"], default=None)
        _metric_card(top_bowler["name"] if top_bowler else "-", "🎯 Top Wicket Taker")
    with c4:
        top_hero = max(players, key=lambda p: p["hero_points"], default=None)
        _metric_card(top_hero["name"] if top_hero else "-", "⭐ #1 Hero Points")

    st.write("")
    st.markdown("#### 🕒 Recent Matches")
    if not matches:
        st.info("No matches recorded yet. Add your first match from the 'New Match' tab.")
        return

    for m in matches[:5]:
        result_emoji = {"Won": "✅", "Lost": "❌", "Tied": "🤝", "No Result": "⛅"}.get(m["result"], "🕓")
        mom = db.get_student(m["player_of_match_id"]) if m["player_of_match_id"] else None
        mom_line = f' · 🏅 MOM: **{mom["name"]}**' if mom else ""
        st.markdown(
            f'''<div class="glass-card">
                <b>SSCA vs {m["opponent"]}</b> — {m["match_format"] or ""} · {m["venue"] or "Venue N/A"}
                <br><span style="color:#8fb8a0;font-size:13px;">{m["match_date"]}</span>
                <br>{result_emoji} <b>{m["our_score"]}/{m["our_wickets"]}</b> vs <b>{m["opponent_score"]}/{m["opponent_wickets"]}</b>
                — {m["result"] or "Result pending"} {m["margin"] or ""}{mom_line}
            </div>''',
            unsafe_allow_html=True,
        )


# ---------------- New Match (create + scorecard entry) ----------------

def _tab_new_match(created_by):
    _section_title("🆕", "Create New Match", "Fill in the match details, then add the scorecard.")

    with st.form("mh_new_match_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            opponent = st.text_input("Opponent Team Name *")
            venue = st.text_input("Venue")
        with c2:
            match_date = st.date_input("Match Date", value=date.today())
            match_format = st.selectbox("Format", FORMATS)
        with c3:
            overs = st.number_input("Overs (per side)", 0.0, 100.0, 20.0, step=1.0)
            toss_winner = st.selectbox("Toss Won By", ["SSCA", "Opponent"])
        c4, c5, c6 = st.columns(3)
        with c4:
            toss_decision = st.selectbox("Chose To", TOSS_DECISIONS)
        with c5:
            our_score = st.number_input("Our Score", 0, 1000, 0)
            our_wickets = st.number_input("Our Wickets Lost", 0, 10, 0)
        with c6:
            opponent_score = st.number_input("Opponent Score", 0, 1000, 0)
            opponent_wickets = st.number_input("Opponent Wickets Lost", 0, 10, 0)
        c7, c8 = st.columns(2)
        with c7:
            result = st.selectbox("Result", RESULTS)
        with c8:
            margin = st.text_input("Margin (e.g. 'by 24 runs' / 'by 4 wickets')")
        notes = st.text_area("Match Notes (optional)", height=80)

        submitted = st.form_submit_button("➡️ Create Match & Add Scorecard", use_container_width=True)
        if submitted:
            if not opponent:
                st.error("Opponent team name is required.")
            else:
                mid = add_match({
                    "opponent": opponent, "venue": venue, "match_date": str(match_date),
                    "match_format": match_format, "overs": overs, "toss_winner": toss_winner,
                    "toss_decision": toss_decision, "our_score": our_score, "our_wickets": our_wickets,
                    "opponent_score": opponent_score, "opponent_wickets": opponent_wickets,
                    "result": result, "margin": margin, "notes": notes, "created_by": created_by,
                })
                st.session_state["mh_editing_match"] = mid
                st.success(f"Match #{mid} create ho gaya! Ab niche scorecard bharein.")
                st.rerun()

    if st.session_state.get("mh_editing_match"):
        st.markdown("---")
        _scorecard_editor(st.session_state["mh_editing_match"])


def _scorecard_editor(match_id):
    match = get_match(match_id)
    if not match:
        return
    st.markdown(f"#### 📋 Scorecard — SSCA vs {match['opponent']} ({match['match_date']})")

    students = db.get_students()
    if not students:
        st.warning("Please register players first from 'Student Management'.")
        return
    name_map = {f"{s['name']} (ID {s['id']})": s["id"] for s in students}

    tabs = st.tabs(["🏏 Batting", "🎯 Bowling", "🧤 Fielding", "🏅 Player of the Match"])

    with tabs[0]:
        st.caption("Add each player's batting entry.")
        with st.form(f"bat_form_{match_id}", clear_on_submit=True):
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            with c1:
                pos = st.number_input("Order", 1, 15, 1)
            with c2:
                player = st.selectbox("Player", list(name_map.keys()), key=f"bat_player_{match_id}")
            with c3:
                runs = st.number_input("Runs", 0, 500, 0, key=f"bat_runs_{match_id}")
            with c4:
                balls = st.number_input("Balls", 0, 500, 0, key=f"bat_balls_{match_id}")
            with c5:
                fours = st.number_input("4s", 0, 50, 0, key=f"bat_4s_{match_id}")
                sixes = st.number_input("6s", 0, 50, 0, key=f"bat_6s_{match_id}")
            with c6:
                dismissal = st.selectbox("Dismissal", DISMISSALS, key=f"bat_out_{match_id}")
            if st.form_submit_button("➕ Add Batting Entry"):
                save_batting_row(match_id, name_map[player], pos, runs, balls, fours, sixes, dismissal)
                st.success("Batting entry add ho gaya.")
                st.rerun()

        sc = get_scorecard(match_id)
        if sc["batting"]:
            df = pd.DataFrame(sc["batting"])[["name", "runs", "balls", "fours", "sixes", "dismissal"]]
            df.columns = ["Player", "Runs", "Balls", "4s", "6s", "Dismissal"]
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tabs[1]:
        st.caption("Add each bowler's figures.")
        with st.form(f"bowl_form_{match_id}", clear_on_submit=True):
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                player = st.selectbox("Player", list(name_map.keys()), key=f"bowl_player_{match_id}")
            with c2:
                overs = st.number_input("Overs", 0.0, 50.0, 0.0, step=0.1, key=f"bowl_overs_{match_id}")
            with c3:
                maidens = st.number_input("Maidens", 0, 20, 0, key=f"bowl_maidens_{match_id}")
            with c4:
                runs_c = st.number_input("Runs Conceded", 0, 300, 0, key=f"bowl_runs_{match_id}")
            with c5:
                wkts = st.number_input("Wickets", 0, 10, 0, key=f"bowl_wkts_{match_id}")
            if st.form_submit_button("➕ Add Bowling Entry"):
                save_bowling_row(match_id, name_map[player], overs, maidens, runs_c, wkts)
                st.success("Bowling entry add ho gaya.")
                st.rerun()

        sc = get_scorecard(match_id)
        if sc["bowling"]:
            df = pd.DataFrame(sc["bowling"])[["name", "overs", "maidens", "runs_conceded", "wickets"]]
            df["economy"] = (df["runs_conceded"] / df["overs"].replace(0, pd.NA)).fillna(0).round(2)
            df.columns = ["Player", "Overs", "Maidens", "Runs", "Wickets", "Economy"]
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tabs[2]:
        st.caption("Add catches, stumpings, and run outs.")
        with st.form(f"field_form_{match_id}", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                player = st.selectbox("Player", list(name_map.keys()), key=f"field_player_{match_id}")
            with c2:
                catches = st.number_input("Catches", 0, 10, 0, key=f"field_catches_{match_id}")
            with c3:
                stump = st.number_input("Stumpings", 0, 10, 0, key=f"field_stump_{match_id}")
            with c4:
                runout = st.number_input("Run Outs", 0, 10, 0, key=f"field_runout_{match_id}")
            if st.form_submit_button("➕ Add Fielding Entry"):
                save_fielding_row(match_id, name_map[player], catches, stump, runout)
                st.success("Fielding entry add ho gaya.")
                st.rerun()

        sc = get_scorecard(match_id)
        if sc["fielding"]:
            df = pd.DataFrame(sc["fielding"])[["name", "catches", "stumpings", "run_outs"]]
            df.columns = ["Player", "Catches", "Stumpings", "Run Outs"]
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tabs[3]:
        suggestion = suggest_player_of_match(match_id)
        if suggestion:
            st.info(f"🤖 Auto-suggested (highest Hero Points): **{suggestion['name']}** — {suggestion['points']} pts")
        options = ["-- Select --"] + list(name_map.keys())
        current_mom = None
        if match.get("player_of_match_id"):
            for label, sid in name_map.items():
                if sid == match["player_of_match_id"]:
                    current_mom = label
        idx = options.index(current_mom) if current_mom in options else 0
        chosen = st.selectbox("Player of the Match (final)", options, index=idx, key=f"mom_{match_id}")
        if st.button("🏅 Confirm Player of the Match", use_container_width=True):
            if chosen != "-- Select --":
                update_match(match_id, {"player_of_match_id": name_map[chosen]})
                st.success(f"{chosen.split(' (ID')[0]} set as Player of the Match!")
                st.rerun()

    st.markdown("---")
    if st.button("✅ Done — Close this match editor", use_container_width=True):
        st.session_state["mh_editing_match"] = None
        st.rerun()


# ---------------- All Matches ----------------

def _tab_all_matches(can_edit):
    _section_title("📋", "All Matches", "Full match history — expand to view the scorecard.")
    matches = get_matches()
    if not matches:
        st.info("No matches recorded yet.")
        return

    for m in matches:
        result_emoji = {"Won": "✅", "Lost": "❌", "Tied": "🤝", "No Result": "⛅"}.get(m["result"], "🕓")
        with st.expander(f"{result_emoji} SSCA vs {m['opponent']} — {m['match_date']} ({m['match_format']})"):
            st.write(f"**Venue:** {m['venue'] or 'N/A'}  |  **Toss:** {m['toss_winner']} chose to {m['toss_decision']}")
            st.write(f"**Score:** SSCA {m['our_score']}/{m['our_wickets']}  vs  {m['opponent']} {m['opponent_score']}/{m['opponent_wickets']}")
            st.write(f"**Result:** {m['result']} {m['margin'] or ''}")
            if m["player_of_match_id"]:
                mom = db.get_student(m["player_of_match_id"])
                if mom:
                    st.markdown(f"🏅 **Player of the Match: {mom['name']}**")
            if m["notes"]:
                st.caption(m["notes"])

            sc = get_scorecard(m["id"])
            if sc["batting"]:
                st.markdown("**🏏 Batting**")
                df = pd.DataFrame(sc["batting"])[["name", "runs", "balls", "fours", "sixes", "dismissal"]]
                df.columns = ["Player", "Runs", "Balls", "4s", "6s", "Dismissal"]
                st.dataframe(df, use_container_width=True, hide_index=True)
            if sc["bowling"]:
                st.markdown("**🎯 Bowling**")
                df = pd.DataFrame(sc["bowling"])[["name", "overs", "maidens", "runs_conceded", "wickets"]]
                df.columns = ["Player", "Overs", "Maidens", "Runs", "Wickets"]
                st.dataframe(df, use_container_width=True, hide_index=True)
            if sc["fielding"]:
                st.markdown("**🧤 Fielding**")
                df = pd.DataFrame(sc["fielding"])[["name", "catches", "stumpings", "run_outs"]]
                df.columns = ["Player", "Catches", "Stumpings", "Run Outs"]
                st.dataframe(df, use_container_width=True, hide_index=True)

            if can_edit:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✏️ Edit Scorecard", key=f"edit_{m['id']}", use_container_width=True):
                        st.session_state["mh_editing_match"] = m["id"]
                        st.info("Now go to the 'New Match' tab to edit the scorecard.")
                with c2:
                    if st.button("🗑️ Delete Match", key=f"del_{m['id']}", use_container_width=True):
                        delete_match(m["id"])
                        st.success("Match delete ho gaya.")
                        st.rerun()


# ---------------- Player Profile ----------------

def _tab_player_profile(default_student_id=None):
    _section_title("🧑\u200d🏏", "Player Profile", "CricHeroes-style career card — everything auto-calculated.")

    students = db.get_students()
    if not students:
        st.info("No students registered.")
        return
    name_map = {f"{s['name']} (ID {s['id']})": s["id"] for s in students}
    default_label = None
    if default_student_id:
        for label, sid in name_map.items():
            if sid == default_student_id:
                default_label = label
    labels = list(name_map.keys())
    idx = labels.index(default_label) if default_label in labels else 0
    choice = st.selectbox("Select Player", labels, index=idx)
    student_id = name_map[choice]
    student = db.get_student(student_id)
    stats = get_career_stats(student_id)

    st.markdown(
        f'''<div class="glass-card">
            <h3 style="margin:0;">🏏 {student["name"]}</h3>
            <span class="badge">{student.get("role") or "Player"}</span>
            <span class="badge badge-orange">⭐ {stats["hero_points"]} Hero Points</span>
            <span class="badge badge-green">🏅 {stats["mom_awards"]} MOM Awards</span>
        </div>''',
        unsafe_allow_html=True,
    )
    st.write("")

    st.markdown("##### 🏏 Batting")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: _metric_card(stats["matches"], "Matches")
    with c2: _metric_card(stats["runs"], "Runs")
    with c3: _metric_card(stats["highest_score"], "Highest")
    with c4: _metric_card(stats["batting_average"], "Average")
    with c5: _metric_card(stats["strike_rate"], "Strike Rate")
    with c6: _metric_card(f'{stats["hundreds"]}/{stats["fifties"]}', "100s/50s")

    st.markdown("##### 🎯 Bowling")
    c1, c2, c3, c4 = st.columns(4)
    with c1: _metric_card(stats["wickets"], "Wickets")
    with c2: _metric_card(stats["best_bowling"], "Best Figures")
    with c3: _metric_card(stats["economy"], "Economy")
    with c4: _metric_card(stats["bowling_average"], "Average")

    st.markdown("##### 🧤 Fielding")
    c1, c2, c3 = st.columns(3)
    with c1: _metric_card(stats["catches"], "Catches")
    with c2: _metric_card(stats["stumpings"], "Stumpings")
    with c3: _metric_card(stats["run_outs"], "Run Outs")

    # Skill radar — reuses the app's existing plotly-dark styling convention
    categories = ["Batting", "Power Hitting", "Bowling", "Fielding", "Consistency"]
    bat_score = min(10, stats["batting_average"] / 5) if stats["batting_average"] else 2
    power_score = min(10, (stats["fours"] + stats["sixes"] * 1.5) / 5) if (stats["fours"] or stats["sixes"]) else 2
    bowl_score = min(10, stats["wickets"] / 2) if stats["wickets"] else 2
    field_score = min(10, stats["catches"] + stats["stumpings"] + stats["run_outs"])
    consistency = min(10, stats["hero_points"] / (max(stats["matches"], 1) * 3)) if stats["matches"] else 2
    values = [round(bat_score, 1), round(power_score, 1), round(bowl_score, 1), round(field_score, 1), round(consistency, 1)]
    fig = go.Figure(data=go.Scatterpolar(r=values, theta=categories, fill="toself", line=dict(color="#FFD166")))
    fig.update_layout(template="plotly_dark", polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                       paper_bgcolor="rgba(0,0,0,0)", height=380)
    st.plotly_chart(fig, use_container_width=True)


# ---------------- Leaderboard ----------------

def _tab_leaderboard():
    _section_title("🏆", "Leaderboard", "The academy's top SSCA Match Heroes — across multiple categories.")
    players = get_all_players_leaderboard()
    if not players:
        st.info("No scorecard data yet.")
        return

    metric_labels = {
        "hero_points": "⭐ Hero Points (Overall Rating)",
        "runs": "🏏 Most Runs",
        "wickets": "🎯 Most Wickets",
        "batting_average": "📊 Best Batting Average",
        "strike_rate": "⚡ Best Strike Rate",
        "economy": "🛡️ Best Economy (lower is better)",
        "mom_awards": "🏅 Most Player of the Match Awards",
        "catches": "🧤 Most Catches",
    }
    metric = st.selectbox("Category", list(metric_labels.keys()), format_func=lambda k: metric_labels[k])

    reverse = metric != "economy"
    filtered = [p for p in players if not (metric == "economy" and p["overs"] == 0)]
    ranked = sorted(filtered, key=lambda p: p[metric], reverse=reverse)[:10]

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    if not ranked:
        st.info("No data available yet for this category.")
    else:
        for i, p in enumerate(ranked):
            st.markdown(_player_card_html(i + 1, p["name"], p["role"], p[metric]), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------- Milestones ----------------

def _tab_milestones():
    _section_title("⭐", "Milestones Wall of Fame", "Every century, fifty, and 5-wicket haul, auto-detected.")
    ms = get_milestones()

    st.markdown("##### 💯 Centuries")
    if not ms["centuries"]:
        st.caption("No centuries yet.")
    for r in ms["centuries"]:
        sr = round(r["runs"] / r["balls"] * 100, 1) if r["balls"] else 0
        st.markdown(f'''<div class="glass-card">🎉 <b>{r["name"]}</b> — {r["runs"]} ({r["balls"]} balls, SR {sr})
            vs {r["opponent"]} · {r["match_date"]}</div>''', unsafe_allow_html=True)

    st.markdown("##### 5⃣0⃣ Fifties")
    if not ms["fifties"]:
        st.caption("No fifties yet.")
    for r in ms["fifties"]:
        sr = round(r["runs"] / r["balls"] * 100, 1) if r["balls"] else 0
        st.markdown(f'''<div class="glass-card">👏 <b>{r["name"]}</b> — {r["runs"]} ({r["balls"]} balls, SR {sr})
            vs {r["opponent"]} · {r["match_date"]}</div>''', unsafe_allow_html=True)

    st.markdown("##### 🎯 5-Wicket Hauls")
    if not ms["five_wicket_hauls"]:
        st.caption("No 5-wicket hauls yet.")
    for r in ms["five_wicket_hauls"]:
        st.markdown(f'''<div class="glass-card">🔥 <b>{r["name"]}</b> — {r["wickets"]}/{r["runs_conceded"]}
            ({r["overs"]} overs) vs {r["opponent"]} · {r["match_date"]}</div>''', unsafe_allow_html=True)


# ---------------- Entry point (called from app.py) ----------------

def page_match_heroes():
    role = st.session_state.get("auth_role")
    is_staff = role in ("admin", "coach")

    if is_staff:
        tabs = st.tabs(["🏠 Dashboard", "🆕 New Match", "📋 All Matches", "🧑\u200d🏏 Player Profile", "🏆 Leaderboard", "⭐ Milestones"])
        with tabs[0]:
            _tab_dashboard()
        with tabs[1]:
            created_by = st.session_state.get("coach_name") or "Admin"
            _tab_new_match(created_by)
        with tabs[2]:
            _tab_all_matches(can_edit=True)
        with tabs[3]:
            _tab_player_profile()
        with tabs[4]:
            _tab_leaderboard()
        with tabs[5]:
            _tab_milestones()
    else:
        default_sid = st.session_state.get("student_id")
        tabs = st.tabs(["🏠 Dashboard", "📋 All Matches", "🧑\u200d🏏 My Profile", "🏆 Leaderboard", "⭐ Milestones"])
        with tabs[0]:
            _tab_dashboard()
        with tabs[1]:
            _tab_all_matches(can_edit=False)
        with tabs[2]:
            _tab_player_profile(default_student_id=default_sid)
        with tabs[3]:
            _tab_leaderboard()
        with tabs[4]:
            _tab_milestones()
