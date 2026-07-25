
from grading import calculate_grade, calculate_gpa, calculate_status


class Student:

    def __init__(self, student_id, name, subject, marks):
        self.student_id = str(student_id).strip().upper()
        self.name = str(name).strip().title()
        self.subject = str(subject).strip().title()
        self.marks = float(marks)

    @property
    def grade(self):
        return calculate_grade(self.marks)

    @property
    def gpa(self):
        return calculate_gpa(self.marks)

    @property
    def status(self):
        return calculate_status(self.marks)

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "name": self.name,
            "subject": self.subject,
            "marks": self.marks,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["student_id"],
            data["name"],
            data["subject"],
            data["marks"],
        )

    def as_row(self):
        return (
            self.student_id,
            self.name,
            self.subject,
            f"{self.marks:.1f}",
            self.grade,
            f"{self.gpa:.2f}",
            self.status,
        )

    def __repr__(self):
        return f"Student({self.student_id}, {self.name}, {self.subject}, {self.marks})"
