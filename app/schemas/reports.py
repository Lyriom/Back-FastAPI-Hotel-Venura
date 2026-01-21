from datetime import date
from pydantic import BaseModel, Field

class WeeklyReportQuery(BaseModel):
    start: date

class MonthlyReportQuery(BaseModel):
    year: int = Field(ge=2000, le=2100)
    month: int = Field(ge=1, le=12)
