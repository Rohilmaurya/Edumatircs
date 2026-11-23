DEFAULT_FILE_PATH = "data/students_data.csv"
DEFAULT_SUBJECTS = ["Mathematics", "Physics", "Chemistry", "Computer_Science", "English"]


def get_csv_path():
    return DEFAULT_FILE_PATH


def initialize_csv(file_path=None):
    path = file_path if file_path else DEFAULT_FILE_PATH
    needs_init = False
    try:
        with open(path, "r") as f:
            content = f.read().strip()
            if not content:
                needs_init = True
    except FileNotFoundError:
        needs_init = True

    if needs_init:
        headers = ["Student_ID", "Name", "Batch", "Term"] + DEFAULT_SUBJECTS
        with open(path, "w") as f:
            f.write(",".join(headers) + "\n")
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
    path = file_path if file_path else DEFAULT_FILE_PATH
    try:
        with open(path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        initialize_csv(path)
        return []

    if not lines:
        return []

    header_line = lines[0].strip()
    if not header_line:
        return []

    header = [h.strip() for h in header_line.split(",")]
    subject_names = header[4:]

    records = []
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 4:
            continue
        item = {
            "Student_ID": parts[0],
            "Name": parts[1],
            "Batch": parts[2],
            "Term": parts[3]
        }
        for i, subj in enumerate(subject_names):
            idx = 4 + i
            if idx < len(parts) and parts[idx] != "":
                try:
                    item[subj] = float(parts[idx])
                except ValueError:
                    item[subj] = 0.0
            else:
                item[subj] = 0.0
        records.append(item)
    return records


def save_all_records(records, file_path=None):
    path = file_path if file_path else DEFAULT_FILE_PATH
    headers = ["Student_ID", "Name", "Batch", "Term"] + DEFAULT_SUBJECTS
    with open(path, "w") as f:
        f.write(",".join(headers) + "\n")
        for r in records:
            row = [
                str(r.get("Student_ID", "")),
                str(r.get("Name", "")),
                str(r.get("Batch", "")),
                str(r.get("Term", ""))
            ]
            for s in DEFAULT_SUBJECTS:
                val = r.get(s, 0.0)
                try:
                    f_val = float(val)
                    if f_val.is_integer():
                        row.append(str(int(f_val)))
                    else:
                        row.append(str(round(f_val, 2)))
                except (ValueError, TypeError):
                    row.append("0")
            f.write(",".join(row) + "\n")
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
