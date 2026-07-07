"""
groq_client.py — thin wrapper around the GroqCloud chat completions API.
Get a free API key at https://console.groq.com/keys
"""

import requests

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

DEFAULT_MODEL = "llama-3.3-70b-versatile"

AVAILABLE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
]


def _call_groq(api_key, messages, model=DEFAULT_MODEL, temperature=0.7, max_tokens=1400):
    if not api_key:
        return None, "⚠️ GroqCloud API key not found. Enter your API key in the sidebar (get one free at console.groq.com/keys)."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    try:
        resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        return text, None
    except requests.exceptions.HTTPError as e:
        return None, f"❌ GroqCloud API error: {e} — {resp.text[:300]}"
    except Exception as e:
        return None, f"❌ Error calling GroqCloud: {e}"


def _profile_summary(student):
    return (
        f"Name: {student.get('name')}, Age: {student.get('age')}, "
        f"Height: {student.get('height_cm')} cm, Weight: {student.get('weight_kg')} kg, "
        f"Role: {student.get('role')}, Dominant hand: {student.get('dominant_hand')}, "
        f"Batting style: {student.get('batting_style')}, Bowling style: {student.get('bowling_style')}, "
        f"Injury history: {student.get('injury_history') or 'None'}"
    )


SYSTEM_BASE = (
    "You are an expert cricket performance coach, sports nutritionist, and strength & "
    "conditioning specialist working for Shree Shyam Cricket Academy in India. "
    "Give practical, safe, age-appropriate, India-friendly advice (use common Indian foods "
    "and easily available gym/ground equipment). Reply using clear headings and bullet points "
    "in Markdown. Keep tone motivating and simple. Reply in Hinglish (Hindi+English mix) unless "
    "asked otherwise, since most students are Hindi speaking."
)


def generate_diet_plan(api_key, student, diet_type, goal, model=DEFAULT_MODEL):
    prompt = (
        f"Student profile: {_profile_summary(student)}\n\n"
        f"Create a detailed 1-day cricket-specific diet plan.\n"
        f"Diet type: {diet_type}\nGoal: {goal}\n\n"
        "Include: Early morning, Breakfast, Mid-morning snack, Lunch, Pre-training snack, "
        "Post-training/Dinner, Before bed. For each meal give Indian food items with approx "
        "quantities. At the end give a summary table of total approx Calories, Protein, Carbs, "
        "Fat, and key micronutrients, plus hydration and supplement suggestions (only common, "
        "safe, legal supplements like whey protein, creatine monohydrate if age appropriate)."
    )
    messages = [
        {"role": "system", "content": SYSTEM_BASE},
        {"role": "user", "content": prompt},
    ]
    return _call_groq(api_key, messages, model=model, max_tokens=1600)


def generate_workout_plan(api_key, student, goal, model=DEFAULT_MODEL):
    prompt = (
        f"Student profile: {_profile_summary(student)}\n\n"
        f"Create a detailed cricket fitness & workout plan for goal: {goal}.\n"
        "Structure it as a 5-6 day weekly split relevant to a cricketer of this role "
        "(strength, conditioning, speed/agility, mobility, and a rest/recovery day). "
        "For each day list exercises with sets/reps/duration. Keep it doable with basic "
        "gym or ground equipment. Add warnings if the student's injury history should modify "
        "any exercise."
    )
    messages = [
        {"role": "system", "content": SYSTEM_BASE},
        {"role": "user", "content": prompt},
    ]
    return _call_groq(api_key, messages, model=model, max_tokens=1600)


def generate_position_training(api_key, student, position, focus_areas, model=DEFAULT_MODEL):
    prompt = (
        f"Student profile: {_profile_summary(student)}\n\n"
        f"Create a focused skill + fitness training session plan for a {position}.\n"
        f"Specific focus areas requested: {', '.join(focus_areas) if focus_areas else 'general improvement'}.\n"
        "Include: warm-up (5-10 min), technical skill drills with sets/reps/duration, "
        "position-specific fitness/strength work, and a cool-down/stretching routine at the end. "
        "Be specific and actionable, like a real coach's session plan."
    )
    messages = [
        {"role": "system", "content": SYSTEM_BASE},
        {"role": "user", "content": prompt},
    ]
    return _call_groq(api_key, messages, model=model, max_tokens=1500)


def generate_stretch_recovery(api_key, student, kind, model=DEFAULT_MODEL):
    prompt = (
        f"Student profile: {_profile_summary(student)}\n\n"
        f"Create a {kind} routine (e.g. Dynamic Stretch / Static Stretch / Warm-up / "
        "Cool-down / Foam Rolling / Yoga / Mobility) specifically useful for cricketers. "
        "List each movement with duration/reps, in a safe sequence, with brief cues on form."
    )
    messages = [
        {"role": "system", "content": SYSTEM_BASE},
        {"role": "user", "content": prompt},
    ]
    return _call_groq(api_key, messages, model=model, max_tokens=1000)


def ai_chat_reply(api_key, student, history, user_message, model=DEFAULT_MODEL):
    messages = [{"role": "system", "content": SYSTEM_BASE + "\n\nStudent profile: " + _profile_summary(student)}]
    for h in history[-10:]:
        role = "user" if h["sender"] == "user" else "assistant"
        messages.append({"role": role, "content": h["message"]})
    messages.append({"role": "user", "content": user_message})
    return _call_groq(api_key, messages, model=model, max_tokens=1000)


def generate_performance_analysis(api_key, student, perf_rows, model=DEFAULT_MODEL):
    perf_text = "\n".join([
        f"Date {p['match_date']}: Runs {p['runs']}({p['balls_faced']}b, {p['fours']}x4, {p['sixes']}x6), "
        f"Bowling {p['overs_bowled']}ov-{p['runs_conceded']}r-{p['wickets']}w, Catches {p['catches']}"
        for p in perf_rows
    ]) or "No match data yet."
    prompt = (
        f"Student profile: {_profile_summary(student)}\n\nMatch history:\n{perf_text}\n\n"
        "Analyse the trend in this player's performance, identify 2-3 strengths, 2-3 weaknesses, "
        "and give 3 concrete, specific action points for the next month of training."
    )
    messages = [
        {"role": "system", "content": SYSTEM_BASE},
        {"role": "user", "content": prompt},
    ]
    return _call_groq(api_key, messages, model=model, max_tokens=900)


def generate_coach_recommendation(api_key, student, coach_type, notes_text, model=DEFAULT_MODEL):
    role_desc = "batting technique" if coach_type == "batting" else "bowling technique"
    prompt = (
        f"Student profile: {_profile_summary(student)}\n\nRecent coach notes on {role_desc}:\n{notes_text}\n\n"
        f"As an expert {coach_type} coach, summarise the player's current technique level and "
        "suggest a focused 2-week improvement plan with specific drills."
    )
    messages = [
        {"role": "system", "content": SYSTEM_BASE},
        {"role": "user", "content": prompt},
    ]
    return _call_groq(api_key, messages, model=model, max_tokens=900)
