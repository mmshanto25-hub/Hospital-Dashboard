"""
test_all_requirements.py
Comprehensive End-to-End Test Suite verifying all 14 Testing Requirements from Section 21.
"""

import unittest
import pandas as pd
from utils.data_loader import load_excel_data
import utils.calculations as calc
import utils.charts as chrt
import utils.filters as flt
import utils.helpers as hlp


class TestHospitalDashboardComprehensive(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = load_excel_data()
        cls.patients = cls.data["Patients"]
        cls.doctors = cls.data["Doctors"]
        cls.nurses = cls.data["Nurses"]
        cls.staffing = cls.data["Daily_Staffing"]
        cls.departments = cls.data["Departments"]

    # 1. Excel workbook loads correctly
    def test_1_workbook_loads(self):
        self.assertIsNotNone(self.data)
        self.assertIsInstance(self.data, dict)

    # 2. All seven worksheets are detected
    def test_2_all_seven_worksheets_detected(self):
        expected_sheets = ["README", "Dashboard_Summary", "Patients", "Doctors", "Nurses", "Daily_Staffing", "Departments"]
        for sheet in expected_sheets:
            self.assertIn(sheet, self.data, f"Sheet '{sheet}' not detected in workbook")

    # 3. Patient records count correctly
    def test_3_patient_records_count(self):
        tot_patients = calc.get_total_patients(self.patients)
        self.assertEqual(tot_patients, 6000)

    # 4. Active doctors and nurses are calculated correctly
    def test_4_active_staff_calculation(self):
        latest_date = self.staffing["Date"].max()
        raw_snap = self.staffing[self.staffing["Date"] == latest_date]
        expected_docs = int(raw_snap["Active_Doctors_On_Duty"].sum())
        expected_nurses = int(raw_snap["Active_Nurses_On_Duty"].sum())

        calc_docs = calc.get_active_doctors(self.staffing, date=latest_date)
        calc_nurses = calc.get_active_nurses(self.staffing, date=latest_date)

        self.assertEqual(calc_docs, expected_docs)
        self.assertEqual(calc_nurses, expected_nurses)

    # 5. Daily patient census is calculated correctly
    def test_5_daily_patient_census_calculation(self):
        latest_date = self.staffing["Date"].max()
        raw_snap = self.staffing[self.staffing["Date"] == latest_date]
        expected_census = int(raw_snap["Daily_Patient_Census"].sum())
        calc_census = calc.get_current_patient_census(self.staffing, date=latest_date)
        self.assertEqual(calc_census, expected_census)

    # 6. Bed occupancy is calculated correctly
    def test_6_bed_occupancy_calculation(self):
        latest_date = self.staffing["Date"].max()
        raw_snap = self.staffing[self.staffing["Date"] == latest_date]
        cap = int(raw_snap["Bed_Capacity"].sum())
        occ = int(raw_snap["Occupied_Beds"].sum())
        expected_rate = round(occ / cap * 100, 2)
        calc_rate = calc.get_bed_occupancy_rate(self.staffing, date=latest_date)
        self.assertEqual(calc_rate, expected_rate)

    # 7. Patient-to-doctor ratio is calculated correctly
    def test_7_patient_to_doctor_ratio(self):
        latest_date = self.staffing["Date"].max()
        raw_snap = self.staffing[self.staffing["Date"] == latest_date]
        census = int(raw_snap["Daily_Patient_Census"].sum())
        docs = int(raw_snap["Active_Doctors_On_Duty"].sum())
        expected_ratio = round(census / docs, 2)
        calc_ratio = calc.get_patients_per_doctor(self.staffing, date=latest_date)
        self.assertEqual(calc_ratio, expected_ratio)

    # 8. Patient-to-nurse ratio is calculated correctly
    def test_8_patient_to_nurse_ratio(self):
        latest_date = self.staffing["Date"].max()
        raw_snap = self.staffing[self.staffing["Date"] == latest_date]
        census = int(raw_snap["Daily_Patient_Census"].sum())
        nurses = int(raw_snap["Active_Nurses_On_Duty"].sum())
        expected_ratio = round(census / nurses, 2)
        calc_ratio = calc.get_patients_per_nurse(self.staffing, date=latest_date)
        self.assertEqual(calc_ratio, expected_ratio)

    # 9. Department filters work
    def test_9_department_filters_work(self):
        dept = "Cardiology"
        p_filtered = flt.filter_patients(self.patients, department=dept)
        self.assertTrue((p_filtered["Department"] == dept).all())
        s_filtered = flt.filter_daily_staffing(self.staffing, department=dept)
        self.assertTrue((s_filtered["Department"] == dept).all())
        d_filtered = flt.filter_doctors(self.doctors, department=dept)
        self.assertTrue((d_filtered["Department"] == dept).all())
        n_filtered = flt.filter_nurses(self.nurses, department=dept)
        self.assertTrue((n_filtered["Department"] == dept).all())

    # 10. Date filters work
    def test_10_date_filters_work(self):
        start = "2025-05-01"
        end = "2025-10-31"
        p_filtered = flt.filter_patients(self.patients, start_date=start, end_date=end)
        self.assertTrue((p_filtered["Admission_Date"] >= pd.to_datetime(start)).all())
        self.assertTrue((p_filtered["Admission_Date"] <= pd.to_datetime(end)).all())

        s_filtered = flt.filter_daily_staffing(self.staffing, start_date=start, end_date=end)
        self.assertTrue((s_filtered["Date"] >= pd.to_datetime(start)).all())
        self.assertTrue((s_filtered["Date"] <= pd.to_datetime(end)).all())

    # 11. Shift filters work
    def test_11_shift_filters_work(self):
        shift = "Night"
        s_filtered = flt.filter_daily_staffing(self.staffing, shift=shift)
        self.assertTrue((s_filtered["Shift"] == shift).all())
        d_filtered = flt.filter_doctors(self.doctors, shift=shift)
        self.assertTrue((d_filtered["Shift"] == shift).all())
        n_filtered = flt.filter_nurses(self.nurses, shift=shift)
        self.assertTrue((n_filtered["Shift"] == shift).all())

    # 12. Empty datasets do not crash the application
    def test_12_empty_datasets_safety(self):
        empty_df = pd.DataFrame()
        self.assertEqual(calc.get_total_patients(empty_df), 0)
        self.assertEqual(calc.get_current_patient_census(empty_df), 0)
        self.assertEqual(calc.get_bed_capacity(empty_df), 0)
        self.assertEqual(calc.get_bed_occupancy_rate(empty_df), 0.0)
        self.assertEqual(calc.get_patients_per_doctor(empty_df), 0.0)
        self.assertEqual(calc.get_patients_per_nurse(empty_df), 0.0)
        self.assertEqual(calc.get_average_length_of_stay(empty_df), 0.0)

        # Charts on empty data
        f1 = chrt.create_line_chart(empty_df, x="Date", y="Val", title="Empty")
        f2 = chrt.create_bar_chart(empty_df, x="Cat", y="Val", title="Empty")
        f3 = chrt.create_donut_chart([], [], title="Empty")
        self.assertIsNotNone(f1)
        self.assertIsNotNone(f2)
        self.assertIsNotNone(f3)

    # 13. Missing values do not break charts
    def test_13_missing_values_handled(self):
        # Patients has 756 null Discharge_Dates
        null_count = self.patients["Discharge_Date"].isnull().sum()
        self.assertEqual(null_count, 756)
        # Verify monthly trend calculates without crash
        trend = calc.get_monthly_admissions_and_discharges(self.patients)
        self.assertFalse(trend.empty)
        # Missing discharges are correctly excluded
        self.assertEqual(trend["Discharges"].sum(), 6000 - 756)

    # 14. CSV and Excel downloads work
    def test_14_csv_and_excel_downloads_work(self):
        csv_bytes = hlp.convert_df_to_csv(self.departments)
        self.assertGreater(len(csv_bytes), 0)

        excel_bytes = hlp.convert_dfs_to_excel({"Departments": self.departments}, apply_styling=True)
        self.assertGreater(len(excel_bytes), 0)


if __name__ == "__main__":
    unittest.main()
