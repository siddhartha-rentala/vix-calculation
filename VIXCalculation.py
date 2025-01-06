import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from datetime import datetime


import pandas as pd

file_paths = [
    r"C:\\Users\\rensi\\Desktop\\Siddhartha Folder\\Fordham University\\Semester 1\\QFGB 8946 Financial Markets and Modeling\\Homework\\HW9\\cleaned_spx_202311_option_chain.csv",
    r"C:\Users\rensi\Desktop\Siddhartha Folder\Fordham University\Semester 1\QFGB 8946 Financial Markets and Modeling\Homework\HW9\cleaned_spx_december_2023_option_chain.csv",
    r"C:\Users\rensi\Desktop\Siddhartha Folder\Fordham University\Semester 1\QFGB 8946 Financial Markets and Modeling\Homework\HW9\cleaned_spx_january_2024_option_chain.csv"
]
columns_to_keep = [
    "Expiration Date",  
    "Strike",           
    "Bid",              
    "Ask",              
    "Bid.1",            
    "Ask.1"             
]

columns_new = {
    "Bid": "Call Bid",
    "Ask": "Call Ask",
    "Bid.1": "Puts Bid",
    "Ask.1": "Puts Ask"
}

dataframes = []

for path in file_paths:
    df = pd.read_csv(path)
    df_cleaned = df[columns_to_keep].rename(columns = columns_new)
    dataframes.append(df_cleaned)

df_combined = pd.concat(dataframes, ignore_index=True)

combined_file_path = r"C:\\Users\\rensi\\Desktop\\Siddhartha Folder\\Fordham University\\Semester 1\\QFGB 8946 Financial Markets and Modeling\\Homework\\HW9\\combined_option_chain.csv"
df_combined.to_csv(combined_file_path, index=False)

df_tbill = pd.read_csv(r'C:\Users\rensi\Desktop\Siddhartha Folder\Fordham University\Semester 1\QFGB 8946 Financial Markets and Modeling\Homework\HW9\TBillQuotes_20231128.csv', header = None)

columns = ['CUSIP', 'Security Type', 'Coupon Rate', 'Maturity Date','Bid Price', 'Ask Price', 'Price', 'YTM' ]

df_tbill.columns = columns

today_date = pd.Timestamp('2023-11-28')
df_tbill['Days to Maturity'] = (pd.to_datetime(df_tbill['Maturity Date']) - today_date).dt.days

df_tbill['Mid Price'] = df_tbill[['Bid Price', 'Ask Price']].mean(axis=1)

df_tbill_cleaned = df_tbill.dropna(subset=['Mid Price', 'Days to Maturity'])

df_tbill_cleaned['YTM'] = (
    (100 - df_tbill_cleaned['Mid Price']) / df_tbill_cleaned['Mid Price']
) * (360 / df_tbill_cleaned['Days to Maturity'])

df_tbill_cleaned = df_tbill_cleaned.sort_values('Days to Maturity').reset_index(drop=True)

x_days = df_tbill_cleaned['Days to Maturity']
y_ytm = df_tbill_cleaned['YTM']
risk_free_curve = interp1d(x_days, y_ytm, kind='linear', fill_value='extrapolate')


def interpolate_interest_rate(dtm, tbill_data):
    """
    Interpolate the interest rate for a given day to maturity.

    Args:
        dtm (int): Days to maturity for which to interpolate the interest rate.
        tbill_data (pd.DataFrame): DataFrame containing treasury bill rates, 
                                   with columns "Days to Maturity" and "YTM".

    Returns:
        float: Interpolated interest rate (YTM) for the given dtm.
    """
    tbill_data = tbill_data.sort_values("Days to Maturity")
    
    x_days = tbill_data["Days to Maturity"]
    y_ytm = tbill_data["YTM"]
    
    risk_free_curve = interp1d(x_days, y_ytm, kind='linear', fill_value='extrapolate')
    
    return float(risk_free_curve(dtm))


x_days = df_tbill_cleaned['Days to Maturity']
y_ytm = df_tbill_cleaned['YTM']

plt.figure(figsize=(10, 6))
plt.plot(x_days, y_ytm, marker='o', linestyle='-', label='Yield Curve')
plt.title('Days to Maturity vs Yield (YTM)', fontsize=14)
plt.xlabel('Days to Maturity', fontsize=12)
plt.ylabel('Yield to Maturity (%)', fontsize=12)
plt.grid(True)
plt.legend()
plt.show()

updated_spot_price = 4549.9102  

import math

def forward_price(spot, div_yield, risk_free_rate, ttm):
    """
    Calculate the forward price.

    Args:
        spot (float): Current spot price.
        div_yield (float): Dividend yield as a decimal (e.g., 0.0156 for 1.56%).
        risk_free_rate (float): Risk-free rate as a decimal.
        ttm (float): Time to maturity (in years).

    Returns:
        float: Forward price.
    """
    forward = spot * math.exp((risk_free_rate - div_yield) * ttm)
    return forward



def calculate_vix(option_data, risk_free_rate):
    """
    Replicate the VIX calculation based on the CBOE VIX methodology.
    """
    minutes_1year = 525600  
    minutes_30_days = 43200  

    near_term = option_data[option_data['Term'] == 'Near']
    next_term = option_data[option_data['Term'] == 'Next']

    def calculate_variance(term_data, time_to_expiration):
        contributions = (
            term_data['Delta-K'] * 
            (term_data['Mid-Price'] / (term_data['Strike']**2))
        )
        sum_contributions = contributions.sum() 
        forward_price = term_data['Forward Price'].iloc[0]  
        first_strike_below_forward = term_data['Strike'].iloc[0]  
        forward_diff = (forward_price / first_strike_below_forward - 1) / time_to_expiration
        variance = (2 / time_to_expiration) * (sum_contributions - forward_diff)
        return variance

    variance_near = calculate_variance(
        near_term, time_to_expiration=near_term['Time to Expiration'].iloc[0]
    )
    variance_next = calculate_variance(
        next_term, time_to_expiration=next_term['Time to Expiration'].iloc[0]
    )

    t1 = near_term['Time to Expiration'].iloc[0]
    t2 = next_term['Time to Expiration'].iloc[0]
    variance_30 = (
        variance_near * (t2 - minutes_30_days) / (t2 - t1) +
        variance_next * (minutes_30_days - t1) / (t2 - t1)
    )

    vix = 100 * np.sqrt(variance_30 * minutes_1year / minutes_30_days)
    return vix

VIX_real = yf.download('^VIX', start='2023-11-28', end='2023-12-29')['Adj Close']
VIX_real.plot(figsize=(10, 6), grid=True)
plt.title('VIX Adj Closing Prices')
plt.xlabel('Date')
plt.ylabel('Adj Closing Price')
plt.show()


