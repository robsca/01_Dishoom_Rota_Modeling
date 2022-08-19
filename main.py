import pandas as pd
import streamlit as st
import plotly.graph_objs as go

def actual_hours(path, restaurant, start_date, end_date):
    # open xlsx file
    data = pd.read_excel(path)
    # consider only day and month
    start_date = start_date.split("-")[:2]
    end_date = end_date.split("-")[:2]


    # translate to date format
    #st.write(start_date, end_date)
    # filter data by restaurant and date
    restaurant_name = restaurant[0].split("-")[1].strip(" ")
    st.subheader(restaurant_name)
    # delete white spaces from Home columns
    data['Home'] = data['Home'].apply(lambda x: x.strip(" "))
    # reorganize datetime format in columns
    data['Shift date'] = pd.to_datetime(data['Shift date'])
    data['Shift date'] = data['Shift date'].dt.strftime('%m-%d-%Y')
    # filter data by restaurant and date
    data = data[(data['Home'] == restaurant_name)]
    # Since it's only a month I can use the day number to check time period
    start_date = int(start_date[1])
    end_date = int(end_date[1])
    # Modify shift date to be the same format as the start and end time values
    data['Shift date'] = data['Shift date'].apply(lambda x: int(x.split("-")[1]))
    # keep only data between start_date and end_date
    data = data[(data['Shift date'] >= start_date) & (data['Shift date'] <= end_date)]
    # modify Paid Actual
    data['Paid/Actual StartTime1'] = data['Paid/Actual StartTime1'].apply(lambda x: str(x)[:-2])
    # drop data with no start time
    data = data[data['Paid/Actual StartTime1'] != ""]

    # Modify Paid/ActualEndTIME keeping only hour as integers
    # Necessity of a for loop?
    # sum 24 for easier plotting
    for i in range(len(data)):
        # create new column with end time
        forecast_start = data['Rota/Forecast StartTime1'].iloc[i]
        forecast_stop = data['Rota/Forecast StopTime1'].iloc[i]
        actual_stop = data['Paid/Actual StopTime1'].iloc[i]
        if len(str(actual_stop)) == 4:
            stop = str(actual_stop)[:-2]
        elif str(actual_stop) == "0":
            stop = str(24)
        else:
            if len(str(actual_stop)) == 3:
                stop = str(int(str(forecast_stop)[0]) + 24)
        data['Paid/Actual StopTime1'].iloc[i] = stop

    # create a new column merging the First Name and Surname
    data['Name'] = data['First Name'] + " " + data['Surname']

   
    # get unique index
    unique_index = data['Shift date'].unique()
    #st.write(unique_index)
    # sort index
    unique_index = sorted(unique_index)
    # Separate in list day by day
    separated_data = []
    for i in range(len(unique_index)):
        separated_data.append(data[data['Shift date'] == unique_index[i]])
    

    hours_all_day = []
    for i, day in enumerate(separated_data):
        features = ['Shift date', 'Paid/Actual StartTime1', 'Paid/Actual StopTime1', 'Division', 'Name']
        day = day[features]
        starts = day['Paid/Actual StartTime1']
        stops = day['Paid/Actual StopTime1']
        roles = day['Division']
        # calculate hours for each day
        day_hours = []
        for start, stop, role in zip(starts, stops, roles):
            hour_ = [i for i in range(int(start), int(stop))]
            roles_ = [hour_, role]
            day_hours.extend(hour_)

        # get unique values
        unique_hours = list(set(day_hours))
        # count how many times each value appears
        count_hours = pd.DataFrame([[i, day_hours.count(i)] for i in unique_hours], columns=['Hour', 'Count'])
        
        hours_all_day.append(count_hours)
        '''
        with st.expander(f'{i}'):
            st.write(day)
            st.write(count_hours)
            fig = go.Figure()
            fig.add_trace(go.Scatter
                            (x=count_hours['Hour'],
                            y=count_hours['Count'],
                            mode='lines+markers'))
            st.plotly_chart(fig)
        '''
    # return hours_all_day
    return hours_all_day

            


    
    # filter data by date
    # show data
    with st.expander("Data"):
        st.write(data)

