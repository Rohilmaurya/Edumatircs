from modules.data_management import DEFAULT_SUBJECTS

def recursive_sum(numbers, index=0):
    if index >= len(numbers):
        return 0.0
    return numbers[index] + recursive_sum(numbers, index + 1)

def assign_grade(score):
    val = float(score)
    if val >= 90.0:
        return {"score": val, "grade": "A+", "grade_point": 10.0, "remark": "Outstanding"}
    elif val >= 80.0:
        return {"score": val, "grade": "A", "grade_point": 9.0, "remark": "Excellent"}
    elif val >= 70.0:
        return {"score": val, "grade": "B", "grade_point": 8.0, "remark": "Good"}
    elif val >= 60.0:
        return {"score": val, "grade": "C", "grade_point": 7.0, "remark": "Average"}
    elif val >= 50.0:
        return {"score": val, "grade": "D", "grade_point": 6.0, "remark": "Pass"}
    else:
        return {"score": val, "grade": "F", "grade_point": 0.0, "remark": "Needs Improvement / Fail"}

def compute_student_term_average(record, subjects=None):
    subj_list = subjects if subjects else DEFAULT_SUBJECTS
    scores = [float(record.get(s, 0.0)) for s in subj_list]
    total = recursive_sum(scores)
    count = len(subj_list)
    average = round(total / count, 2) if count > 0 else 0.0
    grade_info = assign_grade(average)
    
    subject_details = {}
    for s in subj_list:
        sc = float(record.get(s, 0.0))
        g = assign_grade(sc)
        subject_details[s] = {
            "score": sc,
            "grade": g["grade"],
            "grade_point": g["grade_point"],
            "remark": g["remark"]
        }
    
    return {
        "Student_ID": record.get("Student_ID"),
        "Name": record.get("Name"),
        "Batch": record.get("Batch"),
        "Term": record.get("Term"),
        "Total_Marks": round(total, 2),
        "Max_Marks": count * 100,
        "Average": average,
        "Overall_Grade": grade_info["grade"],
        "Grade_Point": grade_info["grade_point"],
        "Remark": grade_info["remark"],
        "Subject_Scores": subject_details
    }

def compute_student_overall_summary(student_records, subjects=None):
    if not student_records:
        return {}
    subj_list = subjects if subjects else DEFAULT_SUBJECTS
    term_count = len(student_records)
    
    term_results = []
    total_avg_sum = 0.0
    total_gp_sum = 0.0
    subj_totals = {s: 0.0 for s in subj_list}
    
    for r in student_records:
        res = compute_student_term_average(r, subj_list)
        term_results.append(res)
        total_avg_sum += res["Average"]
        total_gp_sum += res["Grade_Point"]
        for s in subj_list:
            subj_totals[s] += float(r.get(s, 0.0))
            
    overall_avg = round(total_avg_sum / term_count, 2) if term_count > 0 else 0.0
    cgpa = round(total_gp_sum / term_count, 2) if term_count > 0 else 0.0
    grade_info = assign_grade(overall_avg)
    
    subj_averages = {}
    for s in subj_list:
        subj_averages[s] = round(subj_totals[s] / term_count, 2)
        
    first = student_records[0]
    return {
        "Student_ID": first.get("Student_ID"),
        "Name": first.get("Name"),
        "Batch": first.get("Batch"),
        "Terms_Analyzed": term_count,
        "Overall_Average": overall_avg,
        "CGPA": cgpa,
        "Overall_Grade": grade_info["grade"],
        "Remark": grade_info["remark"],
        "Subject_Averages": subj_averages,
        "Term_Details": term_results
    }

def compute_class_subject_averages(records, term=None):
    if not records:
        return {}
    subj_list = DEFAULT_SUBJECTS
    filtered = records
    if term:
        filtered = list(filter(lambda r: r.get("Term", "").strip().lower() == str(term).strip().lower(), records))
    if not filtered:
        return {s: 0.0 for s in subj_list}
    
    sums = {s: 0.0 for s in subj_list}
    for r in filtered:
        for s in subj_list:
            sums[s] += float(r.get(s, 0.0))
            
    n = len(filtered)
    return {s: round(sums[s] / n, 2) for s in subj_list}

def compute_class_overall_average(records):
    if not records:
        return 0.0
    subj_list = DEFAULT_SUBJECTS
    total_score = 0.0
    total_count = 0
    for r in records:
        for s in subj_list:
            total_score += float(r.get(s, 0.0))
            total_count += 1
    return round(total_score / total_count, 2) if total_count > 0 else 0.0

def compute_grade_distribution(records):
    dist = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for r in records:
        res = compute_student_term_average(r)
        g = res["Overall_Grade"]
        if g in dist:
            dist[g] += 1
    return dist
