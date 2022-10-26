import pandas as pd
import streamlit as st
import numpy as np

# read excel file
df_employees = pd.read_excel('August_Actual_Hours.xlsx')
df_guests = pd.read_csv('Aloha_Sales_Data_Export_2019.csv')


st.write(df_guests)
dates = df_employees['Shift date'].unique()
# to datetime pandas
dates = pd.to_datetime(dates)
# only date
dates = dates.date


# tranlate date to to datetime
df_guests['Date'] = pd.to_datetime(df_guests['Date'])
# keep only the date
df_guests['Date'] = df_guests['Date'].dt.date

other_dates = df_guests['Date'].unique()

df_guests = df_guests[df_guests['Date'].isin(dates)]

st.write(df_guests)

# save to csv
df_guests.to_csv('Aloha_Sales_Data_Export_2019_August.csv', index=False)
