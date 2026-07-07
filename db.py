"""
db.py — SQLite data layer for Shree Shyam Cricket Academy AI Suite
All database setup and CRUD helper functions live here.
"""

import sqlite3
import os
from datetime import date, datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "academy.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        height_cm REAL,
        weight_kg REAL,
        role TEXT,                 -- Batsman / Bowler / All Rounder / Wicket Keeper
        dominant_hand TEXT,        -- Right / Left
        batting_style TEXT,
        bowling_style TEXT,
        contact TEXT,
        injury_history TEXT,
        join_date TEXT,
        photo_path TEXT,
        pin TEXT DEFAULT '1234'
    )
    """)

    # ---- Migration: add email column to students (for diet-plan / fee emails) ----
    cols = [r[1] for r in cur.execute("PRAGMA table_info(students)").fetchall()]
    if "email" not in cols:
        cur.execute("ALTER TABLE students ADD COLUMN email TEXT")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS fees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        month TEXT,                 -- e.g. "July 2026"
        amount REAL DEFAULT 0,
        due_date TEXT,
        paid_date TEXT,
        status TEXT DEFAULT 'Pending',   -- Pending / Paid (Overdue is computed, not stored)
        payment_mode TEXT,
        notes TEXT,
        reminder_sent_date TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        att_date TEXT,
        status TEXT,               -- Present / Absent / Leave
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
        UNIQUE(student_id, att_date)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        match_date TEXT,
        runs INTEGER DEFAULT 0,
        balls_faced INTEGER DEFAULT 0,
        fours INTEGER DEFAULT 0,
        sixes INTEGER DEFAULT 0,
        overs_bowled REAL DEFAULT 0,
        runs_conceded INTEGER DEFAULT 0,
        wickets INTEGER DEFAULT 0,
        catches INTEGER DEFAULT 0,
        run_outs INTEGER DEFAULT 0,
        notes TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS injuries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        body_part TEXT,
        injury_date TEXT,
        severity TEXT,
        status TEXT,               -- Active / Recovering / Recovered
        recovery_notes TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS diet_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        log_date TEXT,
        diet_type TEXT,
        goal TEXT,
        plan_text TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS workout_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        log_date TEXT,
        goal TEXT,
        plan_text TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS coach_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        coach_name TEXT,
        note TEXT,
        rating INTEGER,
        note_date TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        sender TEXT,               -- user / ai
        message TEXT,
        ts TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        message TEXT,
        posted_by TEXT,
        post_date TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------------- Students ----------------

def add_student(data: dict):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO students (name, age, height_cm, weight_kg, role, dominant_hand,
            batting_style, bowling_style, contact, email, injury_history, join_date, photo_path, pin)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name"), data.get("age"), data.get("height_cm"), data.get("weight_kg"),
        data.get("role"), data.get("dominant_hand"), data.get("batting_style"),
        data.get("bowling_style"), data.get("contact"), data.get("email"), data.get("injury_history"),
        data.get("join_date", str(date.today())), data.get("photo_path"),
        data.get("pin", "1234")
    ))
    conn.commit()
    sid = cur.lastrowid
    conn.close()
    return sid


def update_student(student_id, data: dict):
    conn = get_conn()
    cur = conn.cursor()
    fields = ", ".join([f"{k} = ?" for k in data.keys()])
    values = list(data.values()) + [student_id]
    cur.execute(f"UPDATE students SET {fields} WHERE id = ?", values)
    conn.commit()
    conn.close()


def delete_student(student_id):
    conn = get_conn()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()


def get_students():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM students ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_student(student_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_students_by_role(role):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM students WHERE role = ? ORDER BY name", (role,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------- Attendance ----------------

def mark_attendance(student_id, att_date, status):
    conn = get_conn()
    conn.execute("""
        INSERT INTO attendance (student_id, att_date, status) VALUES (?, ?, ?)
        ON CONFLICT(student_id, att_date) DO UPDATE SET status = excluded.status
    """, (student_id, att_date, status))
    conn.commit()
    conn.close()


def get_attendance(student_id=None, att_date=None):
    conn = get_conn()
    q = "SELECT * FROM attendance WHERE 1=1"
    params = []
    if student_id:
        q += " AND student_id = ?"
        params.append(student_id)
    if att_date:
        q += " AND att_date = ?"
        params.append(att_date)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def attendance_summary(student_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT status, COUNT(*) as cnt FROM attendance WHERE student_id = ? GROUP BY status
    """, (student_id,)).fetchall()
    conn.close()
    return {r["status"]: r["cnt"] for r in rows}


# ---------------- Performance ----------------

def add_performance(data: dict):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO performance (student_id, match_date, runs, balls_faced, fours, sixes,
            overs_bowled, runs_conceded, wickets, catches, run_outs, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("student_id"), data.get("match_date", str(date.today())),
        data.get("runs", 0), data.get("balls_faced", 0), data.get("fours", 0),
        data.get("sixes", 0), data.get("overs_bowled", 0), data.get("runs_conceded", 0),
        data.get("wickets", 0), data.get("catches", 0), data.get("run_outs", 0),
        data.get("notes", "")
    ))
    conn.commit()
    conn.close()


def get_performance(student_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM performance WHERE student_id = ? ORDER BY match_date", (student_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------- Injuries ----------------

def add_injury(data: dict):
    conn = get_conn()
    conn.execute("""
        INSERT INTO injuries (student_id, body_part, injury_date, severity, status, recovery_notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data.get("student_id"), data.get("body_part"), data.get("injury_date", str(date.today())),
        data.get("severity"), data.get("status", "Active"), data.get("recovery_notes", "")
    ))
    conn.commit()
    conn.close()


def get_injuries(student_id=None):
    conn = get_conn()
    if student_id:
        rows = conn.execute("SELECT * FROM injuries WHERE student_id = ? ORDER BY injury_date DESC", (student_id,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM injuries ORDER BY injury_date DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_injury_status(injury_id, status, recovery_notes=None):
    conn = get_conn()
    if recovery_notes is not None:
        conn.execute("UPDATE injuries SET status = ?, recovery_notes = ? WHERE id = ?",
                     (status, recovery_notes, injury_id))
    else:
        conn.execute("UPDATE injuries SET status = ? WHERE id = ?", (status, injury_id))
    conn.commit()
    conn.close()


# ---------------- Diet & Workout logs ----------------

def save_diet_log(student_id, diet_type, goal, plan_text):
    conn = get_conn()
    conn.execute("""
        INSERT INTO diet_logs (student_id, log_date, diet_type, goal, plan_text)
        VALUES (?, ?, ?, ?, ?)
    """, (student_id, str(date.today()), diet_type, goal, plan_text))
    conn.commit()
    conn.close()


def get_diet_logs(student_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM diet_logs WHERE student_id = ? ORDER BY log_date DESC", (student_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_workout_log(student_id, goal, plan_text):
    conn = get_conn()
    conn.execute("""
        INSERT INTO workout_logs (student_id, log_date, goal, plan_text)
        VALUES (?, ?, ?, ?)
    """, (student_id, str(date.today()), goal, plan_text))
    conn.commit()
    conn.close()


def get_workout_logs(student_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM workout_logs WHERE student_id = ? ORDER BY log_date DESC", (student_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------- Coach notes ----------------

def add_coach_note(student_id, coach_name, note, rating):
    conn = get_conn()
    conn.execute("""
        INSERT INTO coach_notes (student_id, coach_name, note, rating, note_date)
        VALUES (?, ?, ?, ?, ?)
    """, (student_id, coach_name, note, rating, str(date.today())))
    conn.commit()
    conn.close()


def get_coach_notes(student_id=None, coach_name=None):
    conn = get_conn()
    q = "SELECT * FROM coach_notes WHERE 1=1"
    params = []
    if student_id:
        q += " AND student_id = ?"
        params.append(student_id)
    if coach_name:
        q += " AND coach_name = ?"
        params.append(coach_name)
    q += " ORDER BY note_date DESC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------- Chat history ----------------

def save_chat(student_id, sender, message):
    conn = get_conn()
    conn.execute("""
        INSERT INTO chat_history (student_id, sender, message, ts) VALUES (?, ?, ?, ?)
    """, (student_id, sender, message, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_chat_history(student_id, limit=50):
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM chat_history WHERE student_id = ? ORDER BY id DESC LIMIT ?
    """, (student_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]


# ---------------- Announcements ----------------

def add_announcement(title, message, posted_by):
    conn = get_conn()
    conn.execute("""
        INSERT INTO announcements (title, message, posted_by, post_date) VALUES (?, ?, ?, ?)
    """, (title, message, posted_by, datetime.now().strftime("%d %b %Y, %I:%M %p")))
    conn.commit()
    conn.close()


def get_announcements(limit=20):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM announcements ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_announcement(ann_id):
    conn = get_conn()
    conn.execute("DELETE FROM announcements WHERE id = ?", (ann_id,))
    conn.commit()
    conn.close()


# ---------------- Leaderboard ----------------

def get_leaderboard(metric="runs", limit=10):
    """metric: 'runs', 'wickets', 'catches', 'fours', 'sixes'"""
    conn = get_conn()
    col = metric if metric in ("runs", "wickets", "catches", "fours", "sixes") else "runs"
    rows = conn.execute(f"""
        SELECT s.id, s.name, s.role, SUM(p.{col}) as total
        FROM students s JOIN performance p ON p.student_id = s.id
        GROUP BY s.id ORDER BY total DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------- Fees ----------------

def add_fee(data: dict):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO fees (student_id, month, amount, due_date, paid_date, status, payment_mode, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("student_id"), data.get("month"), data.get("amount", 0),
        data.get("due_date"), data.get("paid_date"), data.get("status", "Pending"),
        data.get("payment_mode"), data.get("notes", "")
    ))
    conn.commit()
    fid = cur.lastrowid
    conn.close()
    return fid


def fee_exists(student_id, month):
    conn = get_conn()
    row = conn.execute("SELECT id FROM fees WHERE student_id = ? AND month = ?", (student_id, month)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_fees(student_id=None):
    conn = get_conn()
    if student_id:
        rows = conn.execute("SELECT * FROM fees WHERE student_id = ? ORDER BY due_date DESC", (student_id,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM fees ORDER BY due_date DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_fee(fee_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM fees WHERE id = ?", (fee_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_fees_with_student():
    conn = get_conn()
    rows = conn.execute("""
        SELECT f.*, s.name as student_name, s.email as student_email, s.contact as student_contact
        FROM fees f JOIN students s ON s.id = f.student_id
        ORDER BY f.due_date ASC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_fee(fee_id, data: dict):
    conn = get_conn()
    cur = conn.cursor()
    fields = ", ".join([f"{k} = ?" for k in data.keys()])
    values = list(data.values()) + [fee_id]
    cur.execute(f"UPDATE fees SET {fields} WHERE id = ?", values)
    conn.commit()
    conn.close()


def mark_fee_paid(fee_id, paid_date=None):
    update_fee(fee_id, {"status": "Paid", "paid_date": paid_date or str(date.today())})


def mark_reminder_sent(fee_id, sent_date=None):
    update_fee(fee_id, {"reminder_sent_date": sent_date or str(date.today())})


def delete_fee(fee_id):
    conn = get_conn()
    conn.execute("DELETE FROM fees WHERE id = ?", (fee_id,))
    conn.commit()
    conn.close()


# ---------------- Backup / Restore ----------------

def backup_path():
    return DB_PATH
