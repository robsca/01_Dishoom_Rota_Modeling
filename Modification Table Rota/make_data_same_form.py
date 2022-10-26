import pandas as pd
import streamlit as st

# data 
df_0 = pd.read_excel('data.xlsx')

# data correction
df_1 = pd.read_excel('data_correct_form.xlsx')



# function to correct data
@st.cache
def correct_dataframe(df):
    features = ['Location', 'Division', 'JobTitle', 'EmployeeName', 'EmpNo', 'ShiftDate', 'Start1', 'Stop1', 'Start2', 'Stop2', 'NoOfHours', 'BreakMinutes',
                 'ShiftCode', 'EmploymentType', 'EmploymentStatus', 'TerminationDate', 'DateFrom', 'DateTo', 'Role', 'Start Time ', 'Finish Time', 'Day']
    correct_features = ['Home', 'Division', 'Job Title', 'Employee Number', 'First Name', 'Surname', 'Shift date', 'Day of the week', 'Paid/Actual StartTime1', 'Paid/Actual StopTime1']
    # first row is the header
    columns = df.iloc[0][:len(features)]
    # keep only that number of columns in df
    df = df.iloc[1:, :len(features)]
    df.columns = columns
    # rename column Location to Home
    df.rename(columns={'Location': 'Home'}, inplace=True)
    # rename start1 and stop1 to start and stop
    df.rename(columns={'Start1': 'Paid/Actual StartTime1', 'Stop1': 'Paid/Actual StopTime1'}, inplace=True)
    # rename ShiftDate to Shift date
    df.rename(columns={'ShiftDate': 'Shift date'}, inplace=True)
    # rename JobTitle to Job Title
    df.rename(columns={'JobTitle': 'Job Title'}, inplace=True)
    # renam Day to Day of the week
    df.rename(columns={'Day': 'Day of the week'}, inplace=True)
    # keep only3 letters of Day of the week
    df['Day of the week'] = df['Day of the week'].str[:3]
    # rename EmployeeName to First Name and Surname
    df['First Name'] = df['EmployeeName'].str.split(' ').str[0]
    df['Surname'] = df['EmployeeName'].str.split(' ').str[1]
    # rename EmpNo to Employee Number
    df.rename(columns={'EmpNo': 'Employee Number'}, inplace=True)
    df = df[correct_features]
    # delete naan
    df = df.dropna()
    # translate column types int to numpy.int64
    df = df.astype({'Employee Number': 'int64'})
    df = df.astype({'Paid/Actual StartTime1': 'int64'})
    df = df.astype({'Paid/Actual StopTime1': 'int64'})
    # translate shift date to datetime
    df['Shift date'] = pd.to_datetime(df['Shift date'])
    return df

correct_features = ['Home', 'Division', 'Job Title', 'Employee Number', 'First Name', 'Surname', 'Shift date', 'Day of the week', 'Paid/Actual StartTime1', 'Paid/Actual StopTime1']

df_0 = correct_dataframe(df_0)
df_1 = df_1[correct_features]
df_1 = df_1.dropna()

st.write(df_0)
# print all columns type
st.write(df_1)


#save data
df_0.to_excel('August_Actual_Hours.xlsx', index=False)




