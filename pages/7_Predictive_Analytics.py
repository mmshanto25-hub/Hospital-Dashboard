"""
pages/7_Predictive_Analytics.py
Page 7: Predictive Analytics & Patient Census Forecasting.
Applies Ordinary Least Squares (OLS) Linear Regression to project future patient census,
evaluates goodness-of-fit metrics (R², MAE, RMSE, Slope), simulates future staffing needs,
and provides multi-format data exports.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import math
from datetime import datetime
import pandas as pd
import numpy as np
import streamlit as st

from utils.data_loader import load_excel_data
import utils.calculations as calc
import utils.charts as chrt
import utils.filters as flt
import utils.helpers as hlp


def main():
    # 1. Page Configuration
    st.set_page_config(
        page_title="Predictive Analytics | MediCore Analytics",
        page_icon="🔮",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 2. Inject Enterprise Custom CSS
    hlp.apply_custom_css()

    # 3. Load Dataset
    uploaded_source = st.session_state.get("uploaded_file", None)
    try:
        data = load_excel_data(uploaded_source)
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")
        st.stop()

    df_daily_staffing = data.get("Daily_Staffing", pd.DataFrame())
    df_departments = data.get("Departments", pd.DataFrame())

    # 4. Global Sidebar & Context Filters
    global_filters = flt.render_global_sidebar(data)
    selected_dept = global_filters["department"]
    selected_shift = global_filters["shift"]
    start_date = global_filters["start_date"]
    end_date = global_filters["end_date"]

    # Filter staffing dataset by selected range and shift
    filtered_staffing = flt.filter_daily_staffing(
        df_daily_staffing,
        start_date=start_date,
        end_date=end_date,
        department=selected_dept,
        shift=selected_shift
    )

    snapshot_date = filtered_staffing["Date"].max() if not filtered_staffing.empty else df_daily_staffing["Date"].max()
    snapshot_str = snapshot_date.strftime("%b %d, %Y") if pd.notna(snapshot_date) else "Live"

    # Dedicated Forecast Horizon Setting in Sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔮 Regression Controls")
    forecast_days = st.sidebar.slider(
        "Forecast Horizon (Days)",
        min_value=7,
        max_value=60,
        value=14,
        step=1,
        help="Number of future days to project using Linear Regression"
    )

    # 5. Executive Header
    hlp.render_page_header(
        title="Predictive Analytics & Census Forecasting",
        subtitle="Ordinary Least Squares (OLS) Linear Regression for Patient Volume Projection & Workforce Planning",
        selected_range=f"{start_date.strftime('%b %d, %Y')} – {end_date.strftime('%b %d, %Y')}",
        selected_dept=selected_dept,
        latest_update=f"Horizon: +{forecast_days} Days"
    )

    if filtered_staffing.empty:
        st.warning("⚠️ No records match the active filter criteria. Adjust your date range or department filter.")
        st.stop()

    # 6. Fit Linear Regression Model
    model_output = calc.train_census_linear_regression(
        filtered_staffing,
        department=selected_dept,
        forecast_days=forecast_days
    )

    metrics = model_output["metrics"]
    historical_df = model_output["historical_df"]
    forecast_df = model_output["forecast_df"]

    # 7. Model Performance & Projection KPI Cards (4 Cards)
    st.markdown("<h3 style='margin-top: 0.5rem; margin-bottom: 0.8rem;'>Model Performance & Projection Indicators</h3>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    # Determine badge color based on R² goodness-of-fit
    r2_val = metrics["r2"]
    if r2_val >= 0.5:
        r2_badge_type = "positive"
        r2_badge_text = "Strong Fit"
    elif r2_val >= 0.2:
        r2_badge_type = "warning"
        r2_badge_text = "Moderate Trend"
    else:
        r2_badge_type = "neutral"
        r2_badge_text = "Weak Linear Trend"

    slope_val = metrics["slope"]
    slope_sign = "+" if slope_val >= 0 else ""
    slope_badge_type = "danger" if slope_val > 1.0 else ("warning" if slope_val > 0 else "positive")
    slope_badge_text = "Increasing Demand" if slope_val > 0 else ("Declining" if slope_val < 0 else "Stable")

    with c1:
        hlp.render_kpi_card(
            title="Goodness of Fit (R²)",
            value=f"{r2_val:.3f}",
            subtitle=f"Trained on {metrics['data_points']} daily records",
            icon="📐",
            badge_text=r2_badge_text,
            badge_type=r2_badge_type
        )

    with c2:
        hlp.render_kpi_card(
            title="Mean Absolute Error (MAE)",
            value=f"±{metrics['mae']:.1f} Pts",
            subtitle=f"RMSE: ±{metrics['rmse']:.1f} Patients",
            icon="🎯",
            badge_text="Prediction Precision",
            badge_type="positive"
        )

    with c3:
        hlp.render_kpi_card(
            title="Daily Trend (Slope)",
            value=f"{slope_sign}{slope_val:.2f} Pts/day",
            subtitle=f"Intercept: {metrics['intercept']:.1f} base census",
            icon="📈" if slope_val >= 0 else "📉",
            badge_text=slope_badge_text,
            badge_type=slope_badge_type
        )

    with c4:
        diff_proj = metrics["projected_census"] - metrics["current_census"]
        diff_sign = "+" if diff_proj >= 0 else ""
        hlp.render_kpi_card(
            title=f"Projected Census (+{forecast_days}d)",
            value=f"{metrics['projected_census']:,} Pts",
            subtitle=f"Baseline: {metrics['current_census']:,} ({diff_sign}{diff_proj} pts)",
            icon="🔮",
            badge_text=f"Day +{forecast_days}",
            badge_type="warning" if diff_proj > 0 else "positive"
        )

    # 8. Interactive Plotly Regression Chart
    st.markdown("<h3 style='margin-top: 1.5rem; margin-bottom: 0.8rem;'>Patient Census Trend & Linear Regression Projections</h3>", unsafe_allow_html=True)
    chart_title = f"Historical Census & {forecast_days}-Day OLS Projection ({selected_dept if selected_dept != 'All' else 'All Departments'})"
    fig = chrt.create_regression_forecast_chart(
        historical_df=historical_df,
        forecast_df=forecast_df,
        title=chart_title,
        height=450
    )
    st.plotly_chart(fig, width="stretch")

    # 9. Interactive What-If Simulation Calculator
    st.markdown("<h3 style='margin-top: 1.5rem; margin-bottom: 0.8rem;'>Workforce Capacity & What-If Simulation Calculator</h3>", unsafe_allow_html=True)

    # Determine benchmark ratios based on selected department or weighted averages
    if selected_dept != "All" and not df_departments.empty and selected_dept in df_departments["Department"].values:
        dept_row = df_departments[df_departments["Department"] == selected_dept].iloc[0]
        target_doc_ratio = float(dept_row.get("Target_Patients_per_Doctor", 12.0))
        target_nurse_ratio = float(dept_row.get("Target_Patients_per_Nurse", 6.0))
        bed_cap = int(dept_row.get("Bed_Capacity", 50))
    else:
        target_doc_ratio = float(df_departments["Target_Patients_per_Doctor"].mean()) if not df_departments.empty else 10.0
        target_nurse_ratio = float(df_departments["Target_Patients_per_Nurse"].mean()) if not df_departments.empty else 5.0
        bed_cap = int(df_departments["Bed_Capacity"].sum()) if not df_departments.empty else 400

    sim_col1, sim_col2 = st.columns([1, 1])

    with sim_col1:
        st.markdown(
            """
            <div style="background-color: #162338; border: 1px solid #1E293B; border-radius: 8px; padding: 1.25rem;">
                <h4 style="margin-top: 0; color: #38BDF8;">⚙️ Simulation Parameters</h4>
                <p style="font-size: 0.85rem; color: #94A3B8;">
                    Input a projected or stress-test patient volume to calculate the required clinical staff on duty.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        simulated_census = st.number_input(
            "Hypothetical Daily Patient Census",
            min_value=0,
            max_value=max(int(bed_cap * 1.5), 1000),
            value=int(metrics["projected_census"]),
            step=5,
            help="Adjust this number to evaluate required clinical staffing levels"
        )

        custom_doc_ratio = st.slider(
            "Target Patients per Doctor",
            min_value=2.0,
            max_value=25.0,
            value=float(target_doc_ratio),
            step=0.5,
            help="Accredited standard workload per doctor"
        )

        custom_nurse_ratio = st.slider(
            "Target Patients per Nurse",
            min_value=1.0,
            max_value=15.0,
            value=float(target_nurse_ratio),
            step=0.5,
            help="Accredited standard workload per nurse"
        )

    # Compute requirements
    required_doctors = math.ceil(simulated_census / custom_doc_ratio) if custom_doc_ratio > 0 and simulated_census > 0 else 0
    required_nurses = math.ceil(simulated_census / custom_nurse_ratio) if custom_nurse_ratio > 0 and simulated_census > 0 else 0
    sim_occ_rate = (simulated_census / bed_cap * 100) if bed_cap > 0 else 0.0

    with sim_col2:
        st.markdown(
            """
            <div style="background-color: #162338; border: 1px solid #1E293B; border-radius: 8px; padding: 1.25rem;">
                <h4 style="margin-top: 0; color: #F59E0B;">📋 Projected Staffing Demand Output</h4>
                <p style="font-size: 0.85rem; color: #94A3B8;">
                    Staffing demand computed to meet clinical accreditation standards without burnout.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        r_card1, r_card2 = st.columns(2)
        with r_card1:
            hlp.render_kpi_card(
                title="Doctors Required",
                value=f"{required_doctors} Active Docs",
                subtitle=f"Target: {custom_doc_ratio:.1f} Pts/Doc",
                icon="🩺",
                badge_text="Shift Requirement",
                badge_type="positive"
            )
        with r_card2:
            hlp.render_kpi_card(
                title="Nurses Required",
                value=f"{required_nurses} Active Nurses",
                subtitle=f"Target: {custom_nurse_ratio:.1f} Pts/Nurse",
                icon="💉",
                badge_text="Shift Requirement",
                badge_type="positive"
            )

        # Capacity gauge indicator
        occ_badge_type = "danger" if sim_occ_rate > 90 else ("warning" if sim_occ_rate > 75 else "positive")
        st.markdown(
            f"""
            <div style="background: #0B1220; border: 1px solid #1E293B; border-radius: 8px; padding: 1rem; margin-top: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.9rem; font-weight: 600; color: #F8FAFC;">Estimated Bed Occupancy:</span>
                    <span style="font-size: 1.1rem; font-weight: 700; color: #38BDF8;">{sim_occ_rate:.1f}% ({simulated_census} / {bed_cap} Beds)</span>
                </div>
                <div style="margin-top: 0.5rem; background: #1E293B; border-radius: 4px; height: 8px; overflow: hidden;">
                    <div style="width: {min(sim_occ_rate, 100.0):.1f}%; height: 100%; background: {'#EF4444' if sim_occ_rate > 90 else ('#F59E0B' if sim_occ_rate > 75 else '#22C55E')};"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 10. Forecast Projection Data Table & Exports
    st.markdown("<h3 style='margin-top: 2rem; margin-bottom: 0.8rem;'>Projected Daily Census & Staffing Surveillance Table</h3>", unsafe_allow_html=True)

    if not forecast_df.empty:
        table_forecast = forecast_df.copy()
        table_forecast["Date_Formatted"] = table_forecast["Date"].dt.strftime("%Y-%m-%d (%a)")
        table_forecast["Projected_Census"] = table_forecast["Fitted_Census"].astype(int)
        table_forecast["Required_Doctors"] = table_forecast["Projected_Census"].apply(
            lambda x: math.ceil(x / target_doc_ratio) if target_doc_ratio > 0 else 0
        )
        table_forecast["Required_Nurses"] = table_forecast["Projected_Census"].apply(
            lambda x: math.ceil(x / target_nurse_ratio) if target_nurse_ratio > 0 else 0
        )
        table_forecast["Expected_Occupancy_Pct"] = table_forecast["Projected_Census"].apply(
            lambda x: round(x / bed_cap * 100, 1) if bed_cap > 0 else 0.0
        )

        display_cols = ["Date_Formatted", "Projected_Census", "Required_Doctors", "Required_Nurses", "Expected_Occupancy_Pct"]
        st.dataframe(
            table_forecast[display_cols].rename(columns={
                "Date_Formatted": "Date",
                "Projected_Census": "Projected Census",
                "Required_Doctors": "Min Doctors Needed",
                "Required_Nurses": "Min Nurses Needed",
                "Expected_Occupancy_Pct": "Projected Occupancy (%)"
            }),
            width="stretch",
            hide_index=True
        )

        # Multi-Format Export Buttons
        col_exp1, col_exp2, _ = st.columns([1, 1, 3])

        with col_exp1:
            csv_data = hlp.convert_df_to_csv(table_forecast[display_cols])
            st.download_button(
                label="📥 Export Projections (CSV)",
                data=csv_data,
                file_name=f"census_projections_{selected_dept}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                width="stretch"
            )

        with col_exp2:
            excel_data = hlp.convert_dfs_to_excel({
                "Forecast_Projections": table_forecast[display_cols],
                "Historical_Census": historical_df
            })
            st.download_button(
                label="📊 Export Projections (Excel)",
                data=excel_data,
                file_name=f"census_projections_{selected_dept}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch"
            )


if __name__ == "__main__":
    main()
