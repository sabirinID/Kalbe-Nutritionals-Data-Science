# -*- coding: utf-8 -*-
"""Data_Modeling_ARIMA_Forecasting.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1c1xtorUzfXif9Cn3JocbK_mFdMM-sNOe

# Supervised Learning: Regression (Time Series)
---

# ***Autoregressive Integrated Moving Average* (ARIMA) Model for Time Series Forecasting**

Referensi:
- https://www.ibm.com/topics/supervised-learning
- https://www.statsmodels.org/dev/generated/statsmodels.tsa.arima.model.ARIMA.html
- https://www.investopedia.com/terms/a/autoregressive-integrated-moving-average-arima.asp

## Import Library
"""

# Data manipulation
import numpy as np
import pandas as pd
import datetime as dt

# Data visualization
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns

# Machine Learning
import sklearn as sk
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Evaluation Metrics
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error

# Iterator
import itertools

# Ignore warning
import warnings
warnings.filterwarnings('ignore')

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

print('NumPy', np.__version__)
print('Pandas', pd.__version__)
print('Matplotlib', mpl.__version__)
print('Seaborn', sns.__version__)
print('Scikit-Learn', sk.__version__)

"""## Read Dataset"""

from google.colab import drive
drive.mount('/content/drive')

# Read the data files
data = pd.read_csv('/content/drive/MyDrive/Kalbe Farma/Cleaned_Data.csv')

data.sample(5)

data.shape

data.info()

data.columns

data_regression = data[['Date', 'Quantity']].copy()

# Convert 'Date'
# data_regression['Date'] = pd.to_datetime(data_regression['Date'])

# Group by 'Date' and .sum() the 'Quantity' column
data_regression = data_regression.groupby('Date')['Quantity'].sum()

# Rename the columns for clarity
data_regression = data_regression.rename('TotalQuantity')

data_regression.head()

data_regression.name, data_regression.shape

from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

plt.rcParams.update({'figure.figsize':(16, 9)})

# Original Series
fig, axes = plt.subplots(3, 2, sharex=True)
axes[0, 0].plot(data_regression); axes[0, 0].set_title('Original Series')
plot_acf(data_regression, ax=axes[0, 1])

# 1st Differencing
axes[1, 0].plot(data_regression.diff()); axes[1, 0].set_title('1st Order Differencing')
plot_acf(data_regression.diff().dropna(), ax=axes[1, 1])

# 2nd Differencing
axes[2, 0].plot(data_regression.diff().diff()); axes[2, 0].set_title('2nd Order Differencing')
plot_acf(data_regression.diff().diff().dropna(), ax=axes[2, 1])

plt.show()

"""### Patterns in a Time Series"""

# Convert 'data_regression' Series to DataFrame
data_reg = data_regression.to_frame()
data_reg.head()

# Transform data
data_log = np.log(data_reg)
data_log.head()

"""- Log-transformasi dapat digunakan untuk mengatasi ketidakstabilan variansi (heteroskedastisitas) dan memastikan data yang memiliki sifat eksponensial dapat dimodelkan dengan lebih baik."""

plt.figure(figsize=(16, 9))

# First Subplot - data_reg
plt.subplot(2, 1, 1)
plt.plot(data_reg)
plt.title('Original Series')
plt.xlabel('Date')
plt.ylabel('Total Quantity')

# Second Subplot - data_log
plt.subplot(2, 1, 2)
plt.plot(data_log)
plt.title('Log Transformed Series')
plt.xlabel('Date')
plt.ylabel('Log Total Quantity')

plt.tight_layout(pad=2)
plt.show()

"""### Decomposition of a Time Series"""

from statsmodels.tsa.seasonal import seasonal_decompose
from dateutil.parser import parse

# Multiplicative Decomposition
multiplicative_decomposition = seasonal_decompose(data_reg, model='multiplicative', period=30)

# Additive Decomposition
additive_decomposition = seasonal_decompose(data_reg, model='additive', period=30)

# Plot
plt.figure(figsize=(16, 12))
multiplicative_decomposition.plot().suptitle('Multiplicative Decomposition', fontsize=16)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

additive_decomposition.plot().suptitle('Additive Decomposition', fontsize=16)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

plt.show()

"""### Stationary and Non-Stationary Time Series"""

from statsmodels.tsa.stattools import adfuller

# Function to perform Augmented Dickey-Fuller Test
def adf_test(timeseries):
    result = adfuller(timeseries, autolag='AIC')
    print(f'ADF Statistic: {result[0]}')
    print(f'p-value: {result[1]}')
    print('Critical Values:')
    for key, value in result[4].items():
        print(f'   {key}: {value}')

# The time series data
time_series_data = data_reg

# Plot
plt.figure(figsize=(16, 6))
plt.plot(time_series_data)
plt.title('Time Series Data')
plt.xlabel('Date')
plt.ylabel('Total Quantity')
plt.show()

# Perform Augmented Dickey-Fuller Test
print('Augmented Dickey-Fuller Test:')
adf_test(time_series_data)

"""🔎 Observasi
- Berdasarkan hasil Augmented Dickey-Fuller Test, menunjukkan bahwa secara keseluruhan, time series tersebut dapat dianggap sebagai stationary, karena
  - *ADF statistic* lebih kecil daripada nilai kritis pada tingkat signifikansi 1%, 5%, dan 10%.
  - P-value kurang dari tingkat signifikansi 0,05.

### Detrend a Time Series
"""

from scipy import signal

# Detrend
detrended = signal.detrend(data_reg.values)

# Plot
plt.figure(figsize=(16, 6))
plt.plot(detrended)
plt.title('Total Quantity Detrended by Subtracting the Line of Best Fit', fontsize=16)

plt.show()

from statsmodels.tsa.seasonal import seasonal_decompose

result_multi = seasonal_decompose(data_reg['TotalQuantity'], model='multiplicative', period=30)
# Detrend
detrended = data_reg['TotalQuantity'].values - result_multi.trend

# Plot
plt.figure(figsize=(16, 6))
plt.plot(detrended)
plt.title('Total Quantity Detrended by Subtracting the Trend Component', fontsize=16)

plt.show()

"""### Deseasonalize a Time Series"""

result_multi = seasonal_decompose(data_reg['TotalQuantity'], model='multiplicative', period=30)
# Deseasonalize
deseasonalized = data_reg['TotalQuantity'].values / result_multi.seasonal

# Plot
plt.figure(figsize=(16, 6))
plt.plot(deseasonalized)
plt.title('Total Quantity Deseasonalized', fontsize=16)

plt.show()

"""### Autocorrelation and Partial Autocorrelation Functions"""

from statsmodels.tsa.stattools import acf, pacf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# Plot
fig, axes = plt.subplots(1, 2, figsize=(16, 3))

# Autocorrelation
plot_acf(data_reg['TotalQuantity'].tolist(), lags=10, ax=axes[0])

# Partial Autocorrelation
plot_pacf(data_reg['TotalQuantity'].tolist(), lags=10, ax=axes[1])

"""## Modeling and Evaluation"""

series = data_reg
# series = data_log

# Split data into train and test sets
train = series.iloc[:-31]
test = series.iloc[-31:]

train.shape, test.shape

"""### Parameter Analysis for the ARIMA Model

#### Auto-ARIMA
"""

pip install pmdarima

import pmdarima as pm

auto_arima = pm.auto_arima(series,
                           start_p=1, start_q=1, # Starting values for p and q
                           test='adf',           # Use adftest to find optimal 'd'
                           max_p=3, max_q=3,     # Maximum values for p and q
                           m=12,                 # Frequency of the time series
                           d=None,               # Let model determine 'd'
                           D=0,                  # Seasonal order of differencing
                           seasonal=False,       # No Seasonality
                           trace=True,
                           error_action='ignore',
                           suppress_warnings=True,
                           stepwise=True)

print(auto_arima.summary())

auto_arima

"""🔎 Observasi
- Berdasarkan hasil SARIMAX, menunjukkan bahwa:
  - Model SARIMAX dengan nilai AIC sebesar 3094.267 dan BIC sebesar 3102.067 dipilih sebagai model terbaik, yaitu **ARIMA(0,0,0)(0,0,0)[0] intercept**.
  - Makin rendah nilai AIC dan BIC, makin baik modelnya.

##### Interpret the Residual Plots in ARIMA Model
"""

auto_arima.plot_diagnostics(figsize=(16, 9))
plt.show()

"""#### Manual ARIMA

##### Parameter Estimation
"""

def manual_arima(p, d, q):
    # Create and fit the ARIMA model
    model = ARIMA(train, order=(p, d, q))
    model_fit = model.fit()

    # Make predictions on the test set
    forecast = model_fit.forecast(steps=len(test))

    # Calculate evaluation metrics
    mae = mean_absolute_error(test, forecast)
    mape = mean_absolute_percentage_error(test, forecast)
    rmse = np.sqrt(mean_squared_error(test, forecast))

    return mae, mape, rmse

def optimal_arima(data, p_values, d_values, q_values):
    best_mae = float('inf')
    best_params = None

    for p, d, q in itertools.product(p_values, d_values, q_values):
        mae, _, _ = manual_arima(p, d, q)

        if mae < best_mae:
            best_mae = mae
            best_params = (p, d, q)

    return best_params, best_mae

# Define the ranges of p, d, and q values for iteration
p_values = range(0, 5) # Order of Autoregression
d_values = range(0, 5) # Order of Differencing
q_values = range(0, 5) # Order of Moving Average

# Find the optimal ARIMA parameters
optimal_params, optimal_mae = optimal_arima(data_reg, p_values, d_values, q_values)

print('Optimal ARIMA Parameters:')
print(f'p={optimal_params[0]}, d={optimal_params[1]}, q={optimal_params[2]}')

combi = list(itertools.product(p_values, d_values, q_values))

param = []
mae_score = []
mape_score = []
rmse_score = []

for i in combi:
    param.append(i)
    score = manual_arima(*i)
    mae_score.append(score[0])
    mape_score.append(score[1])
    rmse_score.append(score[2])

parameter = pd.DataFrame({'Parameters': param,
                          'MAE': mae_score,
                          'MAPE': mape_score,
                          'RMSE': rmse_score})
parameter.sort_values(by='MAE').reset_index(drop=True).head(1)

# Evaluation metrics for ARIMA(0, 2, 1)
mae, mape, rmse = manual_arima(0, 2, 1)

print(f'MAE : {round(mae, 3)}')
print(f'MAPE: {round(mape, 3)}')
print(f'RMSE: {round(rmse, 3)}')

# Split data into training and test sets
train_size = int(len(data_reg) * 0.9175)
train_data, test_data = data_reg[:train_size], data_reg[train_size:]
train_data.shape, test_data.shape

# Fit ARIMA(0, 2, 1)
model_manual = ARIMA(train, order=(0, 2, 1))
model_manual_fit = model_manual.fit()

from statsmodels.tsa.arima.model import ARIMA
from pmdarima.arima import auto_arima

# Fit Manual ARIMA model (with p=0, d=3, q=4) on the training data
model_manual = ARIMA(train_data, order=(0, 3, 4))
model_manual = model_manual.fit()
# Forecast using the manual ARIMA model on the test data
forecast_manual = model_manual_fit.forecast(steps=len(test_data))

# Fit Auto-ARIMA model on the training data
model_auto = auto_arima(train_data,
                        start_p=1, start_q=1,
                        max_p=3, max_q=3,
                        m=12,
                        d=None, D=0,
                        seasonal=False)
# Forecast using the Auto-ARIMA model on the test data
forecast_auto = model_auto.predict(n_periods=len(test_data))

# Plot the forecasts
plt.figure(figsize=(16, 9))

plt.plot(data_reg, label='Original Data', color='tab:blue')
plt.plot(test_data.index, forecast_manual, label='Forecast (Manual ARIMA)', color='tab:orange')
plt.plot(test_data.index, forecast_auto, label='Forecast (Auto-ARIMA)', color='tab:green')
plt.title('Quantity Sold Forecasting')
plt.xlabel('Date')
plt.ylabel('Total Quantity')
plt.legend()

plt.show()

# Plot the forecasts
plt.figure(figsize=(16, 9))

df_plot = data_reg.iloc[train_size:]
df_plot['Forecast (Manual ARIMA)'] = [None] * (len(df_plot) - len(forecast_manual)) + list(forecast_manual)
df_plot['Forecast (Auto-ARIMA)'] = [None] * (len(df_plot) - len(forecast_auto)) + list(forecast_auto)

plt.plot(df_plot)
plt.title('Quantity Sold Forecasting')
plt.xlabel('Date')
plt.ylabel('Total Quantity')

plt.show()

# Auto-ARIMA
mae_auto = mean_absolute_error(test, forecast_auto)
mape_auto = mean_absolute_percentage_error(test, forecast_auto)
rmse_auto = np.sqrt(mean_squared_error(test, forecast_auto))

# Manual ARIMA
mae_manual = mean_absolute_error(test, forecast_manual)
mape_manual = mean_absolute_percentage_error(test, forecast_manual)
rmse_manual = np.sqrt(mean_squared_error(test, forecast_manual))

# Print results
print('Auto-ARIMA  :')
print(f'MAE : {round(mae_auto, 3)}')
print(f'MAPE: {round(mape_auto, 3)}')
print(f'RMSE: {round(rmse_auto, 3)}\n')

print('Manual ARIMA:')
print(f'MAE : {round(mae_manual, 3)}')
print(f'MAPE: {round(mape_manual, 3)}')
print(f'RMSE: {round(rmse_manual, 3)}')

"""🔎 Observasi
- Berdasarkan hasil evaluasi, dapat dilihat bahwa model Manual ARIMA memiliki nilai evaluasi yang jauh lebih baik dibandingkan dengan model Auto-ARIMA.
  - MAE, MAPE, dan RMSE dari model Manual ARIMA jauh lebih kecil, menunjukkan performa yang lebih baik dalam melakukan prediksi.

### Forecasting Overall Quantity
"""

# Apply model
model = ARIMA(data_log, order=(0, 2, 1))
model_fit = model.fit()
forecast = model_fit.forecast(steps=30)

# # Re-transform data
# data_reg = np.exp(data_log)
# forecast = np.exp(forecast)

# Plot the forecast
plt.figure(figsize=(16, 9))

plt.plot(data_reg, label='Original Data', color='tab:blue')
plt.plot(test_data.index, forecast_manual, label='Forecast', color='tab:orange')
plt.title('Quantity Sold Forecasting')
plt.xlabel('Date')
plt.ylabel('Total Quantity')
plt.legend()

plt.show()

forecast_manual.mean().round(0)

"""🔎 Insight
- Berdasarkan hasil prediksi, dapat disimpulkan bahwa jumlah penjualan bulan depan diperkirakan sekitar 45 buah/hari.

### Forecasting Each Product
"""

data.columns

# Forecast for next 30 days for each product
list_p = data['ProductName'].unique()

df_p = pd.DataFrame({'Date': pd.date_range(start='2023-01-01',
                                           end='2023-01-30')})
df_p = df_p.set_index('Date')
for i in list_p:
    df = data[['Date','ProductName','Quantity']]
    df = data[data['ProductName'] == i]
    df = df.groupby('Date')[['Quantity']].sum()
    df = df.reset_index()

    df['Date'] = pd.to_datetime(df['Date'])

    df_t = pd.DataFrame({'Date': pd.date_range(start='2022-01-01',
                                               end='2022-12-31')})
    df_t = df_t.merge(df,
                      how='left',
                      on='Date')
    df_t = df_t.fillna(0)
    df_t = df_t.set_index('Date')

    model_p = ARIMA(df_t, order=(0, 2, 1))
    model_p_fit = model_p.fit()
    forecast_p = model_p_fit.forecast(steps=30)
    df_p[i] = forecast_p.values

df_p.head()

# Plot the forecast
plt.figure(figsize=(16, 9))
plt.plot(df_p)
plt.legend(df_p.columns, loc='center left', bbox_to_anchor=(1, 0.5))
plt.title('Products Quantity Sold Forecasting')
plt.show()

# Products quantity forecast
round(df_p.describe().T['mean'], 0).astype(int)

"""🔎 Insight
- Dengan menggunakan data prediksi produk di atas, kita dapat memperoleh estimasi jumlah rata-rata produk yang terjual setiap harinya.
"""