# 🏏 Shree Shyam Cricket Academy — AI Performance & Fitness Suite Pro

A complete, GUI-based (Streamlit), GroqCloud AI-powered cricket academy management
tool — students, coaches (Mohit Kumar - Batting, Ankush Kumar - Bowling), diet,
fitness, position-wise training, exercise library, attendance, injury tracking,
analytics, and PDF reports, all in one place.

## 🚀 Setup (5 minutes)

1. **Install Python** (3.9+) if you don't already have it: https://python.org

2. **Open a terminal/CMD in this folder** and install the libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. **Get a free GroqCloud API key**: https://console.groq.com/keys
   (Sign-up is free — copy your key and paste it into the app's sidebar.)

4. **Run the app**:
   ```bash
   streamlit run app.py
   ```

5. The app will open in your browser (usually at `http://localhost:8501`).

## 🔐 Default Login

- **Admin:** username `admin`, password `admin123`
- **Coach:** Mohit Kumar / Ankush Kumar, password `coach123`
- **Student:** select your name from the list, default PIN `1234`

⚠️ Be sure to change these passwords at the top of `app.py` before using this in production.

## 🔴 Live Match Center (CricHeroes-style)

The academy also includes **CricHeroes-style live match scoring** — and takes it
a step further:

- **Any two teams** — not limited to just SSCA vs Opponent. Academy matches,
  friendlies, tournaments, or **Corporate Matches** (between two company teams)
  can all be set up.
- **Admin (or Coach) manages both teams** — adding players to Team A and Team B
  either by selecting academy students directly from the list, or by simply
  typing the name of **any outside / opponent / corporate player** (no separate
  login required for them).
- **True ball-by-ball live scoring** — on every ball: runs (0–6), Wide / No Ball /
  Bye / Leg Bye, Wicket (dismissal type, who got out, fielder/keeper), automatic
  strike rotation, over completion, bowler changes, innings breaks, target &
  required run-rate, and the final match result (by runs/wickets) — all
  calculated automatically, just like CricHeroes.
- **"↩️ Undo Last Ball"** — made a mistake entering a ball? Undo it instantly and
  the whole score recalculates correctly right away.
- **Live scoreboard for everyone, no login needed** — anyone (student, parent, or
  any outsider) can add `?live=1` to the app's URL (e.g.
  `http://localhost:8501/?live=1`) to view the live score directly — **no login
  required**. This page auto-refreshes every 15 seconds, just like CricHeroes'
  live match screen.
- **Corporate Matches** are highlighted in their own section on the live scoreboard.

### How to use it
1. Admin/Coach → sidebar → **🔴 Live Match Center**.
2. **🆕 New Match** tab → enter Team A / Team B names, Match Type (Academy /
   Corporate / Tournament / Friendly), venue, date, overs → Create Match.
3. **👥 Playing XI** tab → add players to both teams (select academy students or
   type custom names).
4. **🪙 Toss & Start** tab → enter the toss result + decision → choose opening
   striker, non-striker, and bowler → the match goes live.
5. **🔴 Live Scoring** tab → enter the score ball by ball. Once overs are complete
   or the team is all out, a "Start 2nd Innings" / "Complete Match" button will
   appear automatically.
6. To share the live score, just send your app URL + `?live=1` to anyone — no
   login required on their end.

## 🆕🆕 Live Match Center — Latest Upgrade (Sound + Emoji + Weather + Location + Fees Check)

- **🎨 Team Mascots** — in the "New Match" tab, choose an emoji/mascot for each
  team (🦁🐯🔥⚡🐉 etc.) — the same mascot shows on the scoreboard, Playing XI,
  and match history.
- **📱 Compact Scoreboard** — the live score card is now a small, mobile-friendly
  card (doesn't take up the whole screen) — just like CricHeroes.
- **🌦️ Live Weather + 📍 Location** — once a venue is entered for a match, its
  live weather (temperature, condition, humidity, wind) and location automatically
  appear below the scoreboard — via the 100% free Open-Meteo API, no API key
  needed (just an internet connection).
- **🔊 Sound + Emoji Effects** — on every ball event (Six 🚀🔥, Four 💥, Wicket
  🎯😱, Wide 🙅, No Ball ⚠️, Bye/Leg Bye 🏃, Dot ⚫, Match Win 🏆🎉) — an automatic
  short sound (offline-generated tone, no internet required) and an emoji burst
  animation play automatically.
- **💰 Fees Check in Playing XI** — when adding academy students to a match's
  Playing XI (especially a Corporate Match), a live "Fees Paid / Pending /
  Overdue" badge shows next to their name, plus a clear warning banner if any
  player's fees are pending/overdue — so you know before the match starts who
  hasn't paid.
- **📲 Bulk WhatsApp — "Open All in Tabs"** — in Fees Management → Send Reminders
  → Bulk WhatsApp section, select students and open all their WhatsApp chat tabs
  in one click (with a slight stagger) — each tab only needs a tap on Send.
  (Note: WhatsApp itself doesn't allow any silent/automatic bulk-send without a
  paid Business API — this is the fastest free method available.)

## ✅ What's included

- **Dashboard** — BMI, attendance %, hydration, today's diet/workout, performance graph
- **Student Management** — full registration (age/height/weight/role/batting-bowling style/injury history)
- **AI Diet Planner** — Veg/Non-veg/Jain/Eggetarian, Weight gain/loss, Budget, Match day (GroqCloud AI generated)
- **AI Fitness & Workout** — Fat loss, Muscle gain, Cricket fitness, Match day, Recovery plans
- **Position-Based Training** — Batsman / Bowler / Wicket Keeper / Fielder — AI session generator + drill library
- **Stretching & Recovery** — Dynamic, Static, Warm-up, Cool-down, Foam Rolling, Yoga, Mobility
- **Exercise Library** — 90+ curated cricket-specific exercises, searchable/filterable (plus custom drills on demand via AI Chat)
- **Coach Panel** — Mohit Kumar (Batting) & Ankush Kumar (Bowling) — notes, ratings, progress chart, AI recommendations
- **AI Chat Assistant** — instant answers to students' questions (batting, bowling, diet, injury, and more)
- **Injury Prevention** — log injuries, track recovery status, AI prevention routines
- **Match Performance & Analytics** — runs/wickets/strike-rate/economy trends, skill radar chart, AI performance analysis
- **Attendance** — daily marking + monthly pie summary
- **Fees Management** — add fees per student or bulk-generate for everyone in one click,
  mark paid, auto-computed **Pending/Overdue** status, fees alert banner on the Dashboard, and
  one-click or bulk **email reminders** to students with pending/overdue fees
- **Free Email Sending** — AI Diet Plans and Fees Reminders can be emailed directly to a
  student's registered email address, using your own free Gmail account (SMTP) — no paid service
- **Reports** — professional PDF report generator + Excel export
- **Admin Panel** — database backup/restore, credentials info, data reset

## 📧 Free Email Setup (Diet Plans + Fees Reminders)

Emails are sent using **your own Gmail account** via its free SMTP relay — no paid
API, no monthly limits beyond Gmail's own daily sending limit (~500/day on a
normal Gmail account).

1. Turn on **2-Step Verification** on the Gmail account you want to send from
   (Google Account → Security).
2. In the same Security page, open **App Passwords**, give it any name (e.g.
   "Cricket Academy"), and copy the 16-character password it generates. Your
   normal Gmail login password will **not** work for this.
3. In the app, open the sidebar → **📧 Email Settings (Free Gmail SMTP)** →
   paste your Gmail address and the App Password.
4. Make sure each student has an **Email** saved (Student Management → add/update Email).
5. Now:
   - **AI Diet Planner** page → after generating a plan (or from a past plan) →
     "📧 Email This Diet Plan to Student"
   - **Fees Management** page → per-student "📧 Send Reminder", or "📧 Send
     Reminder to All Pending/Overdue" for a one-click bulk send

## 💰 Fees Management Quick Guide

- Admin → **Fees Management** → "➕ Add / Generate Fees":
  - Add a single fee record for one student, or
  - **Bulk Generate for All Students** — set the month, amount, and due date once
    and it creates a Pending fee record for every registered student (skipping
    students who already have that month's record).
- A fee shows as **Pending** until its due date passes without payment, after
  which it automatically shows as **Overdue** (no manual step needed) — both
  students and admin see this live on the Dashboard as a fees alert banner.
- Admin marks a fee **✅ Paid** once payment is received.
- Coaches get a read-only fees view and can also send reminder emails, but
  can't add/delete records or mark paid (admin-only).

## 📝 Notes

- Data is saved locally in **SQLite** (`academy.db`) — it grows as you use the app.
- Instead of a literal "500+ exercises" library, a more flexible solution is
  provided: 90+ quality-checked cricket-specific exercises + **on-demand custom
  drills/exercises generated via the AI Chat Assistant** whenever needed — more
  flexible and maintainable.
- Photo upload, QR-code attendance, and OpenCV video analysis are not included
  in this version (a much larger scope) — let us know if you'd like these added
  in a future version.
- If you see a `GroqCloud API error`, please check: (1) your API key is correct
  (2) free credits are available at console.groq.com (3) your internet
  connection is working.

## 🛠️ Tech Stack

Python · Streamlit · GroqCloud AI (Llama 3.3 70B) · SQLite · Plotly · ReportLab (PDF) · openpyxl (Excel)

---
Built for Shree Shyam Cricket Academy — Coach Mohit Kumar (Batting) & Coach Ankush Kumar (Bowling) 🏏
