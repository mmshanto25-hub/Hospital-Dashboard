"""
tests/test_phase123.py
Automated validation test for Phase 1, Phase 2, and Phase 3:
- Verifies Excel loading and schema integrity (Phase 1 & 2)
- Verifies all analytical calculation formulas against Excel raw ground truth (Phase 3)
- Verifies edge case safety (zero division, empty DataFrames, missing filters)
"""

import unittest
import pandas as pd
from utils.data_loader import (
    load_excel_data,
    load_patients,
    load_doctors,
    load_nurses,
    load_daily_staffing,
    load_departments
)
import utils.calculations as calc


class TestHospitalDataAndCalculations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = load_excel_data()
        cls.patients = cls.data["Patients"]
        cls.doctors = cls.data["Doctors"]
        cls.nurses = cls.data["Nurses"]
        cls.staffing = cls.data["Daily_Staffing"]
        cls.departments = cls.data["Departments"]

    # --- PHASE 1 & 2: Data Loader & Integrity Tests ---

    def test_sheets_present(self):
        expected_sheets = ["Patients", "Doctors", "Nurses", "Daily_Staffing", "Departments"]
        for s in expected_sheets:
            self.assertIn(s, self.data)

    def test_patients_row_count_and_columns(self):
        self.assertEqual(len(self.patients), 6000)
        self.assertIn("Patient_ID", self.patients.columns)
        self.assertIn("Admission_Date", self.patients.columns)
        self.assertIn("Discharge_Date", self.patients.columns)
        self.assertEqual(self.patients["Patient_ID"].nunique(), 6000)

    def test_doctors_row_count_and_columns(self):
        self.assertEqual(len(self.doctors), 180)
        self.assertEqual(self.doctors["Doctor_ID"].nunique(), 180)

    def test_nurses_row_count_and_columns(self):
        self.assertEqual(len(self.nurses), 480)
        self.assertEqual(self.nurses["Nurse_ID"].nunique(), 480)

    def test_daily_staffing_records(self):
        self.assertEqual(len(self.staffing), 4380)  # 365 days * 12 departments
        self.assertEqual(self.staffing["Department"].nunique(), 12)

    def test_departments_count(self):
        self.assertEqual(len(self.departments), 12)

    # --- PHASE 3: Calculations & KPI Formulas ---

    def test_total_patients(self):
        self.assertEqual(calc.get_total_patients(self.patients), 6000)

    def test_doctor_breakdown(self):
        breakdown = calc.get_doctor_status_breakdown(self.doctors)
        self.assertEqual(breakdown["total"], 180)
        self.assertEqual(breakdown["active"] + breakdown["on_leave"] + breakdown["inactive"], 180)

    def test_nurse_breakdown(self):
        breakdown = calc.get_nurse_status_breakdown(self.nurses)
        self.assertEqual(breakdown["total"], 480)
        self.assertEqual(breakdown["active"] + breakdown["on_leave"] + breakdown["inactive"], 480)

    def test_snapshot_metrics(self):
        latest_date = self.staffing["Date"].max()
        raw_snapshot = self.staffing[self.staffing["Date"] == latest_date]

        # Census
        expected_census = int(raw_snapshot["Daily_Patient_Census"].sum())
        self.assertEqual(calc.get_current_patient_census(self.staffing, date=latest_date), expected_census)

        # On duty doctors & nurses
        expected_docs = int(raw_snapshot["Active_Doctors_On_Duty"].sum())
        expected_nurses = int(raw_snapshot["Active_Nurses_On_Duty"].sum())
        self.assertEqual(calc.get_active_doctors(self.staffing, date=latest_date), expected_docs)
        self.assertEqual(calc.get_active_nurses(self.staffing, date=latest_date), expected_nurses)

        # Bed capacity, occupied, available
        expected_cap = int(raw_snapshot["Bed_Capacity"].sum())
        expected_occ = int(raw_snapshot["Occupied_Beds"].sum())
        self.assertEqual(calc.get_bed_capacity(self.staffing, date=latest_date), expected_cap)
        self.assertEqual(calc.get_occupied_beds(self.staffing, date=latest_date), expected_occ)
        self.assertEqual(calc.get_available_beds(self.staffing, date=latest_date), expected_cap - expected_occ)

        # Bed occupancy rate: Occupied / Capacity * 100
        expected_rate = round(expected_occ / expected_cap * 100, 2)
        self.assertEqual(calc.get_bed_occupancy_rate(self.staffing, date=latest_date), expected_rate)

        # Patients per doctor: Census / Doctors
        expected_p_per_doc = round(expected_census / expected_docs, 2)
        self.assertEqual(calc.get_patients_per_doctor(self.staffing, date=latest_date), expected_p_per_doc)

        # Patients per nurse: Census / Nurses
        expected_p_per_nurse = round(expected_census / expected_nurses, 2)
        self.assertEqual(calc.get_patients_per_nurse(self.staffing, date=latest_date), expected_p_per_nurse)

    def test_average_length_of_stay(self):
        expected_alos = round(float(self.patients["Length_of_Stay_Days"].mean()), 2)
        self.assertEqual(calc.get_average_length_of_stay(self.patients), expected_alos)

    def test_department_statistics_and_alerts(self):
        latest_date = self.staffing["Date"].max()
        dept_stats = calc.get_department_statistics(self.staffing, self.departments, date=latest_date)
        self.assertEqual(len(dept_stats), 12)

        alerts = calc.get_high_workload_departments(self.staffing, self.departments, date=latest_date)
        self.assertIn("high_doctor_load", alerts)
        self.assertIn("high_nurse_load", alerts)
        self.assertIn("high_occupancy", alerts)
        self.assertIn("critical_attention", alerts)

    def test_monthly_admissions_and_discharges(self):
        monthly = calc.get_monthly_admissions_and_discharges(self.patients)
        self.assertFalse(monthly.empty)
        self.assertEqual(monthly["Admissions"].sum(), 6000)
        # Discharges sum must equal non-null discharge dates (5244)
        valid_discharges = self.patients["Discharge_Date"].dropna().count()
        self.assertEqual(monthly["Discharges"].sum(), valid_discharges)

    def test_edge_cases(self):
        empty_df = pd.DataFrame()
        self.assertEqual(calc.get_total_patients(empty_df), 0)
        self.assertEqual(calc.get_current_patient_census(empty_df), 0)
        self.assertEqual(calc.get_bed_capacity(empty_df), 0)
        self.assertEqual(calc.get_occupied_beds(empty_df), 0)
        self.assertEqual(calc.get_bed_occupancy_rate(empty_df), 0.0)
        self.assertEqual(calc.get_patients_per_doctor(empty_df), 0.0)
        self.assertEqual(calc.get_patients_per_nurse(empty_df), 0.0)
        self.assertEqual(calc.get_average_length_of_stay(empty_df), 0.0)


if __name__ == "__main__":
    unittest.main()
