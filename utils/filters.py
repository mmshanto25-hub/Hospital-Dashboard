"""
utils/filters.py
Global and page-specific filtering system for the Hospital Management Dashboard.
Maintains session state, handles compound multi-criteria filtering, and provides reset capabilities.
"""

from typing import Dict, Any, Optional, Tuple, List, Union
from datetime import date, datetime
import pandas as pd
import streamlit as st


# ==============================================================================
# 1. SESSION STATE INITIALIZATION & RESET
# ==============================================================================

def init_filter_state():
    """Initializes default filter values in Streamlit session_state if not present."""
    defaults = {
        "global_dept": "All",
        "global_shift": "All",
        "global_date_range": None,
        "patient_gender": "All",
        "patient_admission_type": "All",
        "patient_status": "All",
        "doctor_employment": "All",
        "doctor_status": "All",
        "doctor_specialization": "All",
        "nurse_ward": "All",
        "nurse_employment": "All",
        "nurse_status": "All",
        "nurse_shift": "All",
        "uploaded_data": None
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def reset_all_filters():
    """Resets all filter state keys back to default values."""
    st.session_state["global_dept"] = "All"
    st.session_state["global_shift"] = "All"
    st.session_state["global_date_range"] = None
    st.session_state["patient_gender"] = "All"
    st.session_state["patient_admission_type"] = "All"
    st.session_state["patient_status"] = "All"
    st.session_state["doctor_employment"] = "All"
    st.session_state["doctor_status"] = "All"
    st.session_state["doctor_specialization"] = "All"
    st.session_state["nurse_ward"] = "All"
    st.session_state["nurse_employment"] = "All"
    st.session_state["nurse_status"] = "All"
    st.session_state["nurse_shift"] = "All"


# ==============================================================================
# 2. SIDEBAR FILTER RENDERING WIDGETS
# ==============================================================================

def render_global_sidebar(data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Renders the common global sidebar containing:
    - Hospital branding / Logo
    - Dataset uploader
    - Global Date Range
    - Department Selector
    - Shift Selector
    - Reset Filters button
    - Dataset Information badge
    Returns dictionary with active global filter values.
    """
    init_filter_state()
    st.sidebar.markdown(
        """
        <div style="text-align: center; padding: 0.5rem 0 1rem 0;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 48px; height: 48px; border-radius: 12px; background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); margin-bottom: 0.5rem;">
                <span style="font-size: 24px; color: #3B82F6;">🏥</span>
            </div>
            <h2 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #F8FAFC; letter-spacing: -0.02em;">
                MEDICORE HEALTH
            </h2>
            <p style="margin: 0; font-size: 0.75rem; color: #94A3B8; font-weight: 500;">
                Hospital Management & Staffing Analytics
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Optional Excel Dataset Upload
    with st.sidebar.expander("📁 Dataset Source & Upload", expanded=False):
        uploaded_file = st.file_uploader(
            "Upload Custom Excel (.xlsx)",
            type=["xlsx"],
            help="Upload a compatible Hospital Management Excel workbook."
        )
        if uploaded_file is not None:
            st.session_state["uploaded_file"] = uploaded_file
            st.success("Custom dataset loaded!")
        else:
            if "uploaded_file" in st.session_state and st.session_state["uploaded_file"] is not None:
                if st.button("Revert to Default Dataset", width="stretch"):
                    st.session_state["uploaded_file"] = None
                    st.rerun()

    st.sidebar.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 0.5rem 0;'>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='font-size: 0.85rem; font-weight: 600; color: #3B82F6; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;'>Global Filters</p>", unsafe_allow_html=True)

    # Date range bounds from Daily_Staffing
    df_staff = data.get("Daily_Staffing", pd.DataFrame())
    if not df_staff.empty and "Date" in df_staff.columns:
        min_date = df_staff["Date"].min().date()
        max_date = df_staff["Date"].max().date()
    else:
        min_date = date(2025, 1, 1)
        max_date = date(2026, 12, 31)

    selected_date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Filters daily census, staffing snapshots, and patient admission cohorts."
    )

    # Handle single date pick vs range
    if isinstance(selected_date_range, (tuple, list)):
        if len(selected_date_range) == 2:
            start_date, end_date = selected_date_range
        elif len(selected_date_range) == 1:
            start_date = end_date = selected_date_range[0]
        else:
            start_date, end_date = min_date, max_date
    else:
        start_date = end_date = selected_date_range

    # Department Filter
    dept_options = ["All"]
    if "Departments" in data and "Department" in data["Departments"].columns:
        dept_options += sorted(data["Departments"]["Department"].dropna().unique().tolist())
    elif not df_staff.empty and "Department" in df_staff.columns:
        dept_options += sorted(df_staff["Department"].dropna().unique().tolist())

    selected_dept = st.sidebar.selectbox(
        "Department",
        options=dept_options,
        index=0 if st.session_state.get("global_dept") not in dept_options else dept_options.index(st.session_state.get("global_dept")),
        key="sb_dept"
    )
    st.session_state["global_dept"] = selected_dept

    # Shift Filter
    shift_options = ["All", "Morning", "Evening", "Night"]
    selected_shift = st.sidebar.selectbox(
        "Shift",
        options=shift_options,
        index=0 if st.session_state.get("global_shift") not in shift_options else shift_options.index(st.session_state.get("global_shift")),
        key="sb_shift"
    )
    st.session_state["global_shift"] = selected_shift

    # Reset Filters Button
    if st.sidebar.button("🔄 Reset All Filters", width="stretch"):
        reset_all_filters()
        st.rerun()

    # Sidebar Dataset Status Footer
    st.sidebar.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 0.75rem 0;'>", unsafe_allow_html=True)
    active_ds = "Custom Upload" if st.session_state.get("uploaded_file") else "hospital_dataset.xlsx"
    total_pts = len(data.get("Patients", []))
    st.sidebar.markdown(
        f"""
        <div style="font-size: 0.75rem; color: #64748B; line-height: 1.4;">
            <div><strong>Active Dataset:</strong> {active_ds}</div>
            <div><strong>Total Patients:</strong> {total_pts:,} records</div>
            <div><strong>Latest Snapshot:</strong> {max_date}</div>
            <div style="margin-top: 0.25rem; color: #22C55E;">● System Operational</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    return {
        "start_date": pd.to_datetime(start_date),
        "end_date": pd.to_datetime(end_date),
        "department": selected_dept,
        "shift": selected_shift
    }


def render_patient_page_filters(df_patients: pd.DataFrame) -> Dict[str, Any]:
    """Renders page-specific filters for the Patient Analytics view."""
    col1, col2, col3 = st.columns(3)

    genders = ["All"] + sorted(df_patients["Gender"].dropna().unique().tolist()) if "Gender" in df_patients.columns else ["All"]
    adm_types = ["All"] + sorted(df_patients["Admission_Type"].dropna().unique().tolist()) if "Admission_Type" in df_patients.columns else ["All"]
    statuses = ["All"] + sorted(df_patients["Patient_Status"].dropna().unique().tolist()) if "Patient_Status" in df_patients.columns else ["All"]

    with col1:
        sel_gender = st.selectbox("Gender Filter", options=genders, index=0)
    with col2:
        sel_adm = st.selectbox("Admission Type", options=adm_types, index=0)
    with col3:
        sel_status = st.selectbox("Patient Status", options=statuses, index=0)

    return {
        "gender": sel_gender,
        "admission_type": sel_adm,
        "patient_status": sel_status
    }


def render_doctor_page_filters(df_doctors: pd.DataFrame) -> Dict[str, Any]:
    """Renders page-specific filters for the Doctor Analytics view."""
    col1, col2, col3 = st.columns(3)

    emp_types = ["All"] + sorted(df_doctors["Employment_Type"].dropna().unique().tolist()) if "Employment_Type" in df_doctors.columns else ["All"]
    statuses = ["All"] + sorted(df_doctors["Status"].dropna().unique().tolist()) if "Status" in df_doctors.columns else ["All"]
    specs = ["All"] + sorted(df_doctors["Specialization"].dropna().unique().tolist()) if "Specialization" in df_doctors.columns else ["All"]

    with col1:
        sel_emp = st.selectbox("Employment Type", options=emp_types, index=0)
    with col2:
        sel_stat = st.selectbox("Doctor Status", options=statuses, index=0)
    with col3:
        sel_spec = st.selectbox("Specialization", options=specs, index=0)

    return {
        "employment_type": sel_emp,
        "status": sel_stat,
        "specialization": sel_spec
    }


def render_nurse_page_filters(df_nurses: pd.DataFrame) -> Dict[str, Any]:
    """Renders page-specific filters for the Nurse Analytics view."""
    col1, col2, col3 = st.columns(3)

    wards = ["All"] + sorted(df_nurses["Ward"].dropna().unique().tolist()) if "Ward" in df_nurses.columns else ["All"]
    emp_types = ["All"] + sorted(df_nurses["Employment_Type"].dropna().unique().tolist()) if "Employment_Type" in df_nurses.columns else ["All"]
    statuses = ["All"] + sorted(df_nurses["Status"].dropna().unique().tolist()) if "Status" in df_nurses.columns else ["All"]

    with col1:
        sel_ward = st.selectbox("Ward Assignment", options=wards, index=0)
    with col2:
        sel_emp = st.selectbox("Employment Type", options=emp_types, index=0)
    with col3:
        sel_stat = st.selectbox("Nurse Status", options=statuses, index=0)

    return {
        "ward": sel_ward,
        "employment_type": sel_emp,
        "status": sel_stat
    }


# ==============================================================================
# 3. DATAFRAME FILTERING ENGINE
# ==============================================================================

def filter_patients(
    df_patients: pd.DataFrame,
    start_date: Optional[Union[str, pd.Timestamp]] = None,
    end_date: Optional[Union[str, pd.Timestamp]] = None,
    department: Optional[str] = None,
    gender: Optional[str] = None,
    admission_type: Optional[str] = None,
    patient_status: Optional[str] = None
) -> pd.DataFrame:
    """
    Filters Patients DataFrame by Admission_Date cohort, department,
    gender, admission type, and status.
    """
    if df_patients.empty:
        return df_patients.copy()

    df = df_patients.copy()

    # Date filter uses Admission_Date
    if start_date is not None and "Admission_Date" in df.columns:
        df = df[df["Admission_Date"] >= pd.to_datetime(start_date)]
    if end_date is not None and "Admission_Date" in df.columns:
        df = df[df["Admission_Date"] <= pd.to_datetime(end_date)]

    # Department
    if department and department != "All" and "Department" in df.columns:
        df = df[df["Department"] == department]

    # Gender
    if gender and gender != "All" and "Gender" in df.columns:
        df = df[df["Gender"] == gender]

    # Admission Type
    if admission_type and admission_type != "All" and "Admission_Type" in df.columns:
        df = df[df["Admission_Type"] == admission_type]

    # Patient Status
    if patient_status and patient_status != "All" and "Patient_Status" in df.columns:
        df = df[df["Patient_Status"] == patient_status]

    return df


def filter_daily_staffing(
    df_daily_staffing: pd.DataFrame,
    start_date: Optional[Union[str, pd.Timestamp]] = None,
    end_date: Optional[Union[str, pd.Timestamp]] = None,
    department: Optional[str] = None,
    shift: Optional[str] = None
) -> pd.DataFrame:
    """
    Filters Daily_Staffing DataFrame by Date range, department, and shift.
    """
    if df_daily_staffing.empty:
        return df_daily_staffing.copy()

    df = df_daily_staffing.copy()

    if start_date is not None and "Date" in df.columns:
        df = df[df["Date"] >= pd.to_datetime(start_date)]
    if end_date is not None and "Date" in df.columns:
        df = df[df["Date"] <= pd.to_datetime(end_date)]

    if department and department != "All" and "Department" in df.columns:
        df = df[df["Department"] == department]

    if shift and shift != "All" and "Shift" in df.columns:
        df = df[df["Shift"] == shift]

    return df


def filter_doctors(
    df_doctors: pd.DataFrame,
    department: Optional[str] = None,
    employment_type: Optional[str] = None,
    status: Optional[str] = None,
    specialization: Optional[str] = None,
    shift: Optional[str] = None
) -> pd.DataFrame:
    """
    Filters Doctors DataFrame by registered staff profile attributes.
    Does not apply unrelated date filters to static staff rosters.
    """
    if df_doctors.empty:
        return df_doctors.copy()

    df = df_doctors.copy()

    if department and department != "All" and "Department" in df.columns:
        df = df[df["Department"] == department]

    if employment_type and employment_type != "All" and "Employment_Type" in df.columns:
        df = df[df["Employment_Type"] == employment_type]

    if status and status != "All" and "Status" in df.columns:
        df = df[df["Status"] == status]

    if specialization and specialization != "All" and "Specialization" in df.columns:
        df = df[df["Specialization"] == specialization]

    if shift and shift != "All" and "Shift" in df.columns:
        df = df[df["Shift"] == shift]

    return df


def filter_nurses(
    df_nurses: pd.DataFrame,
    department: Optional[str] = None,
    ward: Optional[str] = None,
    employment_type: Optional[str] = None,
    status: Optional[str] = None,
    shift: Optional[str] = None
) -> pd.DataFrame:
    """
    Filters Nurses DataFrame by registered staff profile attributes.
    """
    if df_nurses.empty:
        return df_nurses.copy()

    df = df_nurses.copy()

    if department and department != "All" and "Department" in df.columns:
        df = df[df["Department"] == department]

    if ward and ward != "All" and "Ward" in df.columns:
        df = df[df["Ward"] == ward]

    if employment_type and employment_type != "All" and "Employment_Type" in df.columns:
        df = df[df["Employment_Type"] == employment_type]

    if status and status != "All" and "Status" in df.columns:
        df = df[df["Status"] == status]

    if shift and shift != "All" and "Shift" in df.columns:
        df = df[df["Shift"] == shift]

    return df
