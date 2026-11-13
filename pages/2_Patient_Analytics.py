"""
pages/2_Patient_Analytics.py
Page 2: Patient Analytics & Clinical Episode Cohort Analysis.
Features 6 KPI cards, 8 comprehensive analytical charts (trends, demographics,
clinical conditions, admission types, and length-of-stay distributions),
page-specific multi-attribute filters, and an interactive patient registry table.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path so 'utils' can always be imported
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
        page_title="Patient Analytics | MediCore Analytics",
        page_icon="👥",
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

    df_patients = data["Patients"]
    df_daily_staffing = data.get("Daily_Staffing", pd.DataFrame())

    # 4. Render Global Sidebar & Retrieve Filter Settings
    global_filters = flt.render_global_sidebar(data)
    start_date = global_filters["start_date"]
    end_date = global_filters["end_date"]
    selected_dept = global_filters["department"]

    # 5. Page-Specific Sub-Filter Bar (Gender, Admission Type, Status)
    st.markdown("<p style='font-size: 0.85rem; font-weight: 600; color: #3B82F6; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;'>Patient Cohort Filters</p>", unsafe_allow_html=True)
    p_filters = flt.render_patient_page_filters(df_patients)
    sel_gender = p_filters["gender"]
    sel_adm_type = p_filters["admission_type"]
    sel_status = p_filters["patient_status"]

    # 6. Apply Compound Filtering
    # Note: Patient cohort filtering strictly uses Admission_Date for cohort date ranges
    filtered_patients = flt.filter_patients(
        df_patients,
        start_date=start_date,
        end_date=end_date,
        department=selected_dept,
        gender=sel_gender,
        admission_type=sel_adm_type,
        patient_status=sel_status
    )

    # Date range string for header
    date_range_str = f"{start_date.strftime('%b %d, %Y')} – {end_date.strftime('%b %d, %Y')}"
    filter_summary = f"Gender: {sel_gender} | Adm: {sel_adm_type} | Status: {sel_status}"

    # 7. Executive Page Header
    hlp.render_page_header(
        title="Patient Analytics",
        subtitle="Cohort Demographics, Clinical Admission Trends & Length of Stay Analytics",
        selected_range=date_range_str,
        selected_dept=selected_dept,
        latest_update=f"Filtered Cohort: {len(filtered_patients):,} Patients"
    )

    # ==========================================================================
    # SECTION 8.1: PATIENT KPI CARDS (6 CARDS)
    # ==========================================================================
    st.markdown("<h3 style='margin-top: 0.5rem; margin-bottom: 0.8rem;'>Cohort Clinical Indicators</h3>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5, k6 = st.columns(6)

    status_summary = calc.get_patient_status_summary(filtered_patients)
    total_cohort = status_summary["total"]

    with k1:
        hlp.render_kpi_card(
            title="Total Records",
            value=hlp.format_number(total_cohort),
            subtitle="Cohort episodes",
            icon="👥",
            badge_text="Cohort",
            badge_type="neutral"
        )

    with k2:
        admitted_pct = f"{status_summary['admitted'] / total_cohort * 100:.1f}%" if total_cohort > 0 else "0.0%"
        hlp.render_kpi_card(
            title="Admitted",
            value=hlp.format_number(status_summary["admitted"]),
            subtitle=f"{admitted_pct} of cohort",
            icon="🏥",
            badge_text="Active Inpatient",
            badge_type="positive"
        )

    with k3:
        discharged_pct = f"{status_summary['discharged'] / total_cohort * 100:.1f}%" if total_cohort > 0 else "0.0%"
        hlp.render_kpi_card(
            title="Discharged",
            value=hlp.format_number(status_summary["discharged"]),
            subtitle=f"{discharged_pct} of cohort",
            icon="✅",
            badge_text="Completed",
            badge_type="positive"
        )

    with k4:
        hlp.render_kpi_card(
            title="Transferred",
            value=hlp.format_number(status_summary["transferred"]),
            subtitle="External / Other Ward",
            icon="🔄",
            badge_text="Transferred",
            badge_type="warning"
        )

    with k5:
        avg_age = calc.get_average_patient_age(filtered_patients)
        hlp.render_kpi_card(
            title="Average Age",
            value=f"{avg_age:.1f} Yrs",
            subtitle="Patient population",
            icon="🎂",
            badge_text="Demographic",
            badge_type="neutral"
        )

    with k6:
        avg_los = calc.get_average_length_of_stay(filtered_patients)
        hlp.render_kpi_card(
            title="Avg Length of Stay",
            value=f"{avg_los:.1f} Days",
            subtitle="Clinical duration",
            icon="⏳",
            badge_text="Target: <5d",
            badge_type="positive" if avg_los <= 5.0 else "warning"
        )

    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 1.5rem 0;'>", unsafe_allow_html=True)

    # ==========================================================================
    # SECTION 8.2: CHARTS 1 & 2 — MONTHLY ADMISSION & DISCHARGE TRENDS
    # ==========================================================================
    st.markdown("<h3 style='margin-bottom: 0.8rem;'>1. Admission & Discharge Trajectory Over Time</h3>", unsafe_allow_html=True)
    col_adm_trend, col_dis_trend = st.columns(2)

    monthly_data = calc.get_monthly_admissions_and_discharges(filtered_patients)

    with col_adm_trend:
        fig_monthly_adm = chrt.create_line_chart(
            monthly_data,
            x="Month",
            y="Admissions",
            title="Monthly Patient Admissions",
            x_title="Admission Month",
            y_title="Admissions",
            color_map={"Admissions": "#3B82F6"}
        )
        st.plotly_chart(fig_monthly_adm, width="stretch")

    with col_dis_trend:
        fig_monthly_dis = chrt.create_line_chart(
            monthly_data,
            x="Month",
            y="Discharges",
            title="Monthly Patient Discharges (Excluding Active Inpatients)",
            x_title="Discharge Month",
            y_title="Discharges",
            color_map={"Discharges": "#06B6D4"}
        )
        st.plotly_chart(fig_monthly_dis, width="stretch")

    # ==========================================================================
    # SECTION 8.3: CHARTS 3 & 4 — DEPARTMENT DISTRIBUTION & GENDER BREAKDOWN
    # ==========================================================================
    st.markdown("<h3 style='margin-top: 1rem; margin-bottom: 0.8rem;'>2. Department Distribution & Gender Breakdown</h3>", unsafe_allow_html=True)
    col_dept, col_gender = st.columns([1.5, 1])

    with col_dept:
        if not filtered_patients.empty:
            dept_counts = filtered_patients["Department"].value_counts().reset_index()
            dept_counts.columns = ["Department", "Patient_Count"]
        else:
            dept_counts = pd.DataFrame(columns=["Department", "Patient_Count"])

        fig_dept = chrt.create_bar_chart(
            dept_counts,
            x="Patient_Count",
            y="Department",
            title="Patient Volume by Department (Top 3 Highlighted)",
            orientation="h",
            sort_descending=True,
            highlight_top_n=3,
            x_title="Patient Volume",
            y_title="Department"
        )
        st.plotly_chart(fig_dept, width="stretch")

    with col_gender:
        if not filtered_patients.empty:
            gender_series = filtered_patients["Gender"].value_counts()
            g_labels = gender_series.index.tolist()
            g_values = gender_series.values.tolist()
        else:
            g_labels, g_values = [], []

        fig_gender = chrt.create_donut_chart(
            labels=g_labels,
            values=g_values,
            title="Gender Distribution",
            center_text=f"{total_cohort:,}",
            center_subtext="Total Patients",
            colors=["#3B82F6", "#EC4899", "#8B5CF6"]
        )
        st.plotly_chart(fig_gender, width="stretch")

    # ==========================================================================
    # SECTION 8.4: CHARTS 5 & 6 — AGE GROUPS & PRIMARY MEDICAL CONDITIONS
    # ==========================================================================
    st.markdown("<h3 style='margin-top: 1rem; margin-bottom: 0.8rem;'>3. Age Group Stratification & Medical Conditions</h3>", unsafe_allow_html=True)
    col_age, col_condition = st.columns([1, 1.5])

    with col_age:
        age_dist = calc.get_age_group_distribution(filtered_patients)
        fig_age_groups = chrt.create_bar_chart(
            age_dist,
            x="Age_Group",
            y="Count",
            title="Patient Distribution by Age Bracket (0-17 to 76+)",
            orientation="v",
            sort_descending=False,
            color_code="#8B5CF6",
            x_title="Age Group",
            y_title="Patient Count"
        )
        st.plotly_chart(fig_age_groups, width="stretch")

    with col_condition:
        if not filtered_patients.empty:
            cond_counts = filtered_patients["Primary_Condition"].value_counts().reset_index()
            cond_counts.columns = ["Primary_Condition", "Count"]
        else:
            cond_counts = pd.DataFrame(columns=["Primary_Condition", "Count"])

        fig_condition = chrt.create_bar_chart(
            cond_counts,
            x="Count",
            y="Primary_Condition",
            title="Primary Medical Condition Breakdown",
            orientation="h",
            sort_descending=True,
            highlight_top_n=3,
            x_title="Case Volume",
            y_title="Medical Condition"
        )
        st.plotly_chart(fig_condition, width="stretch")

    # ==========================================================================
    # SECTION 8.5: CHARTS 7 & 8 — ADMISSION TYPE & LENGTH OF STAY DISTRIBUTION
    # ==========================================================================
    st.markdown("<h3 style='margin-top: 1rem; margin-bottom: 0.8rem;'>4. Admission Pathways & Clinical Stay Duration</h3>", unsafe_allow_html=True)
    col_adm_type, col_los = st.columns(2)

    with col_adm_type:
        if not filtered_patients.empty:
            adm_type_counts = filtered_patients["Admission_Type"].value_counts().reset_index()
            adm_type_counts.columns = ["Admission_Type", "Count"]
        else:
            adm_type_counts = pd.DataFrame(columns=["Admission_Type", "Count"])

        fig_adm_type = chrt.create_bar_chart(
            adm_type_counts,
            x="Admission_Type",
            y="Count",
            title="Admission Type Breakdown (Emergency vs Scheduled vs Outpatient)",
            orientation="v",
            color_code="#06B6D4",
            x_title="Admission Channel",
            y_title="Patients"
        )
        st.plotly_chart(fig_adm_type, width="stretch")

    with col_los:
        fig_los = chrt.create_histogram(
            filtered_patients,
            x="Length_of_Stay_Days",
            title="Length of Stay (LOS) Frequency Distribution",
            nbins=24,
            x_title="Length of Stay (Days)",
            y_title="Number of Patients",
            color="#22C55E"
        )
        st.plotly_chart(fig_los, width="stretch")

    # ==========================================================================
    # SECTION 8.6: SEARCHABLE CLINICAL REGISTRY TABLE & MULTI-FORMAT EXPORT
    # ==========================================================================
    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 1.5rem 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom: 0.5rem;'>Filtered Patient Cohort Registry</h3>", unsafe_allow_html=True)

    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([2, 1, 1, 1])

    with ctrl1:
        search_query = st.text_input(
            "🔍 Search Patient Cohort",
            placeholder="Search by ID, Name, Condition, Ward, or Doctor ID...",
            label_visibility="collapsed"
        )

    with ctrl2:
        row_limit = st.selectbox(
            "Page Size",
            options=[15, 30, 50, 100, "All"],
            index=0,
            label_visibility="collapsed"
        )

    # Columns to show in the patient directory
    registry_cols = [
        "Patient_ID", "Patient_Name", "Age", "Gender", "Department", "Ward",
        "Admission_Date", "Discharge_Date", "Admission_Type", "Primary_Condition",
        "Length_of_Stay_Days", "Patient_Status", "Attending_Doctor_ID"
    ]
    avail_cols = [c for c in registry_cols if c in filtered_patients.columns]
    table_df = filtered_patients[avail_cols].copy()

    # Search filter
    if search_query:
        q = search_query.strip().lower()
        mask = (
            table_df["Patient_ID"].astype(str).str.lower().str.contains(q, na=False) |
            table_df["Patient_Name"].astype(str).str.lower().str.contains(q, na=False) |
            table_df["Department"].astype(str).str.lower().str.contains(q, na=False) |
            table_df["Ward"].astype(str).str.lower().str.contains(q, na=False) |
            table_df["Primary_Condition"].astype(str).str.lower().str.contains(q, na=False) |
            table_df["Attending_Doctor_ID"].astype(str).str.lower().str.contains(q, na=False)
        )
        table_df = table_df[mask]

    # Sort descending by Admission_Date
    if "Admission_Date" in table_df.columns:
        table_df = table_df.sort_values(by="Admission_Date", ascending=False)

    # Format dates for presentation
    display_table = table_df.copy()
    if "Admission_Date" in display_table.columns:
        display_table["Admission_Date"] = display_table["Admission_Date"].dt.strftime("%Y-%m-%d")
    if "Discharge_Date" in display_table.columns:
        display_table["Discharge_Date"] = display_table["Discharge_Date"].dt.strftime("%Y-%m-%d").fillna("Currently Admitted")

    # Slice for row limit
    if row_limit != "All":
        display_table = display_table.head(int(row_limit))

    # Render interactive table
    st.dataframe(
        display_table,
        width="stretch",
        hide_index=True
    )

    # Export Buttons (CSV & Excel)
    with ctrl3:
        csv_bytes = hlp.convert_df_to_csv(table_df)
        st.download_button(
            label="📥 Export CSV",
            data=csv_bytes,
            file_name=f"patient_cohort_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            width="stretch"
        )

    with ctrl4:
        excel_bytes = hlp.convert_dfs_to_excel({"Patient_Cohort": table_df})
        st.download_button(
            label="📊 Export Excel",
            data=excel_bytes,
            file_name=f"patient_cohort_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
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
