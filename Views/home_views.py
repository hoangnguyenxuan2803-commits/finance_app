import pandas as pd
import streamlit as st
from utils import format_currency, get_date_range_options
from analytics.analyzer import FinanceAnalyzer
from analytics.visualizer import FinananceVisualizer
from database.transaction_models import TransactionModel


def render_dashboard(analyzer_model:FinanceAnalyzer, transaction_model: TransactionModel, visualizer_model: FinananceVisualizer):
    """
    Render the main financial dashboard
    
    Args:
        analyzer_model: FinanceAnalyzer
    """
    st.title("📊 Financial Dashboard")
    
    # Data range selector
    col1,_= st.columns([2,1])
    with col1: 
        date_range_option = st.selectbox(
            "Select Date Range",
            list(get_date_range_options().keys()),
            index = 3 # Default to "last 30 days"
        )
    data_ranges = get_date_range_options() # return dictionary
    start_date, end_date = data_ranges[date_range_option]

    # Display mertrics section
    _render_metrics(analyzer_model, start_date , end_date)
    st.divider()

    # Display chart section
    _render_chart(analyzer_model, visualizer_model , start_date, end_date)

def _render_metrics(analyzer_model: FinanceAnalyzer, start_date, end_date):
    """ Render the metrics cards at the top of dashboard"""
    if start_date and end_date:
        total_expense = analyzer_model.calculate_total_by_type("Expense", start_date, end_date)
        total_income = analyzer_model.calculate_total_by_type("Income", start_date, end_date)
    else: 
        total_expense = analyzer_model.calculate_total_by_type("Expense") or 0
        total_income = analyzer_model.calculate_total_by_type("Income") or 0

    net_balance = total_income - total_expense

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💸 Total Expenses", format_currency(total_expense))
    with col2:
        st.metric("💰 Total Incomes", format_currency(total_income))
    with col3:
        delta_color = "normal" if net_balance >= 0 else "inverse"
        st.metric("𓍝 Net Balance", format_currency(net_balance), delta_color=delta_color)
    with col4:
        daily_avg = analyzer_model.get_daily_average()
        st.metric("📅 Daily Avg Expense", format_currency(daily_avg))

def _render_chart(analyzer_model: FinanceAnalyzer,
                  visualizer_model: FinananceVisualizer,
                  start_date,
                  end_date):
    """Render the chart section and tren visualization"""
    # category chart
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Category Breakdown")
        category_spending = analyzer_model.get_spending_by_category(start_date, end_date)
        if not category_spending.empty:
            fig = visualizer_model.plot_category_spending(category_spending)
            st.plotly_chart(fig, width = 'stretch')
        else:
            st.info("No expense data available for this period")
    
    with col2:
        st.subheader("📈 Category Breakdown")
        if not category_spending.empty:
            fig = visualizer_model.plot_pie_chart(category_spending)
            st.plotly_chart(fig, width = 'stretch')
        else:
            st.info("No expense data available for this period")
        
    # Monthly trend
    st.subheader("📈 Monthly Trend")
    monthly_trend = analyzer_model.get_monthly_trend(months= 6)
    if not monthly_trend.empty:
        fig = visualizer_model.plot_monthly_trend(monthly_trend)
        st.plotly_chart(fig, width = 'stretch')
    else:
        st.info("No expense data available for this period")
        
