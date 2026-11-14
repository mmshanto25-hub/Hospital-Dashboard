"""
test_predictive_analytics.py
Unit tests for Linear Regression modeling and Predictive Analytics module.
"""

import unittest
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.data_loader import load_excel_data
import utils.calculations as calc
import utils.charts as chrt


class TestPredictiveAnalytics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = load_excel_data()
        cls.df_daily_staffing = data.get("Daily_Staffing", pd.DataFrame())
        cls.df_departments = data.get("Departments", pd.DataFrame())

    def test_train_census_linear_regression_overall(self):
        """Verify linear regression executes on full daily staffing dataset."""
        self.assertFalse(self.df_daily_staffing.empty)
        output = calc.train_census_linear_regression(self.df_daily_staffing, department="All", forecast_days=14)

        self.assertIn("combined_df", output)
        self.assertIn("historical_df", output)
        self.assertIn("forecast_df", output)
        self.assertIn("metrics", output)

        metrics = output["metrics"]
        self.assertIn("r2", metrics)
        self.assertIn("mae", metrics)
        self.assertIn("rmse", metrics)
        self.assertIn("slope", metrics)
        self.assertIn("projected_census", metrics)
        self.assertGreater(metrics["data_points"], 0)
        self.assertEqual(len(output["forecast_df"]), 14)

    def test_train_census_linear_regression_department(self):
        """Verify linear regression executes for a specific department."""
        output = calc.train_census_linear_regression(self.df_daily_staffing, department="Emergency", forecast_days=7)
        self.assertEqual(len(output["forecast_df"]), 7)
        self.assertGreater(output["metrics"]["projected_census"], 0)

    def test_train_census_empty_dataset(self):
        """Verify graceful fallback when provided an empty DataFrame."""
        empty_df = pd.DataFrame()
        output = calc.train_census_linear_regression(empty_df, forecast_days=10)
        self.assertTrue(output["combined_df"].empty)
        self.assertEqual(output["metrics"]["r2"], 0.0)
        self.assertEqual(output["metrics"]["projected_census"], 0)

    def test_regression_forecast_chart_generation(self):
        """Verify Plotly figure generation for linear regression forecast."""
        output = calc.train_census_linear_regression(self.df_daily_staffing, department="Cardiology", forecast_days=10)
        fig = chrt.create_regression_forecast_chart(
            historical_df=output["historical_df"],
            forecast_df=output["forecast_df"],
            title="Cardiology Census Forecast"
        )
        self.assertIsInstance(fig, go.Figure)
        # Should contain at least Actual, Fitted, Forecast traces
        self.assertGreaterEqual(len(fig.data), 3)


if __name__ == "__main__":
    unittest.main()
