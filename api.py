# api.py
from flask import Blueprint, request, jsonify
from models import SessionLocal, Student, Course, Record
from sqlalchemy import asc, desc, or_
from datetime import datetime

api = Blueprint('api', __name__, url_prefix='/api')

def parse_sort_order(param):
    if param == 'asc':
        return asc
    if param == 'desc':
        return desc
    return None

# --- Students ---
@api.route('/students', methods=['GET'])
def list_students():
    """Query params: q (search by fio), sort (default, asc, desc) by date_of_birth"""
    q = request.args.get('q', '').strip()
    sort = request.args.get('sort', 'default')
    db = SessionLocal()
    query = db.query(Student)
    if q:
        query = query.filter(Student.fio.ilike(f'%{q}%'))
    if sort == 'asc':
        query = query.order_by(asc(Student.date_of_birth))
    elif sort == 'desc':
        query = query.order_by(desc(Student.date_of_birth))
    students = [s.to_dict() for s in query.all()]
    db.close()
    return jsonify(students)

@api.route('/students', methods=['POST'])
def create_student():
    data = request.json
    db = SessionLocal()
    try:
        dob = datetime.fromisoformat(data['date_of_birth']).date()
    except Exception:
        return jsonify({"error": "Invalid date_of_birth"}), 400
    student = Student(fio=data['fio'], date_of_birth=dob, phone=data.get('phone'))
    db.add(student)
    db.commit()
    db.refresh(student)
    res = student.to_dict()
    db.close()
    return jsonify(res), 201

@api.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.json
    db = SessionLocal()
    student = db.query(Student).get(student_id)
    if not student:
        db.close()
        return jsonify({"error": "Not found"}), 404
    student.fio = data.get('fio', student.fio)
    if data.get('date_of_birth'):
        student.date_of_birth = datetime.fromisoformat(data['date_of_birth']).date()
    student.phone = data.get('phone', student.phone)
    db.commit()
    res = student.to_dict()
    db.close()
    return jsonify(res)

@api.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    db = SessionLocal()
    student = db.query(Student).get(student_id)
    if not student:
        db.close()
        return jsonify({"error": "Not found"}), 404
    db.delete(student)
    db.commit()
    db.close()
    return jsonify({"status": "deleted"})

# --- Courses ---
@api.route('/courses', methods=['GET'])
def list_courses():
    q = request.args.get('q', '').strip()
    teacher = request.args.get('teacher', '').strip()
    db = SessionLocal()
    query = db.query(Course)
    if q:
        query = query.filter(Course.name.ilike(f'%{q}%'))
    if teacher:
        query = query.filter(Course.teacher == teacher)
    courses = [c.to_dict() for c in query.all()]
    db.close()
    return jsonify(courses)

@api.route('/courses', methods=['POST'])
def create_course():
    data = request.json
    db = SessionLocal()
    course = Course(name=data['name'], description=data.get('description'), teacher=data.get('teacher'))
    db.add(course)
    db.commit()
    db.refresh(course)
    res = course.to_dict()
    db.close()
    return jsonify(res), 201

@api.route('/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    data = request.json
    db = SessionLocal()
    course = db.query(Course).get(course_id)
    if not course:
        db.close()
        return jsonify({"error": "Not found"}), 404
    course.name = data.get('name', course.name)
    course.description = data.get('description', course.description)
    course.teacher = data.get('teacher', course.teacher)
    db.commit()
    res = course.to_dict()
    db.close()
    return jsonify(res)

@api.route('/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    db = SessionLocal()
    course = db.query(Course).get(course_id)
    if not course:
        db.close()
        return jsonify({"error": "Not found"}), 404
    db.delete(course)
    db.commit()
    db.close()
    return jsonify({"status": "deleted"})

# --- Records ---
@api.route('/records', methods=['GET'])
def list_records():
    """
    Query params:
      q - search across student fio or course name
      course_id - filter by course
      sort - 'default', 'asc', 'desc' - sort by date
    """
    q = request.args.get('q', '').strip()
    course_id = request.args.get('course_id', '').strip()
    sort = request.args.get('sort', 'default')
    db = SessionLocal()
    query = db.query(Record).join(Record.student).join(Record.course)
    if q:
        query = query.filter(or_(Student.fio.ilike(f'%{q}%'), Course.name.ilike(f'%{q}%')))
    if course_id:
        try:
            cid = int(course_id)
            query = query.filter(Record.course_id == cid)
        except ValueError:
            pass
    if sort == 'asc':
        query = query.order_by(asc(Record.date))
    elif sort == 'desc':
        query = query.order_by(desc(Record.date))
    # eager load relationships by accessing
    results = [r.to_dict() for r in query.all()]
    db.close()
    return jsonify(results)

@api.route('/records', methods=['POST'])
def create_record():
    data = request.json
    db = SessionLocal()
    try:
        dt = datetime.fromisoformat(data['date']).date()
    except Exception:
        return jsonify({"error": "Invalid date"}), 400
    rec = Record(id_student=data['id_student'], course_id=data['course_id'], date=dt, grade=data.get('grade'))
    db.add(rec)
    db.commit()
    db.refresh(rec)
    res = rec.to_dict()
    db.close()
    return jsonify(res), 201

@api.route('/records/<int:rec_id>', methods=['PUT'])
def update_record(rec_id):
    data = request.json
    db = SessionLocal()
    rec = db.query(Record).get(rec_id)
    if not rec:
        db.close()
        return jsonify({"error": "Not found"}), 404
    if 'id_student' in data:
        rec.id_student = data['id_student']
    if 'course_id' in data:
        rec.course_id = data['course_id']
    if 'date' in data:
        rec.date = datetime.fromisoformat(data['date']).date()
    if 'grade' in data:
        rec.grade = data['grade']
    db.commit()
    res = rec.to_dict()
    db.close()
    return jsonify(res)

@api.route('/records/<int:rec_id>', methods=['DELETE'])
def delete_record(rec_id):
    db = SessionLocal()
    rec = db.query(Record).get(rec_id)
    if not rec:
        db.close()
        return jsonify({"error": "Not found"}), 404
    db.delete(rec)
    db.commit()
    db.close()
    return jsonify({"status": "deleted"})
