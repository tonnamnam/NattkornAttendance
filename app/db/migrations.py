from sqlalchemy import Engine, inspect, text


def ensure_student_access_codes(engine: Engine) -> None:
    inspector = inspect(engine)
    if not inspector.has_table("students"):
        return

    columns = {column["name"] for column in inspector.get_columns("students")}
    dialect = engine.dialect.name

    with engine.begin() as connection:
        if "access_code" not in columns:
            if dialect == "postgresql":
                connection.execute(text("ALTER TABLE students ADD COLUMN IF NOT EXISTS access_code VARCHAR(32)"))
            else:
                connection.execute(text("ALTER TABLE students ADD COLUMN access_code VARCHAR(32)"))

        if dialect == "postgresql":
            connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_students_access_code ON students (access_code)"))
        elif dialect == "sqlite":
            connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_students_access_code ON students (access_code)"))

        existing_codes = {
            row[0] for row in connection.execute(text("SELECT access_code FROM students WHERE access_code IS NOT NULL"))
        }
        rows = connection.execute(text("SELECT id FROM students WHERE access_code IS NULL ORDER BY id")).all()
        for row in rows:
            student_id = row[0]
            access_code = f"NKT{student_id:04d}"
            suffix = 1
            while access_code in existing_codes:
                access_code = f"NKT{student_id:04d}{suffix}"
                suffix += 1
            existing_codes.add(access_code)
            connection.execute(
                text("UPDATE students SET access_code = :access_code WHERE id = :student_id"),
                {"access_code": access_code, "student_id": student_id},
            )
