# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, BigInteger, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Faculty(Base):
    __tablename__ = "faculty"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    majors = relationship("Major", back_populates="faculty")
    students = relationship("Student", back_populates="faculty")

class Major(Base):
    __tablename__ = "major"
    __table_args__ = (UniqueConstraint("name", "faculty_id", name="uq_major_name_faculty"),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculty.id"))

    faculty = relationship("Faculty", back_populates="majors")
    students = relationship("Student", back_populates="major")

class Student(Base):
    __tablename__ = "students"

    student_pk = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    student_id = Column(String, unique=True, nullable=False)
    prefix = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    citizen_id = Column(String, nullable=False)
    gender = Column(String, nullable=False)

    faculty_id = Column(Integer, ForeignKey("faculty.id"))
    major_id = Column(Integer, ForeignKey("major.id"))

    faculty = relationship("Faculty", back_populates="students")
    major = relationship("Major", back_populates="students")

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    location = Column(String)
    datein = Column(Date)

class StudentActivity(Base):
    __tablename__ = "student_activities"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_pk"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)

    student = relationship("Student", backref="activities_joined")
    activity = relationship("Activity", backref="participants")
