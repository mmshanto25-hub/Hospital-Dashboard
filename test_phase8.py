"""
tests/test_phase8.py
Automated validation test for Phase 8: Doctor Analytics and Nurse Analytics.
Verifies all 6 Doctor KPIs, 6 Nurse KPIs, 7 Doctor charts, 6 Nurse charts,
workload benchmarking, roster filtering, and multi-format exports.
"""

import unittest
import pandas as pd
from utils.data_loader import load_excel_data
import utils.calculations as calc
import utils.charts as chrt
import utils.filters as flt
import utils.helpers as hlp


class TestDoctorAndNurseAnalyticsPhase8(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = load_excel_data()
        cls.doctors = cls.data["Doctors"]
        cls.nurses = cls.data["Nurses"]
        cls.staffing = cls.data["Daily_Staffing"]
        cls.departments = cls.data["Departments"]

    # --- 1. Doctor Analytics Tests ---

    def test_doctor_kpis(self):
        breakdown = calc.get_doctor_status_breakdown(self.doctors)
        self.assertEqual(breakdown["total"], 180)
        self.assertEqual(breakdown["active"], 168)
        self.assertEqual(breakdown["on_leave"], 9)
        self.assertEqual(breakdown["inactive"], 3)
        self.assertEqual(breakdown["full_time"], 136)
        self.assertEqual(breakdown["part_time"], 29)
        self.assertEqual(breakdown["visiting"], 15)

    def test_doctor_filtering(self):
        filtered = flt.filter_doctors(
            self.doctors,
            department="Cardiology",
            status="Active",
            employment_type="Full-time"
        )
        self.assertFalse(filtered.empty)
        self.assertTrue((filtered["Department"] == "Cardiology").all())
        self.assertTrue((filtered["Status"] == "Active").all())
        self.assertTrue((filtered["Employment_Type"] == "Full-time").all())

    def test_all_7_doctor_charts(self):
        # 1. Depts
        dept_counts = self.doctors["Department"].value_counts().reset_index()
        dept_counts.columns = ["Department", "Count"]
        fig1 = chrt.create_bar_chart(dept_counts, x="Count", y="Department", title="Depts", orientation="h")
        self.assertIsNotNone(fig1)

        # 2. Specs
        spec_counts = self.doctors["Specialization"].value_counts().reset_index()
        spec_counts.columns = ["Specialization", "Count"]
        fig2 = chrt.create_bar_chart(spec_counts, x="Count", y="Specialization", title="Specs", orientation="h")
        self.assertIsNotNone(fig2)

        # 3. Gender
        g_counts = self.doctors["Gender"].value_counts()
        fig3 = chrt.create_donut_chart(g_counts.index.tolist(), g_counts.values.tolist(), title="Gender")
        self.assertIsNotNone(fig3)

        # 4. Employment
        e_counts = self.doctors["Employment_Type"].value_counts()
        fig4 = chrt.create_donut_chart(e_counts.index.tolist(), e_counts.values.tolist(), title="Employment")
        self.assertIsNotNone(fig4)

        # 5. Experience
        exp = calc.get_experience_distribution(self.doctors)
        fig5 = chrt.create_bar_chart(exp, x="Experience_Group", y="Count", title="Experience")
        self.assertIsNotNone(fig5)

        # 6. Shift
        s_counts = self.doctors["Shift"].value_counts().reset_index()
        s_counts.columns = ["Shift", "Count"]
        fig6 = chrt.create_bar_chart(s_counts, x="Shift", y="Count", title="Shift")
        self.assertIsNotNone(fig6)

        # 7. Workload vs Target
        latest_date = self.staffing["Date"].max()
        dept_stats = calc.get_department_statistics(self.staffing, self.departments, date=latest_date)
        fig7 = chrt.create_grouped_bar_chart(
            dept_stats,
            x="Department",
            y_cols=["Patients_per_Doctor", "Target_Patients_per_Doctor"],
            title="Workload"
        )
        self.assertIsNotNone(fig7)

    # --- 2. Nurse Analytics Tests ---

    def test_nurse_kpis(self):
        breakdown = calc.get_nurse_status_breakdown(self.nurses)
        self.assertEqual(breakdown["total"], 480)
        self.assertEqual(breakdown["active"], 444)
        self.assertEqual(breakdown["on_leave"], 28)
        self.assertEqual(breakdown["inactive"], 8)
        self.assertEqual(breakdown["full_time"], 398)
        self.assertEqual(breakdown["part_time"], 82)

    def test_nurse_filtering(self):
        filtered = flt.filter_nurses(
            self.nurses,
            department="ICU",
            ward="ICU-1",
            status="Active"
        )
        self.assertFalse(filtered.empty)
        self.assertTrue((filtered["Department"] == "ICU").all())
        self.assertTrue((filtered["Ward"] == "ICU-1").all())
        self.assertTrue((filtered["Status"] == "Active").all())

    def test_all_6_nurse_charts(self):
        # 1. Depts
        dept_counts = self.nurses["Department"].value_counts().reset_index()
        dept_counts.columns = ["Department", "Count"]
        fig1 = chrt.create_bar_chart(dept_counts, x="Count", y="Department", title="Depts", orientation="h")
        self.assertIsNotNone(fig1)

        # 2. Wards
        w_counts = self.nurses["Ward"].value_counts().reset_index()
        w_counts.columns = ["Ward", "Count"]
        fig2 = chrt.create_bar_chart(w_counts, x="Count", y="Ward", title="Wards", orientation="h")
        self.assertIsNotNone(fig2)

        # 3. Shift
        s_counts = self.nurses["Shift"].value_counts().reset_index()
        s_counts.columns = ["Shift", "Count"]
        fig3 = chrt.create_bar_chart(s_counts, x="Shift", y="Count", title="Shift")
        self.assertIsNotNone(fig3)

        # 4. Employment
        e_counts = self.nurses["Employment_Type"].value_counts()
        fig4 = chrt.create_donut_chart(e_counts.index.tolist(), e_counts.values.tolist(), title="Employment")
        self.assertIsNotNone(fig4)

        # 5. Experience
        exp = calc.get_experience_distribution(self.nurses)
        fig5 = chrt.create_bar_chart(exp, x="Experience_Group", y="Count", title="Experience")
        self.assertIsNotNone(fig5)

        # 6. Workload vs Target
        latest_date = self.staffing["Date"].max()
        dept_stats = calc.get_department_statistics(self.staffing, self.departments, date=latest_date)
        fig6 = chrt.create_grouped_bar_chart(
            dept_stats,
            x="Department",
            y_cols=["Patients_per_Nurse", "Target_Patients_per_Nurse"],
            title="Nurse Workload"
        )
        self.assertIsNotNone(fig6)

    def test_exports(self):
        doc_csv = hlp.convert_df_to_csv(self.doctors.head(20))
        self.assertTrue(len(doc_csv) > 0)
        self.assertIn(b"Doctor_ID", doc_csv)

        nur_excel = hlp.convert_dfs_to_excel({"Nurses": self.nurses.head(20)})
        self.assertTrue(len(nur_excel) > 0)


if __name__ == "__main__":
    unittest.main()
