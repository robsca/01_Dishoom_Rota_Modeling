import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
from functions import *
from helper_functions import *

# title
st.sidebar.title('Rota Modeling')

with st.sidebar.expander('Import data'):
    uploaded_file_1 = st.file_uploader("Select Employees Data")
    uploaded_file_2 = st.file_uploader("Select Covers Data")

if uploaded_file_1 is not None and uploaded_file_2 is not None:

    def create_final_timeseries(uploaded_file_1,uploaded_file_2):
        data_employee = file_handler(uploaded_file_1)
        data_covers = file_handler(uploaded_file_2)
        # ----------------- #
        # Covers - DONE
        data_covers = create_timeries_covers(data_covers)
        
        # ----------------- #
        # Employees - DOne
        # clean from whitespace storename
        data_employee['Home'] = data_employee.apply(lambda x: x['Home'].strip(), axis=1)
        data_covers['Store_Name'] = data_covers.apply(lambda x: x['Store_Name'].strip(), axis=1)

        # get unique restaurants
        restaurants_from_covers_df = data_covers['Store_Name'].unique()
        restaurants_from_employee_df = data_employee['Home'].unique()
        # find the one in both dataframes
        #st.write(restaurants_from_covers_df)
        #st.write(restaurants_from_employee_df)

        # create a list of restaurants
        restaurants_ = [restaurant for restaurant in restaurants_from_covers_df if restaurant in restaurants_from_employee_df]
        #st.write(restaurants_)
        '''
        
        '''
        #restaurants = data_employee['Home'].unique()
        frame = []
        restaurants = restaurants_

        for restaurant in restaurants:
            # 1 - get the df for that restaurant - perform - hour tranformation to time series
            data_employee_single = create_timeries_employees(data_employee,restaurant )
            # 2 - make it compatible with the covers df
            def create_timeries_employees_with_hours(data_employee, store_name):
                frame = []
                for day, date in zip(data_employee[0], data_employee[2]):
                    date_times = day.index.values
                    
                    #1. write functions to transfor to datetime - handling values > 23
                    def tranform_to_date_time(x, date):
                        '''
                        Inside the dataframe there are values > 23 for the hour
                        This function handles this issue, by adding 1 day to the date
                        and using the difference between the value and 23 as the hour
                        '''
                        value_to_change = 23 - x
                        if value_to_change < 0:
                            # find the next day
                            date = pd.to_datetime(date)
                            next_day = date + pd.Timedelta(days=1)
                            # merge the next day with the remainder
                            return pd.to_datetime(str(next_day) + ' ' + str(abs(value_to_change)) + ':00:00')
                        else:
                            return pd.to_datetime(str(date) + ' ' + str(x) + ':00:00')
                    
                    #2. apply the function to the date_times
                    date_times = [tranform_to_date_time(x, date) for x in date_times]
                    
                    #3. set as index
                    day.index = date_times
                    
                    frame.append(day)

                data_employee = pd.concat(frame,axis=0)
                # add column with restaurant name
                data_employee['Store_Name'] = store_name
                
                return data_employee

            # 3 - apply the function 
            data_single_restaurant = create_timeries_employees_with_hours(data_employee_single,restaurant )
            #st.write(data_single_restaurant)


            frame.append(data_single_restaurant)

        data_employee = pd.concat(frame,axis=0)
        # ----------------- #
        # Merge

        # create new column for date
        data_employee['Date'] = data_employee.index
        data_covers['Date'] = data_covers.index
        # delete index
        data_employee = data_employee.reset_index(drop=True)
        data_covers = data_covers.reset_index(drop=True)

        # ----------------- #
        #st.write('Covers')
        features = ['Date', 'Store_Name', 'Guest_Count']
        data_covers = data_covers[features]
        #st.write(data_covers)
        # ----------------- #
        #st.write('Employees')
        #st.write(data_employee)

        # ----------------- #
        # Merge the two dfs
        #add the guest_count to the employee df
        # if the date is the same, add the guest count
        # if the date is not the same, add 0
        data_employee['Guest_Count'] = data_employee['Date'].apply(lambda x: data_covers[data_covers['Date'] == x]['Guest_Count'].values[0] if x in data_covers['Date'].values else 0)
        # set index to date
        data_employee = data_employee.set_index('Date')
        # reorganize columns
        data_employee = data_employee[['Store_Name', 'Guest_Count', 'Count Employees']]
        # reorganize type columns
        data_employee['Guest_Count'] = data_employee['Guest_Count'].astype(int)
        data_employee['Count Employees'] = data_employee['Count Employees'].astype(int)
        # rename columns
        data_employee = data_employee.rename(columns={'Count Employees':'Employees_Count'})
        # add column with the day of the week
        data_employee['Day_of_week'] = data_employee.index.day_name()
        # add column with the hour
        data_employee['Hour'] = data_employee.index.hour
        # add column with the time of the day apply lambda function
        def get_time_of_day(x):
            if x < 8 and x >= 3:
                return 'Before_Opening'
            elif x >= 8 and x < 12:
                return 'Breakfast'
            elif x >= 12 and x <= 15:
                return 'Afternoon'
            elif x > 15 and x <= 18:
                return 'Evening'
            elif x > 18 and x <= 23:
                return 'Dinner'
            else:
                return 'After_Closing'
        data_employee['Time_of_day'] = data_employee['Hour'].apply(lambda x: get_time_of_day(x))
        # ----------------- #
        return data_employee

    data_employee = create_final_timeseries(uploaded_file_1,uploaded_file_2)
    
    with st.expander('Data'):
        st.write(data_employee)

    with st.sidebar.expander('Download data'):
        @st.cache # cache the function
        def convert_df(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv().encode('utf-8')
        
        csv = convert_df(data_employee)
        name = st.text_input('File name', 'data')
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f'{name}.csv',
            mime='text/csv',
        )

    
    # create a list of restaurants
    restaurants = data_employee['Store_Name'].unique()

    selected = st.selectbox('Select a restaurant', restaurants)
    # get the df for that restaurant
    data_employee = data_employee[data_employee['Store_Name'] == selected]

    # ----------------- #
    # plot
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_employee.index, y=data_employee['Guest_Count'], name='Guest Count'))
    fig.add_trace(go.Scatter(x=data_employee.index, y=data_employee['Employees_Count'], name='Employees'))
    fig.update_layout(
        title="Guest Count vs Employees",
        xaxis_title="Date",
        yaxis_title="Count",
        legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            color="#7f7f7f"
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    