import base64
import hashlib
import hmac
from urllib.parse import parse_qs

import requests

from app.core.config import settings
from app.models.student import Student
from app.models.training_class import TrainingClass


LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"
LINE_BROADCAST_URL = "https://api.line.me/v2/bot/message/broadcast"


def verify_signature(body: bytes, signature: str | None) -> bool:
    if not settings.LINE_CHANNEL_SECRET:
        return True
    if not signature:
        return False

    digest = hmac.new(settings.LINE_CHANNEL_SECRET.encode("utf-8"), body, hashlib.sha256).digest()
    expected = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(expected, signature)


def parse_postback_data(data: str) -> dict[str, str]:
    parsed = parse_qs(data, keep_blank_values=True)
    return {key: values[0] for key, values in parsed.items()}


def text_message(text: str) -> dict:
    return {"type": "text", "text": text}


def check_in_button_message() -> dict:
    return {
        "type": "template",
        "altText": "Taekwondo attendance menu",
        "template": {
            "type": "buttons",
            "title": "Taekwondo Attendance",
            "text": "Ready for class?",
            "actions": [{"type": "postback", "label": "Check-in", "data": "action=checkin"}],
        },
    }


def student_selector_message(students: list[Student]) -> dict:
    actions = [
        {"type": "postback", "label": student.name[:20], "data": f"action=select_student&student_id={student.id}"}
        for student in students[:4]
    ]
    return {
        "type": "template",
        "altText": "Select student",
        "template": {
            "type": "buttons",
            "title": "Select Student",
            "text": "Who is checking in?",
            "actions": actions,
        },
    }


def class_selector_message(classes: list[TrainingClass], student_id: int) -> dict:
    actions = [
        {
            "type": "postback",
            "label": training_class.name[:20],
            "data": f"action=select_class&student_id={student_id}&class_id={training_class.id}",
        }
        for training_class in classes[:4]
    ]
    return {
        "type": "template",
        "altText": "Select class",
        "template": {
            "type": "buttons",
            "title": "Select Class",
            "text": "Choose today's class",
            "actions": actions,
        },
    }


def reply_message(reply_token: str, messages: list[dict]) -> None:
    if not settings.LINE_CHANNEL_ACCESS_TOKEN:
        return

    requests.post(
        LINE_REPLY_URL,
        headers={
            "Authorization": f"Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        },
        json={"replyToken": reply_token, "messages": messages},
        timeout=10,
    ).raise_for_status()


def broadcast_text(message: str) -> None:
    if not settings.LINE_CHANNEL_ACCESS_TOKEN:
        raise RuntimeError("LINE_CHANNEL_ACCESS_TOKEN is not configured.")

    requests.post(
        LINE_BROADCAST_URL,
        headers={
            "Authorization": f"Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        },
        json={"messages": [text_message(message)]},
        timeout=10,
    ).raise_for_status()
