"""
SQL Query Lab & Live Query Execution Studio.
"""

import streamlit as st
import pandas as pd
from utils.sql_runner import SQLRunner

def render_sql_studio_view():
    """Renders SQL Query Studio View."""
    st.markdown('<div class="section-header">Interactive SQL Analytics Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Execute production SQL queries against the SQLite database, inspect window functions, CTEs, and export tables for Power BI.</div>', unsafe_allow_html=True)

    runner = SQLRunner(db_path="data/ecommerce.db", sql_dir="sql")
    sql_files = runner.list_sql_files()

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown("### Pre-Built SQL Query Repository")
        selected_file = st.selectbox(
            "Select SQL Analysis Script:",
            sql_files,
            format_func=lambda x: f"📜 {x}"
        )

        query_text = ""
        if selected_file:
            query_text = runner.load_sql_file(selected_file)
            st.markdown("**SQL Script Code:**")
            st.code(query_text, language="sql")

    with col_right:
        st.markdown("### SQL Query Execution & Live Console")
        custom_sql = st.text_area(
            "Modify or write custom SQL query:",
            value=query_text,
            height=250
        )

        if st.button("▶ Execute SQL Query", type="primary"):
            try:
                res_df = runner.run_query(custom_sql)
                st.success(f"Query executed successfully! Returned {len(res_df):,} rows.")
                st.dataframe(res_df, use_container_width=True)

                # Export CSV button
                csv_data = res_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download CSV Export for Power BI",
                    data=csv_data,
                    file_name=f"sql_export_{selected_file.replace('.sql', '') if selected_file else 'custom'}.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"SQL Execution Error: {e}")
