import json
import os

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "students.json")


class FileHandlerError(Exception):
    pass


def save_students(students, path=DATA_FILE):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        records = [s.to_dict() for s in students]
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"students": records}, f, indent=2)
        return len(records)
    except OSError as e:
        raise FileHandlerError(f"Could not save file: {e}")


def load_students(path=DATA_FILE):
    if not os.path.exists(path):
        raise FileHandlerError("No saved data file found. Add students and press Save first.")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        records = data.get("students", [])
        if not isinstance(records, list):
            raise FileHandlerError("Data file is not in the expected format.")
        return records
    except json.JSONDecodeError:
        raise FileHandlerError("Data file is empty or corrupted and could not be read.")
    except OSError as e:
        raise FileHandlerError(f"Could not read file: {e}")