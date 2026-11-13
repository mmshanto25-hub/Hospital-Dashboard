"""
utils/calculations.py
Reusable calculation and business logic module for Hospital Management & Staffing Analytics Dashboard.
All analytical formulas, aggregations, ratio calculations, and alerting rules are centralized here.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
import pandas as pd


def _filter_snapshot(
    df_daily_staffing: pd.DataFrame,
    date: Optional[Union[str, pd.Timestamp]] = None,
    department: Optional[Union[str, List[str]]] = None
) -> pd.DataFrame:
    """
    Filters Daily_Staffing DataFrame to a specific date snapshot and department(s).
    If date is not specified, uses the latest available Date in the DataFrame.
    """
    if df_daily_staffing.empty:
        return df_daily_staffing.copy()

    df = df_daily_staffing.copy()

    # Department filtering
    if department is not None:
        if isinstance(department, str) and department != "All":
            df = df[df["Department"] == department]
        elif isinstance(department, (list, tuple)) and len(department) > 0 and "All" not in department:
            df = df[df["Department"].isin(department)]

    if df.empty:
        return df

    # Date filtering
    if date is not None:
        target_date = pd.to_datetime(date)
        df_snapshot = df[df["Date"] == target_date]
        if not df_snapshot.empty:
            return df_snapshot

    # Default to latest date present in df
    latest_date = df["Date"].max()
    return df[df["Date"] == latest_date]


# ==============================================================================
# SECTION 1: EXECUTIVE OVERVIEW & KPI CALCULATIONS
# ==============================================================================

def get_total_patients(df_patients: pd.DataFrame) -> int:
    """Returns the total number of unique patient records."""
    if df_patients.empty or "Patient_ID" not in df_patients.columns:
        return 0
    return int(df_patients["Patient_ID"].nunique())


def get_patient_status_summary(df_patients: pd.DataFrame) -> Dict[str, int]:
    """Returns breakdown of patients by clinical status (admitted, discharged, transferred, deceased)."""
    if df_patients.empty or "Patient_Status" not in df_patients.columns:
        return {"total": 0, "admitted": 0, "discharged": 0, "transferred": 0, "deceased": 0}
    
    status_counts = df_patients["Patient_Status"].value_counts().to_dict()
    total = int(df_patients["Patient_ID"].nunique()) if "Patient_ID" in df_patients.columns else len(df_patients)
    return {
        "total": total,
        "admitted": int(status_counts.get("Admitted", 0)),
        "discharged": int(status_counts.get("Discharged", 0)),
        "transferred": int(status_counts.get("Transferred", 0)),
        "deceased": int(status_counts.get("Deceased", 0))
    }


def get_average_patient_age(df_patients: pd.DataFrame) -> float:
    """Calculates the average age of patients in the cohort."""
    if df_patients.empty or "Age" not in df_patients.columns:
        return 0.0
    val = df_patients["Age"].mean()
    return round(float(val), 1) if not pd.isna(val) else 0.0


def get_current_patient_census(
    df_daily_staffing: pd.DataFrame,
    date: Optional[Union[str, pd.Timestamp]] = None,
    department: Optional[Union[str, List[str]]] = None
) -> int:
    """
    Calculates current patient census from the latest daily staffing snapshot
    (or selected date snapshot). Sums Daily_Patient_Census across departments.
    """
    snapshot = _filter_snapshot(df_daily_staffing, date=date, department=department)
    if snapshot.empty or "Daily_Patient_Census" not in snapshot.columns:
        return 0
    return int(snapshot["Daily_Patient_Census"].sum())


def get_total_doctors(df_doctors: pd.DataFrame) -> int:
    """Returns the total number of registered doctors."""
    if df_doctors.empty or "Doctor_ID" not in df_doctors.columns:
        return 0
    return int(df_doctors["Doctor_ID"].nunique())


def get_doctor_status_breakdown(df_doctors: pd.DataFrame) -> Dict[str, int]:
    """Returns breakdown of doctors by status and employment type."""
    if df_doctors.empty:
        return {"total": 0, "active": 0, "on_leave": 0, "inactive": 0, "full_time": 0, "part_time": 0, "visiting": 0}

    total = int(df_doctors["Doctor_ID"].nunique())
    status_counts = df_doctors["Status"].value_counts().to_dict()
    emp_counts = df_doctors["Employment_Type"].value_counts().to_dict()

    return {
        "total": total,
        "active": int(status_counts.get("Active", 0)),
        "on_leave": int(status_counts.get("On Leave", 0)),
        "inactive": int(status_counts.get("Inactive", 0)),
        "full_time": int(emp_counts.get("Full-time", 0)),
        "part_time": int(emp_counts.get("Part-time", 0)),
        "visiting": int(emp_counts.get("Visiting", 0))
    }


def get_total_nurses(df_nurses: pd.DataFrame) -> int:
    """Returns the total number of registered nurses."""
    if df_nurses.empty or "Nurse_ID" not in df_nurses.columns:
        return 0
    return int(df_nurses["Nurse_ID"].nunique())


def get_nurse_status_breakdown(df_nurses: pd.DataFrame) -> Dict[str, int]:
    """Returns breakdown of nurses by status and employment type."""
    if df_nurses.empty:
        return {"total": 0, "active": 0, "on_leave": 0, "inactive": 0, "full_time": 0, "part_time": 0}

    total = int(df_nurses["Nurse_ID"].nunique())
    status_counts = df_nurses["Status"].value_counts().to_dict()
    emp_counts = df_nurses["Employment_Type"].value_counts().to_dict()

    return {
        "total": total,
        "active": int(status_counts.get("Active", 0)),
        "on_leave": int(status_counts.get("On Leave", 0)),
        "inactive": int(status_counts.get("Inactive", 0)),
        "full_time": int(emp_counts.get("Full-time", 0)),
        "part_time": int(emp_counts.get("Part-time", 0))
    }


def get_active_doctors(
    df_daily_staffing: pd.DataFrame,
    date: Optional[Union[str, pd.Timestamp]] = None,
    department: Optional[Union[str, List[str]]] = None
) -> int:
    """Sums Active_Doctors_On_Duty for the selected snapshot."""
    snapshot = _filter_snapshot(df_daily_staffing, date=date, department=department)
    if snapshot.empty or "Active_Doctors_On_Duty" not in snapshot.columns:
        return 0
    return int(snapshot["Active_Doctors_On_Duty"].sum())


def get_active_nurses(
    df_daily_staffing: pd.DataFrame,
    date: Optional[Union[str, pd.Timestamp]] = None,
    department: Optional[Union[str, List[str]]] = None
) -> int:
    """Sums Active_Nurses_On_Duty for the selected snapshot."""
    snapshot = _filter_snapshot(df_daily_staffing, date=date, department=department)
    if snapshot.empty or "Active_Nurses_On_Duty" not in snapshot.columns:
        return 0
    return int(snapshot["Active_Nurses_On_Duty"].sum())


def get_bed_capacity(
    df_daily_staffing: pd.DataFrame,
    date: Optional[Union[str, pd.Timestamp]] = None,
    department: Optional[Union[str, List[str]]] = None
) -> int:
    """Sums Bed_Capacity for the selected snapshot."""
    snapshot = _filter_snapshot(df_daily_staffing, date=date, department=department)
    if snapshot.empty or "Bed_Capacity" not in snapshot.columns:
        return 0
    return int(snapshot["Bed_Capacity"].sum())


def get_occupied_beds(
    df_daily_staffing: pd.DataFrame,
    date: Optional[Union[str, pd.Timestamp]] = None,
    department: Optional[Union[str, List[str]]] = None
) -> int:
    """Sums Occupied_Beds for the selected snapshot."""
    snapshot = _filter_snapshot(df_daily_staffing, date=date, department=department)
    if snapshot.empty or "Occupied_Beds" not in snapshot.columns:
        return 0
    return int(snapshot["Occupied_Beds"].sum())


def get_available_beds(
    df_daily_staffing: pd.DataFrame,
    date: Optional[Union[str, pd.Timestamp]] = None,
    department: Optional[Union[str, List[str]]] = None
) -> int:
    """
    Calculates total available beds for the snapshot:
    Available Beds = Bed Capacity - Occupied Beds.
    """
    capacity = get_bed_capacity(df_daily_staffing, date=date, department=department)
    occupied = get_occupied_beds(df_daily_staffing, date=date, department=department)
    return max(0, capacity - occupied)


def get_bed_occupancy_rate(
    df_daily_staffing: pd.DataFrame,
    date: Optional[Union[str, pd.Timestamp]] = None,
    department: Optional[Union[str, List[str]]] = None
) -> float:
    """
    Calculates hospital bed occupancy rate as a percentage:
    Occupancy Rate = (Occupied Beds / Bed Capacity) * 100.
    Always uses aggregated values; never averages individual percentages.
    """
    capacity = get_bed_capacity(df_daily_staffing, date=date, department=department)
    if capacity == 0:
        return 0.0
    occupied = get_occupied_beds(df_daily_staffing, date=date, department=department)
    return round(float(occupied / capacity * 100), 2)


def get_patients_per_doctor(
    df_daily_staffing: pd.DataFrame,
    date: Optional[Union[str, pd.Timestamp]] = None,
    department: Optional[Union[str, List[str]]] = None
) -> float:
    """
    Calculates overall patients per doctor for the snapshot:
    Patients per Doctor = Daily Patient Census / Active Doctors on Duty.
    """
    census = get_current_patient_census(df_daily_staffing, date=date, department=department)
    doctors = get_active_doctors(df_daily_staffing, date=date, department=department)
    if doctors == 0:
        return 0.0 if census == 0 else float("inf")
    return round(float(census / doctors), 2)


def get_patients_per_nurse(
    df_daily_staffing: pd.DataFrame,
    date: Optional[Union[str, pd.Timestamp]] = None,
    department: Optional[Union[str, List[str]]] = None
) -> float:
    """
    Calculates overall patients per nurse for the snapshot:
    Patients per Nurse = Daily Patient Census / Active Nurses on Duty.
    """
    census = get_current_patient_census(df_daily_staffing, date=date, department=department)
    nurses = get_active_nurses(df_daily_staffing, date=date, department=department)
    if nurses == 0:
        return 0.0 if census == 0 else float("inf")
    return round(float(census / nurses), 2)


def get_average_length_of_stay(df_patients: pd.DataFrame) -> float:
    """
    Calculates the average Length_of_Stay_Days from patient records.
    """
    if df_patients.empty or "Length_of_Stay_Days" not in df_patients.columns:
        return 0.0
    val = df_patients["Length_of_Stay_Days"].mean()
    return round(float(val), 2) if not pd.isna(val) else 0.0


# ==============================================================================
# SECTION 2: DEPARTMENT-LEVEL STATISTICS & WORKLOAD ALERTS
# ==============================================================================

def get_department_statistics(
    df_daily_staffing: pd.DataFrame,
    df_departments: pd.DataFrame,
    date: Optional[Union[str, pd.Timestamp]] = None
) -> pd.DataFrame:
    """
    Computes consolidated department-level metrics for the selected snapshot date:
    Bed Capacity, Occupied Beds, Available Beds, Patient Census,
    Active Doctors, Active Nurses, Patients per Doctor, Patients per Nurse,
    Bed Occupancy Rate (%), Target Ratios, and Workload Status flags.
    """
    snapshot = _filter_snapshot(df_daily_staffing, date=date)
    if snapshot.empty:
        return pd.DataFrame()

    # Merge with department targets
    dept_cols = ["Department", "Target_Patients_per_Doctor", "Target_Patients_per_Nurse", "Staffing_Demand_Factor"]
    available_dept_cols = [c for c in dept_cols if c in df_departments.columns]
    merged = pd.merge(snapshot, df_departments[available_dept_cols], on="Department", how="left")

    # Compute Available Beds
    merged["Available_Beds"] = (merged["Bed_Capacity"] - merged["Occupied_Beds"]).clip(lower=0)

    # Compute Occupancy Rate (%)
    merged["Occupancy_Rate_Pct"] = np.where(
        merged["Bed_Capacity"] > 0,
        (merged["Occupied_Beds"] / merged["Bed_Capacity"] * 100).round(1),
        0.0
    )

    # Workload Alert Flags
    if "Target_Patients_per_Doctor" in merged.columns:
        merged["Doctor_Workload_Alert"] = merged["Patients_per_Doctor"] > merged["Target_Patients_per_Doctor"]
    else:
        merged["Doctor_Workload_Alert"] = False

    if "Target_Patients_per_Nurse" in merged.columns:
        merged["Nurse_Workload_Alert"] = merged["Patients_per_Nurse"] > merged["Target_Patients_per_Nurse"]
    else:
        merged["Nurse_Workload_Alert"] = False

    merged["High_Occupancy_Alert"] = merged["Occupancy_Rate_Pct"] >= 85.0

    return merged


def get_high_workload_departments(
    df_daily_staffing: pd.DataFrame,
    df_departments: pd.DataFrame,
    date: Optional[Union[str, pd.Timestamp]] = None,
    occupancy_threshold: float = 85.0
) -> Dict[str, pd.DataFrame]:
    """
    Identifies departments requiring staffing attention based on target thresholds:
    1. High doctor workload (Patients per Doctor > Target)
    2. High nurse workload (Patients per Nurse > Target)
    3. High bed occupancy (Occupancy Rate >= occupancy_threshold)
    4. Combined priority attention (exceeding multiple thresholds)
    """
    dept_stats = get_department_statistics(df_daily_staffing, df_departments, date=date)
    if dept_stats.empty:
        empty_df = pd.DataFrame()
        return {
            "high_doctor_load": empty_df,
            "high_nurse_load": empty_df,
            "high_occupancy": empty_df,
            "critical_attention": empty_df
        }

    high_doc = dept_stats[dept_stats["Doctor_Workload_Alert"]].sort_values(by="Patients_per_Doctor", ascending=False)
    high_nur = dept_stats[dept_stats["Nurse_Workload_Alert"]].sort_values(by="Patients_per_Nurse", ascending=False)
    high_occ = dept_stats[dept_stats["Occupancy_Rate_Pct"] >= occupancy_threshold].sort_values(by="Occupancy_Rate_Pct", ascending=False)

    # Critical: high doctor AND (high nurse OR high occupancy)
    critical = dept_stats[
        dept_stats["Doctor_Workload_Alert"] & (dept_stats["Nurse_Workload_Alert"] | (dept_stats["Occupancy_Rate_Pct"] >= occupancy_threshold))
    ]

    return {
        "high_doctor_load": high_doc,
        "high_nurse_load": high_nur,
        "high_occupancy": high_occ,
        "critical_attention": critical
    }


def get_ratio_extremes(dept_stats: pd.DataFrame) -> Dict[str, Any]:
    """Computes highest, lowest, and average ratios across departments for snapshot."""
    if dept_stats.empty or "Patients_per_Doctor" not in dept_stats.columns:
        return {
            "doc_max": ("N/A", 0.0),
            "doc_min": ("N/A", 0.0),
            "doc_avg": 0.0,
            "nur_max": ("N/A", 0.0),
            "nur_min": ("N/A", 0.0),
            "nur_avg": 0.0
        }

    doc_sorted = dept_stats.sort_values(by="Patients_per_Doctor", ascending=False)
    nur_sorted = dept_stats.sort_values(by="Patients_per_Nurse", ascending=False)

    doc_max_row = doc_sorted.iloc[0]
    doc_min_row = doc_sorted.iloc[-1]
    nur_max_row = nur_sorted.iloc[0]
    nur_min_row = nur_sorted.iloc[-1]

    return {
        "doc_max": (doc_max_row["Department"], float(doc_max_row["Patients_per_Doctor"])),
        "doc_min": (doc_min_row["Department"], float(doc_min_row["Patients_per_Doctor"])),
        "doc_avg": round(float(dept_stats["Patients_per_Doctor"].mean()), 2),
        "nur_max": (nur_max_row["Department"], float(nur_max_row["Patients_per_Nurse"])),
        "nur_min": (nur_min_row["Department"], float(nur_min_row["Patients_per_Nurse"])),
        "nur_avg": round(float(dept_stats["Patients_per_Nurse"].mean()), 2)
    }


# ==============================================================================
# SECTION 3: TREND & DEMOGRAPHIC AGGREGATIONS
# ==============================================================================

def get_monthly_admissions_and_discharges(df_patients: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates patient records by month for admissions and discharges.
    Missing discharge dates are not counted as discharged patients.
    """
    if df_patients.empty or "Admission_Date" not in df_patients.columns:
        return pd.DataFrame(columns=["YearMonth", "Admissions", "Discharges"])

    df = df_patients.copy()

    # Admissions by month
    df["Adm_YearMonth"] = df["Admission_Date"].dt.to_period("M").dt.to_timestamp()
    adm_counts = df.groupby("Adm_YearMonth").size().rename("Admissions")

    # Discharges by month (ignoring missing discharge dates)
    valid_discharges = df.dropna(subset=["Discharge_Date"]).copy()
    valid_discharges["Dis_YearMonth"] = valid_discharges["Discharge_Date"].dt.to_period("M").dt.to_timestamp()
    dis_counts = valid_discharges.groupby("Dis_YearMonth").size().rename("Discharges")

    # Combine into unified monthly index
    merged = pd.concat([adm_counts, dis_counts], axis=1).fillna(0).sort_index()
    merged = merged.reset_index().rename(columns={"index": "Month"})
    merged["Admissions"] = merged["Admissions"].astype(int)
    merged["Discharges"] = merged["Discharges"].astype(int)

    return merged


def get_age_group_distribution(df_patients: pd.DataFrame) -> pd.DataFrame:
    """
    Categorizes patients into specified age groups:
    0–17, 18–30, 31–45, 46–60, 61–75, 76+
    """
    if df_patients.empty or "Age" not in df_patients.columns:
        return pd.DataFrame(columns=["Age_Group", "Count"])

    bins = [-1, 17, 30, 45, 60, 75, 150]
    labels = ["0–17", "18–30", "31–45", "46–60", "61–75", "76+"]
    df = df_patients.copy()
    df["Age_Group"] = pd.cut(df["Age"], bins=bins, labels=labels, right=True)

    dist = df["Age_Group"].value_counts().reindex(labels, fill_value=0).reset_index()
    dist.columns = ["Age_Group", "Count"]
    return dist


def get_experience_distribution(df_staff: pd.DataFrame) -> pd.DataFrame:
    """
    Categorizes staff into specified experience groups:
    0–5 years, 6–10 years, 11–15 years, 16–20 years, 20+ years
    """
    if df_staff.empty or "Experience_Years" not in df_staff.columns:
        return pd.DataFrame(columns=["Experience_Group", "Count"])

    bins = [-1, 5, 10, 15, 20, 100]
    labels = ["0–5 years", "6–10 years", "11–15 years", "16–20 years", "20+ years"]
    df = df_staff.copy()
    df["Experience_Group"] = pd.cut(df["Experience_Years"], bins=bins, labels=labels, right=True)

    dist = df["Experience_Group"].value_counts().reindex(labels, fill_value=0).reset_index()
    dist.columns = ["Experience_Group", "Count"]
    return dist


def get_daily_staffing_trend(
    df_daily_staffing: pd.DataFrame,
    department: Optional[Union[str, List[str]]] = None
) -> pd.DataFrame:
    """
    Aggregates daily ratios and census across time for trend analysis.
    """
    if df_daily_staffing.empty:
        return pd.DataFrame()

    df = df_daily_staffing.copy()
    if department is not None:
        if isinstance(department, str) and department != "All":
            df = df[df["Department"] == department]
        elif isinstance(department, (list, tuple)) and len(department) > 0 and "All" not in department:
            df = df[df["Department"].isin(department)]

    daily = df.groupby("Date").agg(
        Total_Census=("Daily_Patient_Census", "sum"),
        Total_Doctors=("Active_Doctors_On_Duty", "sum"),
        Total_Nurses=("Active_Nurses_On_Duty", "sum"),
        Total_Occupied=("Occupied_Beds", "sum"),
        Total_Capacity=("Bed_Capacity", "sum")
    ).reset_index()

    daily["Overall_Patients_per_Doctor"] = np.where(
        daily["Total_Doctors"] > 0,
        (daily["Total_Census"] / daily["Total_Doctors"]).round(2),
        0.0
    )
    daily["Overall_Patients_per_Nurse"] = np.where(
        daily["Total_Nurses"] > 0,
        (daily["Total_Census"] / daily["Total_Nurses"]).round(2),
        0.0
    )
    daily["Bed_Occupancy_Rate_Pct"] = np.where(
        daily["Total_Capacity"] > 0,
        (daily["Total_Occupied"] / daily["Total_Capacity"] * 100).round(2),
        0.0
    )

    return daily
