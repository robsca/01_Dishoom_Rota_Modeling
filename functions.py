import pandas as pd
import streamlit as st

# 3. Translate the data and store it into the structure   
def rota_tion(rota):
    '''
    This function takes the rota as INPUT -> returns a list of employees with their shifts in memory
    It creates the employee database and store the information find in the rota.
    It creates a graphical representation of the rota.
    '''
    # GET THE DATA READY FOR PROCESSING
    names    = rota['names'] # Get the names of the employees
    mondays = list(rota['mondays']) # Get the mondays of the employees
    tuesdays = list(rota['tuesdays']) # Get the tuesdays of the employees
    wednesdays = list(rota['wednesdays']) # Get the wednesdays of the employees
    thursdays = list(rota['thursdays']) # Get the thursdays of the employees
    fridays = list(rota['fridays']) # Get the fridays of the employees
    saturdays = list(rota['saturdays']) # Get the saturdays of the employees
    sundays = list(rota['sundays']) # Get the sundays of the employees
    
    week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    week_ = [mondays, tuesdays, wednesdays, thursdays, fridays, saturdays, sundays]

    # PREPARE THE DATA FOR THE Shift Object transformation
    week_data_bridge = []
    for d, day in enumerate(week_):
        day_ = [] # emply list to store the day data
        for e, shift in enumerate(day):

            day = week_days[d] # name of the current day
            name = names[e] # name of the current employee

            if shift == '0':
                # Build shift for off day
                start = None
                end = None
                role = None
                off = True
            else:
                shift = str(shift)
                shift = shift.split(',')
                # Build shift for work day
                start = shift[0]
                end = shift[1]
                role = shift[2]
                off = False

            shift_ = [day, name, start, end, role, off] # gather args for shift
            day_.append(shift_)             # add shift to day
        week_data_bridge.append(day_) # add day to week

    # Now the data can be transform into the Shift Object
    employees = []
    mondays = week_data_bridge[0]       # get the monday shifts
    tuesdays = week_data_bridge[1]      # get the tuesday shifts
    wednesdays = week_data_bridge[2]    # get the wednesday shifts
    thursdays = week_data_bridge[3]     # get the thursday shifts
    fridays = week_data_bridge[4]       # get the friday shifts
    saturdays = week_data_bridge[5]     # get the saturday shifts
    sundays = week_data_bridge[6]       # get the sunday shifts

    # CONNECT THE SHIFTS TO THE EMPLOYEES
    for i in range(len(names)):
        employees.append(employee(names[i], mondays[i], tuesdays[i], wednesdays[i], thursdays[i], fridays[i], saturdays[i], sundays[i]))

    # print(employees)
    verbose = False # put it to true to see the output and check for mistakes
    if verbose:
        for employee_ in employees:
            for shift in employee_.week:
                print(employee_.name)
                print(shift.start)
                print(shift.end) 
                print(shift.role)
                print(shift.off)
                print(shift.hour_today)
                print('\n')
    return employees, week_data_bridge

def create_graphs(employees, week_data_bridge):
    # everything works until this point
    #---
    # plot monday
    #---
    weeks_ =[]
    weeks_roles = []
    for i, day in enumerate(week_data_bridge):
        day_ = []
        day_roles = []
        for employee_ in employees:
            if employee_.week[i].off == False:
                today = employee_.week[i].hour_today
                today_role = employee_.week[i].role
                for element in today:
                    day_.append(element)
                    day_roles.append(today_role)

        weeks_.append(day_)
        weeks_roles.append(day_roles)
    # print(weeks_)
    return weeks_

def get_store_data(store_, report):
    '''
    This function take the store name as input,
    and returns the data of the store ordered by date, 
    grouped by hour.
    '''
    df = pd.read_csv(report)

    # Clean from 0 values
    df = df.drop(df[df['Item_Sales'] == 0].index)
    df = df.drop(df[df['Net_Sales'] == df['Void_Total']].index)

    # divide data by store
    df = df[df['Store_Name'] == store_]

    # Create a different table for each date
    dates = df['Date'].unique()
    table_by_date = []
    for date in dates:
        table_by_date.append(pd.DataFrame(df[df['Date'] == date])) 

    hours_stats = []
    for i, df_ in enumerate(table_by_date):
        # group by hour
        data_ = df_.groupby('Hour').sum()
        #plot
        hour_guest_count = list(data_['Guest_Count'].values)

        hours_stats.append(hour_guest_count)
    return hours_stats

def calculate_moving_average(lst, window_size, verbose=False):
    moving_average = []
    for i in range(len(lst)):
        if i < window_size:
            batch = lst[i:i+window_size]
            average = sum(batch)/len(batch)
            moving_average.append(average)
        else:
            batch = lst[i-window_size:i]
            average = sum(batch)/len(batch)
            moving_average.append(average)
    if verbose:
        print('Batch:', batch, 'Average:', average)
    return moving_average

def UI_Plotter(x, rota_, constraint, actual_rota, shifts, week_tot):
    import plotly.graph_objects as go
    ##### Plotting stuff
    if st.selectbox('Plot the rota', ['Line', 'Bar']) == 'Line':
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=rota_, name='Automatic_Rota'))
        fig.add_trace(go.Scatter(x=x, y=constraint, name='Constraint'))
        fig.add_trace(go.Scatter(x=x, y=actual_rota, name='Actual_rota'))
    else:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=x, y=rota_, name='Automatic_Rota'))
        fig.add_trace(go.Bar(x=x, y=constraint, name='Constraint'))
        fig.add_trace(go.Bar(x=x, y=actual_rota, name='Actual_rota'))
    st.plotly_chart(fig)

    optimal_cost = sum(constraint)*9.50
    optimal_hours = sum(constraint)
    algo_esteban_cost = sum(rota_)*9.50
    algo_esteban_hours = sum(rota_)
    actual_cost = sum(actual_rota)*9.50
    actual_hours = sum(actual_rota)

    st.write('Optimal cost:', optimal_cost, 'Optimal hours:', optimal_hours)
    st.write('Algo_Esteban cost:', algo_esteban_cost, 'Algo_Esteban hours:', algo_esteban_hours)
    st.write('Actual cost:', actual_cost, 'Actual hours:', actual_hours)


    


    with st.expander('Weekly Totals'):
        st.write(f'Total Cost with Actual Rota:')
        st.write(f'{sum(week_tot)*9.50}£')

    with st.expander('Show the generated shifts'):
        for i, shift in enumerate(shifts):
            start = shift[0]
            end = shift[1]
            x = st.slider(f'Employee {i+1}', 8, 25, (start, end), key = i)
            if x[0] != start or x[1] != end:
                st.write(f'Employee {i+1} changed from {start} to {x[0]} and from {end} to {x[1]}')
                # modify the shift
                shifts[i] = x
                
            st.write("---")
    
def get_totals(weeks_):
    totals = []
    for week in weeks_:
        # get unique values
        unique_values = list(set(week))
        # get the count of each unique value
        counts = [week.count(i) for i in unique_values]
        # get the total
        total = sum(counts)
        totals.append(total)
    return totals


# Transform the data into the right form -> # get hour_by_hour data
def unified(df):
    # Now we have to store in memory a different table for each store taking into account the date and the time,
    # at the end group by date
    # ---
    stores = df['Store_Name'].unique()
    table_by_store = []
    for store in stores:
        # select only the store
        data_single_store = pd.DataFrame(df[df['Store_Name'] == store])
        data_single_store = data_single_store.drop(columns=['Store_Name'])
        
        # Create a new column with the date and time, merging the two columns
        # lambda function to create a new column with the date ---> pd.to_datetime(df['sale_date'], format='%d/%m/%y %H:%M:%S')
        data_single_store['Date'] = data_single_store.apply(lambda x: x['Date'] + ' ' + str(str(x['Hour']) + ':' + '00'), axis=1)
        # convert to datetime
        data_single_store['Date'] = pd.to_datetime(data_single_store['Date'])
        # set to index
        data_single_store = data_single_store.set_index('Date')
        # group by index
        data_single_store = data_single_store.groupby(data_single_store.index).sum()
        # change columns name
        data_single_store.columns = [f'{col} - {store}' for col in data_single_store.columns]
        # add to the list
        table_by_store.append(pd.DataFrame(data_single_store))

    # unify the dataframe for the plotting
    df_unified = pd.concat(table_by_store, axis=1)
    return df_unified

def unified_(df, store):
    # Now we have to store in memory a different table for each store taking into account the date and the time,
    # at the end group by date
    # ---
    stores = df['Store_Name'] = store
    # select only the store
    data_single_store = pd.DataFrame(df[df['Store_Name'] == store])
    data_single_store = data_single_store.drop(columns=['Store_Name'])
    
    dates = data_single_store['Date'].unique()
    table_by_date = []
    for date in dates:
        day = data_single_store[data_single_store['Date'] == date]
        day = day.drop(columns=['Date'])
        day = day.set_index('Hour')
        day = day.groupby(day.index).sum()
        day.columns = [f'{col} - {store} - {date}' for col in day.columns]
        table_by_date.append(pd.DataFrame(day))
    df_unified = table_by_date
    # unify the dataframe for the plotting
    return df_unified