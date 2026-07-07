"""
sound_fx.py — Live ball-by-ball sound + emoji effects for the Live Match
Center ("SIX!", "OUT!", "WIDE!" etc.), CricHeroes-style.

Every tone is synthesized on the fly with Python's built-in `wave` + `math`
modules (no internet, no external sound files, no extra pip package needed)
and shipped to the browser as a base64 data:// URL, so it works completely
offline once the app is running. A short-lived HTML/CSS/JS snippet plays the
tone and pops a burst of emoji for ~1.6s, then removes itself.
"""

import base64
import io
import math
import struct
import wave

import streamlit.components.v1 as components

SAMPLE_RATE = 22050


def _tone_bytes(notes, volume=0.35):
    """notes: list of (freq_hz, duration_sec) played in sequence.
    freq_hz == 0 means silence (a short pause)."""
    frames = bytearray()
    for freq, dur in notes:
        n_samples = int(SAMPLE_RATE * dur)
        for i in range(n_samples):
            if freq <= 0:
                sample = 0.0
            else:
                t = i / SAMPLE_RATE
                # tiny attack/release envelope so tones don't click at the edges
                attack = i / (SAMPLE_RATE * 0.01)
                release = (n_samples - i) / (SAMPLE_RATE * 0.02)
                env = max(0.0, min(1.0, attack, release + 0.001))
                sample = math.sin(2 * math.pi * freq * t) * volume * env
            frames += struct.pack("<h", int(sample * 32767))
    buf = io.BytesIO()
    wf = wave.open(buf, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(bytes(frames))
    wf.close()
    return buf.getvalue()


def _tone_data_url(notes, volume=0.35):
    wav_bytes = _tone_bytes(notes, volume=volume)
    b64 = base64.b64encode(wav_bytes).decode("ascii")
    return f"data:audio/wav;base64,{b64}"


# Each event: (musical notes for the tone, emoji list for the burst, big label, label color)
_EVENTS = {
    "six":     ([(523, 0.09), (659, 0.09), (784, 0.09), (1047, 0.28)], ["6️⃣", "🚀", "🔥", "🎆", "👏"], "SIX!", "#FFC53D"),
    "four":    ([(523, 0.10), (784, 0.24)], ["4️⃣", "🏏", "💥", "👏"], "FOUR!", "#38bdf8"),
    "wicket":  ([(220, 0.12), (196, 0.12), (164, 0.30)], ["🎯", "🔴", "😱", "🏏"], "OUT!", "#ff5858"),
    "wide":    ([(300, 0.10), (0, 0.03), (300, 0.10)], ["🙅", "↔️"], "WIDE", "#ffe9b0"),
    "no_ball": ([(300, 0.10), (0, 0.03), (300, 0.10), (0, 0.03), (300, 0.10)], ["⚠️", "🚫"], "NO BALL", "#ffe9b0"),
    "bye":     ([(440, 0.10), (523, 0.14)], ["🏃", "➕"], "BYE", "#e2e8f0"),
    "leg_bye": ([(440, 0.10), (523, 0.14)], ["🦵", "➕"], "LEG BYE", "#e2e8f0"),
    "dot":     ([(300, 0.09)], ["⚫"], "DOT BALL", "#7fa892"),
    "run":     ([(440, 0.08), (523, 0.10)], ["🏏", "👍"], "RUN", "#c9f0ff"),
    "over":    ([(392, 0.10), (523, 0.10), (659, 0.20)], ["🔁", "🏁"], "OVER!", "#9fd6bb"),
    "win":     ([(523, 0.12), (659, 0.12), (784, 0.12), (1047, 0.40)], ["🏆", "🎉", "🎊", "👑"], "WINNER!", "#FFC53D"),
}


def classify_ball_event(extra_type_label, runs_batsman, is_wicket):
    """Maps a scored ball's inputs to one of the _EVENTS keys."""
    if is_wicket:
        return "wicket"
    if extra_type_label == "Wide":
        return "wide"
    if extra_type_label == "No Ball":
        return "no_ball"
    if extra_type_label == "Bye":
        return "bye"
    if extra_type_label == "Leg Bye":
        return "leg_bye"
    if runs_batsman == 6:
        return "six"
    if runs_batsman == 4:
        return "four"
    if runs_batsman == 0:
        return "dot"
    return "run"


def render_event_fx(event_key, height=140):
    """Renders (once) the sound + emoji-burst overlay for the given event key.
    Call this right after a rerun where a new ball/event has just landed —
    it self-destructs after ~1.6s so it never lingers or repeats on its own."""
    cfg = _EVENTS.get(event_key)
    if not cfg:
        return
    notes, emojis, label, color = cfg
    audio_url = _tone_data_url(notes)
    emoji_spans = "".join(
        f'<span class="fx-emoji" style="--d:{i*0.08}s; --x:{(i-len(emojis)/2)*34}px;">{e}</span>'
        for i, e in enumerate(emojis)
    )
    html = f"""
    <div id="fx-root" style="display:flex;align-items:center;justify-content:center;
         height:{height}px;overflow:visible;position:relative;font-family:'Poppins',sans-serif;">
      <div style="text-align:center;">
        <div class="fx-label" style="color:{color};">{label}</div>
        <div class="fx-emoji-row">{emoji_spans}</div>
      </div>
      <audio autoplay style="display:none;">
        <source src="{audio_url}" type="audio/wav">
      </audio>
    </div>
    <style>
      .fx-label {{
        font-size: 34px; font-weight: 900; letter-spacing: 1px;
        text-shadow: 0 0 18px currentColor, 0 2px 6px rgba(0,0,0,0.6);
        animation: fx-pop 1.4s ease-out forwards;
      }}
      .fx-emoji-row {{ position:relative; height:40px; }}
      .fx-emoji {{
        position:absolute; left:50%; top:0; font-size:26px;
        transform: translate(-50%, 0);
        animation: fx-burst 1.3s ease-out forwards;
        animation-delay: var(--d);
        opacity:0;
      }}
      @keyframes fx-pop {{
        0%   {{ transform: scale(0.4); opacity:0; }}
        15%  {{ transform: scale(1.15); opacity:1; }}
        30%  {{ transform: scale(1); opacity:1; }}
        80%  {{ transform: scale(1); opacity:1; }}
        100% {{ transform: scale(1); opacity:0; }}
      }}
      @keyframes fx-burst {{
        0%   {{ transform: translate(-50%, 0) scale(0.3); opacity:0; }}
        20%  {{ opacity:1; }}
        100% {{ transform: translate(calc(-50% + var(--x)), -55px) scale(1.2) rotate(15deg); opacity:0; }}
      }}
    </style>
    """
    components.html(html, height=height)
