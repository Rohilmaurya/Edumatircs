from modules.data_management import DEFAULT_SUBJECTS
from modules.grades_and_averages import compute_student_term_average, compute_class_subject_averages

def analyze_student_weak_areas(record, all_class_records, subjects=None):
    subj_list = subjects if subjects else DEFAULT_SUBJECTS
    term = record.get("Term", "")
    student_stats = compute_student_term_average(record, subj_list)
    student_avg = student_stats["Average"]
    
    class_subject_avgs = compute_class_subject_averages(all_class_records, term=term)
    
    diagnostics = []
    critical_count = 0
    moderate_count = 0
    
    for s in subj_list:
        score = float(record.get(s, 0.0))
        class_avg = class_subject_avgs.get(s, 0.0)
        
        personal_gap = round(student_avg - score, 2)
        peer_gap = round(class_avg - score, 2)
        
        is_below_personal = score < (student_avg - 1.0)
        is_below_class = score < class_avg
        
        if is_below_personal and is_below_class:
            severity = "CRITICAL WEAKNESS"
            category = "Critical"
            critical_count += 1
            recommendation = "Score (" + str(score) + ") is below both personal standard and class average. Needs urgent revision."
        elif is_below_class and not is_below_personal:
            severity = "PEER DEFICIT"
            category = "Peer Deficit"
            moderate_count += 1
            recommendation = "Score (" + str(score) + ") matches personal average but lags class average (" + str(class_avg) + "). Recommended peer study."
        elif is_below_personal and not is_below_class:
            severity = "UNDERPERFORMING"
            category = "Underperforming"
            moderate_count += 1
            recommendation = "Score (" + str(score) + ") is above class average but below personal capability (" + str(student_avg) + ")."
        else:
            severity = "STRONG / ON TRACK"
            category = "Strong"
            recommendation = "Consistent strong performance in " + str(s) + "."
            
        diagnostics.append({
            "subject": s,
            "score": score,
            "personal_avg": student_avg,
            "class_avg": class_avg,
            "personal_gap": personal_gap,
            "peer_gap": peer_gap,
            "severity": severity,
            "category": category,
            "recommendation": recommendation
        })
        
    flagged_list = list(filter(lambda d: d["category"] != "Strong", diagnostics))
    strong_list = list(filter(lambda d: d["category"] == "Strong", diagnostics))
    
    if critical_count >= 2:
        status = "High Academic Risk"
    elif critical_count == 1 or moderate_count >= 2:
        status = "Moderate Attention Needed"
    elif moderate_count == 1:
        status = "Minor Remediation Needed"
    else:
        status = "Satisfactory / Strong Performance"
        
    return {
        "Student_ID": record.get("Student_ID"),
        "Name": record.get("Name"),
        "Term": term,
        "Student_Average": student_avg,
        "Academic_Standing": status,
        "Critical_Count": critical_count,
        "Moderate_Count": moderate_count,
        "Flagged_Weak_Areas": flagged_list,
        "Strong_Areas": strong_list,
        "All_Diagnostics": diagnostics
    }

def get_class_weakness_heatmap(all_records):
    if not all_records:
        return {}
    subj_list = DEFAULT_SUBJECTS
    class_avgs = compute_class_subject_averages(all_records)
    total_entries = len(all_records)
    heatmap = {}
    
    for s in subj_list:
        below_50 = 0
        below_avg = 0
        for r in all_records:
            val = float(r.get(s, 0.0))
            if val < 50.0:
                below_50 += 1
            if val < class_avgs.get(s, 0.0):
                below_avg += 1
        pct_failing = round((below_50 / total_entries) * 100, 1) if total_entries > 0 else 0.0
        pct_below = round((below_avg / total_entries) * 100, 1) if total_entries > 0 else 0.0
        
        diff = "Low"
        if pct_failing >= 20.0 or pct_below >= 50.0:
            diff = "High"
        elif pct_failing >= 10.0 or pct_below >= 35.0:
            diff = "Moderate"
            
        heatmap[s] = {
            "Subject": s,
            "Class_Average": class_avgs.get(s, 0.0),
            "Failing_Count": below_50,
            "Failing_Percentage": pct_failing,
            "Below_Avg_Percentage": pct_below,
            "Difficulty_Level": diff
        }
    return heatmap
