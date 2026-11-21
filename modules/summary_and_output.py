import math
import os
from modules.data_management import (
    load_students_data,
    get_all_student_ids,
    get_student_records,
    DEFAULT_SUBJECTS
)
from modules.grades_and_averages import (
    compute_student_overall_summary,
    compute_class_subject_averages,
    compute_class_overall_average,
    compute_grade_distribution
)
from modules.weak_areas import (
    analyze_student_weak_areas,
    get_class_weakness_heatmap
)
from modules.trend_detection import (
    analyze_student_trend,
    compute_cohort_term_trends,
    extract_term_number
)

def compute_subject_statistics(records, subject):
    scores = []
    for r in records:
        if subject in r:
            scores.append(float(r[subject]))
    if not scores:
        return {"Subject": subject, "Count": 0, "Mean": 0.0, "Median": 0.0, "Std_Dev": 0.0, "Min": 0.0, "Max": 0.0, "Pass_Rate": 0.0}
        
    scores.sort()
    n = len(scores)
    mean = sum(scores) / n
    
    if n % 2 == 1:
        median = scores[n // 2]
    else:
        median = (scores[n // 2 - 1] + scores[n // 2]) / 2.0
        
    variance = sum((x - mean) ** 2 for x in scores) / n
    std_dev = math.sqrt(variance)
    
    passed = len(list(filter(lambda x: x >= 50.0, scores)))
    pass_rate = (passed / n) * 100.0
    
    return {
        "Subject": subject,
        "Count": n,
        "Mean": round(mean, 2),
        "Median": round(median, 2),
        "Std_Dev": round(std_dev, 2),
        "Min": round(min(scores), 2),
        "Max": round(max(scores), 2),
        "Pass_Rate": round(pass_rate, 2)
    }

def compute_all_subjects_statistics(records):
    return {s: compute_subject_statistics(records, s) for s in DEFAULT_SUBJECTS}

def get_class_leaderboard(records, top_n=3):
    student_ids = get_all_student_ids(records=records)
    student_summaries = []
    for sid in student_ids:
        s_recs = list(filter(lambda r: r["Student_ID"] == sid, records))
        if s_recs:
            student_summaries.append(compute_student_overall_summary(s_recs))
            
    sorted_students = sorted(student_summaries, key=lambda s: s["Overall_Average"], reverse=True)
    count = len(sorted_students)
    limit = min(top_n, count)
    
    top = sorted_students[:limit]
    lowest = list(reversed(sorted_students[-limit:])) if count > 0 else []
    return {
        "Total_Students": count,
        "Top_Performers": top,
        "Lowest_Performers": lowest,
        "All_Ranked": sorted_students
    }

def generate_student_report_card(student_id, all_records=None):
    records = all_records if all_records is not None else load_students_data()
    sid = str(student_id).strip().lower()
    s_recs = list(filter(lambda r: r["Student_ID"].strip().lower() == sid, records))
    if not s_recs:
        return "Student not found with ID: " + str(student_id)
        
    s_recs = sorted(s_recs, key=lambda r: extract_term_number(r.get("Term", "")))
    summary = compute_student_overall_summary(s_recs)
    trend = analyze_student_trend(s_recs)
    latest_rec = s_recs[-1]
    weak_analysis = analyze_student_weak_areas(latest_rec, records)
    
    lines = []
    lines.append("=" * 68)
    lines.append("           STUDENT ACADEMIC PERFORMANCE REPORT")
    lines.append("             Bennett University - 2026CSAE100")
    lines.append("=" * 68)
    lines.append("ID   : " + str(summary["Student_ID"]) + " | Name: " + str(summary["Name"]) + " | Batch: " + str(summary["Batch"]))
    lines.append("Avg  : " + str(summary["Overall_Average"]) + "% | CGPA: " + str(summary["CGPA"]) + " | Grade: " + str(summary["Overall_Grade"]))
    lines.append("-" * 68)
    lines.append("\n[TERM WISE BREAKDOWN]")
    for t in summary["Term_Details"]:
        lines.append("Term: " + str(t["Term"]) + " | Average: " + str(t["Average"]) + "% | Grade: " + str(t["Overall_Grade"]))
        for subj, info in t["Subject_Scores"].items():
            lines.append("  " + str(subj).ljust(18) + ": " + str(info["score"]) + " (Grade " + str(info["grade"]) + ")")
            
    lines.append("\n[TREND ANALYSIS]")
    lines.append("Trajectory : " + str(trend.get("Overall_Trajectory", "N/A")))
    lines.append("Delta      : " + str(trend.get("Overall_Average_Delta", 0.0)) + " marks")
    for subj, t_data in trend.get("Subject_Trends", {}).items():
        lines.append("  " + str(subj).ljust(18) + ": " + str(t_data["Initial_Score"]) + " to " + str(t_data["Latest_Score"]) + " (" + str(t_data["Classification"]) + ")")
        
    lines.append("\n[WEAK AREA AUDIT]")
    lines.append("Standing: " + str(weak_analysis.get("Academic_Standing", "N/A")))
    flagged = weak_analysis.get("Flagged_Weak_Areas", [])
    if flagged:
        for w in flagged:
            lines.append("  * " + str(w["subject"]) + " (" + str(w["severity"]) + "): " + str(w["recommendation"]))
    else:
        lines.append("  * No weak areas identified. Great performance!")
    lines.append("=" * 68)
    return "\n".join(lines)

def generate_class_summary_report(all_records=None, save_to_file=True):
    records = all_records if all_records is not None else load_students_data()
    if not records:
        return "No student records available."
        
    leaderboard = get_class_leaderboard(records, top_n=3)
    subject_stats = compute_all_subjects_statistics(records)
    grade_dist = compute_grade_distribution(records)
    heatmap = get_class_weakness_heatmap(records)
    overall_avg = compute_class_overall_average(records)
    
    lines = []
    lines.append("*" * 72)
    lines.append("                   BENNETT UNIVERSITY")
    lines.append("         Computational Thinking and Programming (2026CSAE100)")
    lines.append("             STUDENT PERFORMANCE ANALYSIS SYSTEM REPORT")
    lines.append("*" * 72)
    lines.append("Cohort Size : " + str(leaderboard["Total_Students"]) + " students")
    lines.append("Total Rows  : " + str(len(records)) + " term records")
    lines.append("Class Mean  : " + str(overall_avg) + "%")
    lines.append("-" * 72)
    lines.append("\n1. TOP PERFORMERS:")
    for idx, s in enumerate(leaderboard["Top_Performers"], 1):
        lines.append("   " + str(idx) + ". " + str(s["Name"]).ljust(18) + " (ID: " + str(s["Student_ID"]) + ") - Avg: " + str(s["Overall_Average"]) + "% | CGPA: " + str(s["CGPA"]) + " | Grade: " + str(s["Overall_Grade"]))
        
    lines.append("\n2. LOWEST PERFORMERS (ACADEMIC INTERVENTION):")
    for idx, s in enumerate(leaderboard["Lowest_Performers"], 1):
        lines.append("   " + str(idx) + ". " + str(s["Name"]).ljust(18) + " (ID: " + str(s["Student_ID"]) + ") - Avg: " + str(s["Overall_Average"]) + "% | CGPA: " + str(s["CGPA"]) + " | Grade: " + str(s["Overall_Grade"]))
        
    lines.append("\n3. SUBJECT STATISTICS:")
    for s, stat in subject_stats.items():
        lines.append("   " + str(s).ljust(18) + " Mean: " + str(stat["Mean"]) + " | Median: " + str(stat["Median"]) + " | StdDev: " + str(stat["Std_Dev"]) + " | Pass Rate: " + str(stat["Pass_Rate"]) + "%")
        
    lines.append("\n4. GRADE DISTRIBUTION:")
    for g, c in grade_dist.items():
        lines.append("   Grade " + str(g).ljust(3) + ": " + str(c) + " students")
        
    lines.append("\n5. SUBJECT DIFFICULTY & VULNERABILITY:")
    for s, h in heatmap.items():
        lines.append("   " + str(s).ljust(18) + " Below 50%: " + str(h["Failing_Percentage"]) + "% | Difficulty: " + str(h["Difficulty_Level"]))
    lines.append("*" * 72)
    
    report_text = "\n".join(lines)
    if save_to_file:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        out_path = os.path.join(base_dir, "data", "student_analysis_report.txt")
        with open(out_path, "w") as f:
            f.write(report_text)
            
    return report_text
