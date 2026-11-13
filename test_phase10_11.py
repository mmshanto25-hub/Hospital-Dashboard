"""
tests/test_phase10_11.py
Automated validation test for Phase 10 (Export features) and Phase 11 (UI/UX styling).
"""

import io
import unittest
from pathlib import Path
import openpyxl
import pandas as pd

from utils.data_loader import load_excel_data
import utils.helpers as hlp


class TestPhase10And11(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = load_excel_data()
        cls.patients = cls.data["Patients"].head(50)
        cls.departments = cls.data["Departments"]

    def test_csv_export_engine(self):
        csv_bytes = hlp.convert_df_to_csv(self.patients)
        self.assertGreater(len(csv_bytes), 0)
        self.assertIn(b"Patient_ID", csv_bytes)

    def test_openpyxl_styled_excel_export_engine(self):
        export_dict = {
            "Department_Summary": self.departments,
            "Patient_Registry": self.patients
        }
        excel_bytes = hlp.convert_dfs_to_excel(export_dict, apply_styling=True)
        self.assertGreater(len(excel_bytes), 0)

        # Validate structure with openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
        self.assertIn("Department_Summary", wb.sheetnames)
        self.assertIn("Patient_Registry", wb.sheetnames)

        ws = wb["Department_Summary"]
        header_cell = ws.cell(row=1, column=1)
        self.assertEqual(header_cell.value, "Department")
        # Check custom header styling
        self.assertIsNotNone(header_cell.fill)
        self.assertEqual(header_cell.font.color.rgb, "00F8FAFC")
        # Check column width auto-adjustment
        col_dim = ws.column_dimensions["A"]
        self.assertGreater(col_dim.width, 10)

    def test_custom_css_file_integrity(self):
        css_path = Path("assets/custom.css")
        self.assertTrue(css_path.exists())
        content = css_path.read_text(encoding="utf-8")
        self.assertIn("#0B1220", content)
        self.assertIn("#162338", content)
        self.assertIn("#3B82F6", content)

    def test_logo_asset_integrity(self):
        logo_path = Path("assets/logo.png")
        self.assertTrue(logo_path.exists())
        self.assertGreater(logo_path.stat().st_size, 100)


if __name__ == "__main__":
    unittest.main()
