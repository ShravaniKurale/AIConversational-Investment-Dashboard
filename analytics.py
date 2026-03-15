import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor
import numpy as np

def load_portfolio(file_path):
    """Load portfolio data from CSV file."""
    try:
        df = pd.read_csv(file_path)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        return df
    except Exception as e:
        print(f"Error loading portfolio: {e}")
        return None

def calculate_total_investment(df):
    """Calculate total invested and current value."""
    try:
        total_investment = df["Investment"].sum()
        total_current_value = df["Current Value"].sum()
        return total_investment, total_current_value
    except Exception as e:
        print(f"Error calculating totals: {e}")
        return 0, 0

def calculate_growth(df):
    """Calculate overall and stock-wise growth percentage."""
    try:
        df["Growth %"] = ((df["Current Value"] - df["Investment"]) / df["Investment"]) * 100
        overall_growth = df["Growth %"].mean()
        return df, overall_growth
    except Exception as e:
        print(f"Error calculating growth: {e}")
        return df, 0

def sector_summary(df):
    """Summarize investments by sector."""
    try:
        sector_data = df.groupby("Sector")[["Investment", "Current Value"]].sum().reset_index()
        sector_data["Growth %"] = ((sector_data["Current Value"] - sector_data["Investment"]) / sector_data["Investment"]) * 100
        return sector_data
    except Exception as e:
        print(f"Error in sector summary: {e}")
        return pd.DataFrame()

def get_portfolio_insights_gemini(df):
    """Generate AI-powered portfolio insights using Gemini 2.5 Flash"""
    try:
        total_inv, total_cur = calculate_total_investment(df)
        df_growth, overall_growth = calculate_growth(df)
        sector_data = sector_summary(df_growth)
        
        insights = {
            'total_investment': total_inv,
            'current_value': total_cur,
            'overall_growth': overall_growth,
            'sector_performance': sector_data.to_dict('records'),
            'best_performer': sector_data.loc[sector_data['Growth %'].idxmax()] if not sector_data.empty else None,
            'worst_performer': sector_data.loc[sector_data['Growth %'].idxmin()] if not sector_data.empty else None
        }
        
        return insights
    except Exception as e:
        print(f"Error generating portfolio insights: {e}")
        return None