from models import Student
from grading import compute_statistics
from validators import (
    ValidationError,
    validate_student_id,
    validate_name,
    validate_subject,
    validate_marks,
)
import file_handler


class GradeManager:

    def __init__(self):
        self.students = []        
        self.used_keys = set()    

    def add_student(self, student_id, name, subject, marks):
        sid = validate_student_id(student_id)
        sub = validate_subject(subject)
        if (sid, sub) in self.used_keys:
            raise ValidationError(f"Duplicate: student '{sid}' already has a record for '{sub}'.")
        student = Student(sid, validate_name(name), sub, validate_marks(marks))
        self.students.append(student)
        self.used_keys.add((sid, sub))
        return student

    def search_student(self, student_id, subject=None):
        sid = validate_student_id(student_id)
        matches = [s for s in self.students if s.student_id == sid]
        if subject and str(subject).strip():
            sub = validate_subject(subject)
            matches = [s for s in matches if s.subject == sub]
        if not matches:
            raise ValidationError(f"Record not found: no matching record for ID '{sid}'.")
        return matches[0]

    def search_partial(self, text):
        text = str(text).strip().lower()
        if not text:
            raise ValidationError("Enter a Student ID or name to search.")
        matches = [
            s for s in self.students
            if text in s.student_id.lower() or text in s.name.lower()
        ]
        if not matches:
            raise ValidationError(f"Record not found for '{text}'.")
        return matches

    def update_student(self, student_id, name, subject, marks):
        student = self.search_student(student_id, subject)
        student.name = validate_name(name)
        student.marks = validate_marks(marks)
        return student

    def delete_student(self, student_id, subject=None):
        sid = validate_student_id(student_id)
        matches = [s for s in self.students if s.student_id == sid]
        if not matches:
            raise ValidationError(f"Record not found: no student with ID '{sid}'.")
        if subject and str(subject).strip():
            sub = validate_subject(subject)
            matches = [s for s in matches if s.subject == sub]
            if not matches:
                raise ValidationError(f"Record not found: '{sid}' has no record for '{subject}'.")
        elif len(matches) > 1:
            raise ValidationError(
                f"Student '{sid}' has {len(matches)} subject records. "
                "Enter the subject to delete a specific record.")
        student = matches[0]
        self.students.remove(student)
        self.used_keys.discard((student.student_id, student.subject))
        return student

    def get_statistics(self):
        return compute_statistics(self.students)

    def save_to_file(self):
        return file_handler.save_students(self.students)

    def load_from_file(self, path=None):
            records = file_handler.load_students(path) if path else file_handler.load_students()
            self.students = []
            self.used_keys = set()
            skipped = 0
            for record in records:
                try:
                    student = Student.from_dict(record)
                    key = (student.student_id, student.subject)
                    if key in self.used_keys:
                        skipped += 1
                        continue
                    self.students.append(student)
                    self.used_keys.add(key)
                except (KeyError, ValueError, TypeError):
                    skipped += 1
            return len(self.students), skipped
    