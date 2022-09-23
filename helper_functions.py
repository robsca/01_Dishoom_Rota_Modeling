
def file_handler(uploaded_file):
    '''
    This function handles the uploaded file and returns a dataframe
    It can handles multiple formats -> (csv, xlsx, xls)
    '''
    import pandas as pd
    format = uploaded_file.name.split('.')[-1]
    if format == 'csv':
        df = pd.read_csv(uploaded_file) 
    elif format == 'xlsx' or format == 'xls':
        df = pd.read_excel(uploaded_file)
    else:
        print('Format not supported')
    return df

def create_timeries_covers(df):
    import pandas as pd
    '''
    1. Merge time and dates
    2. Get unique restaurants
    3. Create a dataframe for each restaurant
    4. Group by date
    5. Return dataframe -> (date, covers, store_name)
    '''
    # 1. Merge time and dates
    df['Date'] = df.apply(lambda x: x['Date'] + ' ' + str(str(x['Hour']) + ':' + '00'), axis=1)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 2. Get unique restaurants
    # apply a lambda function to modify store name
    df['Store_Name'] = df.apply(lambda x: x['Store_Name'].split('-')[1], axis=1)
    restaurants = df['Store_Name'].unique()
    # modify the restaurants name to match the employees data
    # divide at - and take the first part
    frame = []
    for restaurant in restaurants:
        # 3. Create a dataframe for each restaurant
        # filter data for each restaurant
        df_restaurant = df[df['Store_Name'] == restaurant]
        # 4. Group by date
        df_restaurant = df_restaurant.groupby('Date').sum()
        # Add Restaurant name
        df_restaurant['Store_Name'] = restaurant
        # create a column containing only the hour
        df_restaurant['Hour'] = df_restaurant.index.hour
        # create a column containing only the part of the day
        df_restaurant['Part_of_day'] = df_restaurant.apply(lambda x: 'Breakfast' if x['Hour'] < 12 else 'Lunch' if x['Hour'] <= 15 else 'Afternoon' if x['Hour'] <= 18 else 'Dinner', axis=1)
        # create a column containing only the day of the week
        df_restaurant['Day_of_week'] = df_restaurant.index.day_name()
        # add to the frame
        frame.append(df_restaurant)
    # concat all the dataframes
    df = pd.concat(frame)
    # return dataframe -> (date, covers, store_name, hour, part_of_day, day_of_week)
    features = ['Guest_Count', 'Store_Name', 'Hour', 'Part_of_day', 'Day_of_week']
    return df[features]

def create_timeries_employees(data, restaurant):
    import pandas as pd
    '''
    INPUT -> 
        data, restaurant name, start date, end date, choice of departments
    Output -> 
        It returns a list of dataframe (one for each day) with the Hour, and the Count of empployees working that hour.
        out = [day1, day2, day3, ...]
        day*n = pd.DataFrame([[hour, count], [hour, count], ...], columns=['Hour', 'Count'])

    '''
    # Modify datetime format in Shift date column
    data['Shift date'] = pd.to_datetime(data['Shift date'])
    data['Shift date'] = data['Shift date'].dt.strftime('%m-%d-%Y')

    # get unique restaurants
    data_filtered = data[data['Home'] == restaurant]

    #if choice_of_departments != 'All':
    #   data_filtered = data_filtered[data_filtered['Division']==choice_of_departments]

    # Split dataframe by day
    unique_dates = data_filtered['Shift date'].unique()
    unique_dates = sorted(unique_dates)

    table_by_day = []
    for i in range(len(unique_dates)):
        table_by_day.append(data_filtered[data_filtered['Shift date'] == unique_dates[i]])

    # TRANSFORM DATAFRAME FOR EVERY SINGLE DAY INTO A DATAFRAME WITH THE HOURS AND THE COUNT OF EACH HOUR
    #1.  Create a list with all the shift -> 
    #              list_all_shift =  [ 
    #                                  [shift1, shift2, shift3, ...],
    #                                  [shift1, shift2, shift3, ...],
    #                                  [shift1, shift2, shift3, ...],
    #                                  ...
    #                                ]
    #             shift1 = [start, stop, role]
    #             shift2 = [start, stop, role]
    #             shift3 = [start, stop, role]
    #             ...
    
    list_all_shifts = []
    for i in range(len(table_by_day)):
        all_starts = table_by_day[i]['Paid/Actual StartTime1']
        all_stops  = table_by_day[i]['Paid/Actual StopTime1']
        all_roles  = table_by_day[i]['Division']
        shift_of_the_day = []
        for start, stop, role in zip(all_starts, all_stops, all_roles):
            shift_of_the_day.append([start, stop, role])
        list_all_shifts.append(shift_of_the_day)    
    # get unique roles

    
    #2.  Clean and modify start and end time to be processable
    for i in range(len(list_all_shifts)):
        for j in range(len(list_all_shifts[i])):
            list_all_shifts[i][j][0] = str(list_all_shifts[i][j][0])[:-2] # remove the last two characters
            list_all_shifts[i][j][1] = str(list_all_shifts[i][j][1])[:-2] # remove the last two characters
            if list_all_shifts[i][j][0] == "0" and list_all_shifts[i][j][1] == "0" or list_all_shifts[i][j][0] == 0 and list_all_shifts[i][j][1] == 0:
                continue
            elif list_all_shifts[i][j][1] == "":
                list_all_shifts[i][j][1] = "24"
            elif list_all_shifts[i][j][1] == "0" or list_all_shifts[i][j][1] == 0:
                list_all_shifts[i][j][1] = "24"
            elif list_all_shifts[i][j][1] == "1" or list_all_shifts[i][j][1] == 1:
                list_all_shifts[i][j][1] = "25"
            elif list_all_shifts[i][j][1] == "2" or list_all_shifts[i][j][1] == 2:
                list_all_shifts[i][j][1] = "26"
            elif list_all_shifts[i][j][1] == "3" or list_all_shifts[i][j][1] == 3:
                list_all_shifts[i][j][1] = "27"

    #3. Tranform the list into a list of -> [ [start_time, start_time + 1, start_time +2 ... end_time],
    #                                         [start_time, start_time + 1, start_time +2 ... end_time], 
    #                                         ...]

    list_all_shifts_transformed = []
    roles_all_shifts_tranformed = []
    for e in range(len(list_all_shifts)):
        list_of_day = []
        roles_of_day = []
        for j in range(len(list_all_shifts[e])):
            shift = []
            role_shift = []
            start = list_all_shifts[e][j][0]
            end = list_all_shifts[e][j][1]
            role = list_all_shifts[e][j][2]
            if start == "":
                continue
            else:
                for k in range(int(start), int(end)):
                    shift.append(k)
                    role_shift.append(role)
                list_of_day.append(shift)
                roles_of_day.append(role_shift)


        #4. Merge the list of day into one list -> ndim(1) -> Days = [
        #                                                            [hour, hour, ....] -> day1
        #                                                            [hour, hour, ....] -> day2
        #                                                            ...
        #                                                            [hour, hour, ....] -> dayn
        #                                                            ]
        list_of_day_merged = []
        list_of_roles_merged = []
        for i in range(len(list_of_day)):
            list_of_day_merged.extend(list_of_day[i])
            list_of_roles_merged.extend(roles_of_day[i])

        # Count HOURS EMPLOYEES
        #5. count how many times each value appears
        count_hours = pd.DataFrame([[i, list_of_day_merged.count(i)] for i in list_of_day_merged], columns=['Hour', 'Count Employees'])
        # delete duplicates
        count_hours = count_hours.drop_duplicates()
        # sort by hour
        count_hours = count_hours.sort_values(by=['Hour'])
        # index is hour
        count_hours.index = count_hours['Hour']
        # delete hour column
        count_hours = count_hours.drop(columns=['Hour'])
        # add to list of all days
        list_all_shifts_transformed.append(count_hours)

        # Count ROLES EMPLOYEES
        # count each role in the list of roles
        count_roles = pd.DataFrame([[i, list_of_roles_merged.count(i)] for i in list_of_roles_merged], columns=['Role', 'Count Employees'])
        # delete duplicates
        count_roles = count_roles.drop_duplicates()
        # sort by count
        count_roles = count_roles.sort_values(by=['Count Employees'], ascending=False)
        # change index to role
        count_roles.index = count_roles['Role']
        # delete hour column
        count_roles = count_roles.drop(columns=['Role'])
        # add to list of roles
        roles_all_shifts_tranformed.append(count_roles)
    return list_all_shifts_transformed, roles_all_shifts_tranformed, unique_dates

def create_final_timeseries(uploaded_file_1,uploaded_file_2):
    import pandas as pd
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
