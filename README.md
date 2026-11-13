# MediCore Health: Hospital Management & Staffing Analytics Dashboard

[![Streamlit](https://img.shields.io/badge/Streamlit-1.67.0-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=Python&logoColor=white)](https://www.python.org)
[![Plotly](https://img.shields.io/badge/Plotly-7.1.0-3F4F75?style=for-the-badge&logo=Plotly&logoColor=white)](https://plotly.com)
[![Pandas](https://img.shields.io/badge/Pandas-3.1.1-150458?style=for-the-badge&logo=Pandas&logoColor=white)](https://pandas.pydata.org)
[![OpenPyXL](https://img.shields.io/badge/OpenPyXL-3.1.5-217346?style=for-the-badge&logo=Microsoft-Excel&logoColor=white)](https://openpyxl.readthedocs.io)

An enterprise-grade, data-driven Hospital Management & Staffing Analytics Platform designed to monitor clinical capacity, workforce allocation, patient census, bed occupancy, and staffing ratios across all hospital clinical units.

---

## 1. Project Overview

**MediCore Health Dashboard** transforms complex hospital operational data into actionable clinical intelligence. Built for healthcare operations executives, chief nursing officers, and department directors, this dashboard continuously tracks patient volume, doctor-to-patient ratios, nurse-to-patient ratios, and bed utilization against clinical accreditation targets.

> **Key Distinction:** This platform serves as an operational analytics and staffing surveillance dashboard, not an electronic health record (EHR) or clinical diagnosis transaction engine.

---

## 2. Key Architecture & Features

- **True Data-Driven Analytics**: Every KPI card, bar chart, donut chart, and heatmap is computed dynamically from actual Excel records. Zero hardcoded dummy metrics.
- **Contextual Filtering Architecture**:
  - Global Date Range applied contextually: cohort filtering relies on `Admission_Date`, whereas staffing and census analysis relies on `Daily_Staffing.Date`.
  - Static staff registries (Doctors and Nurses) are protected from arbitrary admission date truncation.
- **Enterprise Dark Navy Design System**:
  - Built with custom CSS (`#0B1220` primary background, `#162338` elevated surfaces, `#3B82F6` primary blue accents).
  - High-contrast accessibility exceeding WCAG AAA standards (>12:1 contrast ratio).
- **Zero-Deprecation Streamlit Standard**:
  - Built natively with `width="stretch"` for all widgets and interactive Plotly figures.
- **PyCharm & IDE One-Click Launcher**:
  - Includes `run.py` and auto-boot interceptors, allowing instant execution in PyCharm via **Right-Click -> Run** or **Shift + F10** without manual terminal commands.
- **Styled Multi-Sheet Excel Reports**:
  - OpenPyXL-powered export engine generating styled spreadsheets with navy headers, bold text, borders, and auto-adjusted column widths.

---

## 3. Technology Stack

- **Core Language**: Python 3.11+ (CPython 3.14 compatible)
- **Web App Framework**: Streamlit (Multipage architecture)
- **Data Manipulation & Analytics**: Pandas, NumPy
- **Interactive Visualizations**: Plotly Express, Plotly Graph Objects
- **Excel Ingestion & Styled Reporting**: OpenPyXL
- **Asset Processing**: Pillow (PIL)
- **Automated Testing**: Python `unittest` (53 automated unit tests)

---

## 4. Project Directory Structure

```text
hospital Overview/
│
├── data/
│   └── hospital_dataset.xlsx          # Standard local hospital dataset
│
├── pages/
│   ├── 1_Hospital_Overview.py         # Executive overview & hospital KPIs
│   ├── 2_Patient_Analytics.py          # Cohort demographics, trends & LOS
│   ├── 3_Doctor_Analytics.py           # Physician capacity, specializations & ratios
│   ├── 4_Nurse_Analytics.py            # Nursing capacity, ward allocation & ratios
│   ├── 5_Department_Analytics.py       # Cross-department capacity & multi-unit comparison
│   └── 6_Staffing_Ratio.py             # Staffing ratio analysis & surveillance logs
│
├── utils/
│   ├── __init__.py                     # Utility package descriptor
│   ├── data_loader.py                  # Schema-validated, cached Excel data loader
│   ├── calculations.py                 # Pure calculation functions & analytical formulas
│   ├── charts.py                       # Unified dark-navy Plotly visualization engine
│   ├── filters.py                      # Multi-attribute compound filtering engine
│   └── helpers.py                      # Formatting, CSS loader, and styled Excel exporter
│
├── assets/
│   ├── custom.css                      # Custom enterprise styling stylesheet
│   └── logo.png                        # Generated MediCore hospital emblem
│
├── .streamlit/
│   └── config.toml                     # Streamlit theme and server configuration
│
├── .idea/
│   └── runConfigurations/              # PyCharm shared Run Configuration
│
├── tests/
│   ├── test_all_requirements.py        # 14-point Section 21 compliance test suite
│   ├── test_phase123.py                # Data loading & calculation tests
│   ├── test_phase45.py                 # Filter & chart tests
│   ├── test_phase7.py                  # Patient analytics tests
│   ├── test_phase8.py                  # Doctor & Nurse analytics tests
│   └── test_phase10_11.py              # Export & UI tests
│
├── app.py                              # Application main entrypoint
├── run.py                              # PyCharm one-click launcher
├── requirements.txt                    # Project dependencies
└── README.md                           # Documentation
```

---

## 5. Dataset Description

The application processes seven sheets from `hospital_dataset.xlsx`:

1. **`README`**: Dataset purpose, definitions, and operational notes.
2. **`Dashboard_Summary`**: Quick-reference KPI definitions and high-level formulas.
3. **`Patients` (6,000 records)**: Patient ID, Name, Age, Gender, Department, Ward, Admission Date, Discharge Date (756 active inpatients with null discharge date), Admission Type, Primary Condition, Length of Stay, Patient Status, Staff IDs.
4. **`Doctors` (180 records)**: Doctor ID, Name, Gender, Department, Specialization, Employment Type, Experience Years, Shift, Status (Active, On Leave, Inactive), Weekly Hours.
5. **`Nurses` (480 records)**: Nurse ID, Name, Gender, Department, Ward (10 wards), Shift, Employment Type, Experience Years, Status, Weekly Hours.
6. **`Daily_Staffing` (4,380 records)**: 365 daily snapshots &times; 12 departments. Date, Department, Bed Capacity, Occupied Beds, Daily Patient Census, Active Doctors on Duty, Active Nurses on Duty, Patients per Doctor, Patients per Nurse, Bed Occupancy Rate, Doctor Ratio Status, Nurse Ratio Status, Shift.
7. **`Departments` (12 records)**: Department, Bed Capacity (30–65 beds), Staffing Demand Factor, Target Patients per Doctor, Target Patients per Nurse.

---

## 6. Installation & Execution

### Prerequisites
- Python 3.11 or higher
- Git

### Installation
Clone the repository and install the dependencies:
```bash
git clone <repository-url>
cd "hospital Overview"
pip install -r requirements.txt
```

### Running the Dashboard

#### Option A: One-Click in PyCharm (Recommended for IDE users)
1. Open the project in PyCharm.
2. Right-click **`run.py`** in the project tree and select **Run 'run'** (or press **Shift + F10**).
3. The dashboard will automatically launch in your default browser at `http://localhost:8501`.

#### Option B: Via Terminal / Command Line
```bash
streamlit run app.py
```

---

## 7. Analytical Pages Walkthrough

### Page 1 — Hospital Overview
- **8 Executive KPI Cards**: Total Patient Records, Current Patient Census, Registered Doctors, Registered Nurses, Doctors on Duty, Nurses on Duty, Hospital Bed Occupancy, and Average Length of Stay.
- **Patient Admission & Discharge Trajectory**: Monthly multi-series time trend. Missing discharge dates are strictly excluded from discharge counts.
- **Hospital Bed Occupancy Donut**: Visualizes occupied vs. available beds with central percentage callout.
- **Patients by Department**: Horizontal bar chart highlighting top-3 volume departments with a toggle between daily snapshot census and historical records.
- **Staff on Duty Comparison**: Grouped bar chart comparing active doctors and nurses on duty across units.
- **Patient Demographics**: Age distribution histogram, gender donut, and admission type breakdown.
- **Threshold-Based Staffing Alerts**: Real-time alerts for high doctor load, high nurse load, and high bed occupancy ($\ge 85\%$).
- **Patient Registry Table**: Searchable by ID, Name, or Condition, with direct CSV and Master Multi-Sheet Excel exports.

### Page 2 — Patient Analytics
- **6 Cohort KPIs**: Total records, Admitted, Discharged, Transferred, Average Age, and Average Length of Stay.
- **8 Visualizations**: Monthly admissions trend, monthly discharges trend, department distribution, gender distribution, 6-tier age bracket stratification (`0–17`, `18–30`, `31–45`, `46–60`, `61–75`, `76+`), primary medical condition breakdown, admission channels, and length of stay distribution.
- **Searchable Patient Registry**: Search across clinical conditions and wards, with page size options and CSV/Excel exports.

### Page 3 — Doctor Analytics
- **6 Physician KPIs**: Total, Active, On Leave, Inactive, Full-time, and Part-time (+ Visiting).
- **7 Charts**: Department distribution, 16 clinical specializations, gender breakdown, contract structures, experience brackets (`0–5`, `6–10`, `11–15`, `16–20`, `20+` years), shift coverage, and **Doctor Workload vs. Target Ratio by Department**.
- **Physician Directory**: Interactive directory with search and data export.

### Page 4 — Nurse Analytics
- **6 Nursing KPIs**: Total, Active, On Leave, Inactive, Full-time, and Part-time.
- **6 Charts**: Department distribution, ward allocations across 10 hospital wards, shift coverage, contract types, experience tiers, and **Nurse Workload vs. Target Ratio by Department**.
- **Nursing Directory**: Complete ward-assignment directory with multi-format export.

### Page 5 — Department Analytics
- **Cross-Department Capacity**: Bed capacity, occupied beds, available beds, patient census, doctors on duty, and nurses on duty across all 12 departments.
- **Side-by-Side Multi-Department Comparator**: Interactive selector to benchmark selected units side-by-side.
- **Department Performance Matrix**: Full consolidated data matrix with target ratio comparisons and export buttons.

### Page 6 — Staffing Ratio Analysis
- **Surveillance & Extremes KPIs**: Hospital overall doctor/nurse ratios, highest and lowest ratios by department.
- **Benchmarking Visualizations**: Doctor and nurse ratios vs. clinical targets, 365-day ratio trajectory, and a 2D Department vs. Shift workload heatmap.
- **High-Load Records Surveillance Log**: Filterable audit log of shifts exceeding target ratios, with CSV and Excel downloads.

---

## 8. Calculation Formulas & Mathematical Foundations

### 1. Hospital Bed Occupancy Rate
$$\text{Occupancy Rate (\%)} = \left( \frac{\sum \text{Occupied Beds}}{\sum \text{Bed Capacity}} \right) \times 100$$
> *Important:* Occupancy rate is strictly calculated from aggregated beds and capacities. Department percentage rates are never averaged.

### 2. Available Beds
$$\text{Available Beds} = \max\left(0, \sum \text{Bed Capacity} - \sum \text{Occupied Beds}\right)$$

### 3. Patient-to-Doctor Ratio
$$\text{Patients per Doctor} = \frac{\text{Daily Patient Census}}{\text{Active Doctors on Duty}}$$
*(When Active Doctors = 0 and Census > 0, system safely flags a Critical Staffing alert rather than dividing by zero).*

### 4. Patient-to-Nurse Ratio
$$\text{Patients per Nurse} = \frac{\text{Daily Patient Census}}{\text{Active Nurses on Duty}}$$

### 5. Average Length of Stay (ALOS)
$$\text{ALOS} = \frac{1}{N} \sum_{i=1}^{N} \text{Length\_of\_Stay\_Days}_i$$

---

## 9. Automated Testing & Verification

The application includes an extensive automated test suite covering all functional, mathematical, and UI requirements:

```bash
# Run the complete test suite
python -m unittest discover -s . -p "test_*.py"
```

### Test Coverage Summary:
- `test_all_requirements.py`: Validates all 14 Section 21 testing criteria.
- `test_phase123.py`: Validates schema integrity, data loader, and pure calculation formulas.
- `test_phase45.py`: Validates filtering logic, UI helpers, and Plotly charts.
- `test_phase7.py`: Validates patient analytics calculations and chart generators.
- `test_phase8.py`: Validates doctor and nurse KPIs, workload metrics, and directories.
- `test_phase10_11.py`: Validates OpenPyXL styled Excel export, CSV generation, and CSS assets.

**Result: 53 Tests Passing (100% Pass Rate).**

---

## 10. Future Improvements

1. **Predictive Admissions Modeling**: Integrate machine learning models (e.g., Prophet or XGBoost) to forecast patient admissions 7 days in advance based on seasonal trends.
2. **Automated Shift Roster Generator**: Algorithmic nurse and doctor scheduling optimizing shift coverage against target ratios.
3. **EHR / FHIR Live Connector**: Ingestion adapters for HL7 FHIR APIs to sync live bed occupancy in real-time.
