from datetime import date
from io import BytesIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.session import get_db
from app.services.attendance_service import list_attendance_report


router = APIRouter(dependencies=[Depends(require_admin)])


@router.get("/attendance")
def export_attendance_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    records = list_attendance_report(db, start_date=start_date, end_date=end_date)

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Attendance"
    sheet.append(["date", "student name", "class name", "check-in time"])

    for record in records:
        sheet.append(
            [
                record.attendance_date.isoformat(),
                record.student.name,
                record.training_class.name,
                record.check_in_time.strftime("%H:%M:%S"),
            ]
        )

    for column in ("A", "B", "C", "D"):
        sheet.column_dimensions[column].width = 20

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    filename = f"attendance_{start_date.isoformat()}_{end_date.isoformat()}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
