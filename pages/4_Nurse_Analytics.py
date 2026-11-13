"""
pages/4_Nurse_Analytics.py
Page 4: Nurse Workforce Analytics & Ward Allocation Directory.
Features 6 KPI cards, 6 comprehensive analytical charts (department distribution,
ward assignments, shift distribution, contract types, experience brackets,
and department workload vs nurse target ratios), interactive directory with search,
and multi-format data export.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from datetime import datetime
import pandas as pd
import streamlit as st

from utils.data_loader import load_excel_data
import utils.calculations as calc
import utils.charts as chrt
import utils.filters as flt
import utils.helpers as hlp


def main():
    # 1. Page Configuration
    st.set_page_config(
        page_title="Nurse Analytics | MediCore Analytics",
        page_icon="👩‍⚕️",
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

    df_nurses = data["Nurses"]
    df_daily_staffing = data.get("Daily_Staffing", pd.DataFrame())
    df_departments = data.get("Departments", pd.DataFrame())

    # 4. Render Global Sidebar & Retrieve Filter Settings
    global_filters = flt.render_global_sidebar(data)
    selected_dept = global_filters["department"]
    selected_shift = global_filters["shift"]
    start_date = global_filters["start_date"]
    end_date = global_filters["end_date"]

    # 5. Page-Specific Sub-Filter Bar (Ward, Employment Type, Status)
    st.markdown("<p style='font-size: 0.85rem; font-weight: 600; color: #3B82F6; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;'>Nurse Roster Filters</p>", unsafe_allow_html=True)
    nurse_filters = flt.render_nurse_page_filters(df_nurses)
    sel_ward = nurse_filters["ward"]
    sel_emp = nurse_filters["employment_type"]
    sel_status = nurse_filters["status"]

    # 6. Apply Filtering to Registered Nurses
    filtered_nurses = flt.filter_nurses(
        df_nurses,
        department=selected_dept,
        ward=sel_ward,
        employment_type=sel_emp,
        status=sel_status,
        shift=selected_shift
    )

    # Filter Daily Staffing for Workload Benchmarking
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
        title="Nurse Analytics",
        subtitle="Nursing Staff Workforce Capacity, Ward Allocation & Workload Analytics",
        selected_range=f"Roster Status ({snapshot_str})",
        selected_dept=selected_dept,
        latest_update=f"Filtered Nurses: {len(filtered_nurses):,} Personnel"
    )

    # ==========================================================================
    # SECTION 10.1: NURSE KPI CARDS (6 CARDS)
    # ==========================================================================
    st.markdown("<h3 style='margin-top: 0.5rem; margin-bottom: 0.8rem;'>Nursing Workforce Capacity Indicators</h3>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5, k6 = st.columns(6)

    breakdown = calc.get_nurse_status_breakdown(filtered_nurses)
    total_nurses = breakdown["total"]

    with k1:
        hlp.render_kpi_card(
            title="Total Nurses",
            value=hlp.format_number(total_nurses),
            subtitle="Registered nursing staff",
            icon="👩‍⚕️",
            badge_text="Registered",
            badge_type="neutral"
        )

    with k2:
        active_pct = f"{breakdown['active'] / total_nurses * 100:.1f}%" if total_nurses > 0 else "0.0%"
        hlp.render_kpi_card(
            title="Active Nurses",
            value=hlp.format_number(breakdown["active"]),
            subtitle=f"{active_pct} operational",
            icon="💉",
            badge_text="Ready for Duty",
            badge_type="positive"
        )

    with k3:
        leave_pct = f"{breakdown['on_leave'] / total_nurses * 100:.1f}%" if total_nurses > 0 else "0.0%"
        hlp.render_kpi_card(
            title="Nurses on Leave",
            value=hlp.format_number(breakdown["on_leave"]),
            subtitle=f"{leave_pct} of roster",
            icon="🏖️",
            badge_text="Temporary Leave",
            badge_type="warning" if breakdown["on_leave"] > 0 else "neutral"
        )

    with k4:
        hlp.render_kpi_card(
            title="Inactive Nurses",
            value=hlp.format_number(breakdown["inactive"]),
            subtitle="Off duty / inactive",
            icon="⏸️",
            badge_text="Inactive",
            badge_type="danger" if breakdown["inactive"] > 0 else "positive"
        )

    with k5:
        ft_pct = f"{breakdown['full_time'] / total_nurses * 100:.1f}%" if total_nurses > 0 else "0.0%"
        hlp.render_kpi_card(
            title="Full-time",
            value=hlp.format_number(breakdown["full_time"]),
            subtitle=f"{ft_pct} staff nurses",
            icon="💼",
            badge_text="Full-time",
            badge_type="positive"
        )

    with k6:
        pt_pct = f"{breakdown['part_time'] / total_nurses * 100:.1f}%" if total_nurses > 0 else "0.0%"
        hlp.render_kpi_card(
            title="Part-time",
            value=hlp.format_number(breakdown["part_time"]),
            subtitle=f"{pt_pct} roster",
            icon="⏱️",
            badge_text="Part-time",
            badge_type="neutral"
        )

    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 1.5rem 0;'>", unsafe_allow_html=True)

    # ==========================================================================
    # SECTION 10.2: CHARTS 1 & 2 — DEPARTMENT ALLOCATION & WARD DISTRIBUTION
    # ==========================================================================
    st.markdown("<h3 style='margin-bottom: 0.8rem;'>1. Department Allocation & Ward Assignments</h3>", unsafe_allow_html=True)
    col_dept, col_ward = st.columns([1, 1.2])

    with col_dept:
        if not filtered_nurses.empty:
            dept_counts = filtered_nurses["Department"].value_counts().reset_index()
            dept_counts.columns = ["Department", "Nurse_Count"]
        else:
            dept_counts = pd.DataFrame(columns=["Department", "Nurse_Count"])

        fig_dept = chrt.create_bar_chart(
            dept_counts,
            x="Nurse_Count",
            y="Department",
            title="Nurses by Department (Top 3 Highlighted)",
            orientation="h",
            sort_descending=True,
            highlight_top_n=3,
            x_title="Nurse Count",
            y_title="Department"
        )
        st.plotly_chart(fig_dept, width="stretch")

    with col_ward:
        if not filtered_nurses.empty:
            ward_counts = filtered_nurses["Ward"].value_counts().reset_index()
            ward_counts.columns = ["Ward", "Nurse_Count"]
        else:
            ward_counts = pd.DataFrame(columns=["Ward", "Nurse_Count"])

        fig_ward = chrt.create_bar_chart(
            ward_counts,
            x="Nurse_Count",
            y="Ward",
            title="Nurses by Ward Deployment (10 Wards)",
            orientation="h",
            sort_descending=True,
            highlight_top_n=3,
            color_code="#06B6D4",
            x_title="Deployed Nurses",
            y_title="Ward Unit"
        )
        st.plotly_chart(fig_ward, width="stretch")

    # ==========================================================================
    # SECTION 10.3: CHARTS 3 & 4 — SHIFTS & CONTRACT TYPE BREAKDOWN
    # ==========================================================================
    st.markdown("<h3 style='margin-top: 1rem; margin-bottom: 0.8rem;'>2. Shift Coverage & Contract Structure</h3>", unsafe_allow_html=True)
    col_shift, col_emp = st.columns(2)

    with col_shift:
        if not filtered_nurses.empty:
            shift_counts = filtered_nurses["Shift"].value_counts().reset_index()
            shift_counts.columns = ["Shift", "Nurse_Count"]
        else:
            shift_counts = pd.DataFrame(columns=["Shift", "Nurse_Count"])

        fig_shift = chrt.create_bar_chart(
            shift_counts,
            x="Shift",
            y="Nurse_Count",
            title="Nurses by Assigned Shift Coverage",
            orientation="v",
            color_code="#F59E0B",
            x_title="Shift",
            y_title="Nurses"
        )
        st.plotly_chart(fig_shift, width="stretch")

    with col_emp:
        if not filtered_nurses.empty:
            emp_series = filtered_nurses["Employment_Type"].value_counts()
            e_labels = emp_series.index.tolist()
            e_values = emp_series.values.tolist()
        else:
            e_labels, e_values = [], []

        fig_emp = chrt.create_donut_chart(
            labels=e_labels,
            values=e_values,
            title="Nurses by Employment Type",
            center_text=f"{total_nurses:,}",
            center_subtext="Total Nurses",
            colors=["#3B82F6", "#8B5CF6"]
        )
        st.plotly_chart(fig_emp, width="stretch")

    # ==========================================================================
    # SECTION 10.4: CHARTS 5 & 6 — EXPERIENCE BRACKETS & WORKLOAD BENCHMARKING
    # ==========================================================================
    st.markdown("<h3 style='margin-top: 1rem; margin-bottom: 0.8rem;'>3. Experience Stratification & Clinical Workload Benchmarking</h3>", unsafe_allow_html=True)
    col_exp, col_workload = st.columns([1, 1.3])

    with col_exp:
        exp_dist = calc.get_experience_distribution(filtered_nurses)
        fig_exp = chrt.create_bar_chart(
            exp_dist,
            x="Experience_Group",
            y="Count",
            title="Nurses by Clinical Experience Bracket",
            orientation="v",
            sort_descending=False,
            color_code="#8B5CF6",
            x_title="Experience Tier",
            y_title="Nurses"
        )
        st.plotly_chart(fig_exp, width="stretch")

    with col_workload:
        dept_stats = calc.get_department_statistics(filtered_staffing, df_departments, date=snapshot_date)

        if not dept_stats.empty and "Patients_per_Nurse" in dept_stats.columns:
            workload_comp = dept_stats[["Department", "Patients_per_Nurse", "Target_Patients_per_Nurse"]].sort_values(by="Patients_per_Nurse", ascending=False)
            fig_workload = chrt.create_grouped_bar_chart(
                workload_comp,
                x="Department",
                y_cols=["Patients_per_Nurse", "Target_Patients_per_Nurse"],
                title=f"Nurse Workload vs Target Ratio by Department ({snapshot_str})",
                x_title="Department",
                y_title="Patients per Nurse",
                colors=["#3B82F6", "#F59E0B"]
            )
            st.plotly_chart(fig_workload, width="stretch")
        else:
            st.info("No daily staffing records available to compute nurse workload for the selected filters.")

    # ==========================================================================
    # SECTION 10.5: NURSE DIRECTORY TABLE & MULTI-FORMAT EXPORT
    # ==========================================================================
    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 1.5rem 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom: 0.5rem;'>Nursing Workforce Directory</h3>", unsafe_allow_html=True)

    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([2, 1, 1, 1])

    with ctrl1:
        search_query = st.text_input(
            "🔍 Search Nurses",
            placeholder="Search by Nurse ID, Name, Ward, or Department...",
            label_visibility="collapsed"
        )

    with ctrl2:
        row_limit = st.selectbox(
            "Page Size",
            options=[15, 30, 50, 100, "All"],
            index=0,
            label_visibility="collapsed"
        )

    dir_cols = [
        "Nurse_ID", "Nurse_Name", "Gender", "Department", "Ward",
        "Shift", "Employment_Type", "Experience_Years", "Status", "Weekly_Hours"
    ]
    avail_cols = [c for c in dir_cols if c in filtered_nurses.columns]
    table_df = filtered_nurses[avail_cols].copy()

    # Search filter
    if search_query:
        q = search_query.strip().lower()
        mask = (
            table_df["Nurse_ID"].astype(str).str.lower().str.contains(q, na=False) |
            table_df["Nurse_Name"].astype(str).str.lower().str.contains(q, na=False) |
            table_df["Department"].astype(str).str.lower().str.contains(q, na=False) |
            table_df["Ward"].astype(str).str.lower().str.contains(q, na=False)
        )
        table_df = table_df[mask]

    # Slice for row limit
    display_table = table_df.copy()
    if row_limit != "All":
        display_table = display_table.head(int(row_limit))

    # Render interactive directory
    st.dataframe(
        display_table,
        width="stretch",
        hide_index=True
    )

    # Export Buttons
    with ctrl3:
        csv_bytes = hlp.convert_df_to_csv(table_df)
        st.download_button(
            label="📥 Export CSV",
            data=csv_bytes,
            file_name=f"nurses_directory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            width="stretch"
        )

    with ctrl4:
        excel_bytes = hlp.convert_dfs_to_excel({"Nurse_Roster": table_df})
        st.download_button(
            label="📊 Export Excel",
            data=excel_bytes,
            file_name=f"nurses_directory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
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
