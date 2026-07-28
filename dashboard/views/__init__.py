"""
Dashboard Views Package.
"""
from .executive_kpi import render_executive_kpi_view
from .sales_analytics import render_sales_analytics_view
from .customer_rfm import render_customer_rfm_view
from .product_inventory import render_product_inventory_view
from .sql_studio import render_sql_studio_view
from .ml_forecasting import render_ml_forecasting_view
from .business_insights import render_business_insights_view

__all__ = [
    "render_executive_kpi_view",
    "render_sales_analytics_view",
    "render_customer_rfm_view",
    "render_product_inventory_view",
    "render_sql_studio_view",
    "render_ml_forecasting_view",
    "render_business_insights_view"
]
