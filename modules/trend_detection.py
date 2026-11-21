from modules.data_management import DEFAULT_SUBJECTS
from modules.grades_and_averages import compute_student_term_average

def extract_term_number(term_str):
    num_str = ""
    for ch in str(term_str):
        if ch.isdigit():
            num_str += ch
    return int(num_str) if num_str else 0

def analyze_student_trend(student_records, subjects=None):
    if not student_records:
        return {"terms_count": 0, "status": "No records found"}
        
    subj_list = subjects if subjects else DEFAULT_SUBJECTS
    sorted_records = sorted(student_records, key=lambda r: extract_term_number(r.get("Term", "")))
    terms_count = len(sorted_records)
    
    first = sorted_records[0]
    sid = first.get("Student_ID")
    name = first.get("Name")
    
    if terms_count < 2:
        return {
            "Student_ID": sid,
            "Name": name,
            "Terms_Count": terms_count,
            "terms_count": terms_count,
            "status": "Need at least 2 terms for trend analysis",
            "Subject_Trends": {},
            "Overall_Trajectory": "Single Term Only",
            "Overall_Delta": 0.0
        }
        
    term_labels = [r.get("Term", "") for r in sorted_records]
    term_averages = []
    subject_scores = {s: [] for s in subj_list}
    
    for r in sorted_records:
        res = compute_student_term_average(r, subj_list)
        term_averages.append(res["Average"])
        for s in subj_list:
            subject_scores[s].append(float(r.get(s, 0.0)))
            
    subject_trends = {}
    improving_count = 0
    declining_count = 0
    stable_count = 0
    
    for s in subj_list:
        scores = subject_scores[s]
        init_sc = scores[0]
        latest_sc = scores[-1]
        delta = round(latest_sc - init_sc, 2)
        
        if delta >= 3.0:
            classification = "Improving"
            improving_count += 1
        elif delta <= -3.0:
            classification = "Declining"
            declining_count += 1
        else:
            classification = "Stable"
            stable_count += 1
            
        spread = round(max(scores) - min(scores), 2)
        is_volatile = spread >= 15.0
        
        subject_trends[s] = {
            "Subject": s,
            "Initial_Score": init_sc,
            "Latest_Score": latest_sc,
            "Delta": delta,
            "Classification": classification,
            "Score_History": scores,
            "Spread": spread,
            "Is_Volatile": is_volatile
        }
        
    first_avg = term_averages[0]
    latest_avg = term_averages[-1]
    overall_avg_delta = round(latest_avg - first_avg, 2)
    
    if overall_avg_delta >= 3.0:
        overall_trajectory = "Improving"
    elif overall_avg_delta <= -3.0:
        overall_trajectory = "Declining"
    else:
        overall_trajectory = "Stable"
        
    return {
        "Student_ID": sid,
        "Name": name,
        "Terms_Count": terms_count,
        "terms_count": terms_count,
        "Term_Labels": term_labels,
        "Term_Averages": term_averages,
        "Initial_Average": first_avg,
        "Latest_Average": latest_avg,
        "Overall_Average_Delta": overall_avg_delta,
        "Overall_Trajectory": overall_trajectory,
        "Improving_Count": improving_count,
        "Declining_Count": declining_count,
        "Stable_Count": stable_count,
        "Subject_Trends": subject_trends
    }

def compute_cohort_term_trends(all_records):
    if not all_records:
        return {}
    subj_list = DEFAULT_SUBJECTS
    terms_dict = {}
    for r in all_records:
        t = r.get("Term", "Unknown")
        if t not in terms_dict:
            terms_dict[t] = []
        terms_dict[t].append(r)
        
    sorted_terms = sorted(terms_dict.keys(), key=lambda t: extract_term_number(t))
    term_subject_averages = {}
    
    for t in sorted_terms:
        recs = terms_dict[t]
        subj_sums = {s: 0.0 for s in subj_list}
        for r in recs:
            for s in subj_list:
                subj_sums[s] += float(r.get(s, 0.0))
        n = len(recs)
        term_subject_averages[t] = {s: round(subj_sums[s] / n, 2) if n > 0 else 0.0 for s in subj_list}
        
    progression = {}
    if len(sorted_terms) >= 2:
        t1 = sorted_terms[0]
        t2 = sorted_terms[-1]
        for s in subj_list:
            delta = round(term_subject_averages[t2][s] - term_subject_averages[t1][s], 2)
            progression[s] = {
                "First_Term": term_subject_averages[t1][s],
                "Latest_Term": term_subject_averages[t2][s],
                "Delta": delta,
                "Classification": "Improving" if delta >= 3.0 else ("Declining" if delta <= -3.0 else "Stable")
            }
            
    return {
        "Sorted_Terms": sorted_terms,
        "Term_Subject_Averages": term_subject_averages,
        "Progression": progression
    }
