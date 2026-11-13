"""
pages/6_Staffing_Ratio.py
Page 6: Staffing Ratio Analysis & Clinical Capacity Optimization.
Deep analysis of Doctor-to-Patient and Nurse-to-Patient ratios against clinical benchmarks,
daily ratio trends, department heatmaps, workload extremes, high-load logs,
and multi-format data exports.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

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
        page_title="Staffing Ratio Analysis | MediCore Analytics",
        page_icon="⚖️",
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

    # 4. Render Global Sidebar & Retrieve Filter Settings
    global_filters = flt.render_global_sidebar(data)
    selected_dept = global_filters["department"]
    selected_shift = global_filters["shift"]
    start_date = global_filters["start_date"]
    end_date = global_filters["end_date"]

    # 5. Apply Filtering to Daily Staffing
    filtered_staffing = flt.filter_daily_staffing(
        df_daily_staffing,
        start_date=start_date,
        end_date=end_date,
        department=selected_dept,
        shift=selected_shift
    )
    snapshot_date = filtered_staffing["Date"].max() if not filtered_staffing.empty else df_daily_staffing["Date"].max()
    snapshot_str = snapshot_date.strftime("%b %d, %Y") if pd.notna(snapshot_date) else "Live"

    # Executive Header
    hlp.render_page_header(
        title="Staffing Ratio Analysis",
        subtitle="Workforce Load Optimization, Doctor & Nurse Ratio Benchmarking & Critical High-Load Surveillance",
        selected_range=f"{start_date.strftime('%b %d, %Y')} – {end_date.strftime('%b %d, %Y')}",
        selected_dept=selected_dept,
        latest_update=f"Snapshot: {snapshot_str}"
    )

    # Compute Snapshot Department Statistics & Extremes
    dept_stats = calc.get_department_statistics(filtered_staffing, df_departments, date=snapshot_date)
    extremes = calc.get_ratio_extremes(dept_stats)

    overall_p_per_doc = calc.get_patients_per_doctor(filtered_staffing, date=snapshot_date, department=selected_dept)
    overall_p_per_nur = calc.get_patients_per_nurse(filtered_staffing, date=snapshot_date, department=selected_dept)

    # ==========================================================================
    # SECTION 12.1: RATIO BENCHMARK & EXTREMES KPIS (6 CARDS)
    # ==========================================================================
    st.markdown("<h3 style='margin-top: 0.5rem; margin-bottom: 0.8rem;'>Workforce Ratio Indicators & Extremes</h3>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5, k6 = st.columns(6)

    with k1:
        hlp.render_kpi_card(
            title="Hospital Pts / Doctor",
            value=f"{overall_p_per_doc:.1f}" if overall_p_per_doc != float("inf") else "Critical (0 Docs)",
            subtitle=f"Aggregated as of {snapshot_str}",
            icon="🩺",
            badge_text="Overall Ratio",
            badge_type="positive"
        )

    with k2:
        doc_max_dept, doc_max_val = extremes["doc_max"]
        hlp.render_kpi_card(
            title="Highest Doctor Ratio",
            value=f"{doc_max_val:.1f} Pts",
            subtitle=f"Unit: {doc_max_dept}",
            icon="📈",
            badge_text="High Load",
            badge_type="danger"
        )

    with k3:
        doc_min_dept, doc_min_val = extremes["doc_min"]
        hlp.render_kpi_card(
            title="Lowest Doctor Ratio",
            value=f"{doc_min_val:.1f} Pts",
            subtitle=f"Unit: {doc_min_dept}",
            icon="📉",
            badge_text="Optimal",
            badge_type="positive"
        )

    with k4:
        hlp.render_kpi_card(
            title="Hospital Pts / Nurse",
            value=f"{overall_p_per_nur:.1f}" if overall_p_per_nur != float("inf") else "Critical (0 Nurses)",
            subtitle=f"Aggregated as of {snapshot_str}",
            icon="💉",
            badge_text="Overall Ratio",
            badge_type="positive"
        )

    with k5:
        nur_max_dept, nur_max_val = extremes["nur_max"]
        hlp.render_kpi_card(
            title="Highest Nurse Ratio",
            value=f"{nur_max_val:.1f} Pts",
            subtitle=f"Unit: {nur_max_dept}",
            icon="📈",
            badge_text="High Load",
            badge_type="danger"
        )

    with k6:
        nur_min_dept, nur_min_val = extremes["nur_min"]
        hlp.render_kpi_card(
            title="Lowest Nurse Ratio",
            value=f"{nur_min_val:.1f} Pts",
            subtitle=f"Unit: {nur_min_dept}",
            icon="📉",
            badge_text="Optimal",
            badge_type="positive"
        )

    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 1.5rem 0;'>", unsafe_allow_html=True)

    # ==========================================================================
    # SECTION 12.2: CHARTS 1 & 2 — WORKLOAD RATIO VS TARGET BY DEPARTMENT
    # ==========================================================================
    st.markdown("<h3 style='margin-bottom: 0.8rem;'>1. Department Ratio Benchmarks vs Clinical Targets</h3>", unsafe_allow_html=True)
    col_doc_bench, col_nur_bench = st.columns(2)

    with col_doc_bench:
        fig_doc_bench = chrt.create_grouped_bar_chart(
            dept_stats,
            x="Department",
            y_cols=["Patients_per_Doctor", "Target_Patients_per_Doctor"],
            title=f"Doctor Ratio: Actual vs Target by Department ({snapshot_str})",
            x_title="Department",
            y_title="Patients per Doctor",
            colors=["#3B82F6", "#F59E0B"]
        )
        st.plotly_chart(fig_doc_bench, width="stretch")

    with col_nur_bench:
        fig_nur_bench = chrt.create_grouped_bar_chart(
            dept_stats,
            x="Department",
            y_cols=["Patients_per_Nurse", "Target_Patients_per_Nurse"],
            title=f"Nurse Ratio: Actual vs Target by Department ({snapshot_str})",
            x_title="Department",
            y_title="Patients per Nurse",
            colors=["#8B5CF6", "#F59E0B"]
        )
        st.plotly_chart(fig_nur_bench, width="stretch")

    # ==========================================================================
    # SECTION 12.3: CHARTS 3 & 4 — DAILY RATIO TREND OVER TIME & HEATMAP
    # ==========================================================================
    st.markdown("<h3 style='margin-top: 1rem; margin-bottom: 0.8rem;'>2. Historical Ratio Trajectory & Department Heatmap Matrix</h3>", unsafe_allow_html=True)
    col_trend, col_heatmap = st.columns([1.3, 1])

    with col_trend:
        daily_trend = calc.get_daily_staffing_trend(filtered_staffing, department=selected_dept)
        fig_time_trend = chrt.create_line_chart(
            daily_trend,
            x="Date",
            y=["Overall_Patients_per_Doctor", "Overall_Patients_per_Nurse"],
            title="Hospital Staffing Ratio Trajectory Over Time",
            x_title="Observation Date",
            y_title="Patients per Staff Member",
            color_map={"Overall_Patients_per_Doctor": "#3B82F6", "Overall_Patients_per_Nurse": "#8B5CF6"}
        )
        st.plotly_chart(fig_time_trend, width="stretch")

    with col_heatmap:
        # Department vs Shift Heatmap
        fig_heat = chrt.create_heatmap(
            filtered_staffing,
            x="Shift",
            y="Department",
            z="Patients_per_Nurse",
            title="Nurse Workload Heatmap by Department & Shift"
        )
        st.plotly_chart(fig_heat, width="stretch")

    # ==========================================================================
    # SECTION 12.4: HIGH-LOAD RECORDS SURVEILLANCE & LOGS
    # ==========================================================================
    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 1.5rem 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom: 0.5rem;'>High-Load Records Surveillance Log</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.85rem; color: #94A3B8;'>Filter historical shifts and department records that exceeded target workload thresholds.</p>", unsafe_allow_html=True)

    log_filter_type = st.radio(
        "Select Surveillance Filter:",
        options=["All High Load Records", "Doctor High Load Only", "Nurse High Load Only", "All Department Logs"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if log_filter_type == "Doctor High Load Only":
        log_df = filtered_staffing[filtered_staffing["Doctor_Ratio_Status"] == "High Load"]
    elif log_filter_type == "Nurse High Load Only":
        log_df = filtered_staffing[filtered_staffing["Nurse_Ratio_Status"] == "High Load"]
    elif log_filter_type == "All High Load Records":
        log_df = filtered_staffing[
            (filtered_staffing["Doctor_Ratio_Status"] == "High Load") | (filtered_staffing["Nurse_Ratio_Status"] == "High Load")
        ]
    else:
        log_df = filtered_staffing

    log_cols = [
        "Date", "Department", "Shift", "Daily_Patient_Census",
        "Active_Doctors_On_Duty", "Patients_per_Doctor", "Doctor_Ratio_Status",
        "Active_Nurses_On_Duty", "Patients_per_Nurse", "Nurse_Ratio_Status", "Bed_Occupancy_Rate"
    ]
    avail_cols = [c for c in log_cols if c in log_df.columns]
    display_log = log_df[avail_cols].sort_values(by="Date", ascending=False).copy()

    # Format Date
    if "Date" in display_log.columns:
        display_log["Date"] = display_log["Date"].dt.strftime("%Y-%m-%d")
    if "Bed_Occupancy_Rate" in display_log.columns:
        display_log["Bed_Occupancy_Rate"] = (display_log["Bed_Occupancy_Rate"] * 100).round(1).astype(str) + "%"

    # Row limit
    col_pg, col_exp1, col_exp2 = st.columns([2, 1, 1])
    with col_pg:
        row_limit = st.selectbox("Display Limit", options=[15, 30, 50, 100, "All"], index=0, label_visibility="collapsed")
    
    if row_limit != "All":
        display_log = display_log.head(int(row_limit))

    st.dataframe(
        display_log,
        width="stretch",
        hide_index=True
    )

    with col_exp1:
        csv_bytes = hlp.convert_df_to_csv(log_df[avail_cols])
        st.download_button(
            label="📥 Export Logs CSV",
            data=csv_bytes,
            file_name=f"staffing_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            width="stretch"
        )

    with col_exp2:
        excel_bytes = hlp.convert_dfs_to_excel({"Staffing_Surveillance": log_df[avail_cols]})
        st.download_button(
            label="📊 Export Logs Excel",
            data=excel_bytes,
            file_name=f"staffing_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch"
        )


if __name__ == "__main__":
    from streamlit.runtime import exists
    if not exists():
        from pathlib import Path
        import sys
        from streamlit.web import cli as stcli
        # Route to app.py to preserve full multipage architecture
        root_app = Path(__file__).resolve().parent.parent / "app.py"
        target = str(root_app) if root_app.exists() else __file__
        sys.argv = ["streamlit", "run", target] + sys.argv[1:]
        sys.exit(stcli.main())
    else:
        main()
