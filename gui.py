import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from manager import GradeManager
from validators import ValidationError
from file_handler import FileHandlerError, DATA_FILE
from grading import GRADE_BANDS, PASS_MARK


COLORS = {
    "bg": "#F4F6FB",          
    "panel": "#FFFFFF",       
    "header": "#1E3A5F",      
    "header2": "#274B79",     
    "accent": "#2563EB",      
    "accent_dark": "#1D4ED8",
    "green": "#15803D",
    "red": "#B91C1C",
    "amber": "#B45309",
    "text": "#1F2937",
    "muted": "#6B7280",
    "border": "#E2E8F0",
    "row_alt": "#F8FAFF",
    "pass_bg": "#DCFCE7",
    "fail_bg": "#FEE2E2",
}

FONT_FAMILY = "DejaVu Sans"
F_TITLE = (FONT_FAMILY, 17, "bold")
F_SUB = (FONT_FAMILY, 9)
F_HEAD = (FONT_FAMILY, 11, "bold")
F_LABEL = (FONT_FAMILY, 9, "bold")
F_BODY = (FONT_FAMILY, 10)
F_STAT = (FONT_FAMILY, 14, "bold")
F_SMALL = (FONT_FAMILY, 8)


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

   
    def _setup_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=COLORS["panel"],
            fieldbackground=COLORS["panel"],
            foreground=COLORS["text"],
            rowheight=30,
            font=F_BODY,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["header"],
            foreground="white",
            font=F_LABEL,
            relief="flat",
            padding=(6, 8),
        )
        style.map("Treeview.Heading", background=[("active", COLORS["header2"])])
        style.map(
            "Treeview",
            background=[("selected", COLORS["accent"])],
            foreground=[("selected", "white")],
        )

   
    def _build_header(self):
        header = tk.Frame(self.root, bg=COLORS["header"], height=74)
        header.pack(fill="x")
        header.pack_propagate(False)

        left = tk.Frame(header, bg=COLORS["header"])
        left.pack(side="left", padx=28, pady=12)
        tk.Label(
            left, text="\u2756  Student Grading System",
            font=F_TITLE, bg=COLORS["header"], fg="white",
        ).pack(anchor="w")

        self.count_label = tk.Label(
            header, text="", font=F_HEAD, bg=COLORS["header2"], fg="white",
            padx=18, pady=8,
        )
        self.count_label.pack(side="right", padx=28)

    
    def _build_body(self):
        body = tk.Frame(self.root, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=18, pady=14)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_left_panel(body)
        self._build_right_panel(body)

    def _card(self, parent):
        outer = tk.Frame(parent, bg=COLORS["border"], padx=1, pady=1)
        inner = tk.Frame(outer, bg=COLORS["panel"])
        inner.pack(fill="both", expand=True)
        return outer, inner

    def _card_title(self, parent, text):
        bar = tk.Frame(parent, bg=COLORS["panel"])
        bar.pack(fill="x", padx=16, pady=(10, 2))
        tk.Label(bar, text=text, font=F_HEAD, bg=COLORS["panel"], fg=COLORS["header"]).pack(side="left")

    
    def _build_left_panel(self, body):
        left = tk.Frame(body, bg=COLORS["bg"], width=330)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 14))
        left.pack_propagate(False)

        form_outer, form = self._card(left)
        form_outer.pack(fill="x")
        self._card_title(form, "\u270E  Student Record")

        self.entries = {}
        fields = (("Student ID", "student_id"), ("Name", "name"),
                  ("Subject", "subject"), ("Marks (0\u2013100)", "marks"))
        for label_text, key in fields:
            row = tk.Frame(form, bg=COLORS["panel"])
            row.pack(fill="x", padx=16, pady=(6, 0))
            tk.Label(row, text=label_text.upper(), font=F_SMALL,
                     bg=COLORS["panel"], fg=COLORS["muted"]).pack(anchor="w")
            entry = tk.Entry(
                row, font=F_BODY, bg="#F9FAFC", fg=COLORS["text"],
                relief="solid", bd=1, highlightthickness=1,
                highlightbackground=COLORS["border"],
                highlightcolor=COLORS["accent"], insertbackground=COLORS["accent"],
            )
            entry.pack(fill="x", ipady=5, pady=(3, 0))
            self.entries[key] = entry

        btns = tk.Frame(form, bg=COLORS["panel"])
        btns.pack(fill="x", padx=16, pady=(12, 12))
        for col in range(2):
            btns.columnconfigure(col, weight=1)

        buttons = (
            ("\u2795  Add", COLORS["accent"], self.on_add, 0, 0),
            ("\u21BB  Update", COLORS["amber"], self.on_update, 0, 1),
            ("\u2716  Delete", COLORS["red"], self.on_delete, 1, 0),
            ("\u239A  Clear", COLORS["muted"], self.on_clear, 1, 1),
        )
        for text, color, cmd, r, c in buttons:
            self._button(btns, text, color, cmd).grid(
                row=r, column=c, sticky="ew", padx=3, pady=3)

        tk.Frame(form, bg=COLORS["panel"], height=2).pack()

        stats_outer, stats = self._card(left)
        stats_outer.pack(fill="both", expand=True, pady=(14, 0))
        self._card_title(stats, "\u2211  Statistics")

        
        self._button(stats, "\u25A4  Show Detailed Statistics", COLORS["header"],
                     self.on_show_statistics).pack(side="bottom", fill="x", padx=16, pady=(6, 12))

        scroll_area = tk.Frame(stats, bg=COLORS["panel"])
        scroll_area.pack(fill="both", expand=True, padx=(16, 4), pady=(2, 4))

        self.stats_canvas = tk.Canvas(scroll_area, bg=COLORS["panel"],
                                      highlightthickness=0, bd=0, height=140)
        stats_scrollbar = ttk.Scrollbar(scroll_area, orient="vertical",
                                        command=self.stats_canvas.yview)
        self.stats_canvas.configure(yscrollcommand=stats_scrollbar.set)
        stats_scrollbar.pack(side="right", fill="y")
        self.stats_canvas.pack(side="left", fill="both", expand=True)

        grid = tk.Frame(self.stats_canvas, bg=COLORS["panel"])
        grid_window = self.stats_canvas.create_window((0, 0), window=grid, anchor="nw")

        def _sync_stats_scroll(_event=None):
            self.stats_canvas.configure(scrollregion=self.stats_canvas.bbox("all"))
            self.stats_canvas.itemconfigure(grid_window, width=self.stats_canvas.winfo_width())
        grid.bind("<Configure>", _sync_stats_scroll)
        self.stats_canvas.bind("<Configure>", _sync_stats_scroll)

        def _on_stats_wheel(event):
            if event.num == 4 or event.delta > 0:
                self.stats_canvas.yview_scroll(-1, "units")
            else:
                self.stats_canvas.yview_scroll(1, "units")

        self.stat_labels = {}
        stat_rows = (("Total Students", "total"), ("Total Records", "records"),
                     ("Average Marks", "average"), ("Highest Marks", "highest"),
                     ("Lowest Marks", "lowest"), ("Pass / Fail", "passfail"))
        for label_text, key in stat_rows:
            row = tk.Frame(grid, bg=COLORS["panel"])
            row.pack(fill="x", pady=3, padx=(0, 8))
            name_label = tk.Label(row, text=label_text, font=F_BODY,
                                  bg=COLORS["panel"], fg=COLORS["muted"])
            name_label.pack(side="left")
            value = tk.Label(row, text="\u2014", font=F_LABEL,
                             bg=COLORS["panel"], fg=COLORS["header"])
            value.pack(side="right")
            self.stat_labels[key] = value
            for w in (row, name_label, value):
                w.bind("<MouseWheel>", _on_stats_wheel)
                w.bind("<Button-4>", _on_stats_wheel)
                w.bind("<Button-5>", _on_stats_wheel)
        for w in (self.stats_canvas, grid):
            w.bind("<MouseWheel>", _on_stats_wheel)
            w.bind("<Button-4>", _on_stats_wheel)
            w.bind("<Button-5>", _on_stats_wheel)

    def _button(self, parent, text, color, command):
        btn = tk.Button(
            parent, text=text, font=F_LABEL, bg=color, fg="white",
            activebackground=COLORS["accent_dark"], activeforeground="white",
            relief="flat", bd=0, padx=10, pady=8, cursor="hand2", command=command,
        )
        btn.bind("<Enter>", lambda e: btn.configure(bg=COLORS["accent_dark"]))
        btn.bind("<Leave>", lambda e: btn.configure(bg=color))
        return btn

    
    def _build_right_panel(self, body):
        right_outer, right = self._card(body)
        right_outer.grid(row=0, column=1, sticky="nsew")

        top = tk.Frame(right, bg=COLORS["panel"])
        top.pack(fill="x", padx=16, pady=(14, 6))
        tk.Label(top, text="\u2637  Student Table", font=F_HEAD,
                 bg=COLORS["panel"], fg=COLORS["header"]).pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.refresh_table())
        search_box = tk.Entry(
            top, textvariable=self.search_var, font=F_BODY, width=18,
            bg="#F9FAFC", relief="solid", bd=1, highlightthickness=1,
            highlightbackground=COLORS["border"], highlightcolor=COLORS["accent"],
        )
        search_box.pack(side="right", ipady=4)
        tk.Label(top, text="Search:", font=F_BODY, bg=COLORS["panel"],
                 fg=COLORS["muted"]).pack(side="right", padx=(0, 6))

        self.subject_filter = tk.StringVar(value="All Subjects")
        self.subject_combo = ttk.Combobox(
            top, textvariable=self.subject_filter, font=F_BODY, width=16,
            state="readonly", values=("All Subjects",),
        )
        self.subject_combo.pack(side="right", padx=(0, 16), ipady=2)
        self.subject_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())
        tk.Label(top, text="Subject:", font=F_BODY, bg=COLORS["panel"],
                 fg=COLORS["muted"]).pack(side="right", padx=(0, 6))

        table_frame = tk.Frame(right, bg=COLORS["panel"])
        table_frame.pack(fill="both", expand=True, padx=16, pady=(4, 16))

        columns = ("id", "name", "subject", "marks", "grade", "gpa", "status")
        headings = ("ID", "Name", "Subject", "Marks", "Grade", "GPA", "Status")
        widths = (70, 190, 150, 70, 65, 65, 75)

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        for col, head, width in zip(columns, headings, widths):
            self.tree.heading(col, text=head)
            anchor = "w" if col in ("name", "subject") else "center"
            self.tree.column(col, width=width, anchor=anchor)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure("odd", background=COLORS["row_alt"])
        self.tree.tag_configure("fail", foreground=COLORS["red"])
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    
    def _build_footer(self):
        footer = tk.Frame(self.root, bg=COLORS["panel"],
                          highlightbackground=COLORS["border"], highlightthickness=1)
        footer.pack(fill="x", side="bottom")

        inner = tk.Frame(footer, bg=COLORS["panel"])
        inner.pack(fill="x", padx=18, pady=10)

        self._button(inner, "\u2913  Save", COLORS["green"], self.on_save).pack(side="left", padx=(0, 8))
        self._button(inner, "\u2912  Load", COLORS["accent"], self.on_load).pack(side="left", padx=(0, 8))
        self._button(inner, "\u23FB  Exit", COLORS["red"], self.on_exit).pack(side="left")

        self.status_label = tk.Label(inner, text="Ready.", font=F_BODY,
                                     bg=COLORS["panel"], fg=COLORS["muted"])
        self.status_label.pack(side="right")

   
    def set_status(self, message, kind="info"):
        color = {"info": COLORS["muted"], "ok": COLORS["green"], "error": COLORS["red"]}[kind]
        self.status_label.configure(text=message, fg=color)

    def get_form_values(self):
        return {key: entry.get() for key, entry in self.entries.items()}

    def fill_form(self, student):
        self.on_clear(keep_status=True)
        self.entries["student_id"].insert(0, student.student_id)
        self.entries["name"].insert(0, student.name)
        self.entries["subject"].insert(0, student.subject)
        self.entries["marks"].insert(0, f"{student.marks:g}")

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        query = self.search_var.get().strip().lower()
        subject_choice = self.subject_filter.get()
        shown = 0
        for student in self.manager.students:
            if subject_choice != "All Subjects" and student.subject != subject_choice:
                continue
            if query and query not in student.student_id.lower() \
                    and query not in student.name.lower():
                continue
            tags = []
            if shown % 2 == 1:
                tags.append("odd")
            if student.status == "Fail":
                tags.append("fail")
            self.tree.insert("", "end", values=student.as_row(), tags=tuple(tags))
            shown += 1
        subjects = sorted(set(s.subject for s in self.manager.students))
        self.subject_combo.configure(values=("All Subjects",) + tuple(subjects))
        if subject_choice not in ("All Subjects", *subjects):
            self.subject_filter.set("All Subjects")
        self.count_label.configure(text=f"{len(self.manager.students)} Records")
        self.refresh_stats()

    def refresh_stats(self):
        stats = self.manager.get_statistics()
        if stats is None:
            for label in self.stat_labels.values():
                label.configure(text="\u2014")
            return
        self.stat_labels["total"].configure(text=str(stats["total"]))
        self.stat_labels["records"].configure(text=str(stats["records"]))
        self.stat_labels["average"].configure(text=f"{stats['average']:.2f}")
        self.stat_labels["highest"].configure(text=f"{stats['highest']:.1f}")
        self.stat_labels["lowest"].configure(text=f"{stats['lowest']:.1f}")
        self.stat_labels["passfail"].configure(
            text=f"{stats['pass_count']} / {stats['fail_count']}")

    
    def on_add(self):
        values = self.get_form_values()
        try:
            student = self.manager.add_student(
                values["student_id"], values["name"], values["subject"], values["marks"])
            self.refresh_table()
            self.on_clear(keep_status=True)
            self.set_status(f"Added {student.name} ({student.student_id}) \u2014 grade {student.grade}.", "ok")
        except ValidationError as e:
            self.set_status(str(e), "error")
            messagebox.showerror("Invalid Input", str(e))

    def on_search(self):
        query = self.entries["student_id"].get().strip() or self.entries["name"].get().strip()
        try:
            matches = self.manager.search_partial(query)
            student = matches[0]
            self.fill_form(student)
            self.search_var.set("")
            for item in self.tree.get_children():
                if self.tree.item(item, "values")[0] == student.student_id:
                    self.tree.selection_set(item)
                    self.tree.see(item)
                    break
            self.set_status(
                f"Found {len(matches)} match(es). Showing {student.name}: "
                f"{student.marks:g} marks, grade {student.grade}, GPA {student.gpa:.2f}.", "ok")
        except ValidationError as e:
            self.set_status(str(e), "error")
            messagebox.showwarning("Search", str(e))

    def on_update(self):
        values = self.get_form_values()
        try:
            student = self.manager.update_student(
                values["student_id"], values["name"], values["subject"], values["marks"])
            self.refresh_table()
            self.set_status(
                f"Updated {student.student_id} ({student.subject}) \u2014 new grade {student.grade}.", "ok")
        except ValidationError as e:
            self.set_status(str(e), "error")
            messagebox.showerror("Update Failed", str(e))

    def on_delete(self):
        sid = self.entries["student_id"].get().strip()
        subject = self.entries["subject"].get().strip()
        if not sid:
            selection = self.tree.selection()
            if selection:
                row = self.tree.item(selection[0], "values")
                sid, subject = row[0], row[2]
        if not sid:
            messagebox.showwarning("Delete", "Enter a Student ID or select a row to delete.")
            return
        try:
            student = self.manager.search_student(sid, subject)
            if not messagebox.askyesno(
                    "Confirm Delete",
                    f"Delete {student.name} ({student.student_id} \u2014 {student.subject})?"):
                return
            self.manager.delete_student(sid, subject)
            self.refresh_table()
            self.on_clear(keep_status=True)
            self.set_status(f"Deleted {student.name} ({student.student_id} \u2014 {student.subject}).", "ok")
        except ValidationError as e:
            self.set_status(str(e), "error")
            messagebox.showerror("Delete Failed", str(e))

    def on_clear(self, keep_status=False):
        for entry in self.entries.values():
            entry.delete(0, "end")
        if not keep_status:
            self.set_status("Form cleared.")

    def on_row_select(self, _event):
        selection = self.tree.selection()
        if not selection:
            return
        row = self.tree.item(selection[0], "values")
        try:
            self.fill_form(self.manager.search_student(row[0], row[2]))
        except ValidationError:
            pass

    def on_save(self):
        try:
            count = self.manager.save_to_file()
            self.set_status(f"Saved {count} record(s) to students.json.", "ok")
            messagebox.showinfo("Save", f"Saved {count} record(s) successfully.")
        except FileHandlerError as e:
            self.set_status(str(e), "error")
            messagebox.showerror("Save Failed", str(e))

    def on_load(self):
        path = filedialog.askopenfilename(
            title="Select a JSON data file to import",
            initialdir=os.path.dirname(DATA_FILE),
            filetypes=(("JSON files", "*.json"), ("All files", "*.*")),
        )
        if not path:
            return
        try:
            loaded, skipped = self.manager.load_from_file(path)
            self.refresh_table()
            note = f" ({skipped} invalid record(s) skipped)" if skipped else ""
            self.set_status(f"Imported {loaded} record(s) from {os.path.basename(path)}{note}.", "ok")
        except FileHandlerError as e:
            self.set_status(str(e), "error")
            messagebox.showerror("Load Failed", str(e))

    def on_exit(self):
        if messagebox.askyesno("Exit", "Save data before exiting?"):
            try:
                self.manager.save_to_file()
            except FileHandlerError as e:
                messagebox.showerror("Save Failed", str(e))
        self.root.destroy()

    def _try_initial_load(self):
        try:
            loaded, _ = self.manager.load_from_file()
            self.set_status(f"Loaded {loaded} record(s) from students.json on startup.", "ok")
        except FileHandlerError:
            self.set_status("No saved data found \u2014 starting with an empty table.")
        self.refresh_table()

    
    def on_show_statistics(self):
        stats = self.manager.get_statistics()
        if stats is None:
            messagebox.showinfo("Statistics", "No students yet. Add some records first.")
            return

        win = tk.Toplevel(self.root)
        win.title("Detailed Statistics")
        win.geometry("560x560")
        win.configure(bg=COLORS["bg"])
        win.transient(self.root)

        header = tk.Frame(win, bg=COLORS["header"])
        header.pack(fill="x")
        tk.Label(header, text="\u2211  Class Statistics", font=F_TITLE,
                 bg=COLORS["header"], fg="white", pady=14, padx=20).pack(anchor="w")

        grid = tk.Frame(win, bg=COLORS["bg"])
        grid.pack(fill="x", padx=20, pady=16)
        for col in range(3):
            grid.columnconfigure(col, weight=1)

        cards = (
            ("Total Students", str(stats["total"]), COLORS["header"]),
            ("Total Records", str(stats["records"]), COLORS["header"]),
            ("Average Marks", f"{stats['average']:.2f}", COLORS["accent"]),
            ("Average GPA", f"{stats['average_gpa']:.2f}", COLORS["accent"]),
            ("Highest", f"{stats['highest']:.1f}", COLORS["green"]),
            ("Lowest", f"{stats['lowest']:.1f}", COLORS["red"]),
            ("Pass / Fail", f"{stats['pass_count']} / {stats['fail_count']} ({stats['pass_rate']:.0f}%)", COLORS["green"]),
        )
        for i, (title, value, color) in enumerate(cards):
            card = tk.Frame(grid, bg=COLORS["panel"], highlightbackground=COLORS["border"],
                            highlightthickness=1)
            card.grid(row=i // 3, column=i % 3, sticky="ew", padx=4, pady=4)
            tk.Label(card, text=title.upper(), font=F_SMALL, bg=COLORS["panel"],
                     fg=COLORS["muted"]).pack(pady=(10, 0))
            tk.Label(card, text=value, font=F_STAT, bg=COLORS["panel"],
                     fg=color).pack(pady=(2, 10))

        dist_frame = tk.Frame(win, bg=COLORS["panel"],
                              highlightbackground=COLORS["border"], highlightthickness=1)
        dist_frame.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        tk.Label(dist_frame, text="GRADE DISTRIBUTION", font=F_LABEL,
                 bg=COLORS["panel"], fg=COLORS["header"]).pack(anchor="w", padx=14, pady=(12, 6))

        max_count = max(stats["grade_distribution"].values())
        for _, grade, _ in GRADE_BANDS:
            count = stats["grade_distribution"].get(grade, 0)
            if count == 0:
                continue
            row = tk.Frame(dist_frame, bg=COLORS["panel"])
            row.pack(fill="x", padx=14, pady=2)
            tk.Label(row, text=f"{grade:<3}", font=F_LABEL, width=4, anchor="w",
                     bg=COLORS["panel"], fg=COLORS["text"]).pack(side="left")
            bar_bg = tk.Frame(row, bg="#EDF1F7", height=16)
            bar_bg.pack(side="left", fill="x", expand=True, padx=6)
            bar = tk.Frame(bar_bg, bg=COLORS["accent"] if grade != "F" else COLORS["red"], height=16)
            bar.place(relwidth=count / max_count, relheight=1)
            tk.Label(row, text=str(count), font=F_LABEL, width=3,
                     bg=COLORS["panel"], fg=COLORS["muted"]).pack(side="right")

        tk.Label(win, text=f"Subjects: {', '.join(stats['unique_subjects'])}   \u2022   Pass mark: {PASS_MARK}",
                 font=F_SMALL, bg=COLORS["bg"], fg=COLORS["muted"]).pack(pady=(0, 12))



