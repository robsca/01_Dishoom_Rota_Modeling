import streamlit as st
st.set_page_config(layout='wide',initial_sidebar_state='collapsed')

import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import hydralit_components as hc
import numpy as np

def menu():
    # Images
    markd = '''
    <img src="https://www.dishoom.com/assets/img/roundel-seva.png" width = "120" heigth = "120" >
    '''
    st.markdown(markd, unsafe_allow_html=True)

    # Menu
    menu_data = [
       
                {'id':'Modeling','label':"Modeling"},
               
                ]

    # Specify the theme
    over_theme = {'menu_background': '#ebd2b9',
                    'txc_inactive': '#6e7074' ,
                    'txc_active':'#6e7074'}

    menu_id = hc.nav_bar(
        menu_definition=menu_data,
        override_theme=over_theme,
        hide_streamlit_markers=True, # Will show the st hamburger as well as the navbar now!
        sticky_nav=False,           # At the top or not
        sticky_mode='sticky',      # jumpy or not-jumpy, but sticky or pinned
    )
    return menu_id
choosen = menu()

# All the paths to the data
path2022_employees = "ActualHoursvRotaHours_2022_Jul.xlsx"
path2022_restautant = "Aloha_Sales_Data_Export_2022_July.csv"
path2019_restaurant = "Aloha_Sales_Data_Export_2019_July.csv"

# Import all the data
data2019 = pd.read_csv(path2019_restaurant)
data2022 = pd.read_csv(path2022_restautant)
data2022_employees = pd.read_excel(path2022_employees)

# Align monday to monday 
date_col_2019 = data2019['Date'].unique()[:-3]
date_col_2022 = data2022['Date'].unique()[3:]

# Get list of restaurants
list_of_restaurants = pd.read_csv(path2019_restaurant)
list_of_restaurants = list_of_restaurants['Store_Name'].unique()

def start_modeling_(verbose = False):

    # Select all the restaurant that you want to see
    restaurants = st.multiselect("Select a restaurant", list_of_restaurants, default=list_of_restaurants[2])

    days_in_month = [
        'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 
        'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
        'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
        'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
        'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
    ]
    # get rid of 26th

    days_in_month = [days_in_month[i] for i in range(len(days_in_month)) if i != 26]
    date_col_2022 = data2022['Date'].unique()
    date_col_2022 = [date_col_2022[i] for i in range(len(date_col_2022)) if i != 26]

    from functions import get_empoloyees_hours_day_by_day_grouped_by_hour_role, get_store_data_day_by_day_grouped_by_hour, get_ratio_GUESTvs_EMPLOYEE, calculate_moving_average
    
    # Get all the possible roles
    unique_roles = data2022_employees['Division'].unique()
    # add "All" to the list of roles
    unique_roles = np.append(unique_roles, "All")
    # reverse list of roles
    unique_roles = unique_roles[::-1]

    choice_of_departments = st.selectbox('Select a department', unique_roles, index=0)
    st.subheader('Department: ' + choice_of_departments)
    
    if choice_of_departments == "All":
        ratio = st.number_input(f"Ratio Guest vs EMPLOYEES", value=2.0, step=0.1, max_value=15.0, min_value=1.0)
    elif choice_of_departments != "All":
        ratio = st.number_input(f"Ratio of guest vs {choice_of_departments}", value=15.0, step=0.1, max_value=30.0, min_value=1.0)

    if st.checkbox('Moving average'):
        window = st.number_input(f"Moving average", value=3, step=1, max_value=10, min_value=1)
    else:
        window = 1

    start_date = st.sidebar.selectbox('Select a start date', date_col_2022, index=0)
    end_date = st.sidebar.selectbox('Select a end date', date_col_2022, index=len(date_col_2022)-1)
    # get only the dates between the start and end date
    date_col_2022 = [date_col_2022[i] for i in range(len(date_col_2022)) if start_date <= date_col_2022[i] <= end_date]

    for restaurant in restaurants:
        employees_data_2022, roles_employees = get_empoloyees_hours_day_by_day_grouped_by_hour_role(path2022_employees, restaurant, start_date, end_date, choice_of_departments)
        store_data_2022 = get_store_data_day_by_day_grouped_by_hour(path2022_restautant, restaurant, start_date, end_date)
        ratio_guest_employee2022 = get_ratio_GUESTvs_EMPLOYEE(path2022_restautant, path2022_employees, restaurant, start_date, end_date)
        
        # remove the 26 of the month
        store_data_2022 = [store_data_2022[i] for i in range(len(store_data_2022)) if i != 26]
        for day2022_empl, day2022, day_col_2022, ratio_col_2022, d, roles in zip(employees_data_2022, store_data_2022, date_col_2022, ratio_guest_employee2022, days_in_month, roles_employees):
            with st.expander(f"{day_col_2022} "):

                # create graph Ratio of guest vs employee
                ideal = list(day2022['Guest_Count']//ratio)
                ideal = calculate_moving_average(ideal, window)
                hours = list(day2022.index)
                ideal = pd.DataFrame({'Hour': hours, 'Ideal': ideal})

                if verbose:
                    c1,c2,c3 = st.columns(3)
                    with c1:
                        st.write(day2022_empl)
                    with c2:
                        st.write(day2022)
                    with c3:
                        st.write(ideal)


                # ADJUST DATA FOR ANALYSIS
                # for every hour in the hour_empl 
                # if the hour is in the hour_ideal 
                    # find the index of the hour in the hour_ideal
                    # find the element at that index in the hour_ideal
                # else:
                    # find the index of the hour in the hour_empl
                    # find the element at that index in the hour_empl
                # add the element at that index to the ideal
                
                #-------------------------------------------
                hour_empl = list(day2022_empl.index)
                hour_ideal = list(ideal['Hour'].values)

                dataframe_for_difference = []
                for i, hour in enumerate(hour_empl):
                    if hour in hour_ideal:
                        # find value of the hour in the ideal
                        index = hour_ideal.index(hour)
                        value = ideal.iloc[index]['Ideal']
                        if value  <= 4:
                            value = day2022_empl.iloc[i]['Count Employees']
                    # add value to the dataframe
                        dataframe_for_difference.append([hour, value])
                    else:
                        # find value of the hour in the empl
                        index = hour_empl.index(hour)
                        value = day2022_empl.iloc[i]['Count Employees']
                        # add value to the dataframe
                        dataframe_for_difference.append([hour, value])

                # Get difference
                dataframe_for_difference = pd.DataFrame(dataframe_for_difference, columns=['Hour', 'Value'])
                l1 = dataframe_for_difference['Value'].values
                l2 = day2022_empl['Count Employees'].values
                diff = [x-y for x,y in zip(l1,l2)]
                diff = pd.DataFrame({'Hour': dataframe_for_difference['Hour'], 'Difference': diff})
                #st.write(diff)
                
                # get hours in excess summing all the positive values
                c1, c2 = st.columns(2)
                with c1:
                    hours_in_excess = sum(diff['Difference'][diff['Difference'] > 0])
                    st.subheader("Hours in excess")
                    st.write(f'{hours_in_excess.__round__(2)}')
                    st.write('---')
                    total_hours_in_rota = sum(day2022_empl['Count Employees'])
                    st.subheader("Total hours in Rota")
                    st.write(f'{total_hours_in_rota.__round__(2)}')
                    st.write('---')
                with c2:
                    # get hours in shortage summing all the negative values
                    hours_in_shortage = sum(diff['Difference'][diff['Difference'] < 0])*-1
                    st.subheader("Hours in shortage")
                    st.write(f'{hours_in_shortage.__round__(2)}')
                    st.write('---')
                    total_hour_ideal = sum(ideal['Ideal'])
                    st.subheader("Total hours Ideally")
                    st.write(f'{total_hour_ideal.__round__(2)}')
                    st.write('---')
                       
                #--------------------------------------------
                ideal = dataframe_for_difference
                # create graph Ratio of guest vs employee
                fig1 = make_subplots(specs=[[{"secondary_y": True}]])
                fig1.add_trace(go.Scatter(x=day2022_empl.index, y=day2022_empl['Count Employees'],
                                name='Employees', fill='tozeroy'))
                #fig1.add_trace(go.Scatter(x=day2022.index, y=day2022['Guest_Count'],
                #                name='Restaurant 2022', fill='tozeroy'), secondary_y=False)

                fig1.add_trace(go.Scatter(x = ideal['Hour'], y=ideal['Value'],
                                name='Ideal', fill='tozeroy'),secondary_y=True)

                fig1.update_layout(title=f"{day_col_2022}", xaxis_title="Hour", yaxis_title="Actual Hours")
                fig1.update_layout(title=f"{day_col_2022}", xaxis_title="Hour", yaxis_title="Ratio")
                c111, c222 = st.columns(2)
                if choice_of_departments == 'All':
                    with c111:
                        st.plotly_chart(fig1, use_container_width=True)
                else:
                    st.plotly_chart(fig1, use_container_width=True)

                # create graph bar for roles
                import random
                if choice_of_departments == 'All':
                    # create a list of colors
                    colors = []
                    while len(colors) < len(roles_employees):
                        # choose random color
                        color = '#%06X' % random.randint(0, 0xFFFFFF)
                        # add color to list
                        if color not in colors:
                            colors.append(color)
                    # add to dataframe
                    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
                    fig2.add_trace(go.Bar(x=roles.index, y=roles['Count Employees'], opacity=0.6, marker=dict(color=colors),
                                    ))
                    # every bar has a different color
                    with c222:
                        st.plotly_chart(fig2, use_container_width=True)


if choosen == 'Modeling':
    start_modeling_(verbose = False)
 
if __name__ == '__main__':
    if not st._is_running_with_streamlit:
        import os
        os.system('streamlit run main.py')
