from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.account_service import get_or_create_account
from app.services.attendance_service import DuplicateAttendanceError, create_attendance
from app.services.class_service import get_class, list_classes
from app.services.line_client import (
    ask_access_code_message,
    check_in_button_message,
    class_selector_message,
    parse_postback_data,
    reply_message,
    student_selector_message,
    text_message,
    verify_signature,
)
from app.services.student_service import (
    DuplicateAccountStudentLinkError,
    account_can_access_student,
    get_student,
    get_student_by_access_code,
    link_account_to_student,
    list_students_by_account,
)


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
                text_message("ยินดีต้อนรับสู่ระบบเช็กชื่อ Nattakorn Taekwondo"),
                ask_access_code_message(),
            ],
        )
        return

    if event_type == "message" and event.get("message", {}).get("type") == "text":
        account = get_or_create_account(db, line_user_id)
        handle_text_message(db, reply_token, account.id, event.get("message", {}).get("text", ""))
        return

    if event_type == "postback":
        account = get_or_create_account(db, line_user_id)
        data = parse_postback_data(event.get("postback", {}).get("data", ""))
        action = data.get("action")

        if action == "request_access_code":
            reply_message(reply_token, [ask_access_code_message()])
            return

        if action == "access_code_help":
            reply_message(
                reply_token,
                [
                    text_message("รหัสเข้าใช้งานจะได้รับจากครูค่ะ กรุณาพิมพ์รหัสนั้นเข้ามาในแชตนี้ เช่น NKT0001"),
                    ask_access_code_message(),
                ],
            )
            return

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

        reply_message(reply_token, [text_message("ขออภัยค่ะ ระบบยังไม่รู้จักคำสั่งนี้")])


def handle_text_message(db: Session, reply_token: str, account_id: int, text: str) -> None:
    access_code = text.strip()
    student = get_student_by_access_code(db, access_code)
    if not student:
        students = list_students_by_account(db, account_id)
        if students:
            reply_message(
                reply_token,
                [
                    text_message("ไม่พบรหัสนี้ค่ะ หากต้องการเพิ่มบุตรหลาน กรุณาตรวจสอบรหัสจากครูแล้วพิมพ์อีกครั้ง"),
                    check_in_button_message(),
                ],
            )
            return

        reply_message(
            reply_token,
            [
                text_message("ยังไม่พบรหัสนี้ค่ะ กรุณาตรวจสอบรหัสเข้าใช้งานของลูกจากครู แล้วพิมพ์ส่งมาอีกครั้ง"),
                ask_access_code_message(),
            ],
        )
        return

    try:
        link_account_to_student(db, account_id=account_id, student_id=student.id, relationship="parent")
    except DuplicateAccountStudentLinkError:
        reply_message(
            reply_token,
            [
                text_message(f"บัญชี LINE นี้เชื่อมกับ {student.name} อยู่แล้วค่ะ"),
                check_in_button_message(),
            ],
        )
        return

    reply_message(
        reply_token,
        [
            text_message(f"เชื่อมบัญชีสำเร็จค่ะ ตอนนี้ผู้ปกครองสามารถเช็กชื่อให้ {student.name} ได้แล้ว"),
            check_in_button_message(),
        ],
    )


def start_check_in(db: Session, reply_token: str, account_id: int) -> None:
    students = list_students_by_account(db, account_id)
    if not students:
        reply_message(
            reply_token,
            [
                text_message("ยังไม่มีนักเรียนที่เชื่อมกับบัญชี LINE นี้ค่ะ"),
                ask_access_code_message(),
            ],
        )
        return

    if len(students) == 1:
        send_class_selector(db, reply_token, account_id, students[0].id)
        return

    reply_message(reply_token, [student_selector_message(students)])


def send_class_selector(db: Session, reply_token: str, account_id: int, student_id: int) -> None:
    student = get_student(db, student_id)
    if not student or not account_can_access_student(db, account_id=account_id, student_id=student_id):
        reply_message(reply_token, [text_message("ไม่พบนักเรียนคนนี้ในบัญชี LINE ของคุณค่ะ")])
        return

    classes = list_classes(db)
    if not classes:
        reply_message(reply_token, [text_message("ยังไม่มีคลาสเรียนในระบบค่ะ")])
        return

    reply_message(reply_token, [class_selector_message(classes, student_id)])


def finish_check_in(db: Session, reply_token: str, account_id: int, student_id: int, class_id: int) -> None:
    student = get_student(db, student_id)
    training_class = get_class(db, class_id)

    if not student or not account_can_access_student(db, account_id=account_id, student_id=student_id):
        reply_message(reply_token, [text_message("ไม่พบนักเรียนคนนี้ในบัญชี LINE ของคุณค่ะ")])
        return

    if not training_class:
        reply_message(reply_token, [text_message("ไม่พบคลาสเรียนนี้ค่ะ")])
        return

    try:
        attendance = create_attendance(db, student_id=student.id, class_id=training_class.id)
    except DuplicateAttendanceError:
        reply_message(reply_token, [text_message(f"วันนี้ {student.name} เช็กชื่อคลาส {training_class.name} แล้วค่ะ")])
        return

    checked_time = attendance.check_in_time.strftime("%H:%M")
    reply_message(reply_token, [text_message(f"เช็กชื่อสำเร็จ: {student.name} - {training_class.name} เวลา {checked_time} น.")])
