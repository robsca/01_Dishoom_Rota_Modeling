import pandas as pd
import time
import numpy as np
from datetime import timedelta


class Analysis_EMP:
    def __init__(self, data, shop_name = None):
        self.data = data
        if shop_name:
            self.shop_name = shop_name
            # filter the data
            self.data = self.data[self.data['Home'] == self.shop_name]
    # helpers
    def change_type(self, table, column, type):
        table[column] = table[column].astype(type)
        return table

    # main functions
    def lambda_function_to_add_date_forecast(self, x):
        x['Shift date'] = pd.to_datetime(x['Shift date'], format='%d/%m/%Y')
        if x['Rota/Forecast StartTime1'] < x['Rota/Forecast StopTime1']:
            # add the date to the start time
            x['Rota/Forecast StartTime1'] = str(x['Shift date']) + ' ' + x['Rota/Forecast StartTime1']
            # add the date to the stop time
            x['Rota/Forecast StopTime1'] = str(x['Shift date']) + ' ' + x['Rota/Forecast StopTime1']
        elif x['Rota/Forecast StartTime1'] > x['Rota/Forecast StopTime1']:
            # add the date to the start time
            x['Rota/Forecast StartTime1'] = str(x['Shift date']) + ' ' + x['Rota/Forecast StartTime1']
            # add 1 day to the stop time
            x['Rota/Forecast StopTime1'] = str(x['Shift date']) + ' ' + x['Rota/Forecast StopTime1']
            x['Rota/Forecast StopTime1'] = pd.to_datetime(x['Rota/Forecast StopTime1']) + timedelta(days=1)
        else:
            # add nan
            x['Rota/Forecast StartTime1'] = np.nan
            x['Rota/Forecast StopTime1'] = np.nan

        # transform in datetime
        x['Rota/Forecast StartTime1'] = pd.to_datetime(x['Rota/Forecast StartTime1'])
        x['Rota/Forecast StopTime1'] = pd.to_datetime(x['Rota/Forecast StopTime1'])

        # same for the second shift
        if x['Rota/Forecast StartTime2'] < x['Rota/Forecast StopTime2']:
            # add the date to the start time
            x['Rota/Forecast StartTime2'] = str(x['Shift date']) + ' ' + x['Rota/Forecast StartTime2']
            # add the date to the stop time
            x['Rota/Forecast StopTime2'] = str(x['Shift date']) + ' ' + x['Rota/Forecast StopTime2']
        
        elif x['Rota/Forecast StartTime2'] > x['Rota/Forecast StopTime2']:
            # add the date to the start time
            x['Rota/Forecast StartTime2'] = str(x['Shift date']) + ' ' + x['Rota/Forecast StartTime2']
            # add 1 day to the stop time
            x['Rota/Forecast StopTime2'] = str(x['Shift date']) + ' ' + x['Rota/Forecast StopTime2']
            x['Rota/Forecast StopTime2'] = pd.to_datetime(x['Rota/Forecast StopTime2']) + timedelta(days=1)
        else:
            # add nan
            x['Rota/Forecast StartTime2'] = np.nan
            x['Rota/Forecast StopTime2'] = np.nan

        # transform in datetime
        x['Rota/Forecast StartTime2'] = pd.to_datetime(x['Rota/Forecast StartTime2'])
        x['Rota/Forecast StopTime2'] = pd.to_datetime(x['Rota/Forecast StopTime2'])
        return x

    def lambda_function_to_add_date_actual(self, x):
        x['Shift date'] = pd.to_datetime(x['Shift date'], format='%d/%m/%Y')
        if x['Paid/Actual StartTime1'] < x['Paid/Actual StopTime1']:
            # add the date to the start time
            x['Paid/Actual StartTime1'] = str(x['Shift date']) + ' ' + x['Paid/Actual StartTime1']
            # add the date to the stop time
            x['Paid/Actual StopTime1'] = str(x['Shift date']) + ' ' + x['Paid/Actual StopTime1']
        elif x['Paid/Actual StartTime1'] > x['Paid/Actual StopTime1']:
            # add the date to the start time
            x['Paid/Actual StartTime1'] = str(x['Shift date']) + ' ' + x['Paid/Actual StartTime1']
            # add 1 day to the stop time
            x['Paid/Actual StopTime1'] = str(x['Shift date']) + ' ' + x['Paid/Actual StopTime1']
            x['Paid/Actual StopTime1'] = pd.to_datetime(x['Paid/Actual StopTime1']) + timedelta(days=1)
        else:
            # add nan
            x['Paid/Actual StartTime1'] = np.nan
            x['Paid/Actual StopTime1'] = np.nan
        # transform in datetime
        x['Paid/Actual StartTime1'] = pd.to_datetime(x['Paid/Actual StartTime1'])
        x['Paid/Actual StopTime1'] = pd.to_datetime(x['Paid/Actual StopTime1'])

        # same for the second shift
        if x['Paid/Actual StartTime2'] < x['Paid/Actual StopTime2']:
            # add the date to the start time
            x['Paid/Actual StartTime2'] = str(x['Shift date']) + ' ' + x['Paid/Actual StartTime2']
            # add the date to the stop time
            x['Paid/Actual StopTime2'] = str(x['Shift date']) + ' ' + x['Paid/Actual StopTime2']
        elif x['Paid/Actual StartTime2'] > x['Paid/Actual StopTime2']:
            # add the date to the start time
            x['Paid/Actual StartTime2'] = str(x['Shift date']) + ' ' + x['Paid/Actual StartTime2']
            # add 1 day to the stop time
            x['Paid/Actual StopTime2'] = str(x['Shift date']) + ' ' + x['Paid/Actual StopTime2']
            x['Paid/Actual StopTime2'] = pd.to_datetime(x['Paid/Actual StopTime2']) + timedelta(days=1)
        else:
            # add nan
            x['Paid/Actual StartTime2'] = np.nan
            x['Paid/Actual StopTime2'] = np.nan
            
        # transform in datetime
        x['Paid/Actual StartTime2'] = pd.to_datetime(x['Paid/Actual StartTime2'])
        x['Paid/Actual StopTime2'] = pd.to_datetime(x['Paid/Actual StopTime2'])
        return x

    def lambda_function_to_change_time(self, x):
        if len(str(x)) == 1:
            return pd.to_datetime('00:0' + str(x)[-1:], format='%H:%M')
        elif len(str(x)) == 2:
            return pd.to_datetime('00:' + str(x), format='%H:%M')
        elif len(str(x)) > 2:
            return pd.to_datetime(str(str(x)[:-2] + ':' + str(x)[-2:]), format='%H:%M')
        
    def lambda_function_to_calculate_total_hours_worked_actual(self,x):
        # get start time and stop time
        start_time1 = x['Paid/Actual StartTime1']
        stop_time1 = x['Paid/Actual StopTime1']
        start_time2 = x['Paid/Actual StartTime2']
        stop_time2 = x['Paid/Actual StopTime2']
        # calculate the difference
        if pd.isnull(start_time1) == False and pd.isnull(stop_time1) == False:
            hours_difference1 = float(pd.Timedelta(stop_time1 - start_time1).seconds / 60 / 60) # convert to hours
        else:
            hours_difference1 = 0
        if pd.isnull(start_time2) == False and pd.isnull(stop_time2) == False:
            hours_difference2 = float(pd.Timedelta(stop_time2 - start_time2).seconds / 60 / 60) # convert to hours
        else:
            hours_difference2 = 0
        # add the difference to the column
        x['Total hours worked'] = float(hours_difference1) + float(hours_difference2)
        return x

    def lambda_function_to_calculate_total_hours_worked_forecast(self,x):
        # get start time and stop time
        start_time1 = x['Rota/Forecast StartTime1']
        stop_time1 = x['Rota/Forecast StopTime1']
        start_time2 = x['Rota/Forecast StartTime2']
        stop_time2 = x['Rota/Forecast StopTime2']
        # calculate the difference
        if pd.isnull(start_time1) == False and pd.isnull(stop_time1) == False:
            hours_difference1 = float(pd.Timedelta(stop_time1 - start_time1).seconds / 60 / 60) # convert to hours
        else:
            hours_difference1 = 0
        if pd.isnull(start_time2) == False and pd.isnull(stop_time2) == False:
            hours_difference2 = float(pd.Timedelta(stop_time2 - start_time2).seconds / 60 / 60) # convert to hours
        else:
            hours_difference2 = 0
        # add the difference to the column
        x['Total hours worked'] = float(hours_difference1) + float(hours_difference2)
        return x

    # transformations      
    def transformation_(self):
        '''
        This function will transform the data in the following way:
        - change the time format
        - keep only the relevant columns
        - drop the nan values
        - transform in integers the columns that will be used in the timeseries calculations
        '''
        print('----------------')
        print('Transformation 1: started ')
        start_process = time.time()
        # drop the columns
        self.data = self.data.drop(['Unnamed: 0'], axis=1)
        # This are the fundamental informations that I need to reformat -> [Rota/Forecast_group] and [Paid/Actual_group]
        # Create two dataframe for the final result
        self.forecast_col = ['Shift date','Rota/Forecast StartTime1', 'Rota/Forecast StopTime1', # first shift
                                'Rota/Forecast StartTime2', 'Rota/Forecast StopTime2', # second shift
                                    'Rota/Forecast Hours', 'Home', 'Division', 'First Name', 'Surname'] # total hours

        self.actual_col = ['Shift date','Paid/Actual StartTime1', 'Paid/Actual StopTime1',
                                    'Paid/Actual StartTime2', 'Paid/Actual StopTime2',
                                    'Paid/Actual Hours', 'Home', 'Division', 'First Name', 'Surname']
        self.forecast_table = self.data[self.forecast_col]
        self.actual_table = self.data[self.actual_col]

        # from nan to 0
        self.forecast_table = self.forecast_table.fillna(0)
        self.actual_table = self.actual_table.fillna(0)

        # if rota forecast hours is 0, then the start and stop time are 0 so I can drop them
        self.forecast_table = self.forecast_table[self.forecast_table['Rota/Forecast Hours'] != 0]
        self.actual_table = self.actual_table[self.actual_table['Paid/Actual Hours'] != 0]

        # change type
        # forecast table
        self.change_type(self.forecast_table, 'Rota/Forecast StartTime1', int)
        self.change_type(self.forecast_table, 'Rota/Forecast StartTime2', int)
        self.change_type(self.forecast_table, 'Rota/Forecast StopTime1', int)
        self.change_type(self.forecast_table, 'Rota/Forecast StopTime2', int)
        # actual table
        self.change_type(self.actual_table, 'Paid/Actual StartTime1', int)
        self.change_type(self.actual_table, 'Paid/Actual StartTime2', int)
        self.change_type(self.actual_table, 'Paid/Actual StopTime1', int)
        self.change_type(self.actual_table, 'Paid/Actual StopTime2', int)
        end = time.time()
        # print the time with 2 decimal places
        print('Transformation 1 - Completed -  {} seconds'.format(round(end - start_process, 2)))
        print('----------------')

    def _transformation_(self):
        '''
        This function will transform the data in the following way:
        - change the time format apply the "function_to_change_time"

        '''
        print('----------------')
        print('Transformation 2: started ')
        print("Part 1 - (INT to TIME) : Started")
        start_process = time.time()
            # apply function to start1 and stop1
        self.forecast_table['Rota/Forecast StartTime1'] = self.forecast_table['Rota/Forecast StartTime1'].apply(self.lambda_function_to_change_time)
        self.forecast_table['Rota/Forecast StartTime1'] = self.forecast_table['Rota/Forecast StartTime1'].dt.strftime('%H:%M')
        self.forecast_table['Rota/Forecast StopTime1'] = self.forecast_table['Rota/Forecast StopTime1'].apply(self.lambda_function_to_change_time)
        self.forecast_table['Rota/Forecast StopTime1'] = self.forecast_table['Rota/Forecast StopTime1'].dt.strftime('%H:%M')
        # apply function to start2 and stop2
        self.forecast_table['Rota/Forecast StartTime2'] = self.forecast_table['Rota/Forecast StartTime2'].apply(self.lambda_function_to_change_time)
        self.forecast_table['Rota/Forecast StartTime2'] = self.forecast_table['Rota/Forecast StartTime2'].dt.strftime('%H:%M')
        self.forecast_table['Rota/Forecast StopTime2'] = self.forecast_table['Rota/Forecast StopTime2'].apply(self.lambda_function_to_change_time)
        self.forecast_table['Rota/Forecast StopTime2'] = self.forecast_table['Rota/Forecast StopTime2'].dt.strftime('%H:%M')
        # apply function to start1 and stop1
        self.actual_table['Paid/Actual StartTime1'] = self.actual_table['Paid/Actual StartTime1'].apply(self.lambda_function_to_change_time)
        self.actual_table['Paid/Actual StartTime1'] = self.actual_table['Paid/Actual StartTime1'].dt.strftime('%H:%M')
        self.actual_table['Paid/Actual StopTime1'] = self.actual_table['Paid/Actual StopTime1'].apply(self.lambda_function_to_change_time)
        self.actual_table['Paid/Actual StopTime1'] = self.actual_table['Paid/Actual StopTime1'].dt.strftime('%H:%M')
        # apply function to start2 and stop2
        self.actual_table['Paid/Actual StartTime2'] = self.actual_table['Paid/Actual StartTime2'].apply(self.lambda_function_to_change_time)
        self.actual_table['Paid/Actual StartTime2'] = self.actual_table['Paid/Actual StartTime2'].dt.strftime('%H:%M')
        self.actual_table['Paid/Actual StopTime2'] = self.actual_table['Paid/Actual StopTime2'].apply(self.lambda_function_to_change_time)
        self.actual_table['Paid/Actual StopTime2'] = self.actual_table['Paid/Actual StopTime2'].dt.strftime('%H:%M')
        end_1 = time.time()
        print('Part 1 - Completed {}'.format(round(end_1 - start_process, 2)))
        print('Part 2 - (TIME to DATETIME ): Started')
        self.actual_table = self.actual_table.apply(self.lambda_function_to_add_date_actual, axis=1)
        self.forecast_table = self.forecast_table.apply(self.lambda_function_to_add_date_forecast, axis=1)
        end_2 = time.time()
        print('Part 2 - Completed {}'.format(round(end_2 - end_1, 2)))
        end = time.time()
        # print time to process rounded at 2 decimal
        print('Transformation 2 took {} seconds'.format(round(end - start_process, 2)))

    def _transformation(self):
        '''
        This function will calculate the total hours worked for each shift,
        and add a column with the total hours
        '''   
        print('Transformation 3')
        start_process = time.time()
        # create a empty column
        self.actual_table['Total hours worked'] = 0
        self.forecast_table['Total hours worked'] = 0
        # create a function that calculate the total of hours worked
        self.actual_table = self.actual_table.apply(self.lambda_function_to_calculate_total_hours_worked_actual, axis=1)
        self.forecast_table = self.forecast_table.apply(self.lambda_function_to_calculate_total_hours_worked_forecast, axis=1)
        end = time.time()
        print('Transformation 3 took {} seconds'.format(round(end - start_process, 2)))
    # save
    def save(self, act_tab = 'actual_table', for_tab  = 'forecast_table', index = False):
        # save both files to csv
        self.actual_table.to_csv(f'data/{act_tab}.csv', index=index)
        self.forecast_table.to_csv(f'data/{for_tab}.csv', index=index)

    # apply all the transformations
    def transform(self):
        self.transformation_()
        self._transformation_()
        self._transformation()
        self.save()
        return self.actual_table, self.forecast_table

    # analysis
    def get_timeseries_total(self):
        # get min and max date
        min_date = min(self.forecast_table['Shift date'])
        max_date = max(self.forecast_table['Shift date']) 
        # as datetime
        min_date = pd.to_datetime(min_date)
        max_date = pd.to_datetime(max_date) + timedelta(days=1)

        # create a list of dates hour by hour
        dates = pd.date_range(min_date, max_date, freq='H')

        # create a dataframe with the dates
        dates = pd.DataFrame(dates, columns=['date'])

        # calculate the total of workers in that hour
        # iterate every row of the forecast table and count +1 if date is in the range(start, stop)
        dates['total_workers'] = 0

        for _, row in self.forecast_table.iterrows():
            # get start time and stop time
            start_time1 = row['Rota/Forecast StartTime1']
            stop_time1 = row['Rota/Forecast StopTime1']
            start_time2 = row['Rota/Forecast StartTime2']
            stop_time2 = row['Rota/Forecast StopTime2']
            # if start time and stop time are not null
            if pd.isnull(start_time1) == False and pd.isnull(stop_time1) == False:
                # and if the date is in the range
                dates.loc[(dates['date'] >= start_time1) & (dates['date'] <= stop_time1), 'total_workers'] += 1
            if pd.isnull(start_time2) == False and pd.isnull(stop_time2) == False:
                # and if the date is in the range
                dates.loc[(dates['date'] >= start_time2) & (dates['date'] <= stop_time2), 'total_workers'] += 1

        # calculate the total of workers in that hour
        # iterate every row of the actual table and count +1 if date is in the range(start, stop)
        dates['total_workers_actual'] = 0
        for _, row in self.actual_table.iterrows():
            # get start time and stop time
            start_time1 = row['Paid/Actual StartTime1']
            stop_time1 = row['Paid/Actual StopTime1']
            start_time2 = row['Paid/Actual StartTime2']
            stop_time2 = row['Paid/Actual StopTime2']
            # if start time and stop time are not null
            if pd.isnull(start_time1) == False and pd.isnull(stop_time1) == False:
                # and if the date is in the range
                dates.loc[(dates['date'] >= start_time1) & (dates['date'] <= stop_time1), 'total_workers_actual'] += 1
            if pd.isnull(start_time2) == False and pd.isnull(stop_time2) == False:
                # and if the date is in the range
                dates.loc[(dates['date'] >= start_time2) & (dates['date'] <= stop_time2), 'total_workers_actual'] += 1
        
        return dates

if __name__ == '__main__':
    # reading the files
    df_1 = 'data/ActualHoursvRotaHours_2019_8_Aug_RS.csv'
    df_2 = 'data/ActualHoursvRotaHours_2019_9_Sep_RS.csv'
    df_3 = 'data/ActualHoursvRotaHours_2019_10_Oct_RS.csv'
    df_1_2019 = pd.read_csv(df_1)
    df_2_2019 = pd.read_csv(df_2)
    df_3_2019 = pd.read_csv(df_3)

    # merge the 3 dataframes from 2019
    df_2019 = pd.concat([df_1_2019, df_2_2019, df_3_2019], axis=0)
    # get all restaurants
    restaurants = df_2019['Home'].unique()
    # for each restaurant
    for i, restaurant in enumerate(restaurants):
        print('Press {} to process {}'.format(i, restaurant))
    # get the input
    input_ = input('Please select a restaurant: ')
    # get the restaurant
    restaurant = restaurants[int(input_)]


    # create a new object
    DATA_2019 = Analysis_EMP(df_2019, restaurant)
    forecast_table, actual_table = DATA_2019.transform()

    #show the data
    print(forecast_table.head())
    print(actual_table.head())
    print('it worked')
    