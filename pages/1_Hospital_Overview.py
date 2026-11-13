"""
pages/1_Hospital_Overview.py
Page 1: Executive Hospital Overview & Core Analytics Dashboard.
Provides high-level hospital KPIs, admission trends, staffing distributions,
bed occupancy metrics, patient demographics, threshold-based staffing alerts,
and searchable patient registry.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path so 'utils' can always be imported regardless of execution context
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
        page_title="Hospital Overview | MediCore Analytics",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 2. Inject Enterprise Custom CSS
    hlp.apply_custom_css()

    # 3. Load Dataset (handles custom upload or default Excel)
    uploaded_source = st.session_state.get("uploaded_file", None)
    try:
        data = load_excel_data(uploaded_source)
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")
        st.stop()

    df_patients = data["Patients"]
    df_doctors = data["Doctors"]
    df_nurses = data["Nurses"]
    df_staffing = data["Daily_Staffing"]
    df_departments = data["Departments"]

    # 4. Render Global Sidebar & Retrieve Filter Settings
    filters = flt.render_global_sidebar(data)
    start_date = filters["start_date"]
    end_date = filters["end_date"]
    selected_dept = filters["department"]
    selected_shift = filters["shift"]

    # 5. Apply Contextual Filters
    # - Patients: filtered by Admission_Date cohort and department
    filtered_patients = flt.filter_patients(
        df_patients,
        start_date=start_date,
        end_date=end_date,
        department=selected_dept
    )

    # - Daily Staffing: filtered by Date range, department, and shift
    filtered_staffing = flt.filter_daily_staffing(
        df_staffing,
        start_date=start_date,
        end_date=end_date,
        department=selected_dept,
        shift=selected_shift
    )

    # - Doctors & Nurses: filtered by registered attributes (not arbitrary cohort dates)
    filtered_doctors = flt.filter_doctors(
        df_doctors,
        department=selected_dept,
        shift=selected_shift
    )
    filtered_nurses = flt.filter_nurses(
        df_nurses,
        department=selected_dept,
        shift=selected_shift
    )

    # Determine Snapshot Date (Latest available in the filtered staffing dataset)
    if not filtered_staffing.empty and "Date" in filtered_staffing.columns:
        snapshot_date = filtered_staffing["Date"].max()
        snapshot_str = snapshot_date.strftime("%b %d, %Y")
    else:
        snapshot_date = df_staffing["Date"].max() if not df_staffing.empty else datetime.now()
        snapshot_str = "No Data"

    # Date range string for header
    date_range_str = f"{start_date.strftime('%b %d, %Y')} – {end_date.strftime('%b %d, %Y')}"

    # 6. Executive Page Header
    hlp.render_page_header(
        title="Hospital Overview",
        subtitle="Hospital Performance, Patient Census & Workforce Analytics",
        selected_range=date_range_str,
        selected_dept=selected_dept,
        latest_update=f"Snapshot: {snapshot_str}"
    )

    # ==========================================================================
    # 7.1 EXECUTIVE KPI CARDS (8 Cards in 2 Rows)
    # ==========================================================================
    st.markdown("<h3 style='margin-top: 0.5rem; margin-bottom: 0.8rem;'>Executive Performance Indicators</h3>", unsafe_allow_html=True)

    # Row 1: Patient & Workforce Totals
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    total_pts = calc.get_total_patients(filtered_patients)
    with kpi1:
        hlp.render_kpi_card(
            title="Total Patient Records",
            value=hlp.format_number(total_pts),
            subtitle="Cohort episode records",
            icon="👥",
            badge_text="Historical",
            badge_type="neutral"
        )

    current_census = calc.get_current_patient_census(filtered_staffing, date=snapshot_date, department=selected_dept)
    with kpi2:
        hlp.render_kpi_card(
            title="Current Patient Census",
            value=hlp.format_number(current_census),
            subtitle=f"As of {snapshot_str}",
            icon="🏥",
            badge_text="Live Census",
            badge_type="positive"
        )

    doc_breakdown = calc.get_doctor_status_breakdown(filtered_doctors)
    with kpi3:
        hlp.render_kpi_card(
            title="Registered Doctors",
            value=hlp.format_number(doc_breakdown["total"]),
            subtitle=f"{doc_breakdown['active']} Active | {doc_breakdown['on_leave']} Leave",
            icon="🩺",
            badge_text=f"{doc_breakdown['active']} Active",
            badge_type="positive" if doc_breakdown["active"] > 0 else "warning"
        )

    nurse_breakdown = calc.get_nurse_status_breakdown(filtered_nurses)
    with kpi4:
        hlp.render_kpi_card(
            title="Registered Nurses",
            value=hlp.format_number(nurse_breakdown["total"]),
            subtitle=f"{nurse_breakdown['active']} Active | {nurse_breakdown['on_leave']} Leave",
            icon="👩‍⚕️",
            badge_text=f"{nurse_breakdown['active']} Active",
            badge_type="positive" if nurse_breakdown["active"] > 0 else "warning"
        )

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    # Row 2: Active Duty & Capacity Metrics
    kpi5, kpi6, kpi7, kpi8 = st.columns(4)

    active_docs_duty = calc.get_active_doctors(filtered_staffing, date=snapshot_date, department=selected_dept)
    with kpi5:
        hlp.render_kpi_card(
            title="Doctors on Duty",
            value=hlp.format_number(active_docs_duty),
            subtitle="Active on shift snapshot",
            icon="👨‍⚕️",
            badge_text="On Shift",
            badge_type="positive"
        )

    active_nurses_duty = calc.get_active_nurses(filtered_staffing, date=snapshot_date, department=selected_dept)
    with kpi6:
        hlp.render_kpi_card(
            title="Nurses on Duty",
            value=hlp.format_number(active_nurses_duty),
            subtitle="Active on shift snapshot",
            icon="💉",
            badge_text="On Shift",
            badge_type="positive"
        )

    bed_occ_rate = calc.get_bed_occupancy_rate(filtered_staffing, date=snapshot_date, department=selected_dept)
    occ_badge = "positive" if bed_occ_rate < 80 else ("warning" if bed_occ_rate < 90 else "danger")
    with kpi7:
        hlp.render_kpi_card(
            title="Hospital Bed Occupancy",
            value=hlp.format_percent(bed_occ_rate),
            subtitle=f"{calc.get_occupied_beds(filtered_staffing, date=snapshot_date, department=selected_dept):,} / {calc.get_bed_capacity(filtered_staffing, date=snapshot_date, department=selected_dept):,} Beds",
            icon="🛏️",
            badge_text="Aggregated",
            badge_type=occ_badge
        )

    avg_los = calc.get_average_length_of_stay(filtered_patients)
    with kpi8:
        hlp.render_kpi_card(
            title="Average Length of Stay",
            value=f"{avg_los:.1f} Days",
            subtitle="Patient admission duration",
            icon="⏳",
            badge_text="Target: <5d",
            badge_type="positive" if avg_los <= 5.0 else "warning"
        )

    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 1.5rem 0;'>", unsafe_allow_html=True)

    # ==========================================================================
    # 7.2 PATIENT ADMISSION & DISCHARGE TREND & 7.5 BED OCCUPANCY DONUT
    # ==========================================================================
    col_trend, col_donut = st.columns([2, 1])

    with col_trend:
        monthly_trend = calc.get_monthly_admissions_and_discharges(filtered_patients)
        fig_trend = chrt.create_line_chart(
            monthly_trend,
            x="Month",
            y=["Admissions", "Discharges"],
            title="Patient Admission & Discharge Trend (Monthly)",
            x_title="Admission / Discharge Month",
            y_title="Patient Volume",
            color_map={"Admissions": "#3B82F6", "Discharges": "#06B6D4"}
        )
        st.plotly_chart(fig_trend, width="stretch")

    with col_donut:
        total_cap = calc.get_bed_capacity(filtered_staffing, date=snapshot_date, department=selected_dept)
        total_occ = calc.get_occupied_beds(filtered_staffing, date=snapshot_date, department=selected_dept)
        total_avail = calc.get_available_beds(filtered_staffing, date=snapshot_date, department=selected_dept)

        fig_donut = chrt.create_donut_chart(
            labels=["Occupied Beds", "Available Beds"],
            values=[total_occ, total_avail],
            title="Hospital Bed Occupancy",
            center_text=f"{bed_occ_rate:.1f}%",
            center_subtext="Occupancy Rate",
            colors=["#3B82F6", "#1E293B"]
        )
        st.plotly_chart(fig_donut, width="stretch")

    # ==========================================================================
    # 7.3 DEPARTMENT-WISE PATIENTS & 7.4 MEDICAL STAFF DISTRIBUTION
    # ==========================================================================
    col_dept_pts, col_staff_dist = st.columns([1, 1])

    with col_dept_pts:
        # User toggle between Snapshot Census and Historical Records
        metric_choice = st.radio(
            "Department Volume Metric:",
            options=["Daily Patient Census (Snapshot)", "Historical Patient Records"],
            horizontal=True,
            label_visibility="collapsed"
        )

        if "Daily Patient Census" in metric_choice:
            snap_staff = filtered_staffing[filtered_staffing["Date"] == snapshot_date] if not filtered_staffing.empty else pd.DataFrame()
            if not snap_staff.empty:
                dept_data = snap_staff[["Department", "Daily_Patient_Census"]].rename(columns={"Daily_Patient_Census": "Patient_Count"})
            else:
                dept_data = pd.DataFrame(columns=["Department", "Patient_Count"])
            chart_subtitle = f"Daily Patient Census ({snapshot_str})"
        else:
            if not filtered_patients.empty:
                dept_data = filtered_patients["Department"].value_counts().reset_index()
                dept_data.columns = ["Department", "Patient_Count"]
            else:
                dept_data = pd.DataFrame(columns=["Department", "Patient_Count"])
            chart_subtitle = "Historical Patient Records"

        fig_dept = chrt.create_bar_chart(
            dept_data,
            x="Patient_Count",
            y="Department",
            title=f"Patients by Department — {chart_subtitle}",
            orientation="h",
            sort_descending=True,
            highlight_top_n=3,
            x_title="Patient Volume",
            y_title="Department"
        )
        st.plotly_chart(fig_dept, width="stretch")

    with col_staff_dist:
        snap_staff = filtered_staffing[filtered_staffing["Date"] == snapshot_date] if not filtered_staffing.empty else pd.DataFrame()
        if not snap_staff.empty:
            staff_comp = snap_staff[["Department", "Active_Doctors_On_Duty", "Active_Nurses_On_Duty"]].sort_values(by="Active_Nurses_On_Duty", ascending=False)
        else:
            staff_comp = pd.DataFrame(columns=["Department", "Active_Doctors_On_Duty", "Active_Nurses_On_Duty"])

        fig_staff_comp = chrt.create_grouped_bar_chart(
            staff_comp,
            x="Department",
            y_cols=["Active_Doctors_On_Duty", "Active_Nurses_On_Duty"],
            title=f"Medical Staff Distribution on Duty ({snapshot_str})",
            x_title="Department",
            y_title="Staff On Duty",
            colors=["#3B82F6", "#8B5CF6"]
        )
        st.plotly_chart(fig_staff_comp, width="stretch")

    # ==========================================================================
    # 7.6 PATIENT DEMOGRAPHICS
    # ==========================================================================
    st.markdown("<h3 style='margin-top: 1rem; margin-bottom: 0.8rem;'>Patient Demographics & Admission Profiles</h3>", unsafe_allow_html=True)
    demo1, demo2, demo3 = st.columns(3)

    with demo1:
        fig_age = chrt.create_histogram(
            filtered_patients,
            x="Age",
            title="Patient Age Distribution",
            nbins=20,
            x_title="Age (Years)",
            y_title="Patient Count",
            color="#3B82F6"
        )
        st.plotly_chart(fig_age, width="stretch")

    with demo2:
        gender_counts = filtered_patients["Gender"].value_counts() if not filtered_patients.empty else pd.Series()
        fig_gender = chrt.create_donut_chart(
            labels=gender_counts.index.tolist(),
            values=gender_counts.values.tolist(),
            title="Gender Distribution",
            center_text=str(len(filtered_patients)),
            center_subtext="Total Cohort",
            colors=["#3B82F6", "#EC4899", "#8B5CF6"]
        )
        st.plotly_chart(fig_gender, width="stretch")

    with demo3:
        adm_counts = filtered_patients["Admission_Type"].value_counts().reset_index() if not filtered_patients.empty else pd.DataFrame(columns=["Admission_Type", "Count"])
        if not adm_counts.empty:
            adm_counts.columns = ["Admission_Type", "Count"]
        fig_adm = chrt.create_bar_chart(
            adm_counts,
            x="Admission_Type",
            y="Count",
            title="Admission Type Breakdown",
            orientation="v",
            color_code="#06B6D4",
            x_title="Admission Type",
            y_title="Patients"
        )
        st.plotly_chart(fig_adm, width="stretch")

    # ==========================================================================
    # 7.7 THRESHOLD-BASED STAFFING & CAPACITY ALERTS
    # ==========================================================================
    st.markdown("<h3 style='margin-top: 1rem; margin-bottom: 0.8rem;'>Workforce Capacity & Threshold Indicators</h3>", unsafe_allow_html=True)
    alerts = calc.get_high_workload_departments(filtered_staffing, df_departments, date=snapshot_date, occupancy_threshold=85.0)

    alert_col1, alert_col2 = st.columns(2)

    with alert_col1:
        high_doc = alerts["high_doctor_load"]
        if not high_doc.empty:
            doc_items = ", ".join([f"{r['Department']} ({r['Patients_per_Doctor']:.1f} vs target {r['Target_Patients_per_Doctor']})" for _, r in high_doc.head(3).iterrows()])
            hlp.render_alert_box(
                title=f"Doctor Workload Alert: {len(high_doc)} Department(s) Above Target",
                message=f"Patients per doctor ratio exceeds recommended target in: {doc_items}.",
                alert_type="warning",
                icon="🩺"
            )
        else:
            hlp.render_alert_box(
                title="Doctor Workload Balanced",
                message="All departments operate within designated patient-to-doctor target ratios.",
                alert_type="success",
                icon="✅"
            )

        high_occ = alerts["high_occupancy"]
        if not high_occ.empty:
            occ_items = ", ".join([f"{r['Department']} ({r['Occupancy_Rate_Pct']:.1f}%)" for _, r in high_occ.head(3).iterrows()])
            hlp.render_alert_box(
                title=f"High Bed Occupancy: {len(high_occ)} Department(s) ≥ 85%",
                message=f"Near-capacity utilization detected in: {occ_items}.",
                alert_type="danger",
                icon="🛏️"
            )
        else:
            hlp.render_alert_box(
                title="Bed Occupancy Optimal",
                message="All departments maintain bed occupancy below the 85% high-utilization threshold.",
                alert_type="success",
                icon="✅"
            )

    with alert_col2:
        high_nur = alerts["high_nurse_load"]
        if not high_nur.empty:
            nur_items = ", ".join([f"{r['Department']} ({r['Patients_per_Nurse']:.1f} vs target {r['Target_Patients_per_Nurse']})" for _, r in high_nur.head(3).iterrows()])
            hlp.render_alert_box(
                title=f"Nurse Workload Alert: {len(high_nur)} Department(s) Above Target",
                message=f"Patients per nurse ratio exceeds recommended target in: {nur_items}.",
                alert_type="warning",
                icon="💉"
            )
        else:
            hlp.render_alert_box(
                title="Nurse Workload Balanced",
                message="All departments operate within designated patient-to-nurse target ratios.",
                alert_type="success",
                icon="✅"
            )

        crit = alerts["critical_attention"]
        if not crit.empty:
            crit_depts = ", ".join(crit["Department"].tolist())
            hlp.render_alert_box(
                title="Priority Attention Required",
                message=f"Departments experiencing compound workload pressures (Doctor ratio + Nurse ratio / High Occupancy): {crit_depts}.",
                alert_type="danger",
                icon="🚨"
            )
        else:
            hlp.render_alert_box(
                title="No Compound Criticalities Detected",
                message="No departments are concurrently facing acute multi-threshold staffing bottlenecks.",
                alert_type="info",
                icon="🛡️"
            )

    # ==========================================================================
    # 7.8 RECENT PATIENT RECORDS (SEARCHABLE, SORTABLE, PAGINATED TABLE)
    # ==========================================================================
    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 1.5rem 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom: 0.5rem;'>Patient Registry & Clinical Episodes</h3>", unsafe_allow_html=True)

    # Search & Page size controls
    t_ctrl1, t_ctrl2, t_ctrl3, t_ctrl4 = st.columns([2, 1, 1, 1])

    with t_ctrl1:
        search_query = st.text_input(
            "🔍 Search Patients",
            placeholder="Search by Patient ID, Name, or Condition...",
            label_visibility="collapsed"
        )

    with t_ctrl2:
        row_limit = st.selectbox(
            "Rows to Display",
            options=[15, 30, 50, 100, "All"],
            index=0,
            label_visibility="collapsed"
        )

    # Prepare Display DataFrame
    display_cols = [
        "Patient_ID", "Patient_Name", "Age", "Gender", "Department",
        "Admission_Date", "Discharge_Date", "Admission_Type",
        "Primary_Condition", "Length_of_Stay_Days", "Patient_Status"
    ]
    available_cols = [c for c in display_cols if c in filtered_patients.columns]
    table_df = filtered_patients[available_cols].copy()

    # Search filter
    if search_query:
        q = search_query.strip().lower()
        mask = (
            table_df["Patient_ID"].astype(str).str.lower().str.contains(q, na=False) |
            table_df["Patient_Name"].astype(str).str.lower().str.contains(q, na=False) |
            table_df["Department"].astype(str).str.lower().str.contains(q, na=False) |
            table_df["Primary_Condition"].astype(str).str.lower().str.contains(q, na=False)
        )
        table_df = table_df[mask]

    # Sort descending by Admission_Date
    if "Admission_Date" in table_df.columns:
        table_df = table_df.sort_values(by="Admission_Date", ascending=False)

    # Format dates for display
    display_table = table_df.copy()
    if "Admission_Date" in display_table.columns:
        display_table["Admission_Date"] = display_table["Admission_Date"].dt.strftime("%Y-%m-%d")
    if "Discharge_Date" in display_table.columns:
        display_table["Discharge_Date"] = display_table["Discharge_Date"].dt.strftime("%Y-%m-%d").fillna("Currently Admitted")

    # Limit rows
    if row_limit != "All":
        display_table = display_table.head(int(row_limit))

    # Render table
    st.dataframe(
        display_table,
        width="stretch",
        hide_index=True
    )

    # Export Buttons (CSV & Styled Executive Master Excel)
    with t_ctrl3:
        csv_data = hlp.convert_df_to_csv(table_df)
        st.download_button(
            label="📥 Export CSV",
            data=csv_data,
            file_name=f"patients_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            width="stretch"
        )

    with t_ctrl4:
        dept_summary = calc.get_department_statistics(filtered_staffing, df_departments, date=snapshot_date)
        snap_export = filtered_staffing[filtered_staffing["Date"] == snapshot_date] if not filtered_staffing.empty else filtered_staffing
        master_dict = {
            "Department_Summary": dept_summary,
            "Patient_Registry": table_df,
            "Daily_Staffing_Snapshot": snap_export,
            "Doctor_Roster": filtered_doctors,
            "Nurse_Roster": filtered_nurses
        }
        excel_data = hlp.convert_dfs_to_excel(master_dict, apply_styling=True)
        st.download_button(
            label="📊 Master Excel",
            data=excel_data,
            file_name=f"hospital_master_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch"
        )


if __name__ == "__main__":
    from streamlit.runtime import exists
    if not exists():
        from pathlib import Path
        import sys
        from streamlit.web import cli as stcli
        root_app = Path(__file__).resolve().parent.parent / "app.py"
        target = str(root_app) if root_app.exists() else __file__
        sys.argv = ["streamlit", "run", target] + sys.argv[1:]
        sys.exit(stcli.main())
    else:
        main()
