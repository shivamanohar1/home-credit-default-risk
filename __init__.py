"""
Utils package for Home Credit Default Risk Analytics Platform.

Modules:
- data_loader: File discovery, raw ingestion, and cached dataset loading.
- preprocessing: Anomaly detection, data cleaning, and categorical value standardizations.
- features: Feature engineering (Age/Tenure/Financial groups, leverage ratios, bureau composite scores).
- filters: Underwriting sidebar filter components.
- kpis: Risk metrics calculation and financial notation formatters.
- charts: Plotly visualizers with standardized themes and responsive layouts.
- page_helpers: UI layout, header rendering, formula callouts, and insight cards.
"""

from utils.data_loader import load_home_credit_data, load_raw_data, get_dataset_path
from utils.preprocessing import preprocess_home_credit_data
from utils.features import engineer_features
from utils.filters import render_sidebar_filters
from utils.kpis import calculate_home_credit_kpis, format_currency, format_percent, format_number, format_ratio
from utils.charts import (
    apply_chart_layout,
    create_donut_chart,
    create_bar_chart,
    create_line_trend,
    create_scatter_plot,
    create_histogram,
    create_box_plot,
    create_heatmap_matrix,
)
from utils.page_helpers import apply_page_config, render_header, render_formula_card, render_insights_card

__all__ = [
    "load_home_credit_data",
    "load_raw_data",
    "get_dataset_path",
    "preprocess_home_credit_data",
    "engineer_features",
    "render_sidebar_filters",
    "calculate_home_credit_kpis",
    "format_currency",
    "format_percent",
    "format_number",
    "format_ratio",
    "apply_chart_layout",
    "create_donut_chart",
    "create_bar_chart",
    "create_line_trend",
    "create_scatter_plot",
    "create_histogram",
    "create_box_plot",
    "create_heatmap_matrix",
    "apply_page_config",
    "render_header",
    "render_formula_card",
    "render_insights_card",
]
