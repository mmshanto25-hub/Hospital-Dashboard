"""
tests/test_phase7.py
Automated validation test for Phase 7: Patient Analytics.
Verifies all 6 KPI calculations, 8 Plotly charts, cohort filtering, and exports.
"""

import unittest
import pandas as pd
from utils.data_loader import load_excel_data
import utils.calculations as calc
import utils.charts as chrt
import utils.filters as flt
import utils.helpers as hlp


class TestPatientAnalyticsPhase7(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = load_excel_data()
        cls.patients = cls.data["Patients"]

    def test_patient_status_kpis(self):
        summary = calc.get_patient_status_summary(self.patients)
        self.assertEqual(summary["total"], 6000)
        self.assertEqual(summary["admitted"], 1042)
        self.assertEqual(summary["discharged"], 4654)
        self.assertEqual(summary["transferred"], 271)
        self.assertEqual(summary["deceased"], 33)
        self.assertEqual(
            summary["admitted"] + summary["discharged"] + summary["transferred"] + summary["deceased"],
            6000
        )

    def test_average_age_and_los(self):
        avg_age = calc.get_average_patient_age(self.patients)
        self.assertAlmostEqual(avg_age, 41.3, delta=0.2)

        avg_los = calc.get_average_length_of_stay(self.patients)
        self.assertAlmostEqual(avg_los, 4.48, delta=0.1)

    def test_age_group_distribution_brackets(self):
        age_dist = calc.get_age_group_distribution(self.patients)
        expected_groups = ["0–17", "18–30", "31–45", "46–60", "61–75", "76+"]
        self.assertEqual(age_dist["Age_Group"].tolist(), expected_groups)
        self.assertEqual(age_dist["Count"].sum(), 6000)

    def test_all_8_patient_charts_generation(self):
        # 1. Monthly Admissions
        monthly = calc.get_monthly_admissions_and_discharges(self.patients)
        fig1 = chrt.create_line_chart(monthly, x="Month", y="Admissions", title="Monthly Admissions")
        self.assertIsNotNone(fig1)

        # 2. Monthly Discharges
        fig2 = chrt.create_line_chart(monthly, x="Month", y="Discharges", title="Monthly Discharges")
        self.assertIsNotNone(fig2)

        # 3. Department Distribution
        dept_counts = self.patients["Department"].value_counts().reset_index()
        dept_counts.columns = ["Department", "Patient_Count"]
        fig3 = chrt.create_bar_chart(dept_counts, x="Patient_Count", y="Department", title="Depts", orientation="h", highlight_top_n=3)
        self.assertIsNotNone(fig3)

        # 4. Gender Distribution
        gender_counts = self.patients["Gender"].value_counts()
        fig4 = chrt.create_donut_chart(gender_counts.index.tolist(), gender_counts.values.tolist(), title="Gender")
        self.assertIsNotNone(fig4)

        # 5. Age Group Distribution
        age_dist = calc.get_age_group_distribution(self.patients)
        fig5 = chrt.create_bar_chart(age_dist, x="Age_Group", y="Count", title="Age Groups")
        self.assertIsNotNone(fig5)

        # 6. Condition Distribution
        cond_counts = self.patients["Primary_Condition"].value_counts().reset_index()
        cond_counts.columns = ["Primary_Condition", "Count"]
        fig6 = chrt.create_bar_chart(cond_counts, x="Count", y="Primary_Condition", title="Conditions", orientation="h")
        self.assertIsNotNone(fig6)

        # 7. Admission Type Distribution
        adm_counts = self.patients["Admission_Type"].value_counts().reset_index()
        adm_counts.columns = ["Admission_Type", "Count"]
        fig7 = chrt.create_bar_chart(adm_counts, x="Admission_Type", y="Count", title="Adm Types")
        self.assertIsNotNone(fig7)

        # 8. Length of Stay Distribution
        fig8 = chrt.create_histogram(self.patients, x="Length_of_Stay_Days", title="LOS Histogram")
        self.assertIsNotNone(fig8)

    def test_cohort_filtering_compound(self):
        filtered = flt.filter_patients(
            self.patients,
            start_date="2025-01-01",
            end_date="2025-12-31",
            department="Emergency",
            gender="Male",
            admission_type="Emergency",
            patient_status="Discharged"
        )
        self.assertFalse(filtered.empty)
        self.assertTrue((filtered["Department"] == "Emergency").all())
        self.assertTrue((filtered["Gender"] == "Male").all())
        self.assertTrue((filtered["Admission_Type"] == "Emergency").all())
        self.assertTrue((filtered["Patient_Status"] == "Discharged").all())

    def test_exports_patient_cohort(self):
        csv_bytes = hlp.convert_df_to_csv(self.patients.head(50))
        self.assertTrue(len(csv_bytes) > 0)
        self.assertIn(b"Patient_ID", csv_bytes)

        excel_bytes = hlp.convert_dfs_to_excel({"Patients": self.patients.head(50)})
        self.assertTrue(len(excel_bytes) > 0)


if __name__ == "__main__":
    unittest.main()
