import pandas as pd
from datetime import datetime, timedelta
from database.transaction_models import TransactionModel

class FinanceAnalyzer:
    def __init__(self,
                 transaction_model: TransactionModel):
        self.transaction_model = transaction_model
    
    def get_transactions_dataframe(self):
        """Convert transactions to pandas Dataframe"""
        transactions = self.transaction_model.get_transaction()
        if not transactions:
            return pd.DataFrame()
        df= pd.DataFrame(transactions)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        return df
    
    def calculate_total_by_type(self, transaction_type, start_date = None, end_date=None):
        """Calculate total amount by type"""
        if start_date and end_date:
            transactions = self.transaction_model.get_transaction_by_date_range(
                start_date, end_date
                )
        else:
            transactions = self.transaction_model.get_transaction()
        total = sum(
            t['amount'] for t in transactions 
            if t.get('transaction_type')== transaction_type)
        return total
    
    def get_spending_by_category(self, start_date=None, end_date=None):
        """Get spending grouped by category"""
        if start_date and end_date:
            transactions = self.transaction_model.get_transaction_by_date_range(
                start_date, end_date
            )
        else:
            transactions = self.transaction_model.get_transactions()
        
        df = pd.DataFrame(transactions)
        
        if df.empty:
            return pd.DataFrame()
        
        # Filter only expenses
        expenses = df[df['transaction_type'] == 'Expense']
        
        if expenses.empty:
            return pd.DataFrame()
        
        category_spending = expenses.groupby('category')['amount'].agg(['sum', 'count', 'mean']).reset_index()
        category_spending.columns = ['Category', 'Total', 'Count', 'Average']
        category_spending = category_spending.sort_values('Total', ascending=False)
        
        return category_spending

    def get_daily_average(self):
        """Caculate daily average spending"""
        transactions = self.transaction_model.get_transaction()
        expenses = [t for t in transactions if t.get('transaction_type') == 'Expense']

        # # approach 2:
        # advanced_filter = {"type": "Expense"}
        # expenses = self.transaction_model.get_transaction(advanced_filter)

        if not expenses:
            return 0
        df = pd.DataFrame(expenses)
        df['transaction_date'] = pd.to_datetime(df['transaction_date']) # make sure convert properly datetime format

        date_range = (df['transaction_date'].max() - df['transaction_date'].min()).days + 1
        total_spending = df['amount'].sum()
        return total_spending / date_range  if date_range > 0 else 0 
    
    def get_monthly_trend(self, months=6):
        """Get monthly spending and income trend"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months*30)
        
        transactions = self.transaction_model.get_transaction_by_date_range(
            start_date, end_date
        )
        
        df = pd.DataFrame(transactions)
        
        if df.empty:
            return pd.DataFrame()
        # ✅ đảm bảo cột tồn tại
        if 'transaction_date' not in df.columns:
            return pd.DataFrame()
        
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df['month'] = df['transaction_date'].dt.to_period('M')
        
        monthly_data = (
            df.groupby(['month', 'transaction_type'])['amount']
            .sum().unstack(fill_value=0)
            )
        monthly_data.index = monthly_data.index.to_timestamp()
        
        return monthly_data