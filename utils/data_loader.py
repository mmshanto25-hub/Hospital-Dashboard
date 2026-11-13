"""
utils/data_loader.py
Reusable and robust data loading module for Hospital Management Dashboard.
Validates schemas, data types, value constraints, and handles missing/duplicate values.
"""

from pathlib import Path
from typing import Dict, Optional, Union, BinaryIO, Tuple, Any
import logging
import pandas as pd
import streamlit as st

# Configure logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Default path to dataset
DEFAULT_DATASET_PATH = Path(__file__).resolve().parent.parent / "data" / "hospital_dataset.xlsx"

# Expected sheets and required columns
REQUIRED_SHEETS = [
    "Patients",
    "Doctors",
    "Nurses",
    "Daily_Staffing",
    "Departments"
]

EXPECTED_COLUMNS = {
    "Patients": [
        "Patient_ID", "Patient_Name", "Age", "Gender", "Department", "Ward",
        "Admission_Date", "Discharge_Date", "Admission_Type", "Primary_Condition",
        "Length_of_Stay_Days", "Patient_Status", "Attending_Doctor_ID", "Assigned_Nurse_ID"
    ],
    "Doctors": [
        "Doctor_ID", "Doctor_Name", "Gender", "Department", "Specialization",
        "Employment_Type", "Experience_Years", "Shift", "Status", "Weekly_Hours"
    ],
    "Nurses": [
        "Nurse_ID", "Nurse_Name", "Gender", "Department", "Ward", "Shift",
        "Employment_Type", "Experience_Years", "Status", "Weekly_Hours"
    ],
    "Daily_Staffing": [
        "Date", "Department", "Bed_Capacity", "Occupied_Beds", "Daily_Patient_Census",
        "Active_Doctors_On_Duty", "Active_Nurses_On_Duty", "Patients_per_Doctor",
        "Patients_per_Nurse", "Bed_Occupancy_Rate", "Doctor_Ratio_Status",
        "Nurse_Ratio_Status", "Shift"
    ],
    "Departments": [
        "Department", "Bed_Capacity", "Staffing_Demand_Factor",
        "Target_Patients_per_Doctor", "Target_Patients_per_Nurse"
    ]
}


def _resolve_source(source: Optional[Union[str, Path, BinaryIO]] = None) -> Union[Path, BinaryIO]:
    """Resolves data source to either default path or provided file/buffer."""
    if source is None:
        if not DEFAULT_DATASET_PATH.exists():
            raise FileNotFoundError(
                f"Default dataset not found at '{DEFAULT_DATASET_PATH}'. "
                "Please place 'hospital_dataset.xlsx' in the 'data' directory or upload an Excel file."
            )
        return DEFAULT_DATASET_PATH
    if isinstance(source, str):
        p = Path(source)
        if not p.exists():
            raise FileNotFoundError(f"Specified dataset file not found: {source}")
        return p
    return source


def _validate_columns(df: pd.DataFrame, sheet_name: str) -> None:
    """Validates that all required columns exist in the DataFrame."""
    required = EXPECTED_COLUMNS.get(sheet_name, [])
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"Sheet '{sheet_name}' is missing required columns: {', '.join(missing)}"
        )


def _clean_patients(df: pd.DataFrame) -> pd.DataFrame:
    """Validates and processes the Patients sheet."""
    _validate_columns(df, "Patients")
    df = df.copy()

    # Parse dates
    df["Admission_Date"] = pd.to_datetime(df["Admission_Date"], errors="coerce")
    df["Discharge_Date"] = pd.to_datetime(df["Discharge_Date"], errors="coerce")

    # Clean strings
    str_cols = ["Patient_ID", "Patient_Name", "Gender", "Department", "Ward",
                "Admission_Type", "Primary_Condition", "Patient_Status",
                "Attending_Doctor_ID", "Assigned_Nurse_ID"]
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()

    # Numeric coercion & validation
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce").fillna(0).astype(int)
    df["Length_of_Stay_Days"] = pd.to_numeric(df["Length_of_Stay_Days"], errors="coerce").fillna(0).astype(int)

    # Sanity checks
    df["Age"] = df["Age"].clip(lower=0)
    df["Length_of_Stay_Days"] = df["Length_of_Stay_Days"].clip(lower=0)

    # Check duplicate patient IDs
    duplicates = df["Patient_ID"].duplicated().sum()
    if duplicates > 0:
        logger.warning("Found %d duplicate Patient_IDs in Patients sheet.", duplicates)

    return df


def _clean_doctors(df: pd.DataFrame) -> pd.DataFrame:
    """Validates and processes the Doctors sheet."""
    _validate_columns(df, "Doctors")
    df = df.copy()

    str_cols = ["Doctor_ID", "Doctor_Name", "Gender", "Department",
                "Specialization", "Employment_Type", "Shift", "Status"]
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()

    df["Experience_Years"] = pd.to_numeric(df["Experience_Years"], errors="coerce").fillna(0).astype(int).clip(lower=0)
    df["Weekly_Hours"] = pd.to_numeric(df["Weekly_Hours"], errors="coerce").fillna(0).astype(int).clip(lower=0)

    duplicates = df["Doctor_ID"].duplicated().sum()
    if duplicates > 0:
        logger.warning("Found %d duplicate Doctor_IDs in Doctors sheet.", duplicates)

    return df


def _clean_nurses(df: pd.DataFrame) -> pd.DataFrame:
    """Validates and processes the Nurses sheet."""
    _validate_columns(df, "Nurses")
    df = df.copy()

    str_cols = ["Nurse_ID", "Nurse_Name", "Gender", "Department",
                "Ward", "Shift", "Employment_Type", "Status"]
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()

    df["Experience_Years"] = pd.to_numeric(df["Experience_Years"], errors="coerce").fillna(0).astype(int).clip(lower=0)
    df["Weekly_Hours"] = pd.to_numeric(df["Weekly_Hours"], errors="coerce").fillna(0).astype(int).clip(lower=0)

    duplicates = df["Nurse_ID"].duplicated().sum()
    if duplicates > 0:
        logger.warning("Found %d duplicate Nurse_IDs in Nurses sheet.", duplicates)

    return df


def _clean_daily_staffing(df: pd.DataFrame) -> pd.DataFrame:
    """Validates and processes the Daily_Staffing sheet."""
    _validate_columns(df, "Daily_Staffing")
    df = df.copy()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    str_cols = ["Department", "Doctor_Ratio_Status", "Nurse_Ratio_Status", "Shift"]
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()

    numeric_int_cols = ["Bed_Capacity", "Occupied_Beds", "Daily_Patient_Census",
                        "Active_Doctors_On_Duty", "Active_Nurses_On_Duty"]
    for col in numeric_int_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int).clip(lower=0)

    numeric_float_cols = ["Patients_per_Doctor", "Patients_per_Nurse", "Bed_Occupancy_Rate"]
    for col in numeric_float_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0).astype(float)

    # Sanity checks
    # Ensure Occupied_Beds does not exceed Bed_Capacity in reporting logic
    invalid_beds = (df["Occupied_Beds"] > df["Bed_Capacity"]).sum()
    if invalid_beds > 0:
        logger.warning("%d records have Occupied_Beds exceeding Bed_Capacity.", invalid_beds)

    return df


def _clean_departments(df: pd.DataFrame) -> pd.DataFrame:
    """Validates and processes the Departments sheet."""
    _validate_columns(df, "Departments")
    df = df.copy()

    df["Department"] = df["Department"].astype(str).str.strip()
    df["Bed_Capacity"] = pd.to_numeric(df["Bed_Capacity"], errors="coerce").fillna(0).astype(int).clip(lower=0)
    df["Staffing_Demand_Factor"] = pd.to_numeric(df["Staffing_Demand_Factor"], errors="coerce").fillna(1.0).astype(float)
    df["Target_Patients_per_Doctor"] = pd.to_numeric(df["Target_Patients_per_Doctor"], errors="coerce").fillna(0).astype(int).clip(lower=1)
    df["Target_Patients_per_Nurse"] = pd.to_numeric(df["Target_Patients_per_Nurse"], errors="coerce").fillna(0).astype(int).clip(lower=1)

    return df


@st.cache_data(show_spinner="Loading hospital dataset from Excel...")
def load_excel_data(file_source: Optional[Union[str, Path, bytes]] = None) -> Dict[str, pd.DataFrame]:
    """
    Loads all required sheets from the Excel workbook.
    Accepts file path or bytes/buffer.
    Returns a dictionary of cleaned DataFrames.
    """
    source = _resolve_source(file_source)

    try:
        excel_file = pd.ExcelFile(source, engine="openpyxl")
    except Exception as e:
        logger.error("Failed to open Excel workbook: %s", str(e))
        raise RuntimeError(f"Could not load Excel workbook: {e}") from e

    sheet_names = excel_file.sheet_names
    missing_sheets = [s for s in REQUIRED_SHEETS if s not in sheet_names]
    if missing_sheets:
        raise ValueError(
            f"The provided workbook is missing required sheets: {', '.join(missing_sheets)}. "
            f"Available sheets: {', '.join(sheet_names)}"
        )

    data: Dict[str, pd.DataFrame] = {}

    # Load and clean each required sheet
    raw_patients = pd.read_excel(excel_file, sheet_name="Patients")
    data["Patients"] = _clean_patients(raw_patients)

    raw_doctors = pd.read_excel(excel_file, sheet_name="Doctors")
    data["Doctors"] = _clean_doctors(raw_doctors)

    raw_nurses = pd.read_excel(excel_file, sheet_name="Nurses")
    data["Nurses"] = _clean_nurses(raw_nurses)

    raw_staffing = pd.read_excel(excel_file, sheet_name="Daily_Staffing")
    data["Daily_Staffing"] = _clean_daily_staffing(raw_staffing)

    raw_departments = pd.read_excel(excel_file, sheet_name="Departments")
    data["Departments"] = _clean_departments(raw_departments)

    # Also load optional summary sheets if present
    if "Dashboard_Summary" in sheet_names:
        data["Dashboard_Summary"] = pd.read_excel(excel_file, sheet_name="Dashboard_Summary")
    if "README" in sheet_names:
        data["README"] = pd.read_excel(excel_file, sheet_name="README")

    return data


def load_patients(file_source: Optional[Union[str, Path, bytes]] = None) -> pd.DataFrame:
    """Convenience function to load Patients DataFrame."""
    return load_excel_data(file_source)["Patients"]


def load_doctors(file_source: Optional[Union[str, Path, bytes]] = None) -> pd.DataFrame:
    """Convenience function to load Doctors DataFrame."""
    return load_excel_data(file_source)["Doctors"]


def load_nurses(file_source: Optional[Union[str, Path, bytes]] = None) -> pd.DataFrame:
    """Convenience function to load Nurses DataFrame."""
    return load_excel_data(file_source)["Nurses"]


def load_daily_staffing(file_source: Optional[Union[str, Path, bytes]] = None) -> pd.DataFrame:
    """Convenience function to load Daily_Staffing DataFrame."""
    return load_excel_data(file_source)["Daily_Staffing"]


def load_departments(file_source: Optional[Union[str, Path, bytes]] = None) -> pd.DataFrame:
    """Convenience function to load Departments DataFrame."""
    return load_excel_data(file_source)["Departments"]
