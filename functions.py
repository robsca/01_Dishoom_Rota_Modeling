import pandas as pd

# clean errors in the data
# if guest_count >= 25, then the number of guest is the gross sales//average spent per guest


def filter(data, start_date, end_date, restaurant):
    '''
    This function takes the data, the start date and the end date, and the list of restaurants.
    It adds the Name of the day of the week to the dataframe,
    and returns the dataframe filtered by the time period.
    '''
    data_filtered = data[(data['Date'] >= start_date) & (data['Date'] <= end_date)]
    data_filtered = data_filtered[data_filtered['Store_Name'] == restaurant]
    
    #for every row in the dataframe if the gross
    for index, row in data_filtered.iterrows():
        # if the guest count is greater than 25, then the number of guest is the gross sales//average spent per guest
        if row['Guest_Count'] >= 25:
            data_filtered.at[index, 'Guest_Count'] = row['Gross_Sales']//25
    return data_filtered

def get_empoloyees_hours_day_by_day_grouped_by_hour_(path, restaurant, start_date, end_date):
    # open xlsx file
    data = pd.read_excel(path)
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

    # Filter data by restaurant and date
    data_filtered = data[(data['Shift date'] >= start_date) & (data['Shift date'] <= end_date)]
    restaurant = restaurant.split("-")[1].strip(" ")  # clean the restaurant Name
    data_filtered = data_filtered[data_filtered['Home']==restaurant]

    # Split dataframe by day
    unique_dates = data_filtered['Shift date'].unique()
    unique_dates = sorted(unique_dates)
    table_by_day = []
    for i in range(len(unique_dates)):
        table_by_day.append(data_filtered[data_filtered['Shift date'] == unique_dates[i]])
    
    # TRANSFORM DATAFRAME FOR EVERY SINGLE DAY INTO A DATAFRAME WITH THE HOURS AND THE COUNT OF EACH HOUR
    #1.  Create a list with all the shift -> 
    #              list_all_shift =  [ 
    #                                  [shift1, shift2, shift3, ...], -> day 1
    #                                  [shift1, shift2, shift3, ...], -> day 2
    #                                  [shift1, shift2, shift3, ...], -> day 3
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
    for e in range(len(list_all_shifts)):
        list_of_day = []
        for j in range(len(list_all_shifts[e])):
            shift = []
            start = list_all_shifts[e][j][0]
            end = list_all_shifts[e][j][1]
            if start == "":
                continue
            else:
                for k in range(int(start), int(end)):
                    shift.append(k)
                list_of_day.append(shift)

        #4. Merge the list of day into one list
        list_of_day_merged = []
        for i in range(len(list_of_day)):
            list_of_day_merged.extend(list_of_day[i])
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
        list_all_shifts_transformed.append(count_hours)

    return list_all_shifts_transformed

def get_empoloyees_hours_day_by_day_grouped_by_hour(data, restaurant, start_date, end_date):
    # open xlsx file
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

    # Filter data by restaurant and date
    data_filtered = data[(data['Shift date'] >= start_date) & (data['Shift date'] <= end_date)]
    restaurant = restaurant.split("-")[1].strip(" ")  # clean the restaurant Name
    data_filtered = data_filtered[data_filtered['Home']==restaurant]

    # Split dataframe by day
    unique_dates = data_filtered['Shift date'].unique()
    unique_dates = sorted(unique_dates)
    table_by_day = []
    for i in range(len(unique_dates)):
        table_by_day.append(data_filtered[data_filtered['Shift date'] == unique_dates[i]])
    
    # TRANSFORM DATAFRAME FOR EVERY SINGLE DAY INTO A DATAFRAME WITH THE HOURS AND THE COUNT OF EACH HOUR
    #1.  Create a list with all the shift -> 
    #              list_all_shift =  [ 
    #                                  [shift1, shift2, shift3, ...], -> day 1
    #                                  [shift1, shift2, shift3, ...], -> day 2
    #                                  [shift1, shift2, shift3, ...], -> day 3
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
    for e in range(len(list_all_shifts)):
        list_of_day = []
        for j in range(len(list_all_shifts[e])):
            shift = []
            start = list_all_shifts[e][j][0]
            end = list_all_shifts[e][j][1]
            if start == "":
                continue
            else:
                for k in range(int(start), int(end)):
                    shift.append(k)
                list_of_day.append(shift)

        #4. Merge the list of day into one list
        list_of_day_merged = []
        for i in range(len(list_of_day)):
            list_of_day_merged.extend(list_of_day[i])
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
        list_all_shifts_transformed.append(count_hours)

    return list_all_shifts_transformed

def get_store_data_day_by_day_grouped_by_hour(path, restaurant, start_date, end_date, measure = 'Guest_Count'):
    df = pd.read_csv(path)
    # for every row in the dataframe if the gross 
    data_single_store = filter(df, start_date, end_date, restaurant)
    # Filter data taking only the store
    data_single_store = pd.DataFrame(data_single_store[data_single_store['Store_Name'] == restaurant])
    data_single_store = data_single_store.drop(columns=['Store_Name'])
    # Get unique dates
    dates = data_single_store['Date'].unique()
    dates = sorted(dates)
    table_by_date = []
    for date in dates:
        day = data_single_store[data_single_store['Date'] == date]
        day = day.drop(columns=['Date'])
        # Group by hour and count how many times each hour appears
        day = day.set_index('Hour')
        day = day.groupby(day.index).sum()
        # guest count is int
        day = day[measure].astype(int)
        table_by_date.append(pd.DataFrame(day))
    return table_by_date
    
def get_ratio_GUESTvs_EMPLOYEE(pathGUEST, pathEMPLOYEE, restaurant, start_date, end_date):
    # import data
    employees_data_2022 = get_empoloyees_hours_day_by_day_grouped_by_hour(pathEMPLOYEE, restaurant, start_date, end_date)
    guests_data_2022 = get_store_data_day_by_day_grouped_by_hour(pathGUEST, restaurant, start_date, end_date)
    
    '''
    Iterate through the days and compare the number of employees and guests

    '''
    ratio_GUESTvsEMPLOYEE = []
    for day in range(len(employees_data_2022)):
        day_df = []
        day_2022_empl = employees_data_2022[day]
        day_2022_guest = guests_data_2022[day]

        for hour in day_2022_empl.index:
            if hour in day_2022_guest.index:
                number_of_employees = day_2022_empl[day_2022_empl.index == hour]['Count Employees'].values[0]
                number_of_guest = day_2022_guest.loc[hour].values[0]
                ratio = number_of_guest/number_of_employees
                row = [hour,ratio]
                # select a specific index
            else:
                ratio = 0
                row = [hour, ratio]

            day_df.append(row)
        day_df = pd.DataFrame(day_df, columns=['Hour', 'Ratio'])
        ratio_GUESTvsEMPLOYEE.append(day_df)
    return ratio_GUESTvsEMPLOYEE

def calculate_moving_average(lst, window_size, verbose=False):
    '''
    Calculate moving average of a list of values with a window size,
    returns a list of same length with the moving average values.
    '''
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

def get_empoloyees_hours_day_by_day_grouped_by_hour_role(path, restaurant, choice_of_departments):
    # open xlsx file
    data = pd.read_excel(path)
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

    # Filter data by restaurant
    restaurant = restaurant.split("-")[1].strip(" ")  # clean the restaurant Name
    if choice_of_departments != 'All':
        data_filtered = data_filtered[data_filtered['Division']==choice_of_departments]

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
    return list_all_shifts_transformed, roles_all_shifts_tranformed

def get_empoloyees_hours_day_by_day_grouped_by_hour_role_(data, restaurant, start_date, end_date, choice_of_departments):
    # open xlsx file
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

    # Filter data by restaurant and date
    data_filtered = data[(data['Shift date'] >= start_date) & (data['Shift date'] <= end_date)]
    restaurant = restaurant.split("-")[1].strip(" ")  # clean the restaurant Name
    data_filtered = data_filtered[data_filtered['Home']==restaurant]
    if choice_of_departments != 'All':
        data_filtered = data_filtered[data_filtered['Division']==choice_of_departments]

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
    return list_all_shifts_transformed, roles_all_shifts_tranformed

