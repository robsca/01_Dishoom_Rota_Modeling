'''
author: Roberto Scalas
date: 2022-09-23
---
This Dashboard take data from Fourth and Aloha (ideally of the same time period) and returns a downloadable csv file.
The csv file contains the following columns:
    - Date_time(index)
    - Store_Name
    - Guest_Count
    - Employee_Count
    - Day_of_Week
    - Hour
    - Time_of_day

A line chart is generated showing the Guest_Count and Employee_Count for the selected store.
A heatmap is also generated to show the ratio of Guests vs Employees per hour.
---
To start the dashboard, run the following command:
    $ streamlit run Dashboard_3.py
'''
from helper_functions import *

def one():
    import streamlit as st
    import pandas as pd

    # 1. Set Title
    st.sidebar.title('Rota Modeling')
    # 2. Import data for processing
    with st.sidebar.expander('Import data'):
        uploaded_file_1 = st.file_uploader("Select Employees Data", key='1')
        uploaded_file_2 = st.file_uploader("Select Covers Data", key='2')

    if uploaded_file_1 is not None and uploaded_file_2 is not None:
        data_employee = create_final_timeseries(uploaded_file_1,uploaded_file_2)
        # 3. Create file for download
        with st.expander('guestsVSlabour - Data'):
            st.write(data_employee)
            @st.cache # cache the function
            def convert_df(df):
                # IMPORTANT: Cache the conversion to prevent computation on every rerun
                return df.to_csv().encode('utf-8')
            
            csv = convert_df(data_employee)
            # get start_date
            start_date = data_employee.index.min().strftime('%Y-%m-%d')
            # get end_date
            end_date = data_employee.index.max().strftime('%Y-%m-%d')
            name_ = f'guestsVSlabour_{start_date}_{end_date}'
            name = st.text_input('File name', name_)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name=f'{name}.csv',
                mime='text/csv',
            )

        # 4. Select restauratn
        # create a list of restaurants
        restaurants = data_employee['Store_Name'].unique()
        # add all restaurants to the list
        import numpy as np
        restaurants = np.append(restaurants, 'All Restaurants')

        selected = st.sidebar.selectbox('Select a restaurant', restaurants)
        if selected == 'All Restaurants':
            # drop the column 'Store_Name'
            data_employee = data_employee.drop(columns=['Store_Name'])
            # group by hour
            data_employee = data_employee.groupby(data_employee.index).sum()
            # create a new column 'Hours'
            data_employee['Hour'] = data_employee.index.hour
            # add a column 'Day'
            data_employee['Day_of_week'] = data_employee.index.day_name()
            #st.write(data_employee)
            st.subheader('Employees Data - All Restaurants')
        # get the df for that restaurant
        else:
            data_employee = data_employee[data_employee['Store_Name'] == selected]
            st.subheader(f'Employees Data - {selected}')
            #st.write(data_employee)
        # ----------------- #
        
        # 5. Plot totals for the selected restaurant
        import plotly.graph_objects as go
        fig_timeries = go.Figure()
        fig_timeries.add_trace(go.Scatter(x=data_employee.index, y=data_employee['Guest_Count'], name='Guest Count', fill='tozeroy'))
        fig_timeries.add_trace(go.Scatter(x=data_employee.index, y=data_employee['Employees_Count'], name='Employees Count', fill='tozeroy'))
        fig_timeries.update_layout(
            title="Guest Count vs Employees",
            xaxis_title="Date",
            yaxis_title="Count",
            legend_title="Legend Title",
            font=dict(
                family="Courier New, monospace",
                color="#7f7f7f"
            )
        )

        # ----------------- #
        # 6. Create Heatmap 
        
        # Filter out hours < 9 and > 23
        data_employee = data_employee[(data_employee.index.hour >= 9) & (data_employee.index.hour < 23)]
        # group by day making average of the guests and employees
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        frame = []
        for day in days_of_week:
            # filter by day
            data_employee_day = data_employee[data_employee['Day_of_week'] == day]
            data_employee_day = data_employee_day.groupby(data_employee['Hour']).mean()
            # modify guest count as ratio
            data_employee_day['Guest_Count'] = data_employee_day['Guest_Count'] / data_employee_day['Employees_Count']        
            # drop hour column
            data_employee_day = data_employee_day.drop(columns=['Hour'])
            # drop employees count
            data_employee_day = data_employee_day.drop(columns=['Employees_Count'])
            # rename guest count
            data_employee_day = data_employee_day.rename(columns={'Guest_Count': day})
            transposed_day = data_employee_day.T
            # add to list
            frame.append(transposed_day)
        # concat all days
        data_employees_heat = pd.concat(frame)
        with st.expander('Heatmap_data'):
            st.write(data_employees_heat)
        
        # 7. Plot heatmap
        from helper_functions import plot_heatmap
        fig = plot_heatmap(data_employees_heat, 'Guests vs Employees', show = False, round=False)

        # 8. Show all graphs
        st.plotly_chart(fig_timeries, use_container_width=True)
        st.plotly_chart(fig, use_container_width=True)

