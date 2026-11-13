"""
tests/test_phase45.py
Automated validation test for Phase 4 (filters & helpers) and Phase 5 (charts).
"""

import unittest
import pandas as pd
from utils.data_loader import load_excel_data
import utils.filters as flt
import utils.helpers as hlp
import utils.charts as chrt
import utils.calculations as calc


class TestFiltersHelpersCharts(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = load_excel_data()
        cls.patients = cls.data["Patients"]
        cls.doctors = cls.data["Doctors"]
        cls.nurses = cls.data["Nurses"]
        cls.staffing = cls.data["Daily_Staffing"]
        cls.departments = cls.data["Departments"]

    # --- PHASE 4: Filters Tests ---

    def test_filter_patients_department_and_gender(self):
        filtered = flt.filter_patients(self.patients, department="Cardiology", gender="Female")
        self.assertFalse(filtered.empty)
        self.assertTrue((filtered["Department"] == "Cardiology").all())
        self.assertTrue((filtered["Gender"] == "Female").all())

    def test_filter_patients_date_range(self):
        start = "2025-06-01"
        end = "2025-08-31"
        filtered = flt.filter_patients(self.patients, start_date=start, end_date=end)
        self.assertFalse(filtered.empty)
        self.assertTrue((filtered["Admission_Date"] >= pd.to_datetime(start)).all())
        self.assertTrue((filtered["Admission_Date"] <= pd.to_datetime(end)).all())

    def test_filter_daily_staffing(self):
        filtered = flt.filter_daily_staffing(
            self.staffing,
            department="Emergency",
            shift="Night"
        )
        self.assertFalse(filtered.empty)
        self.assertTrue((filtered["Department"] == "Emergency").all())
        self.assertTrue((filtered["Shift"] == "Night").all())

    def test_filter_doctors(self):
        filtered = flt.filter_doctors(self.doctors, department="Neurology", status="Active")
        self.assertFalse(filtered.empty)
        self.assertTrue((filtered["Department"] == "Neurology").all())
        self.assertTrue((filtered["Status"] == "Active").all())

    def test_filter_nurses(self):
        filtered = flt.filter_nurses(self.nurses, department="Pediatrics", employment_type="Full-time")
        self.assertFalse(filtered.empty)
        self.assertTrue((filtered["Department"] == "Pediatrics").all())
        self.assertTrue((filtered["Employment_Type"] == "Full-time").all())

    # --- PHASE 4: Helpers Tests ---

    def test_formatting_helpers(self):
        self.assertEqual(hlp.format_number(12500), "12,500")
        self.assertEqual(hlp.format_number(12500.456, decimals=1), "12,500.5")
        self.assertEqual(hlp.format_percent(85.432, decimals=1), "85.4%")

    def test_export_helpers(self):
        csv_bytes = hlp.convert_df_to_csv(self.departments)
        self.assertTrue(len(csv_bytes) > 0)
        self.assertIn(b"Department", csv_bytes)

        excel_bytes = hlp.convert_dfs_to_excel({"Departments": self.departments})
        self.assertTrue(len(excel_bytes) > 0)

    # --- PHASE 5: Charts Tests ---

    def test_line_chart(self):
        monthly = calc.get_monthly_admissions_and_discharges(self.patients)
        fig = chrt.create_line_chart(monthly, x="Month", y=["Admissions", "Discharges"], title="Admissions")
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 2)

    def test_bar_chart(self):
        dept_counts = self.patients["Department"].value_counts().reset_index()
        dept_counts.columns = ["Department", "Count"]
        fig = chrt.create_bar_chart(
            dept_counts,
            x="Count",
            y="Department",
            title="Patients by Dept",
            orientation="h",
            highlight_top_n=3
        )
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 1)

    def test_grouped_bar_chart(self):
        latest = self.staffing[self.staffing["Date"] == self.staffing["Date"].max()]
        fig = chrt.create_grouped_bar_chart(
            latest,
            x="Department",
            y_cols=["Active_Doctors_On_Duty", "Active_Nurses_On_Duty"],
            title="Staff Distribution"
        )
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 2)

    def test_donut_chart(self):
        fig = chrt.create_donut_chart(
            labels=["Occupied", "Available"],
            values=[350, 150],
            title="Bed Occupancy",
            center_text="70.0%"
        )
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 1)

    def test_histogram(self):
        fig = chrt.create_histogram(self.patients, x="Age", title="Age Distribution", nbins=20)
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 1)

    def test_heatmap(self):
        fig = chrt.create_heatmap(
            self.staffing,
            x="Shift",
            y="Department",
            z="Patients_per_Nurse",
            title="Nurse Ratio Heatmap"
        )
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 1)

    def test_area_chart(self):
        trend = calc.get_daily_staffing_trend(self.staffing)
        fig = chrt.create_area_chart(trend, x="Date", y="Total_Census", title="Census Trend")
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 1)

    def test_empty_chart_safety(self):
        empty_df = pd.DataFrame()
        fig_line = chrt.create_line_chart(empty_df, x="Date", y="Census", title="Empty Line")
        fig_bar = chrt.create_bar_chart(empty_df, x="Cat", y="Val", title="Empty Bar")
        fig_donut = chrt.create_donut_chart([], [], title="Empty Donut")
        self.assertIsNotNone(fig_line)
        self.assertIsNotNone(fig_bar)
        self.assertIsNotNone(fig_donut)


if __name__ == "__main__":
    unittest.main()
