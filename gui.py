import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from manager import GradeManager
from validators import ValidationError
from file_handler import FileHandlerError, DATA_FILE
from grading import GRADE_BANDS, PASS_MARK


COLORS = {
    "bg": "#F4F6FB",
    }

class GradingApp:

    def __init__(self, root):
        self.root = root
        self.manager = GradeManager()
    self.root.title("Student Grading System")
        self.root.geometry("1180x760")
        self.root.minsize(1050, 700)
        self.root.configure(bg=COLORS["bg"])

        self._setup_styles()
        self._build_header()
        self._build_body()
        self._build_footer()
        self._try_initial_load()