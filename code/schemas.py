# schemas.py
from pydantic import BaseModel
from datetime import date
from typing import Optional

# Student
class StudentBase(BaseModel):
    prefix: str
    first_name: str
    last_name: str
    citizen_id: str
    gender: str
    faculty_name: str
    major_name: str

class StudentCreate(StudentBase):
    student_id: str

class StudentUpdate(StudentBase):
    pass


# Activity
class ActivityBase(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    datein: date

class ActivityCreate(ActivityBase):
    pass

class ActivityUpdate(ActivityBase):
    pass


# Join Activity
class JoinActivityInput(BaseModel):
    student_id: str
    activity_id: int


# Faculty
class FacultyBase(BaseModel):
    name: str

class FacultyCreate(FacultyBase):
    pass

class FacultyUpdate(FacultyBase):
    pass


# Major
class MajorBase(BaseModel):
    name: str
    faculty_id: int

class MajorCreate(MajorBase):
    pass

class MajorUpdate(MajorBase):
    pass
