from flask import Flask, jsonify
import logging

app = Flask(__name__)

# Настройка встроенного логирования Python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# 1. Модель Student
class Student:
    def __init__(self, student_id, name, group):
        self.id = student_id
        self.name = name
        self.group = group

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "group": self.group
        }


# 2. Интерфейс/контракт сервиса студентов
class IStudentService:
    def get_all(self):
        raise NotImplementedError

    def get_by_id(self, student_id):
        raise NotImplementedError


# Реализация StudentService
class StudentService(IStudentService):
    def __init__(self):
        self.students = [
            Student(1, "Алихан", "ИТ-21"),
            Student(2, "Данияр", "ИТ-22"),
            Student(3, "Аружан", "ИТ-21")
        ]

    def get_all(self):
        return self.students

    def get_by_id(self, student_id):
        for student in self.students:
            if student.id == student_id:
                return student
        return None


# 3–4. Dependency Injection:
# Flask не имеет встроенного DI-контейнера как ASP.NET Core,
# поэтому сервис передается в контроллер через конструктор.
class StudentsController:
    def __init__(self, student_service):
        self.student_service = student_service

    def get_all(self):
        logger.info("Request received: get all students")

        try:
            students = self.student_service.get_all()
            return jsonify([student.to_dict() for student in students]), 200
        except Exception:
            logger.error("Error while getting all students", exc_info=True)
            return jsonify({"error": "Internal Server Error"}), 500

    def get_by_id(self, student_id):
        try:
            student = self.student_service.get_by_id(student_id)

            if student is None:
                logger.warning(
                    "Student with ID %s was not found",
                    student_id
                )
                return jsonify({
                    "error": "Student not found"
                }), 404

            logger.info(
                "Student with ID %s was successfully found",
                student_id
            )
            return jsonify(student.to_dict()), 200

        except Exception:
            logger.error(
                "Error while getting student with ID %s",
                student_id,
                exc_info=True
            )
            return jsonify({"error": "Internal Server Error"}), 500


# 3. Регистрация зависимости.
# Аналог AddTransient<IStudentService, StudentService>() в данном
# небольшом Flask-приложении — создание StudentService при запуске.
student_service = StudentService()

# 4. Constructor Injection
controller = StudentsController(student_service)


# API: GET /api/students
@app.route("/api/students", methods=["GET"])
def get_students():
    return controller.get_all()


# API: GET /api/students/<id>
@app.route("/api/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    return controller.get_by_id(student_id)


if __name__ == "__main__":
    logger.info("Student API started")
    logger.info("Open: http://127.0.0.1:5000/api/students")
    app.run(debug=True)
