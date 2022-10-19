'''
author: Roberto Scalas
date: 2022-09-23
---
---
To start the dashboard, run the following command:
    $ streamlit run dashboard_5.py
'''

from helper_functions import *

import streamlit as st
st.set_page_config(layout='wide',initial_sidebar_state='auto')
import hydralit_components as hc

import pandas as pd
import numpy as np

import plotly.graph_objects as go

def menu():
    # Images
    markd = '''
    <img src="https://www.dishoom.com/assets/img/roundel-seva.png" width = "120" heigth = "120" >
    '''
    st.markdown(markd, unsafe_allow_html=True)

    # Menu
    menu_data = [
        {'id':'heatmap','label':"Heatmap"},
        {'id':'month','label':"Month Analysis"},
        {'id':'week','label':"Week Analysis (to implement)"},
        {'id':'ML','label':"Machine Learning (to implement)"},
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

with st.sidebar.expander('Import data'):
    uploaded_file_1 = st.file_uploader("2019")
    uploaded_file_2 = st.file_uploader("2022")

if uploaded_file_1 is not None and uploaded_file_2 is not None:
    # save data as csv
    df_2019_ = pd.read_csv(uploaded_file_1)
    df_2022_ = pd.read_csv(uploaded_file_2)
    df_2019_.to_csv('Aloha_Sales_Data_Export_2019.csv', index = True)
    df_2022_.to_csv('Aloha_Sales_Data_Export_2022.csv', index = True)
    
    choosen = menu()

    # 1. SPHs
    try:
        SPH_2019 = pd.read_csv('SPH_2019.csv')
        SPH_2022 = pd.read_csv('SPH_2022.csv')
    except:
        # 1. Open the csv files
        df1 = pd.read_csv(uploaded_file_1)
        df2 = pd.read_csv(uploaded_file_2)
        # 2. Get the SPH
        SPH_2019, SPH_2022 = get_SPH(df1,df2)
        # 3. Save the SPH
        SPH_2019.to_csv('SPH_2019.csv', index=False)
        SPH_2022.to_csv('SPH_2022.csv', index=False)
    # 2. df1, df2 -> Replace Nan or False values with the Total Check, divide by the SPH in that part of the day
    try:
        df1 = pd.read_csv('df1.csv')
        df2 = pd.read_csv('df2.csv')
    except:
        # add spent per head to the original dataframes store name and day part
        df1 = df1.merge(SPH_2019, on=['Store_Name', 'Day_Part_Name'])
        df2 = df2.merge(SPH_2022, on=['Store_Name', 'Day_Part_Name'])
        # if guest_count is > 25 divide sales by SPH of the restaurant
        df1['Guest_Count'] = df1.apply(lambda x: x['Net_Sales']//x['Spent_per_head'] if x['Guest_Count'] > 25 else x['Guest_Count'], axis=1)
        df2['Guest_Count'] = df2.apply(lambda x: x['Net_Sales']//x['Spent_per_head'] if x['Guest_Count'] > 25 else x['Guest_Count'], axis=1)
        # if net sales == 0 drop the row
        df1, df2 = df1[df1['Net_Sales'] != 0], df2[df2['Net_Sales'] != 0]
        # if guest count == 0 drop the row
        df1, df2 = df1[df1['Guest_Count'] != 0], df2[df2['Guest_Count'] != 0]
        # if net sales == total void drop the row
        df1, df2 = df1[df1['Net_Sales'] != df1['Void_Total']], df2[df2['Net_Sales'] != df2['Void_Total']]
        # save the dataframes
        df1.to_csv('df1.csv', index=False)
        df2.to_csv('df2.csv', index=False)

    # 3. covers_2019, covers_2022 -> get the timeseries data
    try:
        covers2019 = pd.read_csv('covers_2019.csv')
        covers2022 = pd.read_csv('covers_2022.csv')
    except:
        covers2019 = create_timeries_covers(df1)
        covers2022 = create_timeries_covers(df2)
        # save as csv
        covers2019.to_csv('covers_2019.csv', index=True)
        covers2022.to_csv('covers_2022.csv', index=True)
    
    # DATA 
    restaurants = np.append(covers2019['Store_Name'].unique(), 'All Restaurants') # create a list of restaurants
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
        #'''Correction now - might need to put in a function'''???
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

        '''till here'''
        
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
        SHP_2019_month = plot_SPH(SPH_2019, restaurant, '2019', False)
        SHP_2022_month = plot_SPH(SPH_2022, restaurant, '2022', False)
        
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

        heatmap_2019_month = plot_heatmap(data_guest_heatmap_2019, '2019', False)
        heatmap_2022_month = plot_heatmap(data_guest_heatmap_2022, '2022', False)

        # 11. Plot week_totals_typical
        week_average_2019_f, totals_2019 = plot_week_totals_typical_week(data_guest_heatmap_2019, '2019', False)
        week_average_2022_f, totals_2022 = plot_week_totals_typical_week(data_guest_heatmap_2022, '2022', False)

        # 12 Plot day_part_covers
        day_part_covers_fig_2019 = plot_day_part_covers(data_guest_heatmap_2019, '2019', False)
        day_part_covers_fig_2022 = plot_day_part_covers(data_guest_heatmap_2022, '2022', False)
        
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
        with st.expander('To DO'):
            st.write('''
            ---
            TO DO
            FIRST thing -> Correct covers that exceed 25 guest for check
            1. Add a graph to represent the choosen week in relation to the week before that
            2. Add a graph to represent the choosen week in relation to the week after that
            3. Add a graph to represent the SPH of the choosen week in relation to the week before that
            4. Add a graph to represent the SPH of the choosen week in relation to the week after that
            '''
            )

        week_number = st.sidebar.slider('Select a week', min_value=1, max_value=52, value=1, step=1)

        df1_open = df1.copy()
        df2_open = df2.copy()

        df1_open = add_month_and_week_number(df1_open)
        df2_open = add_month_and_week_number(df2_open)

        # filter out unnecessary weeks
        df1_open = df1_open[df1_open['Week_Number'] == week_number]
        df2_open = df2_open[df2_open['Week_Number'] == week_number]

        restaurant = st.sidebar.selectbox('Select a restaurant', restaurants)
        
        # filter out unnecessary restaurants
        if restaurant != 'All':
            # modify restaurants name
            df1_open['Store_Name'] = df1_open.apply(lambda x: x['Store_Name'].split('-')[1] if '-' in x['Store_Name'] else x['Store_Name'], axis=1)
            df2_open['Store_Name'] = df2_open.apply(lambda x: x['Store_Name'].split('-')[1] if '-' in x['Store_Name'] else x['Store_Name'], axis=1)
            # filter by restaurant
            df1_open = df1_open[df1_open['Store_Name'] == restaurant]
            df2_open = df2_open[df2_open['Store_Name'] == restaurant]
            
        covers2019 = create_timeries_covers(df1_open)
        covers2022 = create_timeries_covers(df2_open)

        SPH_2019, SPH_2022 = get_SPH(df1_open, df2_open)

        SPH_2019_week = plot_SPH(SPH_2019, restaurant, '2019', False)
        SPH_2022_week = plot_SPH(SPH_2022, restaurant, '2022', False)
    
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
        
        '''here'''
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

    elif choosen == 'ML':

        st.title('Machine Learning')
        st.write('This section is under construction')

        data_2019 = pd.read_csv('covers_2019.csv')
        data  = data_2019.copy()
        # sort data
        data = data.sort_values(by=['Date'])
        # only 1 restaurant
        restaurant = data['Store_Name'].unique()[0]
        data = data[data['Store_Name'] == restaurant]
        # transform date in datetime
        data['Date'] = pd.to_datetime(data['Date'])
        # keep only date
        data['Date'] = data['Date'].dt.date
        # to datetime
        data['Date'] = pd.to_datetime(data['Date'])
        # add month column
        data['Month'] = data['Date'].dt.month
        # keep only month <6
        data = data[data['Month'] < 6]
        

        # group by day
        data = data.groupby(['Date']).sum()
        data = data['Guest_Count']
        data_ = data.copy()

        # Connect to MODEL
        import numpy as np
        import torch
        # transform data
        # to tensor
        data = torch.FloatTensor(data)
        print(f'Original dimensions : {data.shape}')
        train_scaled = data.view(-1)
        print(f'Correct dimensions : {data.shape}')

        # import model
        from torch_model_LSTM import predict
        look_back = 31
        predictions = predict(data, look_back)
        
        # get the values in a list
        st.write(data_)
        # rescale history

        st.write(predictions)
        # from numpy to list
        predictions = predictions.tolist()
        # from tensor to numpy
        st.write(type(predictions))

        '''Rescale model'''
        scalar = 500
        predictions = [prediction[0] + scalar for prediction in predictions]
        # plot
        fig = go.Figure()

        # add trace with historical data
        fig.add_trace(go.Scatter(x=[i for i in range(len(data_))], y=data_, name='Historical Data'))
        fig.add_trace(go.Scatter(x=[i+len(data_) for i in range(len(predictions))], y=predictions, name='Predictions'))
        fig.update_layout(title='Predictions')
        st.plotly_chart(fig, use_container_width=True)

    # ----------------- #
