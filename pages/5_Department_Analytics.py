"""
pages/5_Department_Analytics.py
Page 5: Department Performance, Capacity Benchmarking & Multi-Unit Comparison.
Features 6 KPI cards, 6 comprehensive comparative charts across all 12 hospital departments,
multi-department side-by-side comparison, interactive consolidated matrix table,
threshold alerts, and multi-format exports.
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
        page_title="Department Analytics | MediCore Analytics",
        page_icon="🏢",
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
        title="Department Analytics",
        subtitle="Cross-Department Capacity Benchmarking, Census & Resource Allocation",
        selected_range=f"Census Date: {snapshot_str}",
        selected_dept=selected_dept,
        latest_update="All 12 Clinical Units"
    )

    # Calculate Department Consolidated Statistics for Snapshot
    dept_stats = calc.get_department_statistics(filtered_staffing, df_departments, date=snapshot_date)

    # ==========================================================================
    # SECTION 11.1: HOSPITAL-WIDE CAPACITY & STAFFING KPIS (6 CARDS)
    # ==========================================================================
    st.markdown("<h3 style='margin-top: 0.5rem; margin-bottom: 0.8rem;'>Consolidated Department Capacity Indicators</h3>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5, k6 = st.columns(6)

    total_cap = calc.get_bed_capacity(filtered_staffing, date=snapshot_date, department=selected_dept)
    total_occ = calc.get_occupied_beds(filtered_staffing, date=snapshot_date, department=selected_dept)
    total_avail = calc.get_available_beds(filtered_staffing, date=snapshot_date, department=selected_dept)
    occ_rate = calc.get_bed_occupancy_rate(filtered_staffing, date=snapshot_date, department=selected_dept)
    active_docs = calc.get_active_doctors(filtered_staffing, date=snapshot_date, department=selected_dept)
    active_nurses = calc.get_active_nurses(filtered_staffing, date=snapshot_date, department=selected_dept)

    with k1:
        hlp.render_kpi_card(
            title="Bed Capacity",
            value=hlp.format_number(total_cap),
            subtitle="Total configured beds",
            icon="🛏️",
            badge_text="Configured",
            badge_type="neutral"
        )

    with k2:
        hlp.render_kpi_card(
            title="Occupied Beds",
            value=hlp.format_number(total_occ),
            subtitle="Inpatient bed count",
            icon="🏥",
            badge_text="Occupied",
            badge_type="positive"
        )

    with k3:
        hlp.render_kpi_card(
            title="Available Beds",
            value=hlp.format_number(total_avail),
            subtitle="Ready for admission",
            icon="🚪",
            badge_text="Vacant",
            badge_type="positive" if total_avail > 0 else "danger"
        )

    with k4:
        occ_badge = "positive" if occ_rate < 80 else ("warning" if occ_rate < 90 else "danger")
        hlp.render_kpi_card(
            title="Bed Occupancy",
            value=hlp.format_percent(occ_rate),
            subtitle="Hospital-wide utilization",
            icon="📊",
            badge_text="Aggregated",
            badge_type=occ_badge
        )

    with k5:
        hlp.render_kpi_card(
            title="Doctors on Duty",
            value=hlp.format_number(active_docs),
            subtitle="Active medical staff",
            icon="🩺",
            badge_text="On Shift",
            badge_type="positive"
        )

    with k6:
        hlp.render_kpi_card(
            title="Nurses on Duty",
            value=hlp.format_number(active_nurses),
            subtitle="Active nursing staff",
            icon="💉",
            badge_text="On Shift",
            badge_type="positive"
        )

    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 1.5rem 0;'>", unsafe_allow_html=True)

    # ==========================================================================
    # SECTION 11.2: CHARTS 1 & 2 — PATIENT CENSUS & BED OCCUPANCY BY DEPARTMENT
    # ==========================================================================
    st.markdown("<h3 style='margin-bottom: 0.8rem;'>1. Patient Census & Bed Occupancy Comparison</h3>", unsafe_allow_html=True)
    col_census, col_occ = st.columns([1, 1])

    with col_census:
        fig_census = chrt.create_bar_chart(
            dept_stats,
            x="Daily_Patient_Census",
            y="Department",
            title=f"Patient Census by Department ({snapshot_str})",
            orientation="h",
            sort_descending=True,
            highlight_top_n=3,
            x_title="Patient Census",
            y_title="Department"
        )
        st.plotly_chart(fig_census, width="stretch")

    with col_occ:
        fig_occ = chrt.create_bar_chart(
            dept_stats,
            x="Occupancy_Rate_Pct",
            y="Department",
            title=f"Bed Occupancy Rate (%) by Department ({snapshot_str})",
            orientation="h",
            sort_descending=True,
            highlight_top_n=3,
            color_code="#06B6D4",
            x_title="Bed Occupancy Rate (%)",
            y_title="Department"
        )
        st.plotly_chart(fig_occ, width="stretch")

    # ==========================================================================
    # SECTION 11.3: CHARTS 3 & 4 — DOCTOR & NURSE DISTRIBUTION ON DUTY
    # ==========================================================================
    st.markdown("<h3 style='margin-top: 1rem; margin-bottom: 0.8rem;'>2. Medical & Nursing Staff Deployment on Duty</h3>", unsafe_allow_html=True)
    col_doc_dist, col_nur_dist = st.columns(2)

    with col_doc_dist:
        fig_docs = chrt.create_bar_chart(
            dept_stats,
            x="Active_Doctors_On_Duty",
            y="Department",
            title=f"Active Doctors on Duty by Department ({snapshot_str})",
            orientation="h",
            sort_descending=True,
            highlight_top_n=3,
            color_code="#3B82F6",
            x_title="Doctors on Duty",
            y_title="Department"
        )
        st.plotly_chart(fig_docs, width="stretch")

    with col_nur_dist:
        fig_nurses = chrt.create_bar_chart(
            dept_stats,
            x="Active_Nurses_On_Duty",
            y="Department",
            title=f"Active Nurses on Duty by Department ({snapshot_str})",
            orientation="h",
            sort_descending=True,
            highlight_top_n=3,
            color_code="#8B5CF6",
            x_title="Nurses on Duty",
            y_title="Department"
        )
        st.plotly_chart(fig_nurses, width="stretch")

    # ==========================================================================
    # SECTION 11.4: CHARTS 5 & 6 — WORKLOAD VS TARGET RATIO COMPARISON
    # ==========================================================================
    st.markdown("<h3 style='margin-top: 1rem; margin-bottom: 0.8rem;'>3. Patient-to-Staff Ratio Benchmarking vs Targets</h3>", unsafe_allow_html=True)
    col_doc_ratio, col_nur_ratio = st.columns(2)

    with col_doc_ratio:
        fig_doc_comp = chrt.create_grouped_bar_chart(
            dept_stats,
            x="Department",
            y_cols=["Patients_per_Doctor", "Target_Patients_per_Doctor"],
            title="Patients per Doctor vs Target Ratio",
            x_title="Department",
            y_title="Ratio (Patients / Doctor)",
            colors=["#3B82F6", "#F59E0B"]
        )
        st.plotly_chart(fig_doc_comp, width="stretch")

    with col_nur_ratio:
        fig_nur_comp = chrt.create_grouped_bar_chart(
            dept_stats,
            x="Department",
            y_cols=["Patients_per_Nurse", "Target_Patients_per_Nurse"],
            title="Patients per Nurse vs Target Ratio",
            x_title="Department",
            y_title="Ratio (Patients / Nurse)",
            colors=["#8B5CF6", "#F59E0B"]
        )
        st.plotly_chart(fig_nur_comp, width="stretch")

    # ==========================================================================
    # SECTION 11.5: MULTI-DEPARTMENT SIDE-BY-SIDE COMPARISON
    # ==========================================================================
    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 1.5rem 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom: 0.5rem;'>Side-by-Side Multi-Department Comparison</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.85rem; color: #94A3B8;'>Select multiple clinical departments below to inspect their operational metrics side-by-side.</p>", unsafe_allow_html=True)

    all_dept_names = sorted(dept_stats["Department"].unique().tolist()) if not dept_stats.empty else []
    default_selected = [d for d in ["Emergency", "ICU", "Cardiology", "Surgery"] if d in all_dept_names]

    chosen_depts = st.multiselect(
        "Select Departments to Compare:",
        options=all_dept_names,
        default=default_selected,
        label_visibility="collapsed"
    )

    if chosen_depts and not dept_stats.empty:
        comp_df = dept_stats[dept_stats["Department"].isin(chosen_depts)].copy()
        
        # Display side-by-side comparison cards
        comp_cols = st.columns(len(chosen_depts))
        for idx, d_name in enumerate(chosen_depts):
            d_row = comp_df[comp_df["Department"] == d_name]
            if d_row.empty:
                continue
            row = d_row.iloc[0]
            with comp_cols[idx]:
                st.markdown(
                    f"""
                    <div style="background: #162338; border: 1px solid rgba(59,130,246,0.3); border-radius: 10px; padding: 1rem; margin-bottom: 1rem;">
                        <div style="font-size: 1.05rem; font-weight: 700; color: #60A5FA; margin-bottom: 0.5rem;">{d_name}</div>
                        <div style="font-size: 0.8rem; color: #CBD5E1; line-height: 1.7;">
                            <div><strong>Census:</strong> {row['Daily_Patient_Census']} patients</div>
                            <div><strong>Capacity:</strong> {row['Bed_Capacity']} beds</div>
                            <div><strong>Occupancy:</strong> {row['Occupancy_Rate_Pct']:.1f}%</div>
                            <div><strong>Doctors on Duty:</strong> {row['Active_Doctors_On_Duty']}</div>
                            <div><strong>Nurses on Duty:</strong> {row['Active_Nurses_On_Duty']}</div>
                            <div><strong>Pts / Doctor:</strong> {row['Patients_per_Doctor']:.1f} <span style="color: #94A3B8;">(Target: {row['Target_Patients_per_Doctor']})</span></div>
                            <div><strong>Pts / Nurse:</strong> {row['Patients_per_Nurse']:.1f} <span style="color: #94A3B8;">(Target: {row['Target_Patients_per_Nurse']})</span></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # ==========================================================================
    # SECTION 11.6: DEPARTMENT COMPARISON MATRIX TABLE & EXPORT
    # ==========================================================================
    st.markdown("<h3 style='margin-top: 1rem; margin-bottom: 0.5rem;'>Comprehensive Department Comparison Matrix</h3>", unsafe_allow_html=True)

    table_cols = [
        "Department", "Bed_Capacity", "Occupied_Beds", "Available_Beds",
        "Daily_Patient_Census", "Active_Doctors_On_Duty", "Active_Nurses_On_Duty",
        "Patients_per_Doctor", "Target_Patients_per_Doctor",
        "Patients_per_Nurse", "Target_Patients_per_Nurse", "Occupancy_Rate_Pct"
    ]
    avail_cols = [c for c in table_cols if c in dept_stats.columns]
    matrix_df = dept_stats[avail_cols].sort_values(by="Daily_Patient_Census", ascending=False).copy()

    st.dataframe(
        matrix_df,
        width="stretch",
        hide_index=True
    )

    col_btn1, col_btn2, _ = st.columns([1, 1, 2])
    with col_btn1:
        csv_bytes = hlp.convert_df_to_csv(matrix_df)
        st.download_button(
            label="📥 Export Matrix CSV",
            data=csv_bytes,
            file_name=f"department_matrix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            width="stretch"
        )
    with col_btn2:
        excel_bytes = hlp.convert_dfs_to_excel({"Department_Matrix": matrix_df})
        st.download_button(
            label="📊 Export Matrix Excel",
            data=excel_bytes,
            file_name=f"department_matrix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
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
