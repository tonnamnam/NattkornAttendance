from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.account_service import get_or_create_account
from app.services.attendance_service import DuplicateAttendanceError, create_attendance
from app.services.class_service import get_class, list_classes
from app.services.line_client import (
    check_in_button_message,
    class_selector_message,
    parse_postback_data,
    reply_message,
    student_selector_message,
    text_message,
    verify_signature,
)
from app.services.student_service import get_student, list_students_by_account


router = APIRouter()


@router.post("/webhook")
async def line_webhook(
    request: Request,
    x_line_signature: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    body = await request.body()
    if not verify_signature(body, x_line_signature):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid LINE signature.")

    payload = await request.json()
    for event in payload.get("events", []):
        handle_line_event(db, event)

    return {"status": "ok"}


def handle_line_event(db: Session, event: dict) -> None:
    event_type = event.get("type")
    reply_token = event.get("replyToken")
    line_user_id = event.get("source", {}).get("userId")

    if not reply_token or not line_user_id:
        return

    if event_type == "follow":
        get_or_create_account(db, line_user_id)
        reply_message(
            reply_token,
            [
                text_message("Welcome to Nattakorn Taekwondo Attendance."),
                check_in_button_message(),
            ],
        )
        return

    if event_type == "postback":
        account = get_or_create_account(db, line_user_id)
        data = parse_postback_data(event.get("postback", {}).get("data", ""))
        action = data.get("action")

        if action == "checkin":
            start_check_in(db, reply_token, account.id)
            return

        if action == "select_student":
            student_id = int(data["student_id"])
            send_class_selector(db, reply_token, account.id, student_id)
            return

        if action == "select_class":
            student_id = int(data["student_id"])
            class_id = int(data["class_id"])
            finish_check_in(db, reply_token, account.id, student_id, class_id)
            return

        reply_message(reply_token, [text_message("Sorry, I do not understand that action.")])


def start_check_in(db: Session, reply_token: str, account_id: int) -> None:
    students = list_students_by_account(db, account_id)
    if not students:
        reply_message(reply_token, [text_message("No students found. Please ask an admin to add a student first.")])
        return

    if len(students) == 1:
        send_class_selector(db, reply_token, account_id, students[0].id)
        return

    reply_message(reply_token, [student_selector_message(students)])


def send_class_selector(db: Session, reply_token: str, account_id: int, student_id: int) -> None:
    student = get_student(db, student_id)
    if not student or student.account_id != account_id:
        reply_message(reply_token, [text_message("Student not found for this LINE account.")])
        return

    classes = list_classes(db)
    if not classes:
        reply_message(reply_token, [text_message("No classes are available yet.")])
        return

    reply_message(reply_token, [class_selector_message(classes, student_id)])


def finish_check_in(db: Session, reply_token: str, account_id: int, student_id: int, class_id: int) -> None:
    student = get_student(db, student_id)
    training_class = get_class(db, class_id)

    if not student or student.account_id != account_id:
        reply_message(reply_token, [text_message("Student not found for this LINE account.")])
        return

    if not training_class:
        reply_message(reply_token, [text_message("Class not found.")])
        return

    try:
        attendance = create_attendance(db, student_id=student.id, class_id=training_class.id)
    except DuplicateAttendanceError:
        reply_message(reply_token, [text_message(f"{student.name} already checked in for {training_class.name} today.")])
        return

    checked_time = attendance.check_in_time.strftime("%H:%M")
    reply_message(reply_token, [text_message(f"Checked in: {student.name} - {training_class.name} at {checked_time}")])
