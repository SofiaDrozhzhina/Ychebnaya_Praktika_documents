# models.py
from sqlalchemy import create_engine, Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session

from config import DATABASE_URI

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    fio = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    phone = Column(String(50))

    records = relationship("Record", back_populates="student", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "fio": self.fio,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "phone": self.phone
        }

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    teacher = Column(String(255))

    records = relationship("Record", back_populates="course", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "teacher": self.teacher
        }

class Record(Base):
    __tablename__ = 'records'
    id = Column(Integer, primary_key=True)
    id_student = Column(Integer, ForeignKey('students.id', ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    grade = Column(String(10))  # '5','4','3','2' or 'Не оценено'

    student = relationship("Student", back_populates="records")
    course = relationship("Course", back_populates="records")

    def to_dict(self):
        return {
            "id": self.id,
            "id_student": self.id_student,
            "student_fio": self.student.fio if self.student else None,
            "course_id": self.course_id,
            "course_name": self.course.name if self.course else None,
            "date": self.date.isoformat() if self.date else None,
            "grade": self.grade
        }

# DB engine and session factory
engine = create_engine(DATABASE_URI, echo=False, future=True)
SessionLocal = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

def init_db():
    Base.metadata.create_all(bind=engine)
