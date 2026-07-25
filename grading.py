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

