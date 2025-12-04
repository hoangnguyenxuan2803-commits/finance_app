# pip install  seaborn plotly
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Visualize -> Home -> App: Hướng sửa khi có nhu cầu

# set common style 
sns.set_style("whitegrid")
class FinananceVisualizer:
    @staticmethod
    def plot_category_spending(category_data):
        """ Create bar chart for spending by category"""
        if category_data.empty:
            return None
        fig = px.bar(
            category_data,
            x='Category',
            y='Total',
            title ='Spending by Category',
            labels ={'Total': 'Amount $','Category': 'Category'},
            color = 'Total',
            color_continuous_scale='Reds'
        )

        # overwrite common config
        fig.update_layout(
            xaxis_tickangle= -45,
            height = 500
        )
        return fig
    @staticmethod
    def plot_pie_chart(category_data):
        """ Create pie chart for category distribution"""
        if category_data.empty:
            return None
        
        fig = px.pie(
            category_data,
            values='Total',
            names='Category',
            title='Expense Distribution by Category',
            hole=0.3
        )
        fig.update_traces(textposition = 'inside', textinfo = 'percent+label')
        return fig
    
    @staticmethod
    def plot_monthly_trend(monthly_data):
        """Create line chart for monthly trend"""
        if monthly_data.empty:
            return None
        
        fig = go.Figure()
        
        if 'Expense' in monthly_data.columns:
            fig.add_trace(go.Scatter(
                x=monthly_data.index,
                y=monthly_data['Expense'],
                mode='lines+markers',
                name='Expenses',
                line=dict(color='red', width=2)
            ))
        
        if 'Income' in monthly_data.columns:
            fig.add_trace(go.Scatter(
                x=monthly_data.index,
                y=monthly_data['Income'],
                mode='lines+markers',
                name='Income',
                line=dict(color='green', width=2)
            ))
        
        fig.update_layout(
            title='Monthly Income vs Expenses Trend',
            xaxis_title='Month',
            yaxis_title='Amount ($)',
            hovermode='x unified',
            height=500
        )
        
        return fig
                     