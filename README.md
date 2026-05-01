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

- `follow`: creates an `Account` by `line_user_id`
- `postback`: handles `checkin`, `select_student`, and `select_class`

## Attendance Flow

1. User taps `Check-in` in LINE.
2. If the LINE account has no students, the bot asks them to contact an admin.
3. If there are multiple students, the bot asks the user to select one.
4. The bot asks the user to select a class.
5. The system saves attendance and prevents duplicate check-ins for the same student, class, and day.

## Admin Endpoints

Set `ADMIN_API_KEY` in `.env`, then call protected endpoints with:

```text
X-API-Key: your-admin-api-key
```

Useful endpoints:

- `POST /accounts`
- `GET /accounts`
- `POST /students`
- `POST /classes`
- `POST /admin/broadcast`
- `GET /report/attendance?start_date=2026-05-01&end_date=2026-05-31`

## Database Schema

```text
accounts
- id
- line_user_id
- created_at

students
- id
- name
- account_id -> accounts.id
- created_at

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
