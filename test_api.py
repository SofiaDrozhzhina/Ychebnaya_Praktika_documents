import unittest
import json
from unittest.mock import patch, MagicMock
from datetime import date

# SessionLocal ДО импорта модулей приложения
import sys
sys.modules['config'] = MagicMock(DATABASE_URI='sqlite:///:memory:', SECRET_KEY='test')

from models import Base, Student, Course, Record
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#   Вспомогательные функции для создания объектов

def make_student(id=1, fio="Иванов Иван Иванович", dob=date(2000, 1, 1), phone="1234567890"):
    s = Student()
    s.id = id
    s.fio = fio
    s.date_of_birth = dob
    s.phone = phone
    return s

def make_course(id=1, name="Математика", description="Базовый курс", teacher="Сидоров С.С."):
    c = Course()
    c.id = id
    c.name = name
    c.description = description
    c.teacher = teacher
    return c

def make_record(id=1, id_student=1, course_id=1, dt=date(2024, 1, 1), grade="5"):
    r = Record()
    r.id = id
    r.id_student = id_student
    r.course_id = course_id
    r.date = dt
    r.grade = grade
    r.student = make_student()
    r.course = make_course()
    return r

class TestStudentModel(unittest.TestCase):
    """Юнит-тесты модели Student"""

    def test_to_dict_correct_values(self):
        """to_dict() возвращает корректные значения полей"""
        student = make_student(id=1, fio="Петров Пётр Петрович", phone="9991234567")
        result = student.to_dict()
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["fio"], "Петров Пётр Петрович")
        self.assertEqual(result["phone"], "9991234567")

    def test_to_dict_date_as_isoformat(self):
        """to_dict() возвращает дату рождения в формате ISO (YYYY-MM-DD)"""
        student = make_student(dob=date(2001, 6, 15))
        result = student.to_dict()
        self.assertEqual(result["date_of_birth"], "2001-06-15")

    def test_to_dict_none_phone(self):
        """to_dict() возвращает None, если телефон не задан"""
        student = make_student(phone=None)
        result = student.to_dict()
        self.assertIsNone(result["phone"])

class TestCourseModel(unittest.TestCase):
    """Юнит-тесты модели Course"""

    def test_to_dict_correct_values(self):
        """to_dict() возвращает корректные значения полей"""
        course = make_course(id=3, name="Физика", teacher="Иванов И.И.")
        result = course.to_dict()
        self.assertEqual(result["id"], 3)
        self.assertEqual(result["name"], "Физика")
        self.assertEqual(result["teacher"], "Иванов И.И.")

    def test_to_dict_optional_fields_none(self):
        """to_dict() корректно обрабатывает None в необязательных полях"""
        course = make_course(description=None, teacher=None)
        result = course.to_dict()
        self.assertIsNone(result["description"])
        self.assertIsNone(result["teacher"])

class TestRecordModel(unittest.TestCase):
    """Юнит-тесты модели Record"""

    def test_to_dict_correct_values(self):
        """to_dict() возвращает корректные значения и связанные имена"""
        record = make_record(id=2, grade="4", dt=date(2024, 3, 10))
        result = record.to_dict()
        self.assertEqual(result["grade"], "4")
        self.assertEqual(result["date"], "2024-03-10")
        self.assertEqual(result["student_fio"], "Иванов Иван Иванович")
        self.assertEqual(result["course_name"], "Математика")

    def test_to_dict_none_relations(self):
        """to_dict() возвращает None, если связанные объекты не загружены"""
        record = make_record()
        record.student = None
        record.course = None
        result = record.to_dict()
        self.assertIsNone(result["student_fio"])
        self.assertIsNone(result["course_name"])

#   Тесты API-эндпоинтов (через Flask test client)

def make_app():
    """Создаёт тестовое приложение с изолированной SQLite БД"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    patcher = patch('api.SessionLocal', TestSession)
    patcher.start()
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    return app, patcher

class TestStudentsAPI(unittest.TestCase):
    """Тесты эндпоинтов /api/students"""

    def setUp(self):
        self.app, self.patcher = make_app()
        self.client = self.app.test_client()

    def tearDown(self):
        self.patcher.stop()

    def _create_student(self, fio="Иванов Иван Иванович"):
        return self.client.post("/api/students", data=json.dumps({
            "fio": fio, "date_of_birth": "2000-01-01", "phone": "1234567890"
        }), content_type="application/json")

    def test_create_student(self):
        """POST /api/students — создание студента, возвращает 201 и ФИО"""
        response = self._create_student(fio="Петров Пётр Петрович")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["fio"], "Петров Пётр Петрович")

    def test_create_student_invalid_date(self):
        """POST /api/students с неверным форматом даты — возвращает 400"""
        response = self.client.post("/api/students", data=json.dumps({
            "fio": "Тест", "date_of_birth": "01.01.2000"
        }), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_get_students(self):
        """GET /api/students — возвращает 200 и список студентов"""
        self._create_student()
        response = self.client.get("/api/students")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.get_json()), 0)

    def test_update_student(self):
        """PUT /api/students/<id> — обновляет ФИО студента"""
        self._create_student()
        response = self.client.put("/api/students/1", data=json.dumps({
            "fio": "Новое Имя Отчество"
        }), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["fio"], "Новое Имя Отчество")

    def test_update_nonexistent_student(self):
        """PUT /api/students/999 — возвращает 404, если студент не найден"""
        response = self.client.put("/api/students/999", data=json.dumps({
            "fio": "Тест"
        }), content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_delete_student(self):
        """DELETE /api/students/<id> — удаляет студента, возвращает 200"""
        self._create_student()
        self.assertEqual(self.client.delete("/api/students/1").status_code, 200)
        self.assertEqual(len(self.client.get("/api/students").get_json()), 0)

class TestCoursesAPI(unittest.TestCase):
    """Тесты эндпоинтов /api/courses"""

    def setUp(self):
        self.app, self.patcher = make_app()
        self.client = self.app.test_client()

    def tearDown(self):
        self.patcher.stop()

    def _create_course(self, name="Математика"):
        return self.client.post("/api/courses", data=json.dumps({
            "name": name, "description": "Описание", "teacher": "Преподаватель"
        }), content_type="application/json")

    def test_create_course(self):
        """POST /api/courses — создание курса, возвращает 201 и название"""
        response = self._create_course(name="Физика")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["name"], "Физика")

    def test_get_courses(self):
        """GET /api/courses — возвращает 200 и список курсов"""
        self._create_course()
        response = self.client.get("/api/courses")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.get_json()), 0)

    def test_update_nonexistent_course(self):
        """PUT /api/courses/999 — возвращает 404"""
        response = self.client.put("/api/courses/999", data=json.dumps({
            "name": "Тест"
        }), content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_delete_course(self):
        """DELETE /api/courses/<id> — удаляет курс, возвращает 200"""
        self._create_course()
        self.assertEqual(self.client.delete("/api/courses/1").status_code, 200)

class TestRecordsAPI(unittest.TestCase):
    """Тесты эндпоинтов /api/records"""

    def setUp(self):
        self.app, self.patcher = make_app()
        self.client = self.app.test_client()
        self.client.post("/api/students", data=json.dumps({
            "fio": "Иванов Иван Иванович", "date_of_birth": "2000-01-01", "phone": "123"
        }), content_type="application/json")
        self.client.post("/api/courses", data=json.dumps({
            "name": "Физика", "description": "Описание", "teacher": "Сидоров"
        }), content_type="application/json")

    def tearDown(self):
        self.patcher.stop()

    def _create_record(self, dt="2024-01-01", grade="5"):
        return self.client.post("/api/records", data=json.dumps({
            "id_student": 1, "course_id": 1, "date": dt, "grade": grade
        }), content_type="application/json")

    def test_create_record(self):
        """POST /api/records — создание записи, возвращает 201 и оценку"""
        response = self._create_record(grade="4")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["grade"], "4")

    def test_create_record_invalid_date(self):
        """POST /api/records с неверным форматом даты — возвращает 400"""
        self.assertEqual(self._create_record(dt="01.01.2024").status_code, 400)

    def test_get_records(self):
        """GET /api/records — возвращает 200 и список записей"""
        self._create_record()
        response = self.client.get("/api/records")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.get_json()), 0)

    def test_update_record(self):
        """PUT /api/records/<id> — обновляет оценку"""
        self._create_record(grade="5")
        response = self.client.put("/api/records/1", data=json.dumps({
            "grade": "3"
        }), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["grade"], "3")

    def test_delete_nonexistent_record(self):
        """DELETE /api/records/999 — возвращает 404"""
        self.assertEqual(self.client.delete("/api/records/999").status_code, 404)

if __name__ == "__main__":
    unittest.main(verbosity=2)
