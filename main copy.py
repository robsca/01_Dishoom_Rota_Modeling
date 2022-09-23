from turtle import width
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
        {'id':'TP','label':"Time Period"},
        {'id':'Weekly view','label':"Weekly view"},
        {'icon': "",'label':"Days", 
                    'submenu':[
                        {'id':'Monday', 'label':"Monday"},
                        {'id':'Tuesday', 'label':"Tuesday"},
                        {'id':'Wednesday', 'label':"Wednesday"},
                        {'id':'Thursday', 'label':"Thursday"},
                        {'id':'Friday', 'label':"Friday"},
                        {'id':'Saturday', 'label':"Saturday"},
                        {'id':'Sunday', 'label':"Sunday"},
                    ]
                },
                {'id':'Modeling','label':"Modeling"},
                {'id':'Total Excess and Shortage','label':"Total Excess and Shortage"},
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

# Select all the restaurant that you want to see
restaurants = st.sidebar.multiselect("Select a restaurant", list_of_restaurants, default=list_of_restaurants[2])


def plot_each_day_guest_count_vs_employees_count(verbose = False):
    from functions import get_empoloyees_hours_day_by_day_grouped_by_hour, get_store_data_day_by_day_grouped_by_hour
    days_in_a_month = [ 
                        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
                        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
                        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
                        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
                        ]
    for restaurant in restaurants:
        st.subheader(restaurant)
        employees_data_2022 = get_empoloyees_hours_day_by_day_grouped_by_hour(path2022_employees, restaurant, date_col_2022[0], date_col_2022[-1])
        store_data_2022 = get_store_data_day_by_day_grouped_by_hour(path2022_restautant, restaurant, date_col_2022[0], date_col_2022[-1])
        store_data_2019 = get_store_data_day_by_day_grouped_by_hour(path2019_restaurant, restaurant, date_col_2019[0], date_col_2019[-1])
        # get rid of 26th
        import datetime
        mela_day = datetime.date(2022, 7, 27)
        # rearrage the date format -> mm - dd - yyyy
        mela_day = mela_day.strftime("%m-%d-%Y")

        for day2022_empl, day2022, day2019, day_col_2019, day_col_2022, day_ in zip(employees_data_2022, store_data_2022, store_data_2019, date_col_2019, date_col_2022, days_in_a_month):
            # skipe the mela day
            if day_col_2022 == mela_day:
                continue
            with st.expander(f"{day_col_2022} - {day_col_2019} - {day_}"):
                if verbose:
                    c1,c2,c3 = st.columns(3)
                    with c1:
                        st.write(day2022_empl)
                    with c2:
                        st.write(day2022)
                    with c3:
                        st.write(day2019)
                    
                # create graph 2019 vs 2022
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(go.Bar(x=day2022_empl.index, y=day2022_empl['Count Employees'], name='Employees', opacity=0.6), secondary_y=False)
                fig.add_trace(go.Scatter(x=day2022.index, y=day2022['Guest_Count'], name='Restaurant 2022', fill = 'tozeroy'), secondary_y=False)
                fig.add_trace(go.Scatter(x=day2019.index, y=day2019['Guest_Count'], name='Restaurant 2019', fill = 'tozeroy'), secondary_y=False)
                fig.update_layout(title=f"{day_col_2022} - {day_col_2019}", xaxis_title="Hour", yaxis_title="Actual Hours")
                st.plotly_chart(fig)

def plot_each_day_ratio_GUESTSvsEMPLOYEES(verbose = False):
    from functions import get_empoloyees_hours_day_by_day_grouped_by_hour, get_store_data_day_by_day_grouped_by_hour, get_ratio_GUESTvs_EMPLOYEE
    for restaurant in restaurants:
        employees_data_2022 = get_empoloyees_hours_day_by_day_grouped_by_hour(path2022_employees, restaurant, date_col_2022[0], date_col_2022[-1])
        store_data_2022 = get_store_data_day_by_day_grouped_by_hour(path2022_restautant, restaurant, date_col_2022[0], date_col_2022[-1])
        ratio_guest_employee2022 = get_ratio_GUESTvs_EMPLOYEE(path2022_restautant, path2022_employees, restaurant, date_col_2022[0], date_col_2022[-1])

        for day2022_empl, day2022, day_col_2022, ratio_col_2022 in zip(employees_data_2022, store_data_2022, date_col_2022, ratio_guest_employee2022):
            with st.expander(f"{day_col_2022}"):
                if verbose:
                    c1,c2,c3 = st.columns(3)
                    with c1:
                        st.write(day2022_empl)
                    with c2:
                        st.write(day2022)
                    with c3:
                        st.write(ratio_col_2022)

                # create graph Ratio of guest vs employee
                fig1 = make_subplots(specs=[[{"secondary_y": True}]])
                fig1.add_trace(go.Bar(x=day2022_empl.index, y=day2022_empl['Count Employees'],
                                name='Employees', opacity=0.8),secondary_y=False)
                fig1.add_trace(go.Bar(x=day2022.index, y=day2022['Guest_Count'],
                                name='Restaurant 2022', opacity = 0.7), secondary_y=False)
                fig1.add_trace(go.Scatter(x=ratio_col_2022['Hour'], y=ratio_col_2022['Ratio'],
                                name='Ratio GUEST vs EMPLOYEE', fill = 'tonexty'),secondary_y=True)
                
                fig1.update_layout(title=f"{day_col_2022}", xaxis_title="Hour", yaxis_title="Actual Hours")
                fig1.update_layout(title=f"{day_col_2022}", xaxis_title="Hour", yaxis_title="Ratio")
                st.plotly_chart(fig1)

def plot_week_of_choice(verbose = False):
    from functions import get_empoloyees_hours_day_by_day_grouped_by_hour, get_store_data_day_by_day_grouped_by_hour, get_ratio_GUESTvs_EMPLOYEE
    options = ["Guests vs Employees - 2019/2022", "Ratio Guests vs Employees - 2022"]
    measure = st.sidebar.selectbox(label = 'Select measure', options = options)
    if measure == "Guests vs Employees - 2019/2022":
        for restaurant in restaurants:
            st.subheader(restaurant)
            date_col_2019 = data2019['Date'].unique()[:-3]
            date_col_2022 = data2022['Date'].unique()[3:]
            employees_data_2022 = get_empoloyees_hours_day_by_day_grouped_by_hour(path2022_employees, restaurant, date_col_2022[0], date_col_2022[-1])
            store_data_2022 = get_store_data_day_by_day_grouped_by_hour(path2022_restautant, restaurant, date_col_2022[0], date_col_2022[-1])
            store_data_2019 = get_store_data_day_by_day_grouped_by_hour(path2019_restaurant, restaurant, date_col_2019[0], date_col_2019[-1])
            
            # group elements in list 7 elements
            store_data_2022 = [store_data_2022[i*7:(i+1)*7] for i in range(len(date_col_2022)//7)]
            store_data_2019 = [store_data_2019[i*7:(i+1)*7] for i in range(len(date_col_2019)//7)]
            employees_data_2022 = [employees_data_2022[i*7:(i+1)*7] for i in range(len(date_col_2022)//7)]
            date_col_2019 = [date_col_2019[i*7:(i+1)*7] for i in range(len(date_col_2019)//7)]
            date_col_2022 = [date_col_2022[i*7:(i+1)*7] for i in range(len(date_col_2022)//7)]

            week_number = st.sidebar.slider(label = f'{restaurant} - Select week', min_value=1, max_value=len(store_data_2022), step = 1, value = 1)
            
            store_data_2019 = store_data_2019[week_number-1]
            store_data_2022 = store_data_2022[week_number-1]
            employees_data_2022 = employees_data_2022[week_number-1]
            date_col_2019 = date_col_2019[week_number-1]
            date_col_2022 = date_col_2022[week_number-1]
            day_weeks = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            import datetime
            for day2022_empl, day2022, day2019, day_col_2019, day_col_2022, day_week_name in zip(employees_data_2022, store_data_2022, store_data_2019, date_col_2019, date_col_2022, day_weeks):
                
                mela_day = datetime.date(2022, 7, 27)
                # rearrage the date format -> mm - dd - yyyy
                mela_day = mela_day.strftime("%m-%d-%Y")
                if day_col_2022 == mela_day:
                    continue
                with st.expander(f"{day_col_2022} - {day_col_2019} - {day_week_name}"):
                    if verbose:
                        c1,c2,c3 = st.columns(3)
                        with c1:
                            st.write(day2022_empl)
                        with c2:
                            st.write(day2022)
                        with c3:
                            st.write(day2019)
                        
                    # create graph 2019 vs 2022
                    fig = make_subplots(specs=[[{"secondary_y": True}]])
                    fig.add_trace(go.Bar(x=day2022_empl.index, y=day2022_empl['Count Employees'],
                                 name='Employees', opacity=0.6), secondary_y=False)
                    fig.add_trace(go.Scatter(x=day2022.index, y=day2022['Guest_Count'], 
                                name='Restaurant 2022',fill = 'tozeroy'), secondary_y=False)
                    fig.add_trace(go.Scatter(x=day2019.index, y=day2019['Guest_Count'], 
                                name='Restaurant 2019',fill = 'tozeroy'), secondary_y=False)
                    fig.update_layout(title=f"{day_col_2022} - {day_col_2019}", xaxis_title="Hour", yaxis_title="Actual Hours")
                    # set width of the graph
                    st.plotly_chart(fig)
            st.write('---')
    
    elif measure == "Ratio Guests vs Employees - 2022":
        for restaurant in restaurants:
            st.subheader(restaurant)
            date_col_2022 = data2022['Date'].unique()

            employees_data_2022 = get_empoloyees_hours_day_by_day_grouped_by_hour(path2022_employees, restaurant, date_col_2022[0], date_col_2022[-1])
            store_data_2022 = get_store_data_day_by_day_grouped_by_hour(path2022_restautant, restaurant, date_col_2022[0], date_col_2022[-1])
            ratio_guest_employee2022 = get_ratio_GUESTvs_EMPLOYEE(path2022_restautant, path2022_employees, restaurant, date_col_2022[0], date_col_2022[-1])

            # group elements in list 7 elements
            store_data_2022 = [store_data_2022[i*7:(i+1)*7] for i in range(len(date_col_2022)//7)]
            employees_data_2022 = [employees_data_2022[i*7:(i+1)*7] for i in range(len(date_col_2022)//7)]
            date_col_2022 = [date_col_2022[i*7:(i+1)*7] for i in range(len(date_col_2022)//7)]
            ratio_guest_employee2022 = [ratio_guest_employee2022[i*7:(i+1)*7] for i in range(len(ratio_guest_employee2022)//7)]

            week_number = st.sidebar.slider(label = f'{restaurant} - Select week', min_value=1, max_value=len(store_data_2022), step = 1, value = 1)
            
            store_data_2022 = store_data_2022[week_number-1]
            employees_data_2022 = employees_data_2022[week_number-1]
            date_col_2022 = date_col_2022[week_number-1]
            ratio_guest_employee2022 = ratio_guest_employee2022[week_number-1]

            day_weeks = ['Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']

            for day2022_empl, day2022, day_col_2022, ratio_, day_week_name in zip(employees_data_2022, store_data_2022, date_col_2022, ratio_guest_employee2022, day_weeks):
                with st.expander(f"{day_col_2022} - {day_week_name}"):
                    if verbose:
                        c1,c2,c3 = st.columns(3)
                        with c1:
                            st.write(day2022_empl)
                        with c2:
                            st.write(day2022)
                        with c3:
                            st.write(ratio_)
                        
                    # create graph 2019 vs 2022
                    fig = make_subplots(specs=[[{"secondary_y": True}]])
                    fig.add_trace(go.Scatter(x=day2022_empl.index, y=day2022_empl['Count Employees'],
                         name='Employees',fill = 'tozeroy'), secondary_y=False)
                    fig.add_trace(go.Scatter(x=day2022.index, y=day2022['Guest_Count'],
                         name='Restaurant 2022', fill = 'tozeroy'), secondary_y=False)
                    fig.add_trace(go.Bar(x=ratio_['Hour'], y=ratio_['Ratio'],
                         name='Ratio', opacity=0.6), secondary_y=True)
                    fig.update_layout(title=f"{day_col_2022}", xaxis_title="Hour", yaxis_title="Actual Hours")
                    st.plotly_chart(fig)
            st.write('---')

def get_day_of_the_week(verbose = False, day = 'Monday'):
    from functions import get_empoloyees_hours_day_by_day_grouped_by_hour, get_store_data_day_by_day_grouped_by_hour, get_ratio_GUESTvs_EMPLOYEE

    options = ["Guests vs Employees - 2019/2022", "Ratio Guests vs Employees - 2022"]
    measure = st.sidebar.selectbox(label = 'Select measure', options = options)
    if measure == 'Guests vs Employees - 2019/2022':
        st.subheader(f"{day}")
        for restaurant in restaurants:
            st.subheader(restaurant)
            date_col_2019 = data2019['Date'].unique()[:-3]
            date_col_2022 = data2022['Date'].unique()[3:]
            employees_data_2022 = get_empoloyees_hours_day_by_day_grouped_by_hour(path2022_employees, restaurant, date_col_2022[0], date_col_2022[-1])
            store_data_2022 = get_store_data_day_by_day_grouped_by_hour(path2022_restautant, restaurant, date_col_2022[0], date_col_2022[-1])
            store_data_2019 = get_store_data_day_by_day_grouped_by_hour(path2019_restaurant, restaurant, date_col_2019[0], date_col_2019[-1])
            
            day_of_the_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            reminder = day_of_the_week.index(day)
            employees_data_2022 = [employees_data_2022[i] for i in range(len(employees_data_2022)) if i%7 == reminder]
            store_data_2022 = [store_data_2022[i] for i in range(len(store_data_2022)) if i%7 == reminder]
            store_data_2019 = [store_data_2019[i] for i in range(len(store_data_2019)) if i%7 == reminder]
            date_col_2019 = [date_col_2019[i] for i in range(len(date_col_2019)) if i%7 == reminder]
            date_col_2022 = [date_col_2022[i] for i in range(len(date_col_2022)) if i%7 == reminder]

            for day2022_empl, day2022, day2019, day_col_2019, day_col_2022 in zip(employees_data_2022, store_data_2022, store_data_2019, date_col_2019, date_col_2022):
                check_ = st.sidebar.checkbox(f"{day_col_2022} - {day_col_2019} - {restaurant}", value = True, key = f"{day_col_2022} - {day_col_2019} - {restaurant}")
                if check_:
                    with st.expander(f"{day_col_2022} - {day_col_2019}"):
                        if verbose:
                            c1,c2,c3 = st.columns(3)
                            with c1:
                                st.write(day2022_empl)
                            with c2:
                                st.write(day2022)
                            with c3:
                                st.write(day2019)
                            
                        # create graph 2019 vs 2022
                        fig = make_subplots(specs=[[{"secondary_y": True}]])
                        fig.add_trace(go.Bar(x=day2022_empl.index, y=day2022_empl['Count Employees'],
                            name='Employees', opacity=0.6), secondary_y=False)
                        fig.add_trace(go.Scatter(x=day2022.index, y=day2022['Guest_Count'],
                            name='Restaurant 2022', fill = 'tozeroy'), secondary_y=False)
                        fig.add_trace(go.Scatter(x=day2019.index, y=day2019['Guest_Count'], 
                            name='Restaurant 2019', fill = 'tozeroy'), secondary_y=False)
                        fig.update_layout(title=f"{day_col_2022} - {day_col_2019}", xaxis_title="Hour", yaxis_title="Actual Hours")
                        st.plotly_chart(fig)

    elif measure == 'Ratio Guests vs Employees - 2022':
        for restaurant in restaurants:

            date_col_2019 = data2019['Date'].unique()[:-3]
            date_col_2022 = data2022['Date'].unique()[3:]
            employees_data_2022 = get_empoloyees_hours_day_by_day_grouped_by_hour(path2022_employees, restaurant, date_col_2022[0], date_col_2022[-1])
            store_data_2022 = get_store_data_day_by_day_grouped_by_hour(path2022_restautant, restaurant, date_col_2022[0], date_col_2022[-1])
            ratio_guest_employee2022 = get_ratio_GUESTvs_EMPLOYEE(path2022_restautant, path2022_employees, restaurant, date_col_2022[0], date_col_2022[-1])
            
            day_of_the_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            reminder = day_of_the_week.index(day)

            employees_data_2022 = [employees_data_2022[i] for i in range(len(employees_data_2022)) if i%7 == reminder]
            store_data_2022 = [store_data_2022[i] for i in range(len(store_data_2022)) if i%7 == reminder]
            date_col_2022 = [date_col_2022[i] for i in range(len(date_col_2022)) if i%7 == reminder]
            ratio_guest_employee2022 = [ratio_guest_employee2022[i] for i in range(len(ratio_guest_employee2022)) if i%7 == reminder]
            st.subheader(day)
            for day2022_empl, day2022, day_col_2022, ratio_col_2022 in zip(employees_data_2022, store_data_2022, date_col_2022, ratio_guest_employee2022):
                with st.expander(f"{day_col_2022}"):
                    if verbose:
                        c1,c2,c3 = st.columns(3)
                        with c1:
                            st.write(day2022_empl)
                        with c2:
                            st.write(day2022)
                        with c3:
                            st.write(ratio_col_2022)

                    # create graph Ratio of guest vs employee
                    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
                    fig1.add_trace(go.Scatter(x=day2022_empl.index, y=day2022_empl['Count Employees'],
                        name='Employees', fill = 'tozeroy'), secondary_y=False)
                    fig1.add_trace(go.Scatter(x=day2022.index, y=day2022['Guest_Count'], 
                        name='Restaurant 2022', fill = 'tozeroy'), secondary_y=False)
                    fig1.add_trace(go.Bar(x=ratio_col_2022['Hour'], y=ratio_col_2022['Ratio'], 
                        name='Ratio GUEST vs EMPLOYEE', opacity=0.6), secondary_y=True)
                    fig1.update_layout(title=f"{day_col_2022}", xaxis_title="Hour", yaxis_title="Ratio")
                    st.plotly_chart(fig1)

def start_modeling_(verbose = False):
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

    choice_of_departments = st.sidebar.selectbox('Select a department', unique_roles, index=0)
    st.subheader('Department: ' + choice_of_departments)
    
    if choice_of_departments == "All":
        ratio = st.sidebar.number_input(f"Ratio Guest vs EMPLOYEES", value=2.0, step=0.1, max_value=15.0, min_value=1.0)
    elif choice_of_departments != "All":
        ratio = st.sidebar.number_input(f"Ratio of guest vs {choice_of_departments}", value=15.0, step=0.1, max_value=30.0, min_value=1.0)

    if st.checkbox('Moving average'):
        window = st.sidebar.number_input(f"Moving average", value=3, step=1, max_value=10, min_value=1)
    else:
        window = 1

    for restaurant in restaurants:
        employees_data_2022, roles_employees = get_empoloyees_hours_day_by_day_grouped_by_hour_role(path2022_employees, restaurant, date_col_2022[0], date_col_2022[-1], choice_of_departments)
        store_data_2022 = get_store_data_day_by_day_grouped_by_hour(path2022_restautant, restaurant, date_col_2022[0], date_col_2022[-1])
        ratio_guest_employee2022 = get_ratio_GUESTvs_EMPLOYEE(path2022_restautant, path2022_employees, restaurant, date_col_2022[0], date_col_2022[-1])
        # remove the 26 of the month
        store_data_2022 = [store_data_2022[i] for i in range(len(store_data_2022)) if i != 26]
        for day2022_empl, day2022, day_col_2022, ratio_col_2022, d, roles in zip(employees_data_2022, store_data_2022, date_col_2022, ratio_guest_employee2022, days_in_month, roles_employees):
            with st.expander(f"{day_col_2022} - {d}"):

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
                        st.plotly_chart(fig1)
                else:
                    st.plotly_chart(fig1)

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
                        st.plotly_chart(fig2)

#---  
def total_distribution(verbose = False):
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

    choice_of_departments = st.sidebar.selectbox('Select a department', unique_roles, index=0)
    st.subheader('Department: ' + choice_of_departments)
    
    if choice_of_departments == "All":
        ratio = st.sidebar.number_input(f"Ratio Guest vs EMPLOYEES", value=2.0, step=0.1, max_value=15.0, min_value=1.0)
    elif choice_of_departments != "All":
        ratio = st.sidebar.number_input(f"Ratio of guest vs {choice_of_departments}", value=15.0, step=0.1, max_value=30.0, min_value=1.0)

    if st.checkbox('Moving average'):
        window = st.sidebar.number_input(f"Moving average", value=3, step=1, max_value=10, min_value=1)
    else:
        window = 1

    all_restaurant_excess_shortage = []
    for restaurant in restaurants:
        tot_hours_in_excess = 0
        tot_hours_in_shortage = 0
        employees_data_2022, roles_employees = get_empoloyees_hours_day_by_day_grouped_by_hour_role(path2022_employees, restaurant, date_col_2022[0], date_col_2022[-1], choice_of_departments)
        store_data_2022 = get_store_data_day_by_day_grouped_by_hour(path2022_restautant, restaurant, date_col_2022[0], date_col_2022[-1])
        ratio_guest_employee2022 = get_ratio_GUESTvs_EMPLOYEE(path2022_restautant, path2022_employees, restaurant, date_col_2022[0], date_col_2022[-1])
        # remove the 26 of the month
        store_data_2022 = [store_data_2022[i] for i in range(len(store_data_2022)) if i != 26]
        for day2022_empl, day2022, day_col_2022, ratio_col_2022, d, roles in zip(employees_data_2022, store_data_2022, date_col_2022, ratio_guest_employee2022, days_in_month, roles_employees):

            # create graph Ratio of guest vs employee
            ideal = list(day2022['Guest_Count']//ratio)
            ideal = calculate_moving_average(ideal, window)
            hours = list(day2022.index)
            ideal = pd.DataFrame({'Hour': hours, 'Ideal': ideal})

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
            hours_in_excess = sum(diff['Difference'][diff['Difference'] > 0])
                
            # get hours in shortage summing all the negative values
            hours_in_shortage = sum(diff['Difference'][diff['Difference'] < 0])*-1

            # sum the hours in excess and shortage
            tot_hours_in_excess += hours_in_excess
            tot_hours_in_shortage += hours_in_shortage
            #--------------------------------------------
            ideal = dataframe_for_difference

        # add to all totals
        excess_shortage_single_restaurant = [tot_hours_in_excess, tot_hours_in_shortage]
        all_restaurant_excess_shortage.append(excess_shortage_single_restaurant)
    
    # transform in dataframe -> name restaurant, excess, shortage
    df = []
    for restaurant, excess_shortage in zip(restaurants, all_restaurant_excess_shortage):
        df.append([restaurant, excess_shortage[0], excess_shortage[1]])
    df = pd.DataFrame(df, columns=['Restaurant', 'Excess', 'Shortage'])
    # plot as a bar chart multiple bars
    fig  = go.Figure()
    fig.add_trace(go.Bar(x=df['Restaurant'], y=df['Excess'], name='Excess'))
    fig.add_trace(go.Bar(x=df['Restaurant'], y=df['Shortage'], name='Shortage'))
    fig.update_layout(barmode='group')
    fig.update_layout(title='Excess and Shortage Hours - July 2022')
    fig.update_layout(xaxis_tickangle=-45)
    fig.update_layout(xaxis_title="Restaurant")
    fig.update_layout(yaxis_title="Hours")
    st.plotly_chart(fig)

# In Progress
def daily_trends(verbose = False, day = 'Monday'):
    from functions import get_empoloyees_hours_day_by_day_grouped_by_hour, get_store_data_day_by_day_grouped_by_hour, get_ratio_GUESTvs_EMPLOYEE

    options = ["Guests vs Employees - 2019/2022", "Ratio Guests vs Employees - 2022"]
    measure = st.sidebar.selectbox(label = 'Select measure', options = options)
    if measure == 'Guests vs Employees - 2019/2022':
        st.subheader(f"{day}")
        for restaurant in restaurants:
            st.subheader(restaurant)
            date_col_2019 = data2019['Date'].unique()[:-3]
            date_col_2022 = data2022['Date'].unique()[3:]
            employees_data_2022 = get_empoloyees_hours_day_by_day_grouped_by_hour(path2022_employees, restaurant, date_col_2022[0], date_col_2022[-1])
            store_data_2022 = get_store_data_day_by_day_grouped_by_hour(path2022_restautant, restaurant, date_col_2022[0], date_col_2022[-1])
            store_data_2019 = get_store_data_day_by_day_grouped_by_hour(path2019_restaurant, restaurant, date_col_2019[0], date_col_2019[-1])
            
            day_of_the_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            reminder = day_of_the_week.index(day)
            employees_data_2022 = [employees_data_2022[i] for i in range(len(employees_data_2022)) if i%7 == reminder]
            store_data_2022 = [store_data_2022[i] for i in range(len(store_data_2022)) if i%7 == reminder]
            store_data_2019 = [store_data_2019[i] for i in range(len(store_data_2019)) if i%7 == reminder]
            date_col_2019 = [date_col_2019[i] for i in range(len(date_col_2019)) if i%7 == reminder]
            date_col_2022 = [date_col_2022[i] for i in range(len(date_col_2022)) if i%7 == reminder]

            for day2022_empl, day2022, day2019, day_col_2019, day_col_2022 in zip(employees_data_2022, store_data_2022, store_data_2019, date_col_2019, date_col_2022):
                check_ = st.sidebar.checkbox(f"{day_col_2022} - {day_col_2019} - {restaurant}", value = True, key = f"{day_col_2022} - {day_col_2019} - {restaurant}")
                if check_:
                    with st.expander(f"{day_col_2022} - {day_col_2019}"):
                        if verbose:
                            c1,c2,c3 = st.columns(3)
                            with c1:
                                st.write(day2022_empl)
                            with c2:
                                st.write(day2022)
                            with c3:
                                st.write(day2019)
                            
                        # create graph 2019 vs 2022
                        fig = make_subplots(specs=[[{"secondary_y": True}]])
                        fig.add_trace(go.Bar(x=day2022_empl.index, y=day2022_empl['Count Employees'],
                            name='Employees', opacity=0.6), secondary_y=False)
                        fig.add_trace(go.Scatter(x=day2022.index, y=day2022['Guest_Count'],
                            name='Restaurant 2022', fill = 'tozeroy'), secondary_y=False)
                        fig.add_trace(go.Scatter(x=day2019.index, y=day2019['Guest_Count'], 
                            name='Restaurant 2019', fill = 'tozeroy'), secondary_y=False)
                        fig.update_layout(title=f"{day_col_2022} - {day_col_2019}", xaxis_title="Hour", yaxis_title="Actual Hours")
                        st.plotly_chart(fig)

    elif measure == 'Ratio Guests vs Employees - 2022':
        for restaurant in restaurants:

            date_col_2019 = data2019['Date'].unique()[:-3]
            date_col_2022 = data2022['Date'].unique()[3:]
            employees_data_2022 = get_empoloyees_hours_day_by_day_grouped_by_hour(path2022_employees, restaurant, date_col_2022[0], date_col_2022[-1])
            store_data_2022 = get_store_data_day_by_day_grouped_by_hour(path2022_restautant, restaurant, date_col_2022[0], date_col_2022[-1])
            ratio_guest_employee2022 = get_ratio_GUESTvs_EMPLOYEE(path2022_restautant, path2022_employees, restaurant, date_col_2022[0], date_col_2022[-1])
            
            day_of_the_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            reminder = day_of_the_week.index(day)

            employees_data_2022 = [employees_data_2022[i] for i in range(len(employees_data_2022)) if i%7 == reminder]
            store_data_2022 = [store_data_2022[i] for i in range(len(store_data_2022)) if i%7 == reminder]
            date_col_2022 = [date_col_2022[i] for i in range(len(date_col_2022)) if i%7 == reminder]
            ratio_guest_employee2022 = [ratio_guest_employee2022[i] for i in range(len(ratio_guest_employee2022)) if i%7 == reminder]
            st.subheader(day)
            for day2022_empl, day2022, day_col_2022, ratio_col_2022 in zip(employees_data_2022, store_data_2022, date_col_2022, ratio_guest_employee2022):
                with st.expander(f"{day_col_2022}"):
                    if verbose:
                        c1,c2,c3 = st.columns(3)
                        with c1:
                            st.write(day2022_empl)
                        with c2:
                            st.write(day2022)
                        with c3:
                            st.write(ratio_col_2022)

                    # create graph Ratio of guest vs employee
                    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
                    fig1.add_trace(go.Scatter(x=day2022_empl.index, y=day2022_empl['Count Employees'],
                        name='Employees', fill = 'tozeroy'), secondary_y=False)
                    fig1.add_trace(go.Scatter(x=day2022.index, y=day2022['Guest_Count'], 
                        name='Restaurant 2022', fill = 'tozeroy'), secondary_y=False)
                    fig1.add_trace(go.Bar(x=ratio_col_2022['Hour'], y=ratio_col_2022['Ratio'], 
                        name='Ratio GUEST vs EMPLOYEE', opacity=0.6), secondary_y=True)
                    fig1.update_layout(title=f"{day_col_2022}", xaxis_title="Hour", yaxis_title="Ratio")
                    st.plotly_chart(fig1)
    note = '''
        Prediction is based on the hystorical data.
        1. Predict total guest of the entire day
        2. Predict what time the peaks will occur
        3. Predict guest count for each hour of the day
    '''
    st.write(note)


#----------------------------------------------------------------------------------------------------------------------
if choosen == 'TP':
    options = ["GUESTS Count - 2019/2022",
                "GUESTS vs EMPLOYEES Ratio - 2022",
                ]
                
    choice = st.sidebar.selectbox("Select a plot", options)

    if choice == "GUEST Count vs EMPLOYEES Count":
        plot_each_day_guest_count_vs_employees_count()

    elif choice == "Ratio GUESTS vs EMPLOYEES":
        date_col_2022 = data2022['Date'].unique()
        plot_each_day_ratio_GUESTSvsEMPLOYEES()
# Individual week graphs
elif choosen == 'Weekly view':
    plot_week_of_choice()
# Individual Day of the week
elif choosen == 'Monday':
    get_day_of_the_week(day = 'Monday')
elif choosen == 'Tuesday':
    get_day_of_the_week(day = 'Tuesday')
elif choosen == 'Wednesday':
    get_day_of_the_week(day = 'Wednesday')
elif choosen == 'Thursday':
    get_day_of_the_week(day = 'Thursday')
elif choosen == 'Friday':
    get_day_of_the_week(day = 'Friday')
elif choosen == 'Saturday':
    get_day_of_the_week(day = 'Saturday')
elif choosen == 'Sunday':
    get_day_of_the_week(day = 'Sunday')
elif choosen == 'Modeling':
    start_modeling_(verbose = False)
 
# In progress
elif choosen == 'Total Excess and Shortage':
    total_distribution(verbose = False)

elif choosen == 'Daily Trends':
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day = st.selectbox('Select a day', days_of_week, index=0)
    daily_trends(day = day )

if __name__ == '__main__':
    if not st._is_running_with_streamlit:
        import os
        os.system('streamlit run main.py')
