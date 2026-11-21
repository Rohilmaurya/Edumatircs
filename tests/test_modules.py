import os
import tempfile
import pytest

from modules.data_management import (
    initialize_csv,
    validate_student_record,
    load_students_data,
    add_student_record,
    update_student_record,
    delete_student_record,
    find_student_recursive
)
from modules.grades_and_averages import (
    recursive_sum,
    assign_grade,
    compute_student_term_average,
    compute_student_overall_summary,
    compute_class_subject_averages,
    compute_grade_distribution
)
from modules.weak_areas import (
    analyze_student_weak_areas,
    get_class_weakness_heatmap
)
from modules.trend_detection import (
    analyze_student_trend,
    compute_cohort_term_trends
)
from modules.summary_and_output import (
    compute_subject_statistics,
    get_class_leaderboard,
    generate_student_report_card,
    generate_class_summary_report
)

@pytest.fixture
def sample_records():
    return [
        {
            "Student_ID": "101",
            "Name": "Alice",
            "Batch": "56-S28",
            "Term": "Term 1",
            "Mathematics": 90.0,
            "Physics": 85.0,
            "Chemistry": 80.0,
            "Computer_Science": 95.0,
            "English": 90.0
        },
        {
            "Student_ID": "101",
            "Name": "Alice",
            "Batch": "56-S28",
            "Term": "Term 2",
            "Mathematics": 95.0,
            "Physics": 88.0,
            "Chemistry": 85.0,
            "Computer_Science": 98.0,
            "English": 92.0
        },
        {
            "Student_ID": "102",
            "Name": "Bob",
            "Batch": "56-S28",
            "Term": "Term 1",
            "Mathematics": 70.0,
            "Physics": 65.0,
            "Chemistry": 45.0,
            "Computer_Science": 80.0,
            "English": 75.0
        },
        {
            "Student_ID": "102",
            "Name": "Bob",
            "Batch": "56-S28",
            "Term": "Term 2",
            "Mathematics": 65.0,
            "Physics": 60.0,
            "Chemistry": 40.0,
            "Computer_Science": 75.0,
            "English": 70.0
        }
    ]

def test_validation():
    valid_rec = {
        "Student_ID": "1956",
        "Name": "Harshul Yadav",
        "Batch": "56-S28",
        "Term": "Term 1",
        "Mathematics": 85,
        "Physics": 90,
        "Chemistry": 80,
        "Computer_Science": 95,
        "English": 88
    }
    is_valid, msg = validate_student_record(valid_rec)
    assert is_valid is True

    invalid_rec = valid_rec.copy()
    invalid_rec["Mathematics"] = 105
    is_valid, msg = validate_student_record(invalid_rec)
    assert is_valid is False

def test_crud_and_recursive_search():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        temp_path = f.name
    try:
        initialize_csv(temp_path)
        rec = {
            "Student_ID": "999",
            "Name": "Test Student",
            "Batch": "56-S28",
            "Term": "Term 1",
            "Mathematics": 80.0,
            "Physics": 85.0,
            "Chemistry": 75.0,
            "Computer_Science": 90.0,
            "English": 85.0
        }
        success, msg = add_student_record(rec, temp_path)
        assert success is True
        loaded = load_students_data(temp_path)
        assert len(loaded) == 1
        found = find_student_recursive(loaded, "999", 0)
        assert found is not None
        assert found["Name"] == "Test Student"

        update_student_record("999", "Term 1", {"Mathematics": 95.0}, temp_path)
        loaded = load_students_data(temp_path)
        assert loaded[0]["Mathematics"] == 95.0

        delete_student_record("999", "Term 1", temp_path)
        loaded = load_students_data(temp_path)
        assert len(loaded) == 0
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_recursive_sum_and_grades():
    nums = [10.0, 20.0, 30.0]
    assert recursive_sum(nums) == 60.0
    assert assign_grade(95)["grade"] == "A+"
    assert assign_grade(85)["grade"] == "A"
    assert assign_grade(75)["grade"] == "B"
    assert assign_grade(65)["grade"] == "C"
    assert assign_grade(55)["grade"] == "D"
    assert assign_grade(45)["grade"] == "F"

def test_student_averages(sample_records):
    res = compute_student_term_average(sample_records[0])
    assert res["Average"] == 88.0
    alice_recs = [r for r in sample_records if r["Student_ID"] == "101"]
    summary = compute_student_overall_summary(alice_recs)
    assert summary["Overall_Average"] == 89.8

def test_weak_areas(sample_records):
    bob_t1 = sample_records[2]
    res = analyze_student_weak_areas(bob_t1, sample_records)
    flagged = [w["subject"] for w in res["Flagged_Weak_Areas"]]
    assert "Chemistry" in flagged

def test_trends(sample_records):
    alice_recs = [r for r in sample_records if r["Student_ID"] == "101"]
    trend = analyze_student_trend(alice_recs)
    assert trend["Overall_Trajectory"] == "Improving"

    bob_recs = [r for r in sample_records if r["Student_ID"] == "102"]
    trend_bob = analyze_student_trend(bob_recs)
    assert trend_bob["Overall_Trajectory"] == "Declining"

def test_summary_and_reports(sample_records):
    leaderboard = get_class_leaderboard(sample_records, top_n=1)
    assert leaderboard["Top_Performers"][0]["Student_ID"] == "101"
    card = generate_student_report_card("101", sample_records)
    assert "STUDENT ACADEMIC PERFORMANCE REPORT" in card
