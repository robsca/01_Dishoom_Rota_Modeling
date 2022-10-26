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

        # 4. Create a graph to have all restaurant data under control
        dt = data_employee.copy()
        # add ratio column
        dt['ratio'] = dt['Guest_Count']/dt['Employees_Count']
        day_parts = ['Breakfast','Lunch','Afternoon', 'Dinner']
        # get an average of the ratio per day part for every store
        dt = dt.groupby(['Store_Name','Time_of_day'])['ratio'].mean().reset_index()
        # keep only day parts that are in the list
        dt = dt[dt['Time_of_day'].isin(day_parts)] 
        # pivot the table to have the day parts as columns
        dt = dt.pivot_table(index=['Store_Name'], columns='Time_of_day', values='ratio').reset_index()

        # create a graph
        import plotly.express as px
        fig_all_restaurant_day_part = px.bar(dt, x='Store_Name', y=day_parts, barmode='group')
        fig_all_restaurant_day_part.update_layout(
            title='Average ratio of Guests vs Employees per day part',
            xaxis_title='Store Name',
            yaxis_title='Ratio',
            legend_title='Day Part',
        )



        # 4. Select restaurant
        # create a list of restaurants
        restaurants = data_employee['Store_Name'].unique()
        # add all restaurants to the list
        import numpy as np
        restaurants = np.append(restaurants, 'All Restaurants')

        selected = st.sidebar.selectbox('Select a restaurant', restaurants)
        if selected == 'All Restaurants':
            pass
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
            title=f"Guests vs Employees - Averages",
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
        #with st.expander('Heatmap_data'):
        #    st.write(data_employees_heat)
        
        # 7. Plot heatmap
        from helper_functions import plot_heatmap
        fig = plot_heatmap(data_employees_heat, 'Guests vs Employees', show = False, round=False)

        
        # divide in day parts
        data = data_employee.copy()
        # add ratio column
        data['ratio'] = data['Guest_Count'] / data['Employees_Count']
        day_parts = data['Time_of_day'].unique()
        # calculate average ratio in every day part
        frame = []
        for day_part in day_parts:
            data_day_part = data[data['Time_of_day'] == day_part]
            # calculate average ratio
            average_ratio = data_day_part['ratio'].mean()
            # add to list
            frame.append(average_ratio)
        # create df
        data_day_parts = pd.DataFrame(frame, index=day_parts, columns=['ratio'])

        # plot as barchart
        fig_day_part = go.Figure()
        fig_day_part.add_trace(go.Bar(x=data_day_parts.index, y=data_day_parts['ratio'], name='Guests vs Employees'))
        fig_day_part.update_layout(
            title="Guests vs Employees",
            xaxis_title="Day Part",
            yaxis_title="Guests / Employees",
            legend_title="Legend Title",
            font=dict(
                family="Courier New, monospace",
                color="#7f7f7f"
            )   
        )

        
        # 8. Show all graphs
        st.plotly_chart(fig_all_restaurant_day_part, use_container_width=True)

        st.plotly_chart(fig_timeries, use_container_width=True)
        
        st.write('---')
        with st.expander('Averages of month'):
            c1,c2 = st.columns(2)
            c1.plotly_chart(fig_day_part)
            c2.plotly_chart(fig)

        st.write("---")

        with st.expander('Results for selected Week'):
            # week by week
            # 1. Create a list of weeks
            weeks = data_employee.index.week.unique()
            # 2. Select a week
            selected_week = st.sidebar.selectbox('Select a week', weeks)
            # 3. Filter by week
            data_employee_week = data_employee[data_employee.index.week == selected_week]
            # 4. Plot
            fig_timeries_week = go.Figure()
            fig_timeries_week.add_trace(go.Scatter(x=data_employee_week.index, y=data_employee_week['Guest_Count'], name='Guest Count', fill='tozeroy'))
            fig_timeries_week.add_trace(go.Scatter(x=data_employee_week.index, y=data_employee_week['Employees_Count'], name='Employees Count', fill='tozeroy'))
            fig_timeries_week.update_layout(
                title="Guest Count vs Employees",
                xaxis_title="Date",
                yaxis_title="Count",
                legend_title="Legend Title",
                font=dict(
                    family="Courier New, monospace",
                    color="#7f7f7f"
                )
            )
            st.plotly_chart(fig_timeries_week, use_container_width=True)

            # create heatmap for selected week
            # Filter out hours < 9 and > 23
            data_employee_week = data_employee_week[(data_employee_week.index.hour >= 9) & (data_employee_week.index.hour < 23)]
            # group by day making average of the guests and employees
            days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            frame = []
            for day in days_of_week:
                # filter by day
                data_employee_day = data_employee_week[data_employee_week['Day_of_week'] == day]
                data_employee_day = data_employee_day.groupby(data_employee_week['Hour']).mean()
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
            # 7. Plot heatmap
            from helper_functions import plot_heatmap
            fig = plot_heatmap(data_employees_heat, 'Guests vs Employees', show = False, round=False)

            # divide in day parts
            data = data_employee_week.copy()
            # add ratio column
            data['ratio'] = data['Guest_Count'] / data['Employees_Count']
            day_parts = data['Time_of_day'].unique()
            # calculate average ratio in every day part
            frame = []
            for day_part in day_parts:
                data_day_part = data[data['Time_of_day'] == day_part]
                # calculate average ratio
                average_ratio = data_day_part['ratio'].mean()
                # add to list
                frame.append(average_ratio)
            # create df
            data_day_parts = pd.DataFrame(frame, index=day_parts, columns=['ratio'])

            # plot as barchart
            fig_day_part = go.Figure()
            fig_day_part.add_trace(go.Bar(x=data_day_parts.index, y=data_day_parts['ratio'], name='Guests vs Employees'))
            fig_day_part.update_layout(
                title="Guests vs Employees",
                xaxis_title="Day Part",
                yaxis_title="Guests / Employees",
                legend_title="Legend Title",
                font=dict(
                    family="Courier New, monospace",
                    color="#7f7f7f" 
                )
            )
            c1,c2 = st.columns(2)
            c1.plotly_chart(fig_day_part)
            c2.plotly_chart(fig)
