"""
whatsapp_client.py — 100% free WhatsApp fee reminders (no API key, no paid service).

How it works:
    We build a "click to chat" wa.me link (https://wa.me/<number>?text=<message>).
    Clicking it opens WhatsApp (the app on mobile, WhatsApp Web on desktop) with
    the student's number and the reminder message already typed in — the admin
    just has to hit the Send button inside WhatsApp itself.

This is the only way to send WhatsApp messages that is genuinely free with zero
setup: Meta's official WhatsApp Business Cloud API needs a Facebook Business
account + phone number verification (free tier exists but is a multi-day setup
and messages outside a 24h window need pre-approved templates), and any
"automatic sender" library (e.g. pywhatkit) only works on a local desktop that
is already logged into WhatsApp Web — it cannot run on a hosted/cloud server.
So this app uses wa.me links, which work everywhere (cloud or local) instantly.
"""

import re
from urllib.parse import quote


def normalize_indian_number(raw_contact: str):
    """Cleans a stored contact number into wa.me's required format: countrycode+number,
    no +, no spaces, no dashes. Assumes India (91) when a bare 10-digit number is given.
    Returns None if it doesn't look like a usable phone number."""
    if not raw_contact:
        return None
    digits = re.sub(r"\D", "", raw_contact)
    if not digits:
        return None
    if len(digits) == 10:
        return "91" + digits
    if len(digits) == 11 and digits.startswith("0"):
        return "91" + digits[1:]
    if len(digits) >= 11 and digits.startswith("91"):
        return digits
    if len(digits) >= 10:
        return digits
    return None


def wa_link(raw_contact: str, message: str):
    """Builds a https://wa.me/... click-to-chat link. Returns None if the number is unusable."""
    number = normalize_indian_number(raw_contact)
    if not number:
        return None
    return f"https://wa.me/{number}?text={quote(message)}"


def fee_reminder_whatsapp_text(student_name, fee):
    """Plain-text (WhatsApp doesn't render HTML) version of the fee reminder."""
    is_overdue = fee.get("_effective_status") == "Overdue"
    status_word = "is now OVERDUE" if is_overdue else "is due soon"
    return (
        f"🏏 *Shree Shyam Cricket Academy*\n\n"
        f"Namaste {student_name},\n"
        f"Your academy fees *{status_word}*.\n\n"
        f"Month: {fee.get('month')}\n"
        f"Amount: ₹{fee.get('amount')}\n"
        f"Due Date: {fee.get('due_date')}\n\n"
        f"Please contact the academy office/coach as soon as possible to pay the fees. Thank you!"
    )
