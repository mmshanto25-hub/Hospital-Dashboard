"""
utils/helpers.py
UI and Utility helpers for the Hospital Management & Staffing Analytics Dashboard.
Includes custom CSS loader, executive headers, modern KPI card renderer, alert boxes,
number/date formatters, and multi-format export engines (CSV and OpenPyXL styled Excel).
"""

from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import io
import pandas as pd
import streamlit as st
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

CSS_PATH = Path(__file__).resolve().parent.parent / "assets" / "custom.css"


def apply_custom_css():
    """Injects custom CSS from assets/custom.css into the active Streamlit page."""
    if CSS_PATH.exists():
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <style>
            .stApp { background-color: #0B1220; color: #F8FAFC; }
            </style>
            """,
            unsafe_allow_html=True
        )


def render_page_header(
    title: str,
    subtitle: str,
    selected_range: Optional[str] = None,
    selected_dept: Optional[str] = None,
    latest_update: Optional[str] = None
):
    """
    Renders an executive-grade page header with clean typography,
    metadata pills, and context status.
    """
    dept_label = selected_dept if selected_dept and selected_dept != "All" else "All Departments"
    range_label = selected_range if selected_range else "Full Available Period"
    update_label = latest_update if latest_update else "Live Snapshot"

    badges_html = f"""
    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.75rem; margin-bottom: 1.25rem;">
        <span style="background: rgba(59, 130, 246, 0.12); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 6px; padding: 0.2rem 0.6rem; font-size: 0.76rem; font-weight: 500;">
            📅 {range_label}
        </span>
        <span style="background: rgba(139, 92, 246, 0.12); color: #A78BFA; border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 6px; padding: 0.2rem 0.6rem; font-size: 0.76rem; font-weight: 500;">
            🏢 {dept_label}
        </span>
        <span style="background: rgba(34, 197, 94, 0.12); color: #4ADE80; border: 1px solid rgba(34, 197, 94, 0.25); border-radius: 6px; padding: 0.2rem 0.6rem; font-size: 0.76rem; font-weight: 500;">
            ⏱️ {update_label}
        </span>
    </div>
    """

    st.markdown(
        f"""
        <div style="margin-bottom: 0.5rem;">
            <h1 style="margin-bottom: 0.2rem;">{title}</h1>
            <p style="font-size: 0.95rem; color: #94A3B8; margin: 0;">{subtitle}</p>
            {badges_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_kpi_card(
    title: str,
    value: Union[int, float, str],
    subtitle: Optional[str] = None,
    icon: str = "📊",
    badge_text: Optional[str] = None,
    badge_type: str = "positive"
):
    """
    Renders a modern dark navy KPI card using HTML and CSS.
    badge_type: 'positive' (green), 'warning' (yellow), 'danger' (red), 'neutral' (blue/gray).
    """
    badge_class = {
        "positive": "kpi-badge-positive",
        "warning": "kpi-badge-warning",
        "danger": "kpi-badge-danger",
        "neutral": "kpi-badge-positive"
    }.get(badge_type, "kpi-badge-positive")

    badge_html = f'<span class="{badge_class}">{badge_text}</span>' if badge_text else ""
    subtitle_html = f'<div class="kpi-subtitle">{subtitle}</div>' if subtitle else ""

    card_html = f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-header">
                <span class="kpi-title">{title}</span>
                <span class="kpi-icon">{icon}</span>
            </div>
            <div class="kpi-value">{value}</div>
        </div>
        <div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.25rem;">
                {subtitle_html}
                {badge_html}
            </div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_alert_box(
    title: str,
    message: str,
    alert_type: str = "warning",
    icon: Optional[str] = None
):
    """
    Renders a styled alert banner.
    alert_type: 'danger', 'warning', 'success', 'info'
    """
    default_icons = {
        "danger": "⚠️",
        "warning": "⚡",
        "success": "✅",
        "info": "ℹ️"
    }
    ico = icon if icon else default_icons.get(alert_type, "ℹ️")
    css_class = f"alert-box alert-{alert_type}"

    st.markdown(
        f"""
        <div class="{css_class}">
            <div style="display: flex; align-items: flex-start; gap: 0.6rem;">
                <span style="font-size: 1.15rem; line-height: 1.2;">{ico}</span>
                <div>
                    <strong style="color: #F8FAFC; font-size: 0.88rem; display: block; margin-bottom: 0.2rem;">{title}</strong>
                    <span style="color: #CBD5E1; font-size: 0.82rem; line-height: 1.4;">{message}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def format_number(val: Union[int, float], decimals: int = 0) -> str:
    """Formats numeric values with thousands separator and specified decimals."""
    if pd.isna(val):
        return "N/A"
    if decimals == 0:
        return f"{int(round(val)):,}"
    return f"{val:,.{decimals}f}"


def format_percent(val: Union[int, float], decimals: int = 1) -> str:
    """Formats percentage values."""
    if pd.isna(val):
        return "N/A"
    return f"{val:.{decimals}f}%"


# ==============================================================================
# ADVANCED MULTI-FORMAT EXPORT ENGINE (CSV & STYLED OPENPYXL EXCEL)
# ==============================================================================

def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """Encodes a DataFrame into UTF-8 CSV bytes for download."""
    if df.empty:
        return b""
    return df.to_csv(index=False).encode("utf-8")


def convert_dfs_to_excel(
    df_dict: Dict[str, pd.DataFrame],
    apply_styling: bool = True
) -> bytes:
    """
    Writes multiple DataFrames to an in-memory Excel workbook buffer.
    When apply_styling is True, uses OpenPyXL to format headers with a dark navy fill,
    bold white text, thin borders, and automatically adjusted column widths.
    """
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, df in df_dict.items():
            clean_sheet = str(sheet_name)[:31]
            df.to_excel(writer, sheet_name=clean_sheet, index=False)

    if not apply_styling:
        return output.getvalue()

    # Re-open with openpyxl to apply professional formatting
    output.seek(0)
    wb = openpyxl.load_workbook(output)

    header_fill = PatternFill(start_color="162338", end_color="162338", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="F8FAFC")
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    thin_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1")
    )

    for ws in wb.worksheets:
        ws.row_dimensions[1].height = 26

        # Format header row
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_align
            cell.border = thin_border

        # Auto-adjust column widths based on content length
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                if len(val_str) > max_len:
                    max_len = len(val_str)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    styled_output = io.BytesIO()
    wb.save(styled_output)
    return styled_output.getvalue()
