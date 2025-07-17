from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Base, Faculty, Major, Student, Activity, StudentActivity
from schemas import (
    StudentCreate, StudentUpdate,
    FacultyCreate, FacultyUpdate,
    MajorCreate, MajorUpdate,
    ActivityCreate, ActivityUpdate,
    JoinActivityInput
)
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import qrcode

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://rbac:rbacac@localhost:5432/rbac")
print("DEBUG:: DATABASE_URL =", DATABASE_URL)

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set!!!!")

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health-check")
def health_check():
    return {"status": "ok"}


@app.get("/health")
def health_checkDB(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "message": "เชื่อมต่อฐานข้อมูลสำเร็จ"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เชื่อมต่อฐานข้อมูลไม่สำเร็จ: {str(e)}")



def generate_qr(student_id: str):
    img = qrcode.make(student_id)  # หรือจะเก็บเป็น JSON ก็ได้
    img.save(f"{student_id}.png")
    
# -------- Faculty CRUD --------

@app.post("/faculties")
def create_faculty(data: FacultyCreate, db: Session = Depends(get_db)):
    existing = db.query(Faculty).filter(Faculty.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="คณะนี้มีอยู่แล้ว")
    faculty = Faculty(name=data.name)
    db.add(faculty)
    db.commit()
    db.refresh(faculty)
    return faculty

@app.get("/faculties")
def list_faculties(db: Session = Depends(get_db)):
    return db.query(Faculty).all()

@app.get("/faculties/{faculty_id}")
def get_faculty(faculty_id: int, db: Session = Depends(get_db)):
    faculty = db.query(Faculty).get(faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="ไม่พบคณะ")
    return faculty

@app.put("/faculties/{faculty_id}")
def update_faculty(faculty_id: int, data: FacultyUpdate, db: Session = Depends(get_db)):
    faculty = db.query(Faculty).get(faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="ไม่พบคณะ")
    faculty.name = data.name
    db.commit()
    db.refresh(faculty)
    return faculty

@app.delete("/faculties/{faculty_id}")
def delete_faculty(faculty_id: int, db: Session = Depends(get_db)):
    faculty = db.query(Faculty).get(faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="ไม่พบคณะ")
    db.delete(faculty)
    db.commit()
    return {"message": "ลบคณะเรียบร้อยแล้ว"}


# -------- Major CRUD --------

@app.post("/majors")
def create_major(data: MajorCreate, db: Session = Depends(get_db)):
    # ตรวจสอบว่าคณะมีอยู่ไหม
    faculty = db.query(Faculty).get(data.faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="ไม่พบคณะ")

    existing = db.query(Major).filter(Major.name == data.name, Major.faculty_id == data.faculty_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="สาขานี้มีอยู่แล้วในคณะนี้")

    major = Major(name=data.name, faculty_id=data.faculty_id)
    db.add(major)
    db.commit()
    db.refresh(major)
    return major

@app.get("/majors")
def list_majors(db: Session = Depends(get_db)):
    return db.query(Major).all()

@app.get("/majors/{major_id}")
def get_major(major_id: int, db: Session = Depends(get_db)):
    major = db.query(Major).get(major_id)
    if not major:
        raise HTTPException(status_code=404, detail="ไม่พบสาขา")
    return major

@app.put("/majors/{major_id}")
def update_major(major_id: int, data: MajorUpdate, db: Session = Depends(get_db)):
    major = db.query(Major).get(major_id)
    if not major:
        raise HTTPException(status_code=404, detail="ไม่พบสาขา")
    major.name = data.name
    major.faculty_id = data.faculty_id
    db.commit()
    db.refresh(major)
    return major

@app.delete("/majors/{major_id}")
def delete_major(major_id: int, db: Session = Depends(get_db)):
    major = db.query(Major).get(major_id)
    if not major:
        raise HTTPException(status_code=404, detail="ไม่พบสาขา")
    db.delete(major)
    db.commit()
    return {"message": "ลบสาขาเรียบร้อยแล้ว"}


# -------- Student CRUD --------

@app.post("/create/students")
def create_student(data: StudentCreate, db: Session = Depends(get_db)):
    # หา faculty ตามชื่อ
    faculty = db.query(Faculty).filter(Faculty.name == data.faculty_name).first()
    if not faculty:
        faculty = Faculty(name=data.faculty_name)
        db.add(faculty)
        db.commit()
        db.refresh(faculty)

    # หา major ตามชื่อและ faculty_id
    major = db.query(Major).filter(Major.name == data.major_name, Major.faculty_id == faculty.id).first()
    if not major:
        major = Major(name=data.major_name, faculty_id=faculty.id)
        db.add(major)
        db.commit()
        db.refresh(major)

    # ตรวจสอบ student_id ซ้ำ
    existing = db.query(Student).filter(Student.student_id == data.student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="รหัสนิสิตซ้ำ")

    student = Student(
        student_id=data.student_id,
        prefix=data.prefix,
        first_name=data.first_name,
        last_name=data.last_name,
        citizen_id=data.citizen_id.replace(" ", ""),
        gender=data.gender,
        faculty_id=faculty.id,
        major_id=major.id
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    return student

@app.get("/students")
def list_students(db: Session = Depends(get_db)):
    return db.query(Student).all()

@app.get("/students/{student_pk}")
def get_student(student_pk: int, db: Session = Depends(get_db)):
    student = db.query(Student).get(student_pk)
    if not student:
        raise HTTPException(status_code=404, detail="ไม่พบนิสิต")
    return student

@app.put("/students/{student_pk}")
def update_student(student_pk: int, data: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(Student).get(student_pk)
    if not student:
        raise HTTPException(status_code=404, detail="ไม่พบนิสิต")

    # Update fields
    student.prefix = data.prefix
    student.first_name = data.first_name
    student.last_name = data.last_name
    student.citizen_id = data.citizen_id.replace(" ", "")
    student.gender = data.gender

    # Update faculty and major
    faculty = db.query(Faculty).filter(Faculty.name == data.faculty_name).first()
    if not faculty:
        faculty = Faculty(name=data.faculty_name)
        db.add(faculty)
        db.commit()
        db.refresh(faculty)
    student.faculty_id = faculty.id

    major = db.query(Major).filter(Major.name == data.major_name, Major.faculty_id == faculty.id).first()
    if not major:
        major = Major(name=data.major_name, faculty_id=faculty.id)
        db.add(major)
        db.commit()
        db.refresh(major)
    student.major_id = major.id

    db.commit()
    db.refresh(student)
    return student

@app.delete("/students/{student_pk}")
def delete_student(student_pk: int, db: Session = Depends(get_db)):
    student = db.query(Student).get(student_pk)
    if not student:
        raise HTTPException(status_code=404, detail="ไม่พบนิสิต")
    db.delete(student)
    db.commit()
    return {"message": "ลบนิสิตเรียบร้อยแล้ว"}


# -------- Activity CRUD --------

@app.post("/activities")
def create_activity(data: ActivityCreate, db: Session = Depends(get_db)):
    activity = Activity(
        name=data.name,
        description=data.description,
        location=data.location,
        datein=data.datein
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity

@app.get("/activities")
def list_activities(db: Session = Depends(get_db)):
    return db.query(Activity).all()

@app.get("/activities/{activity_id}")
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = db.query(Activity).get(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="ไม่พบบกิจกรรม")
    return activity

@app.put("/activities/{activity_id}")
def update_activity(activity_id: int, data: ActivityUpdate, db: Session = Depends(get_db)):
    activity = db.query(Activity).get(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="ไม่พบบกิจกรรม")

    activity.name = data.name
    activity.description = data.description
    activity.location = data.location
    activity.datein = data.datein

    db.commit()
    db.refresh(activity)
    return activity

@app.delete("/activities/{activity_id}")
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = db.query(Activity).get(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="ไม่พบบกิจกรรม")
    db.delete(activity)
    db.commit()
    return {"message": "ลบกิจกรรมเรียบร้อยแล้ว"}

# -------- Join Activity --------

@app.post("/activities/join")
def join_activity(data: JoinActivityInput, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="ไม่พบนิสิต")

    activity = db.query(Activity).filter(Activity.id == data.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="ไม่พบกิจกรรม")

    existing = db.query(StudentActivity).filter_by(student_id=student.student_pk, activity_id=data.activity_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="นิสิตเข้าร่วมกิจกรรมนี้แล้ว")

    join = StudentActivity(student_id=student.student_pk, activity_id=data.activity_id)
    db.add(join)
    db.commit()
    return {"message": "บันทึกการเข้าร่วมเรียบร้อย"}
