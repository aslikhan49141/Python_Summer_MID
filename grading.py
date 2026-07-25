import numpy as np

GRADE_BANDS = (
    (90, "A+", 4.00),
    (85, "A",  3.75),
    (80, "B+", 3.50),
    (75, "B",  3.25),
    (70, "C+", 3.00),
    (65, "C",  2.75),
    (60, "D+", 2.50),
    (50, "D",  2.25),
    (0,  "F",  0.00),
)

PASS_MARK = 50

def calculate_grade(marks):
    for min_marks, grade, _ in GRADE_BANDS:
        if marks >= min_marks:
            return grade
    return "F"

def calculate_gpa(marks):
    for min_marks, _, gpa in GRADE_BANDS:
        if marks >= min_marks:
            return gpa
    return 0.00

def calculate_status(marks):
    return "Pass" if marks >= PASS_MARK else "Fail"

def compute_statistics(students):
    if not students:
        return None

    marks = np.array([s.marks for s in students], dtype=float)
    pass_count =0;
    fail_count =0;
    for s in students:
        if s.status == "Pass":
            pass_count += 1
        else:
            fail_count += 1

    


