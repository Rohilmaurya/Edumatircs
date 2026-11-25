DEFAULT_SUBJECTS = ["Mathematics", "Physics", "Chemistry", "Computer_Science", "English"]
MAX_ROLL_NO_LENGTH = 4
MAX_NAME_LENGTH = 30
MAX_BATCH_LENGTH = 15
MAX_TERM_NUMBER = 99


def validate_roll_number(student_id):
    if student_id is None:
        return False, "Roll No. / Student ID cannot be empty."
    sid = str(student_id).strip()
    if not sid:
        return False, "Roll No. / Student ID cannot be empty."
    is_numeric = all("0" <= ch <= "9" for ch in sid)
    if not is_numeric and len(sid) > MAX_ROLL_NO_LENGTH:
        return False, "Roll No. / Student ID must be numeric and at most " + str(MAX_ROLL_NO_LENGTH) + " digits long."
    if not is_numeric:
        return False, "Roll No. / Student ID must be in numeric form (digits 0-9 only)."
    if len(sid) > MAX_ROLL_NO_LENGTH:
        return False, "Roll No. / Student ID cannot be more than " + str(MAX_ROLL_NO_LENGTH) + " digits long."
    return True, "Valid"


def validate_student_name(name):
    if name is None:
        return False, "Student Name cannot be empty."
    cleaned = " ".join(str(name).strip().split())
    if not cleaned:
        return False, "Student Name cannot be empty."
    if len(cleaned) > MAX_NAME_LENGTH:
        return False, "Student Name cannot exceed " + str(MAX_NAME_LENGTH) + " characters."
    has_letter = False
    for ch in cleaned:
        if ch.isalpha():
            has_letter = True
        elif ch not in (" ", ".", "'", "-"):
            return False, "Student Name must contain only letters and spaces (no numbers or special characters)."
    if not has_letter:
        return False, "Student Name must contain at least one letter."
    return True, "Valid"


def validate_batch(batch):
    if batch is None:
        return False, "Batch cannot be empty."
    cleaned = str(batch).strip()
    if not cleaned:
        return False, "Batch cannot be empty."
    if "," in cleaned:
        return False, "Batch cannot contain commas."
    if len(cleaned) > MAX_BATCH_LENGTH:
        return False, "Batch cannot exceed " + str(MAX_BATCH_LENGTH) + " characters."
    return True, "Valid"


def validate_and_format_term(term):
    if term is None:
        return False, "", "Term cannot be empty."
    raw = str(term).strip()
    if not raw:
        return False, "", "Term cannot be empty."
    parts = raw.split()
    if len(parts) != 2 or parts[0].lower() != "term":
        return False, "", "Term must be in 'Term <number>' format (e.g. Term 1, Term 2)."
    num_part = parts[1]
    if not all("0" <= ch <= "9" for ch in num_part):
        return False, "", "Term must be in 'Term <number>' format (e.g. Term 1, Term 2)."
    term_num = int(num_part)
    if term_num < 1 or term_num > MAX_TERM_NUMBER:
        return False, "", "Term number must be between 1 and " + str(MAX_TERM_NUMBER) + " (e.g. Term 1, Term 2)."
    return True, "Term " + str(term_num), "Valid"


def get_csv_path():
    try:
        with open("data/students_data.csv", "r"):
            return "data/students_data.csv"
    except Exception:
        pass
    base = __file__.replace("\\", "/").rsplit("/", 2)[0]
    return base + "/data/students_data.csv"


def initialize_csv(file_path=None):
    path = file_path if file_path else get_csv_path()
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


def validate_student_record(record, subjects=None, validate_identity=True):
    subj_list = subjects if subjects else DEFAULT_SUBJECTS
    required = ["Student_ID", "Name", "Batch", "Term"]
    for key in required:
        if key not in record or str(record[key]).strip() == "":
            return False, "Missing required field: " + str(key)
    if validate_identity:
        valid_id, id_msg = validate_roll_number(record["Student_ID"])
        if not valid_id:
            return False, id_msg
        valid_name, name_msg = validate_student_name(record["Name"])
        if not valid_name:
            return False, name_msg
        valid_batch, batch_msg = validate_batch(record["Batch"])
        if not valid_batch:
            return False, batch_msg
        valid_term, _, term_msg = validate_and_format_term(record["Term"])
        if not valid_term:
            return False, term_msg
    for s in subj_list:
        if s in record:
            try:
                score = float(record[s])
                if score < 0 or score > 100:
                    return False, "Marks must be between 0 and 100"
            except (ValueError, TypeError):
                return False, "Invalid number for " + s
    return True, "Valid"


def load_students_data(file_path=None):
    path = file_path if file_path else get_csv_path()
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
    path = file_path if file_path else get_csv_path()
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
    _, formatted_term, _ = validate_and_format_term(record["Term"])
    normalized = dict(record)
    normalized["Student_ID"] = str(record["Student_ID"]).strip()
    normalized["Name"] = " ".join(str(record["Name"]).strip().split())
    normalized["Batch"] = str(record["Batch"]).strip()
    normalized["Term"] = formatted_term
    records = load_students_data(file_path)
    sid = normalized["Student_ID"].lower()
    term = normalized["Term"].lower()
    for r in records:
        if r["Student_ID"].strip().lower() == sid and r["Term"].strip().lower() == term:
            return False, "Record already exists for this term"
    records.append(normalized)
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
            if "Name" in updated_fields:
                valid_name, name_msg = validate_student_name(r.get("Name"))
                if not valid_name:
                    return False, name_msg
                r["Name"] = " ".join(str(r["Name"]).strip().split())
            if "Batch" in updated_fields:
                valid_batch, batch_msg = validate_batch(r.get("Batch"))
                if not valid_batch:
                    return False, batch_msg
                r["Batch"] = str(r["Batch"]).strip()
            is_valid, msg = validate_student_record(r, validate_identity=False)
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
