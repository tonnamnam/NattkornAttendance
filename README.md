# Nattakorn Taekwondo Attendance

FastAPI backend for Taekwondo attendance with LINE Messaging API, PostgreSQL, and Excel reports.

## Quick Start

```powershell
cd C:\Users\Choln\OneDrive\Desktop\NattakornAttendance
python -m pip install -r requirements.txt
copy .env.example .env
python -m uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## LINE Webhook

Set the LINE Messaging API webhook URL to:

```text
https://YOUR_DOMAIN/line/webhook
```

Supported events:

- `follow`: creates an `Account` by `line_user_id` and asks for the child's access code
- `message`: treats text as a student access code and links the parent LINE account
- `postback`: handles `checkin`, `select_student`, and `select_class`

## Attendance Flow

1. A parent follows/adds the LINE bot.
2. The bot asks for the child's access code in Thai.
3. The parent types the code they received from the teacher.
4. The system finds the matching student by `students.access_code` and links the LINE account through `account_students`.
5. The parent taps `เช็กชื่อเข้าเรียน`.
6. If there are multiple students, the bot asks the parent to select one.
7. The bot asks the parent to select a class.
8. The system saves attendance and prevents duplicate check-ins for the same student, class, and day.

## Account And Student Linking

`Account` means a LINE account. `Student` means the real student profile. They are connected through `account_students`, so the same student can be linked to their own LINE account and parent LINE accounts.

Example:

```text
Student: Nattakorn
- access_code=NKT0001
- Account A relationship=self
- Account B relationship=parent
- Account C relationship=parent
```

One account can also be linked to multiple students.

When creating students through `POST /students` or `POST /students/with-account`, `access_code` is optional. If omitted, the system generates a unique 6-character code. Existing SQLite databases are updated on startup and old students receive codes like `NKT0001`.

## Admin Endpoints

Set `ADMIN_API_KEY` in `.env`, then call protected endpoints with:

```text
X-API-Key: your-admin-api-key
```

Useful endpoints:

- `POST /accounts`
- `GET /accounts`
- `POST /students`
- `POST /students/with-account`
- `POST /students/link`
- `POST /classes`
- `POST /admin/broadcast`
- `GET /report/attendance?start_date=2026-05-01&end_date=2026-05-31`

## Database Schema

```text
accounts
- id
- line_user_id
- role
- created_at

students
- id
- name
- access_code
- created_at

account_students
- id
- account_id -> accounts.id
- student_id -> students.id
- relationship
- created_at
- unique(account_id, student_id)

classes
- id
- name
- start_time
- end_time
- created_at

attendances
- id
- student_id -> students.id
- class_id -> classes.id
- attendance_date
- check_in_time
- unique(student_id, class_id, attendance_date)
```

## Render

Use `render.yaml` or configure manually:

- Build command: `pip install -r requirements.txt`
- Start command: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
- Environment variables: see `.env.example`

Render may provide PostgreSQL URLs that start with `postgres://`; the app normalizes them for SQLAlchemy automatically.
