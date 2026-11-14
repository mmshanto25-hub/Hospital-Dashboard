"""
utils/charts.py
Reusable Plotly visualization engine for the Hospital Management Dashboard.
Enforces consistent dark-theme palette (#0B1220 / #162338), responsive sizing,
interactive tooltips, custom annotations, and graceful handling of empty data.
"""

from typing import List, Optional, Union, Dict, Any
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Enterprise Dark Navy Palette
THEME_COLORS = {
    "background": "#162338",
    "paper": "#162338",
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "grid": "#1E293B",
    "blue": "#3B82F6",
    "cyan": "#06B6D4",
    "green": "#22C55E",
    "purple": "#8B5CF6",
    "orange": "#F59E0B",
    "red": "#EF4444",
    "palette": ["#3B82F6", "#06B6D4", "#22C55E", "#8B5CF6", "#F59E0B", "#EC4899", "#14B8A6"]
}


def _apply_standard_layout(
    fig: go.Figure,
    title: str,
    x_title: Optional[str] = None,
    y_title: Optional[str] = None,
    height: int = 380,
    show_legend: bool = True
) -> go.Figure:
    """Applies unified styling, fonts, margins, and dark theme colors to any Plotly figure."""
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>",
            "y": 0.95,
            "x": 0.02,
            "xanchor": "left",
            "yanchor": "top",
            "font": {"size": 15, "color": THEME_COLORS["text_primary"], "family": "Inter, sans-serif"}
        },
        paper_bgcolor=THEME_COLORS["paper"],
        plot_bgcolor=THEME_COLORS["background"],
        font={"color": THEME_COLORS["text_secondary"], "family": "Inter, sans-serif", "size": 12},
        height=height,
        margin={"l": 40, "r": 30, "t": 55, "b": 45},
        showlegend=show_legend,
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {"size": 11, "color": THEME_COLORS["text_secondary"]},
            "bgcolor": "rgba(0,0,0,0)"
        },
        hoverlabel={
            "bgcolor": "#1E293B",
            "font_size": 12,
            "font_family": "Inter, sans-serif",
            "font_color": "#F8FAFC",
            "bordercolor": THEME_COLORS["blue"]
        }
    )

    fig.update_xaxes(
        title_text=x_title,
        showgrid=True,
        gridwidth=1,
        gridcolor=THEME_COLORS["grid"],
        zeroline=False,
        tickfont={"color": THEME_COLORS["text_secondary"], "size": 11}
    )

    fig.update_yaxes(
        title_text=y_title,
        showgrid=True,
        gridwidth=1,
        gridcolor=THEME_COLORS["grid"],
        zeroline=False,
        tickfont={"color": THEME_COLORS["text_secondary"], "size": 11}
    )

    return fig


def _create_empty_figure(title: str, message: str = "No data available for the active filters") -> go.Figure:
    """Returns an elegant placeholder figure when data is filtered down to empty."""
    fig = go.Figure()
    fig.add_annotation(
        text=f"ℹ️ {message}",
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font={"size": 14, "color": THEME_COLORS["text_secondary"]}
    )
    return _apply_standard_layout(fig, title=title, show_legend=False)


# ==============================================================================
# 1. TIME-SERIES & LINE CHARTS
# ==============================================================================

def create_line_chart(
    df: pd.DataFrame,
    x: str,
    y: Union[str, List[str]],
    title: str,
    x_title: Optional[str] = None,
    y_title: Optional[str] = None,
    color_map: Optional[Dict[str, str]] = None,
    markers: bool = True,
    height: int = 380
) -> go.Figure:
    """
    Creates a time-series or multi-series line chart with smooth curves,
    markers, and custom tooltips.
    """
    if df.empty or x not in df.columns:
        return _create_empty_figure(title)

    fig = go.Figure()

    series_list = [y] if isinstance(y, str) else y
    default_colors = [THEME_COLORS["blue"], THEME_COLORS["cyan"], THEME_COLORS["purple"], THEME_COLORS["green"]]

    for idx, col in enumerate(series_list):
        if col not in df.columns:
            continue
        c = color_map.get(col, default_colors[idx % len(default_colors)]) if color_map else default_colors[idx % len(default_colors)]
        fig.add_trace(go.Scatter(
            x=df[x],
            y=df[col],
            mode="lines+markers" if markers else "lines",
            name=col.replace("_", " "),
            line={"color": c, "width": 2.5},
            marker={"size": 5, "color": c},
            hovertemplate=f"<b>%{{x|%b %Y}}</b><br>{col.replace('_', ' ')}: %{{y:,.0f}}<extra></extra>"
            if pd.api.types.is_datetime64_any_dtype(df[x]) else
            f"<b>%{{x}}</b><br>{col.replace('_', ' ')}: %{{y:,.1f}}<extra></extra>"
        ))

    return _apply_standard_layout(fig, title, x_title, y_title, height=height)


# ==============================================================================
# 2. BAR CHARTS (VERTICAL & HORIZONTAL WITH HIGHLIGHTING)
# ==============================================================================

def create_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    orientation: str = "v",
    sort_descending: bool = True,
    highlight_top_n: Optional[int] = None,
    x_title: Optional[str] = None,
    y_title: Optional[str] = None,
    color_code: Optional[str] = None,
    height: int = 380
) -> go.Figure:
    """
    Creates a modern bar chart. Supports horizontal orientation with top-N highlight coloring.
    """
    if df.empty or x not in df.columns or y not in df.columns:
        return _create_empty_figure(title)

    data = df.copy()

    val_col = y if orientation == "v" else x
    cat_col = x if orientation == "v" else y

    if sort_descending:
        data = data.sort_values(by=val_col, ascending=(orientation == "h"))

    base_color = color_code if color_code else THEME_COLORS["blue"]
    colors = [base_color] * len(data)

    # Highlight top N if requested
    if highlight_top_n is not None and highlight_top_n > 0:
        if orientation == "h":
            # For horizontal sorted ascending, top values are at the end
            for i in range(max(0, len(data) - highlight_top_n), len(data)):
                colors[i] = THEME_COLORS["cyan"]
        else:
            # For vertical sorted descending, top values are at the start
            for i in range(min(highlight_top_n, len(data))):
                colors[i] = THEME_COLORS["cyan"]

    fig = go.Figure()

    if orientation == "h":
        fig.add_trace(go.Bar(
            x=data[x],
            y=data[y],
            orientation="h",
            marker={"color": colors, "line": {"width": 0}},
            hovertemplate="<b>%{y}</b><br>Count: %{x:,.0f}<extra></extra>"
        ))
    else:
        fig.add_trace(go.Bar(
            x=data[x],
            y=data[y],
            orientation="v",
            marker={"color": colors, "line": {"width": 0}},
            hovertemplate="<b>%{x}</b><br>Count: %{y:,.0f}<extra></extra>"
        ))

    return _apply_standard_layout(fig, title, x_title, y_title, height=height, show_legend=False)


# ==============================================================================
# 3. GROUPED BAR CHARTS
# ==============================================================================

def create_grouped_bar_chart(
    df: pd.DataFrame,
    x: str,
    y_cols: List[str],
    title: str,
    x_title: Optional[str] = None,
    y_title: Optional[str] = None,
    colors: Optional[List[str]] = None,
    height: int = 380
) -> go.Figure:
    """
    Creates a grouped bar chart comparing multiple metric series across categories.
    """
    if df.empty or x not in df.columns:
        return _create_empty_figure(title)

    fig = go.Figure()
    palette = colors if colors else [THEME_COLORS["blue"], THEME_COLORS["purple"], THEME_COLORS["cyan"]]

    for idx, col in enumerate(y_cols):
        if col not in df.columns:
            continue
        fig.add_trace(go.Bar(
            x=df[x],
            y=df[col],
            name=col.replace("_", " "),
            marker={"color": palette[idx % len(palette)]},
            hovertemplate=f"<b>%{{x}}</b><br>{col.replace('_', ' ')}: %{{y:,.1f}}<extra></extra>"
        ))

    fig.update_layout(barmode="group")
    return _apply_standard_layout(fig, title, x_title, y_title, height=height)


# ==============================================================================
# 4. DONUT CHARTS
# ==============================================================================

def create_donut_chart(
    labels: List[str],
    values: List[Union[int, float]],
    title: str,
    hole: float = 0.65,
    colors: Optional[List[str]] = None,
    center_text: Optional[str] = None,
    center_subtext: Optional[str] = None,
    height: int = 360
) -> go.Figure:
    """
    Creates a refined donut chart with central KPI callout.
    """
    if not values or sum(values) == 0:
        return _create_empty_figure(title)

    palette = colors if colors else [THEME_COLORS["blue"], THEME_COLORS["cyan"], THEME_COLORS["purple"], THEME_COLORS["orange"], THEME_COLORS["green"]]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=hole,
        marker={"colors": palette[:len(labels)]},
        textinfo="percent",
        textfont={"color": "#F8FAFC", "size": 12, "family": "Inter, sans-serif"},
        hoverinfo="label+value+percent",
        hovertemplate="<b>%{label}</b><br>Value: %{value:,.0f}<br>Share: %{percent}<extra></extra>"
    )])

    # Center text annotations if provided
    annotations = []
    if center_text:
        annotations.append({
            "text": f"<b>{center_text}</b>",
            "x": 0.5,
            "y": 0.53 if center_subtext else 0.5,
            "font": {"size": 22, "color": THEME_COLORS["text_primary"], "family": "Inter, sans-serif"},
            "showarrow": False
        })
    if center_subtext:
        annotations.append({
            "text": center_subtext,
            "x": 0.5,
            "y": 0.44,
            "font": {"size": 11, "color": THEME_COLORS["text_secondary"], "family": "Inter, sans-serif"},
            "showarrow": False
        })

    fig.update_layout(annotations=annotations)
    return _apply_standard_layout(fig, title, height=height)


# ==============================================================================
# 5. HISTOGRAMS
# ==============================================================================

def create_histogram(
    df: pd.DataFrame,
    x: str,
    title: str,
    nbins: Optional[int] = None,
    x_title: Optional[str] = None,
    y_title: str = "Patient Count",
    color: Optional[str] = None,
    height: int = 380
) -> go.Figure:
    """
    Creates a histogram for continuous distributions (e.g., Age, Length of Stay).
    """
    if df.empty or x not in df.columns:
        return _create_empty_figure(title)

    bar_color = color if color else THEME_COLORS["blue"]

    fig = go.Figure(data=[go.Histogram(
        x=df[x],
        nbinsx=nbins,
        marker={"color": bar_color, "line": {"color": THEME_COLORS["paper"], "width": 1}},
        hovertemplate=f"Range: %{{x}}<br>{y_title}: %{{y:,.0f}}<extra></extra>"
    )])

    return _apply_standard_layout(fig, title, x_title, y_title, height=height, show_legend=False)


# ==============================================================================
# 6. HEATMAPS
# ==============================================================================

def create_heatmap(
    df: pd.DataFrame,
    x: str,
    y: str,
    z: str,
    title: str,
    x_title: Optional[str] = None,
    y_title: Optional[str] = None,
    height: int = 400
) -> go.Figure:
    """
    Creates a 2D matrix heatmap (e.g. Department vs Shift ratios or day-by-day ratios).
    """
    if df.empty or not all(c in df.columns for c in [x, y, z]):
        return _create_empty_figure(title)

    # Pivot table to 2D grid
    pivot_df = df.pivot_table(index=y, columns=x, values=z, aggfunc="mean").round(2)

    # Navy to Cyan/Orange/Red color scale
    custom_colorscale = [
        [0.0, "#0E3A5A"],
        [0.4, "#1E5894"],
        [0.7, "#06B6D4"],
        [0.85, "#F59E0B"],
        [1.0, "#EF4444"]
    ]

    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns.astype(str),
        y=pivot_df.index.astype(str),
        colorscale=custom_colorscale,
        colorbar={"title": z.replace("_", " "), "tickfont": {"color": THEME_COLORS["text_secondary"]}},
        hovertemplate=f"<b>%{{y}}</b> | %{{x}}<br>{z.replace('_', ' ')}: %{{z:.2f}}<extra></extra>"
    ))

    return _apply_standard_layout(fig, title, x_title, y_title, height=height, show_legend=False)


# ==============================================================================
# 7. AREA CHARTS
# ==============================================================================

def create_area_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    x_title: Optional[str] = None,
    y_title: Optional[str] = None,
    color: Optional[str] = None,
    height: int = 380
) -> go.Figure:
    """
    Creates a smooth filled area chart for continuous volume trends (e.g. Hospital Census over time).
    """
    if df.empty or x not in df.columns or y not in df.columns:
        return _create_empty_figure(title)

    line_color = color if color else THEME_COLORS["blue"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x],
        y=df[y],
        mode="lines",
        line={"color": line_color, "width": 2},
        fill="tozeroy",
        fillcolor="rgba(59, 130, 246, 0.15)",
        hovertemplate=f"<b>%{{x|%b %d, %Y}}</b><br>{y.replace('_', ' ')}: %{{y:,.0f}}<extra></extra>"
        if pd.api.types.is_datetime64_any_dtype(df[x]) else
        f"<b>%{{x}}</b><br>{y.replace('_', ' ')}: %{{y:,.0f}}<extra></extra>"
    ))

    return _apply_standard_layout(fig, title, x_title, y_title, height=height, show_legend=False)


# ==============================================================================
# 8. LINEAR REGRESSION FORECAST CHART
# ==============================================================================

def create_regression_forecast_chart(
    historical_df: pd.DataFrame,
    forecast_df: pd.DataFrame,
    title: str = "Patient Census Trend & Linear Regression Forecast",
    x_title: Optional[str] = "Date",
    y_title: Optional[str] = "Patient Census",
    height: int = 420
) -> go.Figure:
    """
    Renders an interactive multi-trace chart showing:
    - Actual historical census (points + smooth curve)
    - OLS Linear Regression fitted trendline (dashed line across historical data)
    - Future projected forecast (amber highlighted line with markers)
    - Vertical transition line separating history from forecast
    """
    if historical_df.empty:
        return _create_empty_figure(title)

    fig = go.Figure()

    # 1. Actual Historical Observations
    fig.add_trace(go.Scatter(
        x=historical_df["Date"],
        y=historical_df["Actual_Census"],
        mode="lines+markers",
        name="Actual Census",
        line={"color": "#38BDF8", "width": 2},
        marker={"size": 4, "color": "#38BDF8", "opacity": 0.8},
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>Actual Census: <b>%{y:,.0f}</b><extra></extra>"
    ))

    # 2. Fitted OLS Line on Historical Data
    if "Fitted_Census" in historical_df.columns:
        fig.add_trace(go.Scatter(
            x=historical_df["Date"],
            y=historical_df["Fitted_Census"],
            mode="lines",
            name="OLS Fitted Trend",
            line={"color": "#94A3B8", "width": 2, "dash": "dot"},
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>Fitted Trend: <b>%{y:,.1f}</b><extra></extra>"
        ))

    # 3. Forecast Projections
    if not forecast_df.empty and "Fitted_Census" in forecast_df.columns:
        # Connect last historical fitted point to first forecast point for seamless continuity
        connect_x = [historical_df["Date"].iloc[-1]] + list(forecast_df["Date"])
        connect_y = [historical_df["Fitted_Census"].iloc[-1]] + list(forecast_df["Fitted_Census"])

        fig.add_trace(go.Scatter(
            x=connect_x,
            y=connect_y,
            mode="lines+markers",
            name="Projected Forecast",
            line={"color": "#F59E0B", "width": 3, "dash": "dash"},
            marker={"size": 6, "color": "#F59E0B", "symbol": "diamond"},
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>Projected: <b>%{y:,.1f}</b><extra></extra>"
        ))

        # Add vertical dividing line indicating forecast inception
        split_date = historical_df["Date"].iloc[-1]
        fig.add_vline(
            x=split_date,
            line_width=1.5,
            line_dash="dash",
            line_color="#EF4444",
            annotation_text="Forecast Start",
            annotation_position="top left",
            annotation_font={"size": 11, "color": "#FCA5A5"}
        )

    return _apply_standard_layout(fig, title, x_title, y_title, height=height, show_legend=True)

