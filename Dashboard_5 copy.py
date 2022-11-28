import pandas as pd

class Aloha_DATA:
    def __init__(self, df):
        self.df = df
        self.df_ = df.copy()
        self.unique_restaurants = df['Store_Name'].unique()
        self.day_parts = self.df['Day_Part_Name'].unique() 
        # take off late night
        self.day_parts = self.day_parts[self.day_parts != 'Late Night']

    def preprocess(self):
        self.df = self.df[self.df['Net_Sales'] != 0] # if net sales == 0 drop the row
        self.df = self.df[self.df['Guest_Count'] != 0] # if guest count == 0 drop the row
        self.df = self.df[self.df['Net_Sales'] != self.df['Void_Total']]  # if net sales == total void drop the row

    def get_SPH(self, save = False, name = 'SPH_'):
        self.df = self.df[self.df['Guest_Count'] <= 25] # take off guest_count > 25 - probably a mistake
        self.df['Spent_per_head'] = self.df['Net_Sales']/self.df['Guest_Count'] # create a new columns calls Spent Per Head
        
        SPH_list_2019 = []
        for restaurant in self.unique_restaurants:                                  # for each restaurant
            df1_restaurant = self.df[self.df['Store_Name'] == restaurant]                   # filter out the the other restaurants
            for day_part in self.day_parts:                                                 # for each day part      
                df_day_part = df1_restaurant[df1_restaurant['Day_Part_Name'] == day_part]       # filter out the other day parts
                SPH_ = df_day_part['Spent_per_head'].mean()                                     # get the mean of the SPH at that day part
                SPH_list_2019.append([restaurant, SPH_, day_part])                              # add to the list 

        # transform the list into a dataframe
        SPH = pd.DataFrame(SPH_list_2019, columns=['Store_Name', 'Spent_per_head', 'Day_Part_Name'])
        # 3. take off day part late night
        SPH = SPH[SPH['Day_Part_Name'] != 'Late Night']
        # 4. save the data
        if save:
            SPH.to_csv(f'data/{name}.csv', index=False)
        self.SPH_table = SPH
        return SPH

    def normalize_df(self, save = False, name = 'df1'):
        # add spent per head to the original dataframes store name and day part
        self.df = self.df.merge(self.SPH_table, on=['Store_Name', 'Day_Part_Name'])
        # if guest_count is > 25 divide sales by SPH of the restaurant
        self.df['Guest_Count'] = self.df.apply(lambda x: x['Net_Sales']//x['Spent_per_head'] if x['Guest_Count'] > 25 else x['Guest_Count'], axis=1)
        # save the dataframes
        self.df.to_csv(f'data/{name}.csv', index=False)

    def create_timeseries_covers(self, save = False, name = 'covers'):
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
        # if name contain '-'replace it with only the second part of the name
        df['Store_Name'] = df.apply(lambda x: x['Store_Name'].split('-')[1] if '-' in x['Store_Name'] else x['Store_Name'], axis=1)
        restaurants = df['Store_Name'].unique()
        # modify the restaurants name to match the employees data
        # divide at - and take the first part
        frame = []
        for restaurant in restaurants:
            # 3. Create a dataframe for each restaurant
            # filter data for each restaurant
            df_restaurant = df[df['Store_Name'] == restaurant]
            # 4. Group by date
            df_restaurant = df_restaurant.groupby('Date').sum(numeric_only=True) # if error take out numeric_only=True or try adding columns
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
        df = df[features]
        # save the data
        if save:
            df.to_csv(f'data/{name}.csv', index=False)
        return df

    def create_heatmap(self):
        pass
        
# try to create a class for the employees data
url = 'data/Aloha_Sales_Data_Export_2019.csv'
df = pd.read_csv(url)
data_2019 = Aloha_DATA(df)
data_2019.get_SPH(save = False)
print(data_2019.SPH_table)
print(data_2019.df)

'''
    # DATA 
    #---
    if choosen == 'heatmap':
     
        # 1. Select the restaurant
        restaurant = st.sidebar.selectbox('Select restaurant', restaurants)
        
        # 2. Filter the data
        if restaurant != 'All Restaurant':
            # filter out not choosen restaurants
            covers2019 = covers2019[covers2019['Store_Name'] == restaurant]
            covers2022 = covers2022[covers2022['Store_Name'] == restaurant]

        #---
        #3. Filter out hours < 9 and > 22
        covers2019 = covers2019[covers2019['Hour'] >= 9]
        covers2019 = covers2019[covers2019['Hour'] <= 23]
        covers2022 = covers2022[covers2022['Hour'] >= 9]
        covers2022 = covers2022[covers2022['Hour'] <= 23]
        
        # 4. Trasform the data in a matrix arrays -> rows = days, columns = hours
        data_guest_heatmap_2019 = create_heatmap_data_weekly(data= covers2019)
        data_guest_heatmap_2022 = create_heatmap_data_weekly(data= covers2022)
        
        # 5. Create the heatmap
        heatmap_2019 = plot_heatmap(data_guest_heatmap_2019, 'Covers 2019', show=False)
        heatmap_2022 = plot_heatmap(data_guest_heatmap_2022, 'Covers 2022', show=False)
        
        # 6. Create the SPH graphs
        SPH_fig_2019 = plot_SPH(SPH_2019, restaurant, show=False)
        SPH_fig_2022 = plot_SPH(SPH_2022, restaurant, show=False)

        # 7. Create the weekly totals
        weekly_covers_fig_2019, totals_2019 = plot_week_totals_typical_week(data_guest_heatmap_2019, 'Weekly Covers 2019', show=False)
        weekly_covers_fig_2022, totals_2022 = plot_week_totals_typical_week(data_guest_heatmap_2022, 'Weekly Covers 2022', show=False)

        # 8. Create the day_part_plot
        day_part_covers_fig_2019 = plot_day_part_covers(data_guest_heatmap_2019, 'Day Part Covers 2019', show=False)
        day_part_covers_fig_2022 = plot_day_part_covers(data_guest_heatmap_2022, 'Day Part Covers 2022', show=False)

        # 9. Create heatmap differences
        difference_between_years = data_guest_heatmap_2022 - data_guest_heatmap_2019
        difference_between_years = difference_between_years.round(0)         # round to 0 decimal
        # take out the day_part values
        hours = difference_between_years.columns[:-4] # the last 4 columns are totals - breakfast, lunch, dinner, total
        # create the heatmap
        difference_between_years_fig = plot_heatmap(difference_between_years[hours], 'Difference between years', show=False)

        # 10. Create the difference between years in %
        difference_between_years = data_guest_heatmap_2022 - data_guest_heatmap_2019
        difference_between_years = difference_between_years/data_guest_heatmap_2019 * 100
        difference_between_years = difference_between_years.round(0)
        hours = difference_between_years.columns[:-4]
        # create the heatmap
        difference_between_years_fig_percentage = plot_heatmap(difference_between_years[hours], 'Difference between years', show=False)
        
        
        # 11. 
        # 1. Day_Part Differences -> last 4 columns -> breakfast, lunch, afternoon, dinner
        day_parts = difference_between_years.columns[-4:]
        fig_day_part_ = go.Figure()
        for day_part in day_parts:
            fig_day_part_.add_trace(go.Bar(x=difference_between_years.index, y=difference_between_years[day_part], name=f'{day_part}'))
        fig_day_part_.update_layout(title='DAY PART - Differences - 2019 vs 2022 in %')

        # 2 . Graph Weekly Covers 2019vs2022
        fig_2019_2022 = go.Figure()
        fig_2019_2022.add_trace(go.Scatter(x=totals_2019.index, y=totals_2019['Total'], name='2019', fill = 'tozeroy'))
        fig_2019_2022.add_trace(go.Scatter(x=totals_2022.index, y=totals_2022['Total'], name='2022', fill = 'tozeroy'))
        fig_2019_2022.update_layout(title='Weekly Covers 2019 vs 2022')

        #----------------- #
        # Difference between years Bar Chart
        # filter restaurants
        SPH_2019 = SPH_2019[SPH_2019['Store_Name'] == restaurant]
        SPH_2022 = SPH_2022[SPH_2022['Store_Name'] == restaurant]
        # get difference
        sph_diff = SPH_2022['Spent_per_head'] - SPH_2019['Spent_per_head']
        # create a dataframe
        SPH_DIFF = {'Day_Part_Name': SPH_2019['Day_Part_Name'], 'Difference': sph_diff}
        # add store name
        SPH_DIFF['Store_Name'] = restaurant
        # create dataframe
        SPH_DIFF = pd.DataFrame(SPH_DIFF)

        diff_sph_fig = go.Figure()
        diff_sph_fig.add_trace(go.Scatter(x=SPH_DIFF['Day_Part_Name'], y=SPH_DIFF['Difference'], name='Difference'))
        # add 2019
        diff_sph_fig.add_trace(go.Bar(x=SPH_DIFF['Day_Part_Name'], y=SPH_2019['Spent_per_head'], name='2019'))
        # add 2022
        diff_sph_fig.add_trace(go.Bar(x=SPH_DIFF['Day_Part_Name'], y=SPH_2022['Spent_per_head'], name='2022'))
        diff_sph_fig.update_layout(title='Difference SPH 2019 vs 2022')

        
        # -----------------
        # SHOW ALL GRAPHS -> file 1
        with st.expander(f'{restaurant} - 2019'):
            c1,c2 = st.columns(2)
            c1.plotly_chart(heatmap_2019)
            c1.plotly_chart(day_part_covers_fig_2019)
            c2.plotly_chart(weekly_covers_fig_2019)
            c2.plotly_chart(SPH_fig_2019)

        # -----------------
        # SHOW ALL GRAPHS -> file 2
        with st.expander(f'{restaurant} - 2022'):
            c1,c2 = st.columns(2)
            c1.plotly_chart(heatmap_2022)
            c1.plotly_chart(day_part_covers_fig_2022)
            c2.plotly_chart(weekly_covers_fig_2022)
            c2.plotly_chart(SPH_fig_2022)
        
        # ----------------- #
        
        # SHOW ALL GRAPHS -> difference between files
        with st.expander(f'{restaurant} - 2019 vs 2022'):
            c1,c2 = st.columns(2)
            # row 1
            c1.plotly_chart(difference_between_years_fig)
            c2.plotly_chart(difference_between_years_fig_percentage)
            # row 2
            c1.plotly_chart(diff_sph_fig)
            c2.plotly_chart(fig_day_part_)
            # row 3
            st.plotly_chart(fig_2019_2022, use_container_width=True)

    # ----------------- #
    
    elif choosen == 'month':
        # get files
        df1_open = df1.copy()
        df2_open = df2.copy()

        df1_open = add_month_and_week_number(df1_open)
        df2_open = add_month_and_week_number(df2_open)

        covers2019 = add_month_and_week_number(covers2019)
        covers2022 = add_month_and_week_number(covers2022)

        c_2019 = covers2019.copy()
        c_2022 = covers2022.copy()

        # 1. Select restarants
        restaurant = st.sidebar.selectbox('Select restaurant', restaurants)
        
        # 3. Select month
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        month = st.sidebar.selectbox('Select month', months)
        
        # 4. Filter by month
        df1_open = df1_open[df1_open['Month'] == months.index(month)+1]
        df2_open = df2_open[df2_open['Month'] == months.index(month)+1]
        covers2019 = covers2019[covers2019['Month'] == months.index(month)+1]
        covers2022 = covers2022[covers2022['Month'] == months.index(month)+1]
        # 5. Drop month and week columns
        df1_open = df1_open.drop(['Month', 'Week_Number'], axis=1)
        df2_open = df2_open.drop(['Month', 'Week_Number'], axis=1)
        covers2019 = covers2019.drop(['Month', 'Week_Number'], axis=1)
        covers2022 = covers2022.drop(['Month', 'Week_Number'], axis=1)
        # 6. Get SPH Data
        SPH_2019, SPH_2022 = get_SPH(df1_open, df2_open)
        # 7. Get plot of SPHs, filter by restaurant
        SHP_2019_month = plot_SPH(SPH_2019, restaurant, f'SPH - 2019 - {restaurant}', False)
        SHP_2022_month = plot_SPH(SPH_2022, restaurant, f'SPH - 2022 - {restaurant}', False)
        
        # 8. Filter by restaurant
        if restaurant != 'All Restaurant':
            # filter out not choosen restaurants
            covers2019 = covers2019[covers2019['Store_Name'] == restaurant]
            covers2022 = covers2022[covers2022['Store_Name'] == restaurant]
            df1_open = df1_open[df1_open['Store_Name'] == restaurant]
            df2_open = df2_open[df2_open['Store_Name'] == restaurant]
            SPH_2019 = SPH_2019[SPH_2019['Store_Name'] == restaurant]
            SPH_2022 = SPH_2022[SPH_2022['Store_Name'] == restaurant]
        
        # 9. Filter out hours < 9 and > 22
        covers2019 = covers2019[covers2019['Hour'] >= 9]
        covers2019 = covers2019[covers2019['Hour'] <= 22]
        covers2022 = covers2022[covers2022['Hour'] >= 9]
        covers2022 = covers2022[covers2022['Hour'] <= 22]

        # 10. Create Heatmaps
        data_guest_heatmap_2019 = create_heatmap_data_weekly(covers2019)
        data_guest_heatmap_2022 = create_heatmap_data_weekly(covers2022)
        
        heatmap_2019_month = plot_heatmap(data_guest_heatmap_2019, f'Hour by Hour Volume - 2019 - {restaurant}', False)
        heatmap_2022_month = plot_heatmap(data_guest_heatmap_2022, f'Hour by Hour Volume - 2022 - {restaurant}', False)

        # 11. Plot week_totals_typicalß
        week_average_2019_f, totals_2019 = plot_week_totals_typical_week(data_guest_heatmap_2019, f'Day of the Week - 2019 - {restaurant}', False)
        week_average_2022_f, totals_2022 = plot_week_totals_typical_week(data_guest_heatmap_2022, f'Day of the Week - 2022 - {restaurant}', False)

        # 12 Plot day_part_covers
        day_part_covers_fig_2019 = plot_day_part_covers(data_guest_heatmap_2019, f'Day Part - 2019 - {restaurant}', False)
        day_part_covers_fig_2022 = plot_day_part_covers(data_guest_heatmap_2022, f'Day Part - 2022 - {restaurant}', False)
        
        # 13. Plot difference between years
        difference_between_years = data_guest_heatmap_2022 - data_guest_heatmap_2019
        difference_between_years = difference_between_years.round(0)
        hours = difference_between_years.columns[:-4]
        difference_between_years_fig = plot_heatmap(difference_between_years[hours], 'Difference', False)

        # 14. Plot difference between years in percentage
        difference_between_years = data_guest_heatmap_2022 - data_guest_heatmap_2019
        difference_between_years = difference_between_years/data_guest_heatmap_2019 * 100
        difference_between_years = difference_between_years.round(0)
        hours = difference_between_years.columns[:-4]
        difference_between_years_percentage_fig = plot_heatmap(difference_between_years[hours], f'Difference 2019 ~ 2022 - {restaurant}', False)

        # 15
        # 1. Graph day_part - plot as bar the last 4 columns in heatmap data (day_part) == 'Breakfast', 'Lunch', 'Afternoon', 'Dinner'
        day_parts = difference_between_years.columns[-4:]
        fig_day_part_ = go.Figure()
        for day_part in day_parts:
            fig_day_part_.add_trace(go.Bar(x=difference_between_years.index, y=difference_between_years[day_part], name=f'{day_part}'))
        fig_day_part_.update_layout(title='DAY PART - Differences - 2019 vs 2022 in %')
        #-----------------#
        # 2. Graph totals_2019-2022
        fig_2019_2022 = go.Figure()
        fig_2019_2022.add_trace(go.Scatter(x=totals_2019.index, y=totals_2019['Total'], name='2019', fill = 'tozeroy'))
        fig_2019_2022.add_trace(go.Scatter(x=totals_2022.index, y=totals_2022['Total'], name='2022', fill = 'tozeroy'))
        fig_2019_2022.update_layout(title='Weekly Covers 2019 vs 2022')
        #----------------- #
        # 3. Graph SPH 2019-2022 differences
        SPH_DIFF = SPH_2022['Spent_per_head'] - SPH_2019['Spent_per_head']
        SPH_DIFF = {'Day_Part_Name': SPH_2019['Day_Part_Name'], 'Difference': SPH_DIFF}
        SPH_DIFF['Store_Name'] = restaurant
        SPH_DIFF = pd.DataFrame(SPH_DIFF)
        
        diff_sph_fig = go.Figure()
        diff_sph_fig.add_trace(go.Scatter(x=SPH_DIFF['Day_Part_Name'], y=SPH_DIFF['Difference'], name='Difference'))
        diff_sph_fig.add_trace(go.Bar(x=SPH_DIFF['Day_Part_Name'], y=SPH_2019['Spent_per_head'], name='2019'))
        diff_sph_fig.add_trace(go.Bar(x=SPH_DIFF['Day_Part_Name'], y=SPH_2022['Spent_per_head'], name='2022'))
        diff_sph_fig.update_layout(title=f'Difference SPH 2019 vs 2022 {restaurant} - {month}')
        
    # 16. create dataframe = month and totals
        # filter c_2019 and c_2022 by restaurant
        c_2019 = c_2019[c_2019['Store_Name'] == restaurant]
        c_2022 = c_2022[c_2022['Store_Name'] == restaurant]

        # apply function
        month_df_2019 = get_month_totals(c_2019)
        month_df_2022 = get_month_totals(c_2022)
        # plot 2019
        year_month_by_month_2019 = go.Figure()
        year_month_by_month_2019.add_trace(go.Scatter(x=month_df_2019.index, y=month_df_2019['Guest_Count'], name='2019'))
        # plot 2022
        year_month_by_month_2022 = go.Figure()
        year_month_by_month_2022.add_trace(go.Scatter(x=month_df_2022.index, y=month_df_2022['Guest_Count'], name='2022'))
        # plot difference
        month_df_2019['Guest_Count'] = month_df_2019['Guest_Count'].astype(int)
        month_df_2022['Guest_Count'] = month_df_2022['Guest_Count'].astype(int)
        diff_months = month_df_2022['Guest_Count'] - month_df_2019['Guest_Count']
        # as percentage
        diff_months = diff_months/month_df_2019['Guest_Count'] * 100
        diff_months = {'Month': month_df_2019.index, 'Difference': diff_months}
        diff_months = pd.DataFrame(diff_months)
        # make subplot and set second y axis
        from plotly.subplots import make_subplots
        diff_months_fig = make_subplots(specs=[[{"secondary_y": True}]])
        diff_months_fig.add_trace(go.Scatter(x=diff_months['Month'], y=diff_months['Difference'], name='Difference', fill = 'tonexty'), secondary_y=True)
        diff_months_fig.add_trace(go.Bar(x=diff_months['Month'], y=month_df_2019['Guest_Count'], name='2019', opacity=0.6), secondary_y=False)
        diff_months_fig.add_trace(go.Bar(x=diff_months['Month'], y=month_df_2022['Guest_Count'], name='2022', opacity= 0.6), secondary_y=False)
        
        # 17. Create a plot month by month that show day_part
        #2019
        breakfast_2019 = day_part_month_totals(c_2019, 'Breakfast')
        lunch_2019 = day_part_month_totals(c_2019, 'Lunch')
        afternoon_2019 = day_part_month_totals(c_2019, 'Afternoon')
        dinner_2019 = day_part_month_totals(c_2019, 'Dinner')
        #2022
        breakfast_2022 = day_part_month_totals(c_2022, 'Breakfast')
        lunch_2022 = day_part_month_totals(c_2022, 'Lunch')
        afternoon_2022 = day_part_month_totals(c_2022, 'Afternoon')
        dinner_2022 = day_part_month_totals(c_2022, 'Dinner')

        #
        day_part_month_by_month_2019 = go.Figure()
        day_part_month_by_month_2019.add_trace(go.Bar(x=breakfast_2019.index, y=breakfast_2019['Guest_Count'], name='Breakfast 2019', opacity=0.6))
        day_part_month_by_month_2019.add_trace(go.Bar(x=lunch_2019.index, y=lunch_2019['Guest_Count'], name='Lunch 2019', opacity=0.6))
        day_part_month_by_month_2019.add_trace(go.Bar(x=afternoon_2019.index, y=afternoon_2019['Guest_Count'], name='Afternoon 2019', opacity=0.6))
        day_part_month_by_month_2019.add_trace(go.Bar(x=dinner_2019.index, y=dinner_2019['Guest_Count'], name='Dinner 2019', opacity=0.6))

        #  
        day_part_month_by_month_2022 = go.Figure()
        day_part_month_by_month_2022.add_trace(go.Bar(x=breakfast_2022.index, y=breakfast_2022['Guest_Count'], name='Breakfast 2022', opacity=0.6))
        day_part_month_by_month_2022.add_trace(go.Bar(x=lunch_2022.index, y=lunch_2022['Guest_Count'], name='Lunch 2022', opacity=0.6))
        day_part_month_by_month_2022.add_trace(go.Bar(x=afternoon_2022.index, y=afternoon_2022['Guest_Count'], name='Afternoon 2022', opacity=0.6))
        day_part_month_by_month_2022.add_trace(go.Bar(x=dinner_2022.index, y=dinner_2022['Guest_Count'], name='Dinner 2022', opacity=0.6))
        # 

        # get differences 
        diff_break = breakfast_2022['Guest_Count'] - breakfast_2019['Guest_Count']
        diff_break = diff_break.fillna(0)
        diff_lunch = lunch_2022['Guest_Count'] - lunch_2019['Guest_Count']
        diff_lunch = diff_lunch.fillna(0)
        diff_after = afternoon_2022['Guest_Count'] - afternoon_2019['Guest_Count']
        diff_after = diff_after.fillna(0)
        diff_dinner = dinner_2022['Guest_Count'] - dinner_2019['Guest_Count']
        diff_dinner = diff_dinner.fillna(0)
        # as percentage
        diff_break = diff_break/breakfast_2019['Guest_Count'] * 100
        diff_lunch = diff_lunch/lunch_2019['Guest_Count'] * 100
        diff_after = diff_after/afternoon_2019['Guest_Count'] * 100
        diff_dinner = diff_dinner/dinner_2019['Guest_Count'] * 100
        
        # -----------------
        # SHOW ALL GRAPHS - file 1
        with st.expander(f'{month} - {restaurant} - 2019'):
            c1,c2 = st.columns(2)
            c1.plotly_chart(heatmap_2019_month)
            c1.plotly_chart(day_part_covers_fig_2019)
            c2.plotly_chart(week_average_2019_f)
            c2.plotly_chart(SHP_2019_month)
            st.plotly_chart(day_part_month_by_month_2019, use_container_width=True) # ok

        # SHOW ALL GRAPHS - file 2
        with st.expander(f'{month} - {restaurant} - 2022'):
            c1,c2 = st.columns(2)
            c1.plotly_chart(heatmap_2022_month)
            c1.plotly_chart(day_part_covers_fig_2022)
            c2.plotly_chart(week_average_2022_f)
            c2.plotly_chart(SHP_2022_month)
            st.plotly_chart(day_part_month_by_month_2022, use_container_width=True) # ok


        # PLOT ALL GRAPHS - difference between files
        with st.expander(f'{month} - {restaurant} - 2019 vs 2022'):
            c1,c2 = st.columns(2)
            # row 1
            c1.plotly_chart(difference_between_years_fig)
            c2.plotly_chart(difference_between_years_percentage_fig)
            # row 2
            c1.plotly_chart(diff_sph_fig)
            c2.plotly_chart(fig_day_part_)
            # row 3
            st.plotly_chart(fig_2019_2022, use_container_width=True)
            st.plotly_chart(diff_months_fig, use_container_width=True) # ok


    # ----------------- #

    elif choosen == 'week':
        week_number = st.sidebar.slider('Select a week', min_value=1, max_value=52, value=1, step=1)
        df1_open = df1.copy()
        df2_open = df2.copy()

        restaurant = st.sidebar.selectbox('Select a restaurant', restaurants)
        # filter out unnecessary restaurants
        if restaurant == 'All':
            pass

        # modify restaurants name
        df1_open['Store_Name'] = df1_open.apply(lambda x: x['Store_Name'].split('-')[1] if '-' in x['Store_Name'] else x['Store_Name'], axis=1)
        df2_open['Store_Name'] = df2_open.apply(lambda x: x['Store_Name'].split('-')[1] if '-' in x['Store_Name'] else x['Store_Name'], axis=1)
        # filter by restaurant
        df1_open = df1_open[df1_open['Store_Name'] == restaurant]
        df2_open = df2_open[df2_open['Store_Name'] == restaurant]

        # ----------------- #
        look_up_table = pd.read_csv('CalendarLookupTable.csv')
        # from date to str
        look_up_table['Date'] = look_up_table['Date'].astype(str)
        # change the separator
        look_up_table['Date'] = look_up_table['Date'].str.replace('/', '-')
        # concatenate the dates from day, month and year
        look_up_table['Date'] = look_up_table['Date'].astype(str) + '-' + look_up_table['Month'].astype(str) + '-' + look_up_table['Year'].astype(str)
        # translate to datetime only the date
        look_up_table['Date'] = pd.to_datetime(look_up_table['Date'])
        # translate to datetime only the date
        look_up_table['Date'] = look_up_table['Date'].dt.strftime('%d-%m-%Y')
        #st.write(look_up_table)

        # ----------------- #
        # change format in order to be able to merge
        # to datetime
        df1_open['Date'] = pd.to_datetime(df1_open['Date'])
        df2_open['Date'] = pd.to_datetime(df2_open['Date'])
        # to string
        df1_open['Date'] = df1_open['Date'].dt.strftime('%d-%m-%Y')
        df2_open['Date'] = df2_open['Date'].dt.strftime('%d-%m-%Y')

        # merge the two dataframes
        df1_open = pd.merge(df1_open, look_up_table, how='left', left_on='Date', right_on='Date')
        df2_open = pd.merge(df2_open, look_up_table, how='left', left_on='Date', right_on='Date')

        # filter out unnecessary weeks
        df1_open = df1_open[df1_open['Week Number'] == week_number]
        df2_open = df2_open[df2_open['Week Number'] == week_number]

        #st.write(df1_open)
        #st.write(df2_open)

        covers2019 = create_timeries_covers(df1_open)
        covers2022 = create_timeries_covers(df2_open)

        SPH_2019, SPH_2022 = get_SPH(df1_open, df2_open)

        # get start and end date of the week
        start_date_2019 = df1_open['Date'].min()
        end_date_2019 = df1_open['Date'].max()

        start_date_2022 = df2_open['Date'].min()
        end_date_2022 = df2_open['Date'].max()

        # keep only the date
        start_date_2019 = str(start_date_2019).split(' ')[0]
        end_date_2019 = str(end_date_2019).split(' ')[0]

        start_date_2022 = str(start_date_2022).split(' ')[0]
        end_date_2022 = str(end_date_2022).split(' ')[0]
        
        st.subheader(f'Week {week_number} - {restaurant}')
        st.subheader(f'{start_date_2019} - {end_date_2019} vs {start_date_2022} - {end_date_2022}')

        # ----------------- #

        SPH_2019_week = plot_SPH(SPH_2019, restaurant, f'2019 ', False)
        SPH_2022_week = plot_SPH(SPH_2022, restaurant, f'2022 ', False)
    
        covers2019 = covers2019[covers2019['Hour'] >= 9]
        covers2019 = covers2019[covers2019['Hour'] <= 22]
        covers2022 = covers2022[covers2022['Hour'] >= 9]
        covers2022 = covers2022[covers2022['Hour'] <= 22]

        heatmap_2019_week_data = create_heatmap_data_weekly(covers2019)
        heatmap_2022_week_data = create_heatmap_data_weekly(covers2022)

        heatmap_2019_week_f = plot_heatmap(heatmap_2019_week_data, '2019', False)
        heatmap_2022_week_f = plot_heatmap(heatmap_2022_week_data, '2022', False)

        week_average_2019_f, totals_2019 = plot_week_totals_typical_week(heatmap_2019_week_data, '2019', False)
        week_average_2022_f, totals_2022 = plot_week_totals_typical_week(heatmap_2022_week_data, '2022', False)

        # 12 Plot day_part_covers
        day_part_covers_fig_2019 = plot_day_part_covers(heatmap_2019_week_data, '2019', False)
        day_part_covers_fig_2022 = plot_day_part_covers(heatmap_2022_week_data, '2022', False)
        
        # 13. Plot difference between years
        difference_between_years = heatmap_2022_week_data - heatmap_2019_week_data
        difference_between_years = difference_between_years.round(0)
        hours = difference_between_years.columns[:-4]
        difference_between_years_fig = plot_heatmap(difference_between_years[hours], 'Difference', False)

        # 14. Plot difference between years in percentage
        difference_between_years = heatmap_2022_week_data - heatmap_2019_week_data
        difference_between_years = difference_between_years/heatmap_2019_week_data * 100
        difference_between_years = difference_between_years.round(0)
        hours = difference_between_years.columns[:-4]
        difference_between_years_percentage_fig = plot_heatmap(difference_between_years[hours], 'Difference', False)

        # 15
        # 1. Graph day_part - plot as bar the last 4 columns in heatmap data (day_part) == 'Breakfast', 'Lunch', 'Afternoon', 'Dinner'
        day_parts = difference_between_years.columns[-4:]
        fig_day_part_ = go.Figure()
        for day_part in day_parts:
            fig_day_part_.add_trace(go.Bar(x=difference_between_years.index, y=difference_between_years[day_part], name=f'{day_part}'))
        fig_day_part_.update_layout(title='DAY PART - Differences - 2019 vs 2022 in %')
        #-----------------#
        # 2. Graph totals_2019-2022
        fig_2019_2022 = go.Figure()
        fig_2019_2022.add_trace(go.Scatter(x=totals_2019.index, y=totals_2019['Total'], name='2019', fill = 'tozeroy'))
        fig_2019_2022.add_trace(go.Scatter(x=totals_2022.index, y=totals_2022['Total'], name='2022', fill = 'tozeroy'))
        fig_2019_2022.update_layout(title='Weekly Covers 2019 vs 2022')
        #----------------- #
        # 3. Graph SPH 2019-2022 differences
        SPH_DIFF = SPH_2022['Spent_per_head'] - SPH_2019['Spent_per_head']
        SPH_DIFF = {'Day_Part_Name': SPH_2019['Day_Part_Name'], 'Difference': SPH_DIFF}
        SPH_DIFF['Store_Name'] = restaurant
        SPH_DIFF = pd.DataFrame(SPH_DIFF)
        
        diff_sph_fig = go.Figure()
        diff_sph_fig.add_trace(go.Scatter(x=SPH_DIFF['Day_Part_Name'], y=SPH_DIFF['Difference'], name='Difference'))
        diff_sph_fig.add_trace(go.Bar(x=SPH_DIFF['Day_Part_Name'], y=SPH_2019['Spent_per_head'], name='2019'))
        diff_sph_fig.add_trace(go.Bar(x=SPH_DIFF['Day_Part_Name'], y=SPH_2022['Spent_per_head'], name='2022'))
        diff_sph_fig.update_layout(title=f'Difference SPH 2019 vs 2022 {restaurant} - {week_number}')
        

        # -----------------
        # SHOW ALL GRAPHS - file 1
        with st.expander(f'Week {week_number} - {restaurant} - 2019'):
            c1,c2 = st.columns(2)
            c1.plotly_chart(heatmap_2019_week_f)
            c1.plotly_chart(day_part_covers_fig_2019)
            c2.plotly_chart(week_average_2019_f)
            c2.plotly_chart(SPH_2019_week)

        # -----------------
        # SHOW ALL GRAPHS - file 2
        with st.expander(f'Week {week_number} - {restaurant} - 2022'):
            c1,c2 = st.columns(2)
            c1.plotly_chart(heatmap_2022_week_f)
            c1.plotly_chart(day_part_covers_fig_2022)
            c2.plotly_chart(week_average_2022_f)
            c2.plotly_chart(SPH_2022_week)

        # PLOT ALL GRAPHS - differences between files
        with st.expander(f'Week {week_number} - {restaurant} - 2019 vs 2022'):
            c1,c2 = st.columns(2)
            # row 1
            c1.plotly_chart(difference_between_years_fig)
            c2.plotly_chart(difference_between_years_percentage_fig)
            # row 2
            c1.plotly_chart(diff_sph_fig)
            c2.plotly_chart(fig_day_part_)
            # row 3
            st.plotly_chart(fig_2019_2022, use_container_width=True)

    # ----------------- #
'''