
class ValidationError(Exception):
    pass


def validate_student_id(student_id):
    student_id = str(student_id).strip()
    if not student_id:
        raise ValidationError("Student ID cannot be empty.")
    if not student_id.isalnum():
        raise ValidationError("Student ID may only contain letters and digits.")
    letter_count = sum(1 for ch in student_id if ch.isalpha())
    if letter_count > 1:
        raise ValidationError("Student ID can contain at most one English letter (e.g. S001).")
    if len(student_id) > 15:
        raise ValidationError("Student ID must be at most 15 characters.")
    return student_id.upper()


def validate_name(name):
    name = str(name).strip()
    if not name:
        raise ValidationError("Name cannot be empty.")
    if not all(ch.isalpha() or ch in " ." for ch in name):
        raise ValidationError("Name may only contain letters, spaces and dots.")
    if len(name) > 40:
        raise ValidationError("Name must be at most 40 characters.")
    return name.title()


def validate_subject(subject):
    subject = str(subject).strip()
    if not subject:
        raise ValidationError("Subject cannot be empty.")
    if len(subject) > 30:
        raise ValidationError("Subject must be at most 30 characters.")
    return subject.title()


def validate_marks(marks):
    try:
        value = float(str(marks).strip())
    except (ValueError, TypeError):
        raise ValidationError("Marks must be a number (e.g. 85 or 72.5).")
    if value < 0 or value > 100:
        raise ValidationError("Marks must be between 0 and 100.")
    return value
