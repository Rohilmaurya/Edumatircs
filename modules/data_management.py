import csv
import os

DEFAULT_SUBJECTS = ["Mathematics", "Physics", "Chemistry", "Computer_Science", "English"]

def get_csv_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "data", "students_data.csv")

def initialize_csv(file_path=None):
    path = file_path if file_path else get_csv_path()
    folder = os.path.dirname(path)
    if not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Student_ID", "Name", "Batch", "Term"] + DEFAULT_SUBJECTS)
    return path

def validate_student_record(record, subjects=None):
    subj_list = subjects if subjects else DEFAULT_SUBJECTS
    required = ["Student_ID", "Name", "Batch", "Term"]
    for key in required:
        if key not in record or str(record[key]).strip() == "":
            return False, "Missing required field: " + str(key)
    for s in subj_list:
        if s in record:
            try:
                score = float(record[s])
                if score < 0 or score > 100:
                    return False, "Marks must be between 0 and 100"
            except ValueError:
                return False, "Invalid number for " + s
    return True, "Valid"

def load_students_data(file_path=None):
    path = file_path if file_path else get_csv_path()
    if not os.path.exists(path):
        initialize_csv(path)
        return []
    records = []
    with open(path, mode="r", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            return []
        subject_names = header[4:]
        for row in reader:
            if not row or len(row) < 4:
                continue
            item = {
                "Student_ID": row[0].strip(),
                "Name": row[1].strip(),
                "Batch": row[2].strip(),
                "Term": row[3].strip()
            }
            for i, subj in enumerate(subject_names):
                idx = 4 + i
                if idx < len(row) and row[idx].strip() != "":
                    try:
                        item[subj] = float(row[idx])
                    except ValueError:
                        item[subj] = 0.0
                else:
                    item[subj] = 0.0
            records.append(item)
    return records

def save_all_records(records, file_path=None):
    path = file_path if file_path else get_csv_path()
    folder = os.path.dirname(path)
    if not os.path.exists(folder):
        os.makedirs(folder)
    headers = ["Student_ID", "Name", "Batch", "Term"] + DEFAULT_SUBJECTS
    with open(path, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for r in records:
            row = [
                r.get("Student_ID", ""),
                r.get("Name", ""),
                r.get("Batch", ""),
                r.get("Term", "")
            ]
            for s in DEFAULT_SUBJECTS:
                val = r.get(s, 0.0)
                row.append(str(int(val)) if float(val).is_integer() else str(round(float(val), 2)))
            writer.writerow(row)
    return True

def add_student_record(record, file_path=None):
    is_valid, msg = validate_student_record(record)
    if not is_valid:
        return False, msg
    records = load_students_data(file_path)
    sid = str(record["Student_ID"]).strip().lower()
    term = str(record["Term"]).strip().lower()
    for r in records:
        if r["Student_ID"].strip().lower() == sid and r["Term"].strip().lower() == term:
            return False, "Record already exists for this term"
    records.append(record)
    save_all_records(records, file_path)
    return True, "Record added successfully"

def update_student_record(student_id, term, updated_fields, file_path=None):
    records = load_students_data(file_path)
    found = False
    sid = str(student_id).strip().lower()
    t = str(term).strip().lower()
    for r in records:
        if r["Student_ID"].strip().lower() == sid and r["Term"].strip().lower() == t:
            for k, v in updated_fields.items():
                if k not in ["Student_ID", "Term"]:
                    r[k] = v
            is_valid, msg = validate_student_record(r)
            if not is_valid:
                return False, msg
            found = True
            break
    if not found:
        return False, "Record not found"
    save_all_records(records, file_path)
    return True, "Record updated successfully"

def delete_student_record(student_id, term=None, file_path=None):
    records = load_students_data(file_path)
    sid = str(student_id).strip().lower()
    new_records = []
    deleted = 0
    for r in records:
        match_id = r["Student_ID"].strip().lower() == sid
        if term:
            match_term = r["Term"].strip().lower() == str(term).strip().lower()
            if match_id and match_term:
                deleted += 1
                continue
        else:
            if match_id:
                deleted += 1
                continue
        new_records.append(r)
    if deleted == 0:
        return False, "No records matched"
    save_all_records(new_records, file_path)
    return True, "Deleted successfully"

def get_student_records(student_id, file_path=None):
    records = load_students_data(file_path)
    sid = str(student_id).strip().lower()
    return list(filter(lambda r: r["Student_ID"].strip().lower() == sid, records))

def get_all_student_ids(records=None, file_path=None):
    data = records if records is not None else load_students_data(file_path)
    seen = []
    for r in data:
        sid = r.get("Student_ID")
        if sid and sid not in seen:
            seen.append(sid)
    return seen

def find_student_recursive(records, student_id, index=0):
    if index >= len(records):
        return None
    if records[index].get("Student_ID", "").strip().lower() == str(student_id).strip().lower():
        return records[index]
    return find_student_recursive(records, student_id, index + 1)
