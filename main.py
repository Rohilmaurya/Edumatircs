from modules.data_management import (
    initialize_csv,
    load_students_data,
    add_student_record,
    update_student_record,
    delete_student_record,
    get_student_records,
    get_all_student_ids,
    find_student_recursive,
    DEFAULT_SUBJECTS
)
from modules.grades_and_averages import (
    compute_student_term_average,
    compute_student_overall_summary,
    compute_class_subject_averages,
    compute_class_overall_average,
    compute_grade_distribution,
    assign_grade
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
from modules.summary_and_output import (
    get_class_leaderboard,
    generate_student_report_card,
    generate_class_summary_report
)

def clear_screen():
    print("\033[H\033[J", end="")

def display_menu():
    print("\n" + "=" * 65)
    print("      STUDENT PERFORMANCE ANALYSIS SYSTEM - 2026CSAE100")
    print("               Bennett University - Batch 56 / S28")
    print("=" * 65)
    print("  [1] View All Student Records")
    print("  [2] Add New Student Record")
    print("  [3] Update Student Record")
    print("  [4] Delete Student Record")
    print("  [5] Search Student Record (Recursive Search)")
    print("  [6] Student Averages & Grades")
    print("  [7] Diagnose Weak Areas (Dual Benchmark)")
    print("  [8] Multi-Term Trend Detection")
    print("  [9] Class Summary & Report Card Export")
    print("  [0] Exit Application")
    print("=" * 65)

def get_float_input(prompt, min_val=0.0, max_val=100.0):
    while True:
        val_str = input(prompt).strip()
        try:
            val = float(val_str)
            if min_val <= val <= max_val:
                return val
            print("Value must be between " + str(min_val) + " and " + str(max_val) + ". Please retry.")
        except ValueError:
            print("Invalid number entered. Please enter a valid numerical value.")

def handle_view_all():
    records = load_students_data()
    if not records:
        print("\nNo student records found in the database.")
        return
    print("\n" + "-" * 115)
    header = (
        "ID".ljust(15) +
        "Name".ljust(20) +
        "Batch".ljust(10) +
        "Term".ljust(10) +
        "Math".rjust(7) +
        "Phys".rjust(7) +
        "Chem".rjust(7) +
        "CS".rjust(7) +
        "Eng".rjust(7) +
        "Avg".rjust(9) +
        "Grade".rjust(8)
    )
    print(header)
    print("-" * 115)
    for r in records:
        avg_res = compute_student_term_average(r)
        row = (
            str(r.get("Student_ID", "")).ljust(15) +
            str(r.get("Name", ""))[:18].ljust(20) +
            str(r.get("Batch", "")).ljust(10) +
            str(r.get("Term", "")).ljust(10) +
            str(int(r.get("Mathematics", 0))).rjust(7) +
            str(int(r.get("Physics", 0))).rjust(7) +
            str(int(r.get("Chemistry", 0))).rjust(7) +
            str(int(r.get("Computer_Science", 0))).rjust(7) +
            str(int(r.get("English", 0))).rjust(7) +
            (str(avg_res["Average"]) + "%").rjust(9) +
            str(avg_res["Overall_Grade"]).rjust(8)
        )
        print(row)
    print("-" * 115)
    print("Total Records Displayed: " + str(len(records)))

def handle_add_record():
    print("\n--- Add New Student Record ---")
    sid = input("Enter Student ID (e.g. S26CSEU1936 or 1936): ").strip()
    if not sid:
        print("Student ID cannot be empty.")
        return
    name = input("Enter Student Name: ").strip()
    if not name:
        print("Student Name cannot be empty.")
        return
    batch = input("Enter Batch (Default: 56-S28): ").strip()
    if not batch:
        batch = "56-S28"
    term = input("Enter Term (e.g. Term 1, Term 2, Term 3): ").strip()
    if not term:
        print("Term cannot be empty.")
        return
    
    existing = get_student_records(sid)
    for r in existing:
        if r.get("Term", "").strip().lower() == term.lower():
            print("Error: Record for student " + sid + " in " + term + " already exists.")
            return

    new_rec = {
        "Student_ID": sid,
        "Name": name,
        "Batch": batch,
        "Term": term
    }
    for s in DEFAULT_SUBJECTS:
        score = get_float_input("Enter marks for " + s + " (0-100): ")
        new_rec[s] = score

    success, msg = add_student_record(new_rec)
    if success:
        print("\nSuccess: " + msg)
    else:
        print("\nFailed: " + msg)

def handle_update_record():
    print("\n--- Update Student Record ---")
    sid = input("Enter Student ID to update: ").strip()
    if not sid:
        print("Student ID cannot be empty.")
        return
    existing = get_student_records(sid)
    if not existing:
        print("No student found with ID: " + sid)
        return
    print("\nTerms available for " + sid + ":")
    for r in existing:
        print("  - " + r.get("Term", ""))
    term = input("Enter Term to update: ").strip()
    target_rec = None
    for r in existing:
        if r.get("Term", "").strip().lower() == term.lower():
            target_rec = r
            break
    if not target_rec:
        print("Term '" + term + "' not found for student " + sid)
        return

    print("\nCurrent marks for " + target_rec.get("Name", sid) + " (" + term + "):")
    updated_fields = {}
    for s in DEFAULT_SUBJECTS:
        current_val = target_rec.get(s, 0.0)
        user_input = input("Enter new marks for " + s + " [Current: " + str(current_val) + "] (Press Enter to keep): ").strip()
        if user_input != "":
            try:
                new_val = float(user_input)
                if 0 <= new_val <= 100:
                    updated_fields[s] = new_val
                else:
                    print("Invalid range. Keeping previous value: " + str(current_val))
            except ValueError:
                print("Invalid input. Keeping previous value: " + str(current_val))
    if not updated_fields:
        print("No fields updated.")
        return
    success, msg = update_student_record(sid, term, updated_fields)
    if success:
        print("\nSuccess: " + msg)
    else:
        print("\nFailed: " + msg)

def handle_delete_record():
    print("\n--- Delete Student Record ---")
    sid = input("Enter Student ID to delete: ").strip()
    if not sid:
        print("Student ID cannot be empty.")
        return
    existing = get_student_records(sid)
    if not existing:
        print("No student found with ID: " + sid)
        return
    print("\nFound " + str(len(existing)) + " record(s) for " + sid + ":")
    for r in existing:
        print("  - Term: " + r.get("Term", "") + " | Batch: " + r.get("Batch", ""))
    term_input = input("\nEnter specific Term to delete (or press Enter to delete ALL records of this student): ").strip()
    confirm = input("Are you sure you want to proceed with deletion? (y/n): ").strip().lower()
    if confirm != "y":
        print("Deletion cancelled.")
        return
    target_term = term_input if term_input != "" else None
    success, msg = delete_student_record(sid, term=target_term)
    if success:
        print("\nSuccess: " + msg)
    else:
        print("\nFailed: " + msg)

def handle_search_record():
    print("\n--- Search Student Record (Recursive Search) ---")
    sid = input("Enter Student ID to search: ").strip()
    if not sid:
        print("Student ID cannot be empty.")
        return
    records = load_students_data()
    found_rec = find_student_recursive(records, sid)
    if not found_rec:
        print("No record found matching Student ID: " + sid)
        return
    print("\n[RECURSIVE SEARCH RESULT - MATCH FOUND]")
    print("Student ID : " + str(found_rec.get("Student_ID")))
    print("Name       : " + str(found_rec.get("Name")))
    print("Batch      : " + str(found_rec.get("Batch")))
    all_terms = get_student_records(sid)
    print("\nAll Recorded Terms (" + str(len(all_terms)) + "):")
    for t in all_terms:
        term_res = compute_student_term_average(t)
        print("  - " + str(t.get("Term")).ljust(10) + " Average: " + (str(term_res["Average"]) + "%").ljust(8) + " Grade: " + str(term_res["Overall_Grade"]))

def handle_averages_and_grades():
    print("\n--- Student Averages & Grades ---")
    choice = input("Enter Student ID (or type 'ALL' to view cohort summary): ").strip()
    if not choice:
        print("Input cannot be empty.")
        return
    records = load_students_data()
    if choice.upper() == "ALL":
        leaderboard = get_class_leaderboard(records, top_n=len(records))
        print("\n" + "-" * 75)
        print("Rank".ljust(6) + "ID".ljust(15) + "Name".ljust(22) + "Average".rjust(10) + "CGPA".rjust(8) + "Grade".rjust(8))
        print("-" * 75)
        for idx, sm in enumerate(leaderboard["All_Ranked"], 1):
            row = (
                str(idx).ljust(6) +
                str(sm["Student_ID"]).ljust(15) +
                str(sm["Name"])[:20].ljust(22) +
                (str(sm["Overall_Average"]) + "%").rjust(10) +
                str(sm["CGPA"]).rjust(8) +
                str(sm["Overall_Grade"]).rjust(8)
            )
            print(row)
        print("-" * 75)
        return

    s_recs = get_student_records(choice)
    if not s_recs:
        print("No student found with ID: " + choice)
        return
    summary = compute_student_overall_summary(s_recs)
    print("\n" + "=" * 60)
    print("ACADEMIC PERFORMANCE SUMMARY: " + str(summary["Name"]) + " (" + str(summary["Student_ID"]) + ")")
    print("=" * 60)
    print("Batch            : " + str(summary["Batch"]))
    print("Terms Completed  : " + str(summary["Terms_Analyzed"]))
    print("Overall Average  : " + str(summary["Overall_Average"]) + "%")
    print("Cumulative GPA   : " + str(summary["CGPA"]))
    print("Overall Grade    : " + str(summary["Overall_Grade"]) + " (" + str(summary["Remark"]) + ")")
    print("-" * 60)
    print("Subject-wise Cumulative Averages:")
    for subj, avg in summary["Subject_Averages"].items():
        g_info = assign_grade(avg)
        print("  " + subj.ljust(18) + ": " + (str(avg) + "%").ljust(8) + " Grade: " + g_info["grade"])
    print("-" * 60)
    print("Term Breakdown:")
    for t_res in summary["Term_Details"]:
        print("  * " + str(t_res["Term"]).ljust(10) + " Total: " + str(t_res["Total_Marks"]) + "/" + str(t_res["Max_Marks"]) + " | Avg: " + str(t_res["Average"]) + "% | Grade: " + t_res["Overall_Grade"])
    print("=" * 60)

def handle_weak_areas():
    print("\n--- Diagnose Weak Areas (Dual Benchmark) ---")
    sid = input("Enter Student ID to diagnose: ").strip()
    if not sid:
        print("Student ID cannot be empty.")
        return
    all_records = load_students_data()
    s_recs = get_student_records(sid)
    if not s_recs:
        print("No student found with ID: " + sid)
        return
    s_recs = sorted(s_recs, key=lambda r: extract_term_number(r.get("Term", "")))
    target_rec = s_recs[-1]
    if len(s_recs) > 1:
        print("\nMultiple terms found for " + sid + ":")
        for idx, r in enumerate(s_recs, 1):
            print("  [" + str(idx) + "] " + r.get("Term", ""))
        pick = input("Select term number (Press Enter for latest - " + target_rec.get("Term", "") + "): ").strip()
        if pick != "":
            try:
                pick_idx = int(pick) - 1
                if 0 <= pick_idx < len(s_recs):
                    target_rec = s_recs[pick_idx]
            except ValueError:
                pass

    analysis = analyze_student_weak_areas(target_rec, all_records)
    print("\n" + "=" * 68)
    print("WEAK AREA DIAGNOSTICS: " + str(analysis["Name"]) + " (" + str(analysis["Student_ID"]) + ")")
    print("Term Evaluated   : " + str(analysis["Term"]))
    print("Term Average     : " + str(analysis["Student_Average"]) + "%")
    print("Academic Status  : " + str(analysis["Academic_Standing"]))
    print("=" * 68)
    print("\nDetailed Diagnostic Matrix:")
    print("Subject".ljust(18) + "Score".rjust(7) + "ClassAvg".rjust(10) + "PersonalGap".rjust(13) + "Severity".rjust(20))
    print("-" * 68)
    for d in analysis["All_Diagnostics"]:
        row = (
            d["subject"].ljust(18) +
            str(d["score"]).rjust(7) +
            str(d["class_avg"]).rjust(10) +
            str(d["personal_gap"]).rjust(13) +
            d["severity"].rjust(20)
        )
        print(row)
    print("-" * 68)
    flagged = analysis["Flagged_Weak_Areas"]
    if flagged:
        print("\nSpecific Actionable Recommendations:")
        for w in flagged:
            print("  * [" + w["severity"] + "] " + w["subject"] + ": " + w["recommendation"])
    else:
        print("\nExceptional Performance: No weak areas flagged for this term!")
    print("=" * 68)

def handle_trend():
    print("\n--- Multi-Term Trend Detection ---")
    sid = input("Enter Student ID (or type 'COHORT' to view cohort progression): ").strip()
    if not sid:
        print("Input cannot be empty.")
        return
    all_records = load_students_data()
    if sid.upper() == "COHORT":
        cohort_res = compute_cohort_term_trends(all_records)
        terms = cohort_res.get("Sorted_Terms", [])
        if len(terms) < 2:
            print("Need at least 2 distinct terms across the cohort for trend analysis.")
            return
        print("\nCohort Subject Progression (" + terms[0] + " to " + terms[-1] + "):")
        print("Subject".ljust(18) + "First Term".rjust(12) + "Latest Term".rjust(14) + "Delta".rjust(9) + "Trend".rjust(12))
        print("-" * 65)
        for s, p in cohort_res.get("Progression", {}).items():
            row = (
                s.ljust(18) +
                str(p["First_Term"]).rjust(12) +
                str(p["Latest_Term"]).rjust(14) +
                (str(p["Delta"]) if p["Delta"] <= 0 else "+" + str(p["Delta"])).rjust(9) +
                p["Classification"].rjust(12)
            )
            print(row)
        print("-" * 65)
        return

    s_recs = get_student_records(sid)
    if not s_recs:
        print("No student found with ID: " + sid)
        return
    trend = analyze_student_trend(s_recs)
    if trend.get("terms_count", 0) < 2:
        print("\nStudent has only 1 term on record.")
        print("Multi-term trend detection requires at least 2 terms.")
        first_t = s_recs[0]
        avg_res = compute_student_term_average(first_t)
        print("Current Record: " + first_t.get("Term", "") + " with average " + str(avg_res["Average"]) + "% (" + avg_res["Overall_Grade"] + ").")
        return

    print("\n" + "=" * 65)
    print("MULTI-TERM TREND REPORT: " + str(trend["Name"]) + " (" + str(trend["Student_ID"]) + ")")
    print("=" * 65)
    print("Terms Analyzed    : " + ", ".join(trend["Term_Labels"]))
    print("Initial Average   : " + str(trend["Initial_Average"]) + "%")
    print("Latest Average    : " + str(trend["Latest_Average"]) + "%")
    delta_str = "+" + str(trend["Overall_Average_Delta"]) if trend["Overall_Average_Delta"] > 0 else str(trend["Overall_Average_Delta"])
    print("Net Score Delta   : " + delta_str + " marks")
    print("Overall Direction : " + str(trend["Overall_Trajectory"]))
    print("-" * 65)
    print("Subject-by-Subject Trajectory:")
    print("Subject".ljust(18) + "Initial".rjust(9) + "Latest".rjust(9) + "Delta".rjust(9) + "Trajectory".rjust(14))
    print("-" * 65)
    for s, st in trend["Subject_Trends"].items():
        s_delta = "+" + str(st["Delta"]) if st["Delta"] > 0 else str(st["Delta"])
        row = (
            s.ljust(18) +
            str(st["Initial_Score"]).rjust(9) +
            str(st["Latest_Score"]).rjust(9) +
            s_delta.rjust(9) +
            st["Classification"].rjust(14)
        )
        print(row)
    print("=" * 65)

def handle_summary_and_export():
    print("\n--- Class Summary & Report Card Export ---")
    all_records = load_students_data()
    if not all_records:
        print("No student records available.")
        return
    report_text = generate_class_summary_report(all_records, save_to_file=True)
    print("\n" + report_text)
    print("\n[EXPORT COMPLETED] Full summary written to: data/student_analysis_report.txt")
    export_card = input("\nWould you like to export an individual student's report card to a text file? (y/n): ").strip().lower()
    if export_card == "y":
        sid = input("Enter Student ID: ").strip()
        card_text = generate_student_report_card(sid, all_records)
        print("\n" + card_text)
        card_filename = "data/report_card_" + sid + ".txt"
        try:
            with open(card_filename, "w") as f:
                f.write(card_text)
        except Exception:
            base = __file__.replace("\\", "/").rsplit("/", 1)[0]
            card_filename = base + "/data/report_card_" + sid + ".txt"
            with open(card_filename, "w") as f:
                f.write(card_text)
        print("\n[EXPORT COMPLETED] Student report card written to: " + card_filename)

def main():
    initialize_csv()
    while True:
        display_menu()
        choice = input("\nEnter your choice (0-9): ").strip()
        if choice == "1":
            handle_view_all()
        elif choice == "2":
            handle_add_record()
        elif choice == "3":
            handle_update_record()
        elif choice == "4":
            handle_delete_record()
        elif choice == "5":
            handle_search_record()
        elif choice == "6":
            handle_averages_and_grades()
        elif choice == "7":
            handle_weak_areas()
        elif choice == "8":
            handle_trend()
        elif choice == "9":
            handle_summary_and_export()
        elif choice == "0":
            print("\nThank you for using the Student Performance Analysis System. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please enter a number between 0 and 9.")
        input("\nPress Enter to return to main menu...")

if __name__ == "__main__":
    main()
