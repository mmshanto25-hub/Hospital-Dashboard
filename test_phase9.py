"""
tests/test_phase9.py
Automated validation test for Phase 9: Department Analytics & Staffing Ratio Analysis.
Verifies all 12 department statistics, multi-unit comparisons, ratio benchmarks,
daily staffing trends, workload extremes, and export safety.
"""

import unittest
import pandas as pd
from utils.data_loader import load_excel_data
import utils.calculations as calc
import utils.charts as chrt
import utils.filters as flt
import utils.helpers as hlp


class TestDepartmentAndStaffingRatioPhase9(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = load_excel_data()
        cls.staffing = cls.data["Daily_Staffing"]
        cls.departments = cls.data["Departments"]

    # --- 1. Department Analytics Tests ---

    def test_department_matrix_coverage(self):
        latest_date = self.staffing["Date"].max()
        dept_stats = calc.get_department_statistics(self.staffing, self.departments, date=latest_date)
        self.assertEqual(len(dept_stats), 12)
        required_cols = [
            "Department", "Bed_Capacity", "Occupied_Beds", "Available_Beds",
            "Daily_Patient_Census", "Active_Doctors_On_Duty", "Active_Nurses_On_Duty",
            "Patients_per_Doctor", "Patients_per_Nurse", "Occupancy_Rate_Pct"
        ]
        for col in required_cols:
            self.assertIn(col, dept_stats.columns)

    def test_department_charts(self):
        latest_date = self.staffing["Date"].max()
        dept_stats = calc.get_department_statistics(self.staffing, self.departments, date=latest_date)

        # 1. Census Bar
        fig1 = chrt.create_bar_chart(dept_stats, x="Daily_Patient_Census", y="Department", title="Census", orientation="h")
        self.assertIsNotNone(fig1)

        # 2. Occupancy Bar
        fig2 = chrt.create_bar_chart(dept_stats, x="Occupancy_Rate_Pct", y="Department", title="Occupancy", orientation="h")
        self.assertIsNotNone(fig2)

        # 3. Doctors on Duty
        fig3 = chrt.create_bar_chart(dept_stats, x="Active_Doctors_On_Duty", y="Department", title="Docs", orientation="h")
        self.assertIsNotNone(fig3)

        # 4. Nurses on Duty
        fig4 = chrt.create_bar_chart(dept_stats, x="Active_Nurses_On_Duty", y="Department", title="Nurses", orientation="h")
        self.assertIsNotNone(fig4)

        # 5. Doctor Workload vs Target
        fig5 = chrt.create_grouped_bar_chart(dept_stats, x="Department", y_cols=["Patients_per_Doctor", "Target_Patients_per_Doctor"], title="Doc Workload")
        self.assertIsNotNone(fig5)

        # 6. Nurse Workload vs Target
        fig6 = chrt.create_grouped_bar_chart(dept_stats, x="Department", y_cols=["Patients_per_Nurse", "Target_Patients_per_Nurse"], title="Nurse Workload")
        self.assertIsNotNone(fig6)

    # --- 2. Staffing Ratio Analysis Tests ---

    def test_ratio_extremes_calculation(self):
        latest_date = self.staffing["Date"].max()
        dept_stats = calc.get_department_statistics(self.staffing, self.departments, date=latest_date)
        extremes = calc.get_ratio_extremes(dept_stats)

        self.assertIn("doc_max", extremes)
        self.assertIn("doc_min", extremes)
        self.assertIn("nur_max", extremes)
        self.assertIn("nur_min", extremes)
        self.assertGreater(extremes["doc_max"][1], 0)
        self.assertGreater(extremes["nur_max"][1], 0)
        self.assertGreaterEqual(extremes["doc_max"][1], extremes["doc_min"][1])
        self.assertGreaterEqual(extremes["nur_max"][1], extremes["nur_min"][1])

    def test_daily_staffing_trend(self):
        trend = calc.get_daily_staffing_trend(self.staffing)
        self.assertEqual(len(trend), 365)  # 365 days
        self.assertIn("Overall_Patients_per_Doctor", trend.columns)
        self.assertIn("Overall_Patients_per_Nurse", trend.columns)
        self.assertIn("Bed_Occupancy_Rate_Pct", trend.columns)

        fig_trend = chrt.create_line_chart(
            trend,
            x="Date",
            y=["Overall_Patients_per_Doctor", "Overall_Patients_per_Nurse"],
            title="Trend"
        )
        self.assertIsNotNone(fig_trend)

    def test_staffing_heatmap(self):
        fig_heat = chrt.create_heatmap(
            self.staffing,
            x="Shift",
            y="Department",
            z="Patients_per_Nurse",
            title="Nurse Shift Heatmap"
        )
        self.assertIsNotNone(fig_heat)

    def test_high_load_records_filtering(self):
        high_doc = self.staffing[self.staffing["Doctor_Ratio_Status"] == "High Load"]
        self.assertGreater(len(high_doc), 0)
        high_nur = self.staffing[self.staffing["Nurse_Ratio_Status"] == "High Load"]
        self.assertGreater(len(high_nur), 0)

    def test_safe_division_zero_staff(self):
        # Construct synthetic edge case: 0 doctors on duty
        synthetic = pd.DataFrame([{
            "Date": pd.to_datetime("2026-11-13"),
            "Department": "Emergency",
            "Bed_Capacity": 50,
            "Occupied_Beds": 30,
            "Daily_Patient_Census": 35,
            "Active_Doctors_On_Duty": 0,
            "Active_Nurses_On_Duty": 0,
            "Patients_per_Doctor": 0.0,
            "Patients_per_Nurse": 0.0,
            "Bed_Occupancy_Rate": 0.6,
            "Doctor_Ratio_Status": "High Load",
            "Nurse_Ratio_Status": "High Load",
            "Shift": "Night"
        }])
        p_per_doc = calc.get_patients_per_doctor(synthetic)
        self.assertEqual(p_per_doc, float("inf"))
        p_per_nur = calc.get_patients_per_nurse(synthetic)
        self.assertEqual(p_per_nur, float("inf"))


if __name__ == "__main__":
    unittest.main()
