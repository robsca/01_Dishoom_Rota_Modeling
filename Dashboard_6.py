import streamlit as st
st.set_page_config(layout="wide")

import pandas as pd
from classes import Analysis_EMP

'''
try:
    # open csv file
    forecast_table = pd.read_csv('data/forecast_table.csv')
    actual_table = pd.read_csv('data/actual_table.csv')
except:
'''
# reading the files
# 2019
df_1 = 'data/ActualHoursvRotaHours_2019_8_Aug_RS.csv'
df_2 = 'data/ActualHoursvRotaHours_2019_9_Sep_RS.csv'
df_3 = 'data/ActualHoursvRotaHours_2019_10_Oct_RS.csv'
# 2022
df_4 = 'data/ActualHoursvRotaHours_2022_Aug_Dec_RS.csv'
# open csv files
df_1_2019 = pd.read_csv(df_1)
df_2_2019 = pd.read_csv(df_2)
df_3_2019 = pd.read_csv(df_3)
df_2022 = pd.read_csv(df_4)

# merge the 3 dataframes from 2019
df_2019 = pd.concat([df_1_2019, df_2_2019, df_3_2019], axis=0)

# create a new object
DATA_2019 = Analysis_EMP(df_2019)

actual_table, forecast_table = DATA_2019.transform()
timeseries = DATA_2019.get_timeseries_total()

# show results 
st.write(timeseries)

# plot the results
import plotly.express as px
fig = px.line(timeseries, x='date', y='total_workers', title='Total workers in the warehouse')
fig.add_scatter(x=timeseries['date'], y=timeseries['total_workers_actual'], name='Total workers in the warehouse (actual)')
st.plotly_chart(fig)