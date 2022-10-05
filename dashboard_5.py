from helper_functions import *
import hydralit_components as hc
import streamlit as st
st.set_page_config(layout='wide',initial_sidebar_state='auto')

import pandas as pd
import numpy as np

import plotly.graph_objects as go
import plotly.express as px


with st.sidebar.expander('Import data'):
    uploaded_file_1 = st.file_uploader("2019")
    uploaded_file_2 = st.file_uploader("2022")

def get_SPH(df1,df2):
    # This function returns the SPH for the 2019 and 2022 dataframes in every daypart
    #-----------------
    # take off guest_count 0
    df1 = df1[df1['Guest_Count'] != 0]
    df2 = df2[df2['Guest_Count'] != 0]
    # take off guest_count > 25
    df1 = df1[df1['Guest_Count'] <= 25]
    df2 = df2[df2['Guest_Count'] <= 25]
    
    # create a new columns calls Spent Per Head
    df1['Spent_per_head'] = df1['Net_Sales']/df1['Guest_Count']
    df2['Spent_per_head'] = df2['Net_Sales']/df2['Guest_Count']
    
    # get unique restaurants
    restaurants = df1['Store_Name'].unique()
    SPH_list_2019 = []
    SPH_list_2022 = []
    for restaurant in restaurants:
        # filter by restaurant
        df1_restaurant = df1[df1['Store_Name'] == restaurant]
        df2_restaurant = df2[df2['Store_Name'] == restaurant]
        # get unique day part
        day_parts = df1[df1['Store_Name'] == restaurant]['Day_Part_Name'].unique()
        for day_part in day_parts:
            # filter by day part
            df1_day_part = df1_restaurant[df1_restaurant['Day_Part_Name'] == day_part]
            df2_day_part = df2_restaurant[df2_restaurant['Day_Part_Name'] == day_part]
            # make an average of the spent per head columns
            SPH = df1_day_part['Spent_per_head'].mean()
            SPH_list_2019.append([restaurant, SPH, day_part])
            SPH = df2_day_part['Spent_per_head'].mean()
            SPH_list_2022.append([restaurant, SPH, day_part])

    # transform the list into a dataframe
    SPH_2019 = pd.DataFrame(SPH_list_2019, columns=['Store_Name', 'Spent_per_head', 'Day_Part_Name'])
    SPH_2022 = pd.DataFrame(SPH_list_2022, columns=['Store_Name', 'Spent_per_head',  'Day_Part_Name'])
    #st.write(SPH_2019)
    #st.write(SPH_2022)
    return SPH_2019, SPH_2022
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

if uploaded_file_1 is not None and uploaded_file_2 is not None:
    choosen = menu()
    if choosen == 'heatmap':

        # 1. Open the csv files
        df1 = pd.read_csv(uploaded_file_1)
        df2 = pd.read_csv(uploaded_file_2)

        # 2. try opening the csv file
        try:
            SPH_2019 = pd.read_csv('SPH_2019.csv')
            SPH_2022 = pd.read_csv('SPH_2022.csv')
        except:
            SPH_2019, SPH_2022 = get_SPH(df1,df2)
            SPH_2019.to_csv('SPH_2019.csv', index=False)
            SPH_2022.to_csv('SPH_2022.csv', index=False)

        # 3. take off day part late night
        SPH_2019 = SPH_2019[SPH_2019['Day_Part_Name'] != 'Late Night']
        SPH_2022 = SPH_2022[SPH_2022['Day_Part_Name'] != 'Late Night']

        # 4. Plot Data - SPH
        fig_2019 = go.Figure()
        for restaurant in SPH_2019['Store_Name'].unique():
            fig_2019.add_trace(go.Bar
                            (x=SPH_2019[SPH_2019['Store_Name'] == restaurant]['Day_Part_Name'],
                            y=SPH_2019[SPH_2019['Store_Name'] == restaurant]['Spent_per_head'],
                            name=restaurant))
        fig_2019.update_layout(title='SPH 2019')
        #---
        fig_2022 = go.Figure()
        for restaurant in SPH_2022['Store_Name'].unique():
            fig_2022.add_trace(go.Bar
                            (x=SPH_2022[SPH_2022['Store_Name'] == restaurant]['Day_Part_Name'],
                            y=SPH_2022[SPH_2022['Store_Name'] == restaurant]['Spent_per_head'],
                            name=restaurant))
        fig_2022.update_layout(title='SPH 2022')

        # 5. Precisly fill invalid data -> 
        # If guest count > 25 fill the values with the totals sales divided by SPH in that day part
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
        
        # 7. Open the csv file of timeseries cover data if not exist create it
        try:
            covers2019 = pd.read_csv('covers_2019.csv')
            covers2022 = pd.read_csv('covers_2022.csv')
        except:
            covers2019 = create_timeries_covers(df1)
            covers2022 = create_timeries_covers(df2)
            # save as csv
            covers2019.to_csv('covers_2019.csv', index=False)
            covers2022.to_csv('covers_2022.csv', index=False)
        
        
        # 9. Select restarants
        # Create a list of restaurants
        restaurants = covers2019['Store_Name'].unique()
        restaurants = np.append(restaurants, 'All Restaurants')

        restaurant = st.sidebar.selectbox('Select restaurant', restaurants)
        
        # 10. Filter the data
        if restaurant is not 'All Restaurant':
            # filter out not choosen restaurants
            covers2019 = covers2019[covers2019['Store_Name'] == restaurant]
            covers2022 = covers2022[covers2022['Store_Name'] == restaurant]
        else:
            # drop store name
            covers2019 = covers2019.drop('Store_Name', axis=1)
            covers2022 = covers2022.drop('Store_Name', axis=1)

        # ----------------- #
        # CREATE HEATMAP 2019 and 2022
        # Filter out hours < 9 and > 22
        covers2019 = covers2019[covers2019['Hour'] >= 9]
        covers2019 = covers2019[covers2019['Hour'] <= 22]
        covers2022 = covers2022[covers2022['Hour'] >= 9]
        covers2022 = covers2022[covers2022['Hour'] <= 22]
        
        # group by day making average of the guests and employees
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        frame_2019 = []
        frame_2022 = []
        for day in days_of_week:
            # filter by day
            data_guest_day_2019 = covers2019[covers2019['Day_of_week'] == day]
            data_guest_day_2019 = data_guest_day_2019.groupby(covers2019['Hour']).mean()
            # drop Hour columns
            data_guest_day_2019 = data_guest_day_2019.drop(columns=['Hour'])
            # rename guest count
            data_guest_day_2019 = data_guest_day_2019.rename(columns={'Guest_Count': day})
            transposed_day_2019 = data_guest_day_2019.T
            # add to list
            frame_2019.append(transposed_day_2019)


            # filter by day
            data_guest_day_2022 = covers2022[covers2022['Day_of_week'] == day]
            data_guest_day_2022 = data_guest_day_2022.groupby(covers2022['Hour']).mean()
            # drop Hour columns
            data_guest_day_2022 = data_guest_day_2022.drop(columns=['Hour'])
            # rename guest count
            data_guest_day_2022 = data_guest_day_2022.rename(columns={'Guest_Count': day})
            transposed_day_2022 = data_guest_day_2022.T
            # add to list
            frame_2022.append(transposed_day_2022)

        data_guest_heatmap_2019 = pd.concat(frame_2019)
        data_guest_heatmap_2022 = pd.concat(frame_2022)

        #--- PLOT THE DATA
        # 1st Graph - HEATMAP 2019
        z = data_guest_heatmap_2019
        # round the values
        z = z.round(0)
        z = z.values.tolist()
        fig = px.imshow(z, text_auto=True, title='Heatmap 2019 - Covers')
        fig.update_xaxes(
            ticktext=data_guest_heatmap_2019.columns,
            tickvals=list(range(len(data_guest_heatmap_2019.columns))),
            tickangle=45,
            tickfont=dict(
                family="Rockwell",
                size=14,
            )
        )
        fig.update_yaxes(
            ticktext=[day[:3] for day in data_guest_heatmap_2019.index],
            tickvals=list(range(len(data_guest_heatmap_2019.index))),
            tickangle=0,
            tickfont=dict(
                family="Rockwell",
                size=14,
            )
        )
        # modify size
        fig.update_layout(
            autosize=True,
            #width=1400,
            #height=600,
        )
        #-------------------
        # 2nd Graph - SPENT PER HEAD 2019
        # 1. Get Data
        sph_2019 = SPH_2019
        sph_2022 = SPH_2022
        # Modify store names with the second element after the dash
        sph_2019['Store_Name'] = sph_2019['Store_Name'].str.split('-').str[1]
        sph_2022['Store_Name'] = sph_2022['Store_Name'].str.split('-').str[1]
        if restaurant != 'All Restaurant':
            sph_2019 = sph_2019[sph_2019['Store_Name'] == restaurant]
            sph_2022 = sph_2022[sph_2022['Store_Name'] == restaurant]
        else:
            # drop store name
            sph_2019 = sph_2019.drop('Store_Name', axis=1)
            sph_2022 = sph_2022.drop('Store_Name', axis=1)
            # 2. Create Graph
        SPH_fig_2019 = px.bar(sph_2019, x='Day_Part_Name', y='Spent_per_head', title='SPH 2019')
        # -----------------
        # 3rd Graph - WEEKLY COVERS 2019
            # 1. Get Data
        grouped_2019 = data_guest_heatmap_2019.T  # transposing to have the days as columns
        totals_2019 = grouped_2019.sum(axis=0)   # summing the rows
        totals_2019 = pd.DataFrame(totals_2019) # converting to dataframe
        totals_2019.columns = ['Total']        # renaming the column
            # 2. Create graph  
        weekly_covers_fig_2019 = go.Figure()
        weekly_covers_fig_2019.add_trace(go.Scatter(x=totals_2019.index, y=totals_2019['Total'], name='2019', fill = 'tozeroy'))
        weekly_covers_fig_2019.update_layout(title='Weekly Covers 2019')
        # -----------------
        # 4th Graph - WEEKLY COVERS 2022
            # 1. Get Data
        data_day_part_day = data_guest_heatmap_2019
        # transform columns in strings
        data_day_part_day.columns = data_day_part_day.columns.astype(str)
        # group 9-12, 12-15, 15-18, 18-21, 21-24
        data_day_part_day['Breakfast'] = data_day_part_day['9'] + data_day_part_day['10'] + data_day_part_day['11']
        data_day_part_day['Lunch'] = data_day_part_day['12'] + data_day_part_day['13'] + data_day_part_day['14'] + data_day_part_day['15']
        data_day_part_day['Afternoon'] = data_day_part_day['16'] + data_day_part_day['17'] + data_day_part_day['18']
        data_day_part_day['Dinner'] = data_day_part_day['19'] + data_day_part_day['20'] + data_day_part_day['21'] + data_day_part_day['22']
            # 2. Create graph
        day_part_covers_fig = go.Figure()
        for day_part in ['Breakfast', 'Lunch', 'Afternoon', 'Dinner']:
            day_part_covers_fig.add_trace(go.Bar(x=data_day_part_day.index, y=data_day_part_day[day_part], name=f'{day_part}'))
        day_part_covers_fig.update_layout(title='Day Part Covers 2019')

        # -----------------
        # SHOW ALL GRAPHS
        with st.expander(f'{restaurant} - 2019'):
            c1,c2 = st.columns(2)
            c1.plotly_chart(fig)
            c1.plotly_chart(day_part_covers_fig)
            c2.plotly_chart(weekly_covers_fig_2019)
            c2.plotly_chart(SPH_fig_2019)

        # ------
        # HEATMAP 2022
        #--- PLOT THE DATA
        # 1st Graph - HEATMAP 2022
        z = data_guest_heatmap_2022
        # round the values
        z = z.round(0)
        z = z.values.tolist()
        fig = px.imshow(z, text_auto=True, title='Heatmap 2022 - Covers')
        fig.update_xaxes(
            ticktext=data_guest_heatmap_2022.columns,
            tickvals=list(range(len(data_guest_heatmap_2022.columns))),
            tickangle=45,
            tickfont=dict(
                family="Rockwell",
                size=14,
            )
        )
        fig.update_yaxes(
            ticktext=[day[:3] for day in data_guest_heatmap_2022.index],
            tickvals=list(range(len(data_guest_heatmap_2022.index))),
            tickangle=0,
            tickfont=dict(
                family="Rockwell",
                size=14,
            )
        )
        # modify size
        fig.update_layout(
            autosize=True,
            #width=1400,
            #height=600,
        )
        
        #-------------------
        # 2nd Graph - SPENT PER HEAD 2022
            # 1. Get Data
        SPH_fig_2022 = px.bar(sph_2022, x='Day_Part_Name', y='Spent_per_head', title='SPH 2022')
        # -----------------
        # 3rd Graph - WEEKLY COVERS 2019
            # 1. Get Data
        grouped_2022 = data_guest_heatmap_2022.T  # transposing to have the days as columns
        totals_2022 = grouped_2022.sum(axis=0)   # summing the rows
        totals_2022 = pd.DataFrame(totals_2022) # converting to dataframe
        totals_2022.columns = ['Total']        # renaming the column
            # 2. Create graph  
        weekly_covers_fig_2022 = go.Figure()
        weekly_covers_fig_2022.add_trace(go.Scatter(x=totals_2022.index, y=totals_2022['Total'], name='2022', fill = 'tozeroy'))
        weekly_covers_fig_2022.update_layout(title='Weekly Covers 2022')
        # -----------------
        # 4th Graph - WEEKLY COVERS 2022
            # 1. Get Data
        data_day_part_day = data_guest_heatmap_2022
        # transform columns in strings
        data_day_part_day.columns = data_day_part_day.columns.astype(str)
        # group 9-12, 12-15, 15-18, 18-21, 21-24
        data_day_part_day['Breakfast'] = data_day_part_day['9'] + data_day_part_day['10'] + data_day_part_day['11']
        data_day_part_day['Lunch'] = data_day_part_day['12'] + data_day_part_day['13'] + data_day_part_day['14'] + data_day_part_day['15']
        data_day_part_day['Afternoon'] = data_day_part_day['16'] + data_day_part_day['17'] + data_day_part_day['18']
        data_day_part_day['Dinner'] = data_day_part_day['19'] + data_day_part_day['20'] + data_day_part_day['21'] + data_day_part_day['22']
            # 2. Create graph
        day_part_covers_fig = go.Figure()
        for day_part in ['Breakfast', 'Lunch', 'Afternoon', 'Dinner']:
            day_part_covers_fig.add_trace(go.Bar(x=data_day_part_day.index, y=data_day_part_day[day_part], name=f'{day_part}'))
        day_part_covers_fig.update_layout(title='Day Part Covers 2022')

        # -----------------
        # SHOW ALL GRAPHS
        with st.expander(f'{restaurant} - 2022'):
            c1,c2 = st.columns(2)
            c1.plotly_chart(fig)
            c1.plotly_chart(day_part_covers_fig)
            c2.plotly_chart(weekly_covers_fig_2022)
            c2.plotly_chart(SPH_fig_2022)
        
        # ----------------- #
        # DIFFERENCE HEATMAP
        difference_between_years = data_guest_heatmap_2022 - data_guest_heatmap_2019
        # express difference in %
        difference_between_years = difference_between_years/data_guest_heatmap_2019 * 100
        # round to 0 decimal
        difference_between_years = difference_between_years.round(0)
        hours = difference_between_years.columns[:-4]
        z = difference_between_years[hours]
        # transform in list of list
        z = z.values.tolist()
        fig = px.imshow(z, text_auto=True, title='Difference between 2019 and 2022 in %')
        # add index
        fig.update_xaxes(
            ticktext=difference_between_years.columns,
            tickvals=list(range(len(difference_between_years.columns))),
            tickangle=45,
            tickfont=dict(
                family="Rockwell",
                size=14,
            )
        )
        fig.update_yaxes(
            ticktext=difference_between_years.index,
            tickvals=list(range(len(difference_between_years.index))),
            tickangle=0,
            tickfont=dict(
                family="Rockwell",
                size=14,
            )
        )
        # modify size
        fig.update_layout(
            autosize=True,
            #width=1400,
            #height=600,
        )

        # ----------------- #

        # plot differences last 4 columns
        day_parts = difference_between_years.columns[-4:]
        fig_day_part_ = go.Figure()
        for day_part in day_parts:
            fig_day_part_.add_trace(go.Bar(x=difference_between_years.index, y=difference_between_years[day_part], name=f'{day_part}'))
        fig_day_part_.update_layout(title='DAY PART - Differences - 2019 vs 2022 in %')

        # 3. Graph Weekly Covers 2019vs2022
        fig_2019_2022 = go.Figure()
        # add 2019
        fig_2019_2022.add_trace(go.Scatter
                                (x=totals_2019.index, y=totals_2019['Total'], name='2019', fill = 'tozeroy'))
        # add 2022
        fig_2019_2022.add_trace(go.Scatter
                                (x=totals_2022.index, y=totals_2022['Total'], name='2022', fill = 'tozeroy'))
        fig_2019_2022.update_layout(title='Weekly Covers 2019 vs 2022')
        #----------------- #
        # set day part as index
        store_name = sph_2019['Store_Name'].unique()[0]
        day_part_columns = sph_2019['Day_Part_Name']
        sph_diff = sph_2022['Spent_per_head'] - sph_2019['Spent_per_head']
        SPH_DIFF = {'Day_Part_Name': day_part_columns, 'Difference': sph_diff}
        # add store name
        SPH_DIFF['Store_Name'] = store_name
        # create dataframe
        SPH_DIFF = pd.DataFrame(SPH_DIFF)
            #2.  Create Graph
        diff_sph_fig = go.Figure()
        diff_sph_fig.add_trace(go.Scatter(x=SPH_DIFF['Day_Part_Name'], y=SPH_DIFF['Difference'], name='Difference'))
        # add 2019
        diff_sph_fig.add_trace(go.Bar(x=SPH_DIFF['Day_Part_Name'], y=sph_2019['Spent_per_head'], name='2019'))
        # add 2022
        diff_sph_fig.add_trace(go.Bar(x=SPH_DIFF['Day_Part_Name'], y=sph_2022['Spent_per_head'], name='2022'))
        diff_sph_fig.update_layout(title='Difference SPH 2019 vs 2022')

        # PLOT ALL GRAPHS
        with st.expander(f'{restaurant} - 2019 vs 2022'):
            c1,c2 = st.columns(2)
            c1.plotly_chart(fig)
            c1.plotly_chart(diff_sph_fig)
            c2.plotly_chart(fig_2019_2022)
            c2.plotly_chart(fig_day_part_)
    
    # ----------------- #
    
    elif choosen == 'month':
    # 1. Open the csv files
        df1 = pd.read_csv(uploaded_file_1)
        df2 = pd.read_csv(uploaded_file_2)
        df1_open = df1.copy()
        df2_open = df2.copy()

        # 2. try opening the csv file
        try:
            SPH_2019 = pd.read_csv('SPH_2019.csv')
            SPH_2022 = pd.read_csv('SPH_2022.csv')
        except:
            SPH_2019, SPH_2022 = get_SPH(df1,df2)
            SPH_2019.to_csv('SPH_2019.csv', index=False)
            SPH_2022.to_csv('SPH_2022.csv', index=False)

        # 3. take off day part late night
        SPH_2019 = SPH_2019[SPH_2019['Day_Part_Name'] != 'Late Night']
        SPH_2022 = SPH_2022[SPH_2022['Day_Part_Name'] != 'Late Night']

        # 5. Precisly fill invalid data -> 
        # If guest count > 25 fill the values with the totals sales divided by SPH in that day part
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
        
        # 7. Open the csv file of timeseries cover data if not exist create it
        try:
            covers2019 = pd.read_csv('covers_2019.csv')
            covers2022 = pd.read_csv('covers_2022.csv')
        except:
            covers2019 = create_timeries_covers(df1)
            covers2022 = create_timeries_covers(df2)
            # save as csv
            covers2019.to_csv('covers_2019.csv', index=False)
            covers2022.to_csv('covers_2022.csv', index=False)
         
        # 9. Select restarants
        # Create a list of restaurants
        restaurants = covers2019['Store_Name'].unique()
        restaurants = np.append(restaurants, 'All Restaurants')

        restaurant = st.sidebar.selectbox('Select restaurant', restaurants)
        
        # 10. Filter the data
        if restaurant is not 'All Restaurant':
            # filter out not choosen restaurants
            covers2019 = covers2019[covers2019['Store_Name'] == restaurant]
            covers2022 = covers2022[covers2022['Store_Name'] == restaurant]
        else:
            # drop store name
            covers2019 = covers2019.drop('Store_Name', axis=1)
            covers2022 = covers2022.drop('Store_Name', axis=1)

        # ----------------- #
        # CREATE HEATMAP 2019 and 2022
        # Filter out hours < 9 and > 22
        covers2019 = covers2019[covers2019['Hour'] >= 9]
        covers2019 = covers2019[covers2019['Hour'] <= 22]
        covers2022 = covers2022[covers2022['Hour'] >= 9]
        covers2022 = covers2022[covers2022['Hour'] <= 22]
        
        # group by day making average of the guests and employees
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        frame_2019 = []
        frame_2022 = []
        for day in days_of_week:
            # filter by day
            data_guest_day_2019 = covers2019[covers2019['Day_of_week'] == day]
            data_guest_day_2019 = data_guest_day_2019.groupby(covers2019['Hour']).mean()
            # drop Hour columns
            data_guest_day_2019 = data_guest_day_2019.drop(columns=['Hour'])
            # rename guest count
            data_guest_day_2019 = data_guest_day_2019.rename(columns={'Guest_Count': day})
            transposed_day_2019 = data_guest_day_2019.T
            # add to list
            frame_2019.append(transposed_day_2019)


            # filter by day
            data_guest_day_2022 = covers2022[covers2022['Day_of_week'] == day]
            data_guest_day_2022 = data_guest_day_2022.groupby(covers2022['Hour']).mean()
            # drop Hour columns
            data_guest_day_2022 = data_guest_day_2022.drop(columns=['Hour'])
            # rename guest count
            data_guest_day_2022 = data_guest_day_2022.rename(columns={'Guest_Count': day})
            transposed_day_2022 = data_guest_day_2022.T
            # add to list
            frame_2022.append(transposed_day_2022)

        data_guest_heatmap_2019 = pd.concat(frame_2019)
        data_guest_heatmap_2022 = pd.concat(frame_2022)

        # show tables
        #with st.expander('Show tables'):
        #    c1,c2 = st.columns(2)
        #    c1.subheader('Guests Heatmap 2019 - All Year')
        #    c1.write(data_guest_heatmap_2019)
        #    c2.subheader('Guests Heatmap 2022 - All Year')
        #    c2.write(data_guest_heatmap_2022)
            
        
        # HERE 
        # modify df1_open and df2_open to have the same columns
        # transfor date to datetime
        df1_open['Date_'] = pd.to_datetime(df1_open['Date'])
        df2_open['Date_'] = pd.to_datetime(df2_open['Date'])
        # add month column
        df1_open['Month'] = df1_open['Date_'].dt.month
        df2_open['Month'] = df2_open['Date_'].dt.month
        # add week number
        df1_open['Week_Number'] = df1_open['Date_'].apply(lambda x: x.week)
        df2_open['Week_Number'] = df2_open['Date_'].apply(lambda x: x.week)
        # select month
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        month = st.sidebar.selectbox('Select month', months)
        # filter by month
        df1_open = df1_open[df1_open['Month'] == months.index(month)+1]
        df2_open = df2_open[df2_open['Month'] == months.index(month)+1]

        SPH_2019, SPH_2022 = get_SPH(df1_open,df2_open) # only the selected month

        # 3. take off day part late night
        SPH_2019 = SPH_2019[SPH_2019['Day_Part_Name'] != 'Late Night']
        SPH_2022 = SPH_2022[SPH_2022['Day_Part_Name'] != 'Late Night']

        # add spent per head to the original dataframes store name and day part
        df1_open = df1_open.merge(SPH_2019, on=['Store_Name', 'Day_Part_Name'])
        df2_open = df2_open.merge(SPH_2022, on=['Store_Name', 'Day_Part_Name'])
        # if guest_count is > 25 divide sales by SPH of the restaurant
        df1_open['Guest_Count'] = df1_open.apply(lambda x: x['Net_Sales']//x['Spent_per_head'] if x['Guest_Count'] > 25 else x['Guest_Count'], axis=1)
        df2_open['Guest_Count'] = df2_open.apply(lambda x: x['Net_Sales']//x['Spent_per_head'] if x['Guest_Count'] > 25 else x['Guest_Count'], axis=1)
        # if net sales == 0 drop the row
        df1_open, df2_open = df1_open[df1_open['Net_Sales'] != 0], df2_open[df2_open['Net_Sales'] != 0]
        # if guest count == 0 drop the row
        df1_open, df2_open = df1_open[df1_open['Guest_Count'] != 0], df2_open[df2_open['Guest_Count'] != 0]
        # if net sales == total void drop the row
        df1_open, df2_open = df1_open[df1_open['Net_Sales'] != df1_open['Void_Total']], df2_open[df2_open['Net_Sales'] != df2_open['Void_Total']]
    
        covers2019 = create_timeries_covers(df1_open) # only the selected month
        covers2022 = create_timeries_covers(df2_open) # only the selected month

       # restaurant should already be in memory
        # 10. Filter the data
        if restaurant is not 'All Restaurant':
            # filter out not choosen restaurants
            covers2019 = covers2019[covers2019['Store_Name'] == restaurant]
            covers2022 = covers2022[covers2022['Store_Name'] == restaurant]
        else:
            # drop store name
            covers2019 = covers2019.drop('Store_Name', axis=1)
            covers2022 = covers2022.drop('Store_Name', axis=1)

        # ----------------- #
        # CREATE HEATMAP 2019 and 2022
        # Filter out hours < 9 and > 22
        covers2019 = covers2019[covers2019['Hour'] >= 9]
        covers2019 = covers2019[covers2019['Hour'] <= 22]
        covers2022 = covers2022[covers2022['Hour'] >= 9]
        covers2022 = covers2022[covers2022['Hour'] <= 22]
        
        # group by day making average of the guests and employees
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        frame_2019 = []
        frame_2022 = []
        for day in days_of_week:
            # filter by day
            data_guest_day_2019 = covers2019[covers2019['Day_of_week'] == day]
            data_guest_day_2019 = data_guest_day_2019.groupby(covers2019['Hour']).mean()
            # drop Hour columns
            data_guest_day_2019 = data_guest_day_2019.drop(columns=['Hour'])
            # rename guest count
            data_guest_day_2019 = data_guest_day_2019.rename(columns={'Guest_Count': day})
            transposed_day_2019 = data_guest_day_2019.T
            # add to list
            frame_2019.append(transposed_day_2019)


            # filter by day
            data_guest_day_2022 = covers2022[covers2022['Day_of_week'] == day]
            data_guest_day_2022 = data_guest_day_2022.groupby(covers2022['Hour']).mean()
            # drop Hour columns
            data_guest_day_2022 = data_guest_day_2022.drop(columns=['Hour'])
            # rename guest count
            data_guest_day_2022 = data_guest_day_2022.rename(columns={'Guest_Count': day})
            transposed_day_2022 = data_guest_day_2022.T
            # add to list
            frame_2022.append(transposed_day_2022)

        data_guest_heatmap_2019 = pd.concat(frame_2019) # only the selected month
        data_guest_heatmap_2022 = pd.concat(frame_2022) # only the selected month
        
        #'''Adding stuff 2019 '''
        #------------------- 
        # Week graphs
        #--- PLOT THE DATA
        # 1st Graph - HEATMAP 2019
        z = data_guest_heatmap_2019
        # round the values
        z = z.round(0)
        z = z.values.tolist()
        fig = px.imshow(z, text_auto=True, title='Heatmap 2019 - Covers')
        fig.update_xaxes(
            ticktext=data_guest_heatmap_2019.columns,
            tickvals=list(range(len(data_guest_heatmap_2019.columns))),
            tickangle=45,
            tickfont=dict(
                family="Rockwell",
                size=14,
            )
        )
        fig.update_yaxes(
            ticktext=[day[:3] for day in data_guest_heatmap_2019.index],
            tickvals=list(range(len(data_guest_heatmap_2019.index))),
            tickangle=0,
            tickfont=dict(
                family="Rockwell",
                size=14,
            )
        )
        # modify size
        fig.update_layout(
            autosize=True,
            #width=1400,
            #height=600,
        )
        #-------------------
        # 2nd Graph - SPENT PER HEAD 2019
        # 1. Get Data
        sph_2019 = SPH_2019
        sph_2022 = SPH_2022
        # Modify store names with the second element after the dash
        sph_2019['Store_Name'] = sph_2019['Store_Name'].str.split('-').str[1]
        sph_2022['Store_Name'] = sph_2022['Store_Name'].str.split('-').str[1]
        if restaurant != 'All Restaurant':
            sph_2019 = sph_2019[sph_2019['Store_Name'] == restaurant]
            sph_2022 = sph_2022[sph_2022['Store_Name'] == restaurant]
        else:
            # drop store name
            sph_2019 = sph_2019.drop('Store_Name', axis=1)
            sph_2022 = sph_2022.drop('Store_Name', axis=1)
            # 2. Create Graph
        SPH_fig_2019 = px.bar(sph_2019, x='Day_Part_Name', y='Spent_per_head', title='SPH 2019')
        # -----------------
        # 3rd Graph - WEEKLY COVERS 2019
            # 1. Get Data
        grouped_2019 = data_guest_heatmap_2019.T  # transposing to have the days as columns
        totals_2019 = grouped_2019.sum(axis=0)   # summing the rows
        totals_2019 = pd.DataFrame(totals_2019) # converting to dataframe
        totals_2019.columns = ['Total']        # renaming the column
            # 2. Create graph  
        weekly_covers_fig_2019 = go.Figure()
        weekly_covers_fig_2019.add_trace(go.Scatter(x=totals_2019.index, y=totals_2019['Total'], name='2019', fill = 'tozeroy'))
        weekly_covers_fig_2019.update_layout(title='Weekly Covers 2019')
        # -----------------
        # 4th Graph - WEEKLY COVERS 2022
            # 1. Get Data
        data_day_part_day = data_guest_heatmap_2019
        # transform columns in strings
        data_day_part_day.columns = data_day_part_day.columns.astype(str)
        # group 9-12, 12-15, 15-18, 18-21, 21-24
        data_day_part_day['Breakfast'] = data_day_part_day['9'] + data_day_part_day['10'] + data_day_part_day['11']
        data_day_part_day['Lunch'] = data_day_part_day['12'] + data_day_part_day['13'] + data_day_part_day['14'] + data_day_part_day['15']
        data_day_part_day['Afternoon'] = data_day_part_day['16'] + data_day_part_day['17'] + data_day_part_day['18']
        data_day_part_day['Dinner'] = data_day_part_day['19'] + data_day_part_day['20'] + data_day_part_day['21'] + data_day_part_day['22']
            # 2. Create graph
        day_part_covers_fig = go.Figure()
        for day_part in ['Breakfast', 'Lunch', 'Afternoon', 'Dinner']:
            day_part_covers_fig.add_trace(go.Bar(x=data_day_part_day.index, y=data_day_part_day[day_part], name=f'{day_part}'))
        day_part_covers_fig.update_layout(title=f'Day Part Covers 2019 - {restaurant} - {month}')

        # -----------------
        # SHOW ALL GRAPHS
        with st.expander(f'{month} - {restaurant} - 2019'):
            c1,c2 = st.columns(2)
            c1.plotly_chart(fig)
            c1.plotly_chart(day_part_covers_fig)
            c2.plotly_chart(weekly_covers_fig_2019)
            c2.plotly_chart(SPH_fig_2019)

        # ------

        #'''Adding stuff 2022 '''

        # ------
        # HEATMAP 2022
        #--- PLOT THE DATA
        # 1st Graph - HEATMAP 2022
        z = data_guest_heatmap_2022
        # round the values
        z = z.round(0)
        z = z.values.tolist()
        fig = px.imshow(z, text_auto=True, title=f'Heatmap 2022 {restaurant} - Covers {month}')
        fig.update_xaxes(
            ticktext=data_guest_heatmap_2022.columns,
            tickvals=list(range(len(data_guest_heatmap_2022.columns))),
            tickangle=45,
            tickfont=dict(
                family="Rockwell",
                size=14,
            )
        )
        fig.update_yaxes(
            ticktext=[day[:3] for day in data_guest_heatmap_2022.index],
            tickvals=list(range(len(data_guest_heatmap_2022.index))),
            tickangle=0,
            tickfont=dict(
                family="Rockwell",
                size=14,
            )
        )
        # modify size
        fig.update_layout(
            autosize=True,
            #width=1400,
            #height=600,
        )
        
        #-------------------
        # 2nd Graph - SPENT PER HEAD 2022
            # 1. Get Data
        SPH_fig_2022 = px.bar(sph_2022, x='Day_Part_Name', y='Spent_per_head', title='SPH 2022')
        # -----------------
        # 3rd Graph - WEEKLY COVERS 2019
            # 1. Get Data
        grouped_2022 = data_guest_heatmap_2022.T  # transposing to have the days as columns
        totals_2022 = grouped_2022.sum(axis=0)   # summing the rows
        totals_2022 = pd.DataFrame(totals_2022) # converting to dataframe
        totals_2022.columns = ['Total']        # renaming the column
            # 2. Create graph  
        weekly_covers_fig_2022 = go.Figure()
        weekly_covers_fig_2022.add_trace(go.Scatter(x=totals_2022.index, y=totals_2022['Total'], name='2022', fill = 'tozeroy'))
        weekly_covers_fig_2022.update_layout(title='Weekly Covers 2022')
        # -----------------
        # 4th Graph - WEEKLY COVERS 2022
            # 1. Get Data
        data_day_part_day = data_guest_heatmap_2022
        # transform columns in strings
        data_day_part_day.columns = data_day_part_day.columns.astype(str)
        # group 9-12, 12-15, 15-18, 18-21, 21-24
        data_day_part_day['Breakfast'] = data_day_part_day['9'] + data_day_part_day['10'] + data_day_part_day['11']
        data_day_part_day['Lunch'] = data_day_part_day['12'] + data_day_part_day['13'] + data_day_part_day['14'] + data_day_part_day['15']
        data_day_part_day['Afternoon'] = data_day_part_day['16'] + data_day_part_day['17'] + data_day_part_day['18']
        data_day_part_day['Dinner'] = data_day_part_day['19'] + data_day_part_day['20'] + data_day_part_day['21'] + data_day_part_day['22']
            # 2. Create graph
        day_part_covers_fig = go.Figure()
        for day_part in ['Breakfast', 'Lunch', 'Afternoon', 'Dinner']:
            day_part_covers_fig.add_trace(go.Bar(x=data_day_part_day.index, y=data_day_part_day[day_part], name=f'{day_part}'))
        day_part_covers_fig.update_layout(title='Day Part Covers 2022')

        # -----------------
        # SHOW ALL GRAPHS
        with st.expander(f'{month} - {restaurant} - 2022'):
            c1,c2 = st.columns(2)
            c1.plotly_chart(fig)
            c1.plotly_chart(day_part_covers_fig)
            c2.plotly_chart(weekly_covers_fig_2022)
            c2.plotly_chart(SPH_fig_2022)

        # ------
        # ----------------- #
        # DIFFERENCE HEATMAP
        difference_between_years = data_guest_heatmap_2022 - data_guest_heatmap_2019
        # express difference in %
        difference_between_years = difference_between_years/data_guest_heatmap_2019 * 100
        # round to 0 decimal
        difference_between_years = difference_between_years.round(0)
        hours = difference_between_years.columns[:-4]
        z = difference_between_years[hours]
        # transform in list of list
        z = z.values.tolist()
        fig = px.imshow(z, text_auto=True, title=f'Difference between 2019 and 2022 in % - {restaurant} - {month}')
        # add index
        fig.update_xaxes(
            ticktext=difference_between_years.columns,
            tickvals=list(range(len(difference_between_years.columns))),
            tickangle=45,
            tickfont=dict(
                family="Rockwell",
                size=14,
            )
        )
        fig.update_yaxes(
            ticktext=difference_between_years.index,
            tickvals=list(range(len(difference_between_years.index))),
            tickangle=0,
            tickfont=dict(
                family="Rockwell",
                size=14,
            )
        )
        # modify size
        fig.update_layout(
            autosize=True,
            #width=1400,
            #height=600,
        )

        # ----------------- #

        # plot differences last 4 columns
        day_parts = difference_between_years.columns[-4:]
        fig_day_part_ = go.Figure()
        for day_part in day_parts:
            fig_day_part_.add_trace(go.Bar(x=difference_between_years.index, y=difference_between_years[day_part], name=f'{day_part}'))
        fig_day_part_.update_layout(title='DAY PART - Differences - 2019 vs 2022 in %')

        # 3. Graph Weekly Covers 2019vs2022
        fig_2019_2022 = go.Figure()
        # add 2019
        fig_2019_2022.add_trace(go.Scatter
                                (x=totals_2019.index, y=totals_2019['Total'], name='2019', fill = 'tozeroy'))
        # add 2022
        fig_2019_2022.add_trace(go.Scatter
                                (x=totals_2022.index, y=totals_2022['Total'], name='2022', fill = 'tozeroy'))
        fig_2019_2022.update_layout(title='Weekly Covers 2019 vs 2022')
        #----------------- #
        # set day part as index
        store_name = sph_2019['Store_Name'].unique()[0]
        day_part_columns = sph_2019['Day_Part_Name']
        sph_diff = sph_2022['Spent_per_head'] - sph_2019['Spent_per_head']
        SPH_DIFF = {'Day_Part_Name': day_part_columns, 'Difference': sph_diff}
        # add store name
        SPH_DIFF['Store_Name'] = store_name
        # create dataframe
        SPH_DIFF = pd.DataFrame(SPH_DIFF)
            #2.  Create Graph
        diff_sph_fig = go.Figure()
        diff_sph_fig.add_trace(go.Scatter(x=SPH_DIFF['Day_Part_Name'], y=SPH_DIFF['Difference'], name='Difference'))
        # add 2019
        diff_sph_fig.add_trace(go.Bar(x=SPH_DIFF['Day_Part_Name'], y=sph_2019['Spent_per_head'], name='2019'))
        # add 2022
        diff_sph_fig.add_trace(go.Bar(x=SPH_DIFF['Day_Part_Name'], y=sph_2022['Spent_per_head'], name='2022'))
        diff_sph_fig.update_layout(title=f'Difference SPH 2019 vs 2022 {restaurant} - {month}')

        # PLOT ALL GRAPHS
        with st.expander(f'{month} - {restaurant} - 2019 vs 2022'):
            c1,c2 = st.columns(2)
            c1.plotly_chart(fig)
            c1.plotly_chart(diff_sph_fig)
            c2.plotly_chart(fig_2019_2022)
            c2.plotly_chart(fig_day_part_)
    
    # ----------------- #

    elif choosen == 'week':
        st.write('''

        DONE
        ---
        1. Create a representation of the week as heatmap, compare it to the base week of that year.
        2. Compare the day part covers of the week to the base week of that year.
        3. Compare the SPH of the week to the base week of that year.
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

        df1 = pd.read_csv(uploaded_file_1)
        df2 = pd.read_csv(uploaded_file_2)
        df1_open = df1.copy()
        df2_open = df2.copy()

        # transform date to datetime
        df1_open['Date_'] = pd.to_datetime(df1_open['Date'])
        # add week number
        df1_open['Week_Number'] = df1_open['Date_'].dt.week
        # transform date to datetime
        df2_open['Date_'] = pd.to_datetime(df2_open['Date'])
        # add week number
        df2_open['Week_Number'] = df2_open['Date_'].dt.week

        # filter out unnecessary weeks
        df1_open = df1_open[df1_open['Week_Number'] == week_number]
        df2_open = df2_open[df2_open['Week_Number'] == week_number]

        restaurants = df1_open['Store_Name'].unique()
        #add all
        restaurants = np.append(restaurants, 'All')
        restaurant = st.sidebar.selectbox('Select a restaurant', restaurants)
        
        # filter out unnecessary restaurants
        if restaurant != 'All':
            df1_open = df1_open[df1_open['Store_Name'] == restaurant]
            df2_open = df2_open[df2_open['Store_Name'] == restaurant]
        # ----------------- #

        # get sph from both years
        SPH_2019, SPH_2022 = get_SPH(df1_open, df2_open)

        

        covers2019 = create_timeries_covers(df1_open)
        covers2022 = create_timeries_covers(df2_open)

        #st.write(covers2019)
        #st.write(covers2022)

        #'''Adding stuff here'''
        # ----------------- #
        # CREATE HEATMAP 2019 and 2022
        # Filter out hours < 9 and > 22
        covers2019 = covers2019[covers2019['Hour'] >= 9]
        covers2019 = covers2019[covers2019['Hour'] <= 22]
        covers2022 = covers2022[covers2022['Hour'] >= 9]
        covers2022 = covers2022[covers2022['Hour'] <= 22]
        
        # group by day making average of the guests and employees
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        frame_2019 = []
        frame_2022 = []
        for day in days_of_week:
            # filter by day
            data_guest_day_2019 = covers2019[covers2019['Day_of_week'] == day]
            data_guest_day_2019 = data_guest_day_2019.groupby(covers2019['Hour']).mean()
            # drop Hour columns
            data_guest_day_2019 = data_guest_day_2019.drop(columns=['Hour'])
            # rename guest count
            data_guest_day_2019 = data_guest_day_2019.rename(columns={'Guest_Count': day})
            transposed_day_2019 = data_guest_day_2019.T
            # add to list
            frame_2019.append(transposed_day_2019)

            # filter by day
            data_guest_day_2022 = covers2022[covers2022['Day_of_week'] == day]
            data_guest_day_2022 = data_guest_day_2022.groupby(covers2022['Hour']).mean()
            # drop Hour columns
            data_guest_day_2022 = data_guest_day_2022.drop(columns=['Hour'])
            # rename guest count
            data_guest_day_2022 = data_guest_day_2022.rename(columns={'Guest_Count': day})
            transposed_day_2022 = data_guest_day_2022.T
            # add to list
            frame_2022.append(transposed_day_2022)

        data_guest_heatmap_2019 = pd.concat(frame_2019)
        data_guest_heatmap_2022 = pd.concat(frame_2022)

        #--- PLOT THE DATA
        # 1st Graph - HEATMAP 2019
        z = data_guest_heatmap_2019
        # round the values
        z = z.round(0)
        z = z.values.tolist()
        fig = px.imshow(z, text_auto=True, title='Heatmap 2019 - Covers')
        fig.update_xaxes(
            ticktext=data_guest_heatmap_2019.columns,
            tickvals=list(range(len(data_guest_heatmap_2019.columns))),
            tickangle=45,
            tickfont=dict(
                family="Rockwell",
                size=14,
            )
        )
        fig.update_yaxes(
            ticktext=[day[:3] for day in data_guest_heatmap_2019.index],
            tickvals=list(range(len(data_guest_heatmap_2019.index))),
            tickangle=0,
            tickfont=dict(
                family="Rockwell",
                size=14,
            )
        )
        # modify size
        fig.update_layout(
            autosize=True,
            #width=1400,
            #height=600,
        )
        #-------------------
        # 2nd Graph - SPENT PER HEAD 2019
        # 1. Get Data
        sph_2019 = SPH_2019
        sph_2022 = SPH_2022
            # 2. Create Graph
        SPH_fig_2019 = px.bar(sph_2019, x='Day_Part_Name', y='Spent_per_head', title='SPH 2019')
        # -----------------
        # 3rd Graph - WEEKLY COVERS 2019
            # 1. Get Data
        grouped_2019 = data_guest_heatmap_2019.T  # transposing to have the days as columns
        totals_2019 = grouped_2019.sum(axis=0)   # summing the rows
        totals_2019 = pd.DataFrame(totals_2019) # converting to dataframe
        totals_2019.columns = ['Total']        # renaming the column
            # 2. Create graph  
        weekly_covers_fig_2019 = go.Figure()
        weekly_covers_fig_2019.add_trace(go.Scatter(x=totals_2019.index, y=totals_2019['Total'], name='2019', fill = 'tozeroy'))
        weekly_covers_fig_2019.update_layout(title='Weekly Covers 2019')
        # -----------------
        # 4th Graph - WEEKLY COVERS 2022
            # 1. Get Data
        data_day_part_day = data_guest_heatmap_2019
        # transform columns in strings
        data_day_part_day.columns = data_day_part_day.columns.astype(str)
        # group 9-12, 12-15, 15-18, 18-21, 21-24
        data_day_part_day['Breakfast'] = data_day_part_day['9'] + data_day_part_day['10'] + data_day_part_day['11']
        data_day_part_day['Lunch'] = data_day_part_day['12'] + data_day_part_day['13'] + data_day_part_day['14'] + data_day_part_day['15']
        data_day_part_day['Afternoon'] = data_day_part_day['16'] + data_day_part_day['17'] + data_day_part_day['18']
        data_day_part_day['Dinner'] = data_day_part_day['19'] + data_day_part_day['20'] + data_day_part_day['21'] + data_day_part_day['22']
            # 2. Create graph
        day_part_covers_fig = go.Figure()
        for day_part in ['Breakfast', 'Lunch', 'Afternoon', 'Dinner']:
            day_part_covers_fig.add_trace(go.Bar(x=data_day_part_day.index, y=data_day_part_day[day_part], name=f'{day_part}'))
        day_part_covers_fig.update_layout(title='Day Part Covers 2019')

        # -----------------
        # SHOW ALL GRAPHS
        with st.expander(f'Week {week_number} - {restaurant} - 2019'):
            c1,c2 = st.columns(2)
            c1.plotly_chart(fig)
            c1.plotly_chart(day_part_covers_fig)
            c2.plotly_chart(weekly_covers_fig_2019)
            c2.plotly_chart(SPH_fig_2019)

        # ------
        # HEATMAP 2022
        #--- PLOT THE DATA
        # 1st Graph - HEATMAP 2022
        z = data_guest_heatmap_2022
        # round the values
        z = z.round(0)
        z = z.values.tolist()
        fig = px.imshow(z, text_auto=True, title='Heatmap 2022 - Covers')
        fig.update_xaxes(
            ticktext=data_guest_heatmap_2022.columns,
            tickvals=list(range(len(data_guest_heatmap_2022.columns))),
            tickangle=45,
            tickfont=dict(
                family="Rockwell",
                size=14,
            )
        )
        fig.update_yaxes(
            ticktext=[day[:3] for day in data_guest_heatmap_2022.index],
            tickvals=list(range(len(data_guest_heatmap_2022.index))),
            tickangle=0,
            tickfont=dict(
                family="Rockwell",
                size=14,
            )
        )
        # modify size
        fig.update_layout(
            autosize=True,
            #width=1400,
            #height=600,
        )
        
        #-------------------
        # 2nd Graph - SPENT PER HEAD 2022
            # 1. Get Data
        SPH_fig_2022 = px.bar(sph_2022, x='Day_Part_Name', y='Spent_per_head', title='SPH 2022')
        # -----------------
        # 3rd Graph - WEEKLY COVERS 2019
            # 1. Get Data
        grouped_2022 = data_guest_heatmap_2022.T  # transposing to have the days as columns
        totals_2022 = grouped_2022.sum(axis=0)   # summing the rows
        totals_2022 = pd.DataFrame(totals_2022) # converting to dataframe
        totals_2022.columns = ['Total']        # renaming the column
            # 2. Create graph  
        weekly_covers_fig_2022 = go.Figure()
        weekly_covers_fig_2022.add_trace(go.Scatter(x=totals_2022.index, y=totals_2022['Total'], name='2022', fill = 'tozeroy'))
        weekly_covers_fig_2022.update_layout(title=f'Weekly Covers 2022 - Week {week_number} - {restaurant}')
        # -----------------
        # 4th Graph - WEEKLY COVERS 2022
            # 1. Get Data
        data_day_part_day = data_guest_heatmap_2022
        # transform columns in strings
        data_day_part_day.columns = data_day_part_day.columns.astype(str)
        # group 9-12, 12-15, 15-18, 18-21, 21-24
        data_day_part_day['Breakfast'] = data_day_part_day['9'] + data_day_part_day['10'] + data_day_part_day['11']
        data_day_part_day['Lunch'] = data_day_part_day['12'] + data_day_part_day['13'] + data_day_part_day['14'] + data_day_part_day['15']
        data_day_part_day['Afternoon'] = data_day_part_day['16'] + data_day_part_day['17'] + data_day_part_day['18']
        data_day_part_day['Dinner'] = data_day_part_day['19'] + data_day_part_day['20'] + data_day_part_day['21'] + data_day_part_day['22']
            # 2. Create graph
        day_part_covers_fig = go.Figure()
        for day_part in ['Breakfast', 'Lunch', 'Afternoon', 'Dinner']:
            day_part_covers_fig.add_trace(go.Bar(x=data_day_part_day.index, y=data_day_part_day[day_part], name=f'{day_part}'))
        day_part_covers_fig.update_layout(title='Day Part Covers 2022')

        # -----------------
        # SHOW ALL GRAPHS
        with st.expander(f'Week {week_number} - {restaurant} - 2022'):
            c1,c2 = st.columns(2)
            c1.plotly_chart(fig)
            c1.plotly_chart(day_part_covers_fig)
            c2.plotly_chart(weekly_covers_fig_2022)
            c2.plotly_chart(SPH_fig_2022)
        
        # ----------------- #
        # DIFFERENCE HEATMAP
        difference_between_years = data_guest_heatmap_2022 - data_guest_heatmap_2019
        # express difference in %
        difference_between_years = difference_between_years/data_guest_heatmap_2019 * 100
        # round to 0 decimal
        difference_between_years = difference_between_years.round(0)
        hours = difference_between_years.columns[:-4]
        z = difference_between_years[hours]
        # transform in list of list
        z = z.values.tolist()
        fig = px.imshow(z, text_auto=True, title='Difference between 2019 and 2022 in %')
        # add index
        fig.update_xaxes(
            ticktext=difference_between_years.columns,
            tickvals=list(range(len(difference_between_years.columns))),
            tickangle=45,
            tickfont=dict(
                family="Rockwell",
                size=14,
            )
        )
        fig.update_yaxes(
            ticktext=difference_between_years.index,
            tickvals=list(range(len(difference_between_years.index))),
            tickangle=0,
            tickfont=dict(
                family="Rockwell",
                size=14,
            )
        )
        # modify size
        fig.update_layout(
            autosize=True,
            #width=1400,
            #height=600,
        )

        # ----------------- #
        # plot differences last 4 columns
        day_parts = difference_between_years.columns[-4:]
        fig_day_part_ = go.Figure()
        for day_part in day_parts:
            fig_day_part_.add_trace(go.Bar(x=difference_between_years.index, y=difference_between_years[day_part], name=f'{day_part}'))
        fig_day_part_.update_layout(title='DAY PART - Differences - 2019 vs 2022 in %')

        # 3. Graph Weekly Covers 2019vs2022
        fig_2019_2022 = go.Figure()
        # add 2019
        fig_2019_2022.add_trace(go.Scatter
                                (x=totals_2019.index, y=totals_2019['Total'], name='2019', fill = 'tozeroy'))
        # add 2022
        fig_2019_2022.add_trace(go.Scatter
                                (x=totals_2022.index, y=totals_2022['Total'], name='2022', fill = 'tozeroy'))
        fig_2019_2022.update_layout(title='Weekly Covers 2019 vs 2022')
        #----------------- #
        # set day part as index
        store_name = restaurant
        day_part_columns = sph_2019['Day_Part_Name']
        sph_diff = sph_2022['Spent_per_head'] - sph_2019['Spent_per_head']
        SPH_DIFF = {'Day_Part_Name': day_part_columns, 'Difference': sph_diff}
        # add store name
        SPH_DIFF['Store_Name'] = store_name
        # create dataframe
        SPH_DIFF = pd.DataFrame(SPH_DIFF)
            #2.  Create Graph
        diff_sph_fig = go.Figure()
        diff_sph_fig.add_trace(go.Scatter(x=SPH_DIFF['Day_Part_Name'], y=SPH_DIFF['Difference'], name='Difference'))
        # add 2019
        diff_sph_fig.add_trace(go.Bar(x=SPH_DIFF['Day_Part_Name'], y=sph_2019['Spent_per_head'], name='2019'))
        # add 2022
        diff_sph_fig.add_trace(go.Bar(x=SPH_DIFF['Day_Part_Name'], y=sph_2022['Spent_per_head'], name='2022'))
        diff_sph_fig.update_layout(title='Difference SPH 2019 vs 2022')

        # PLOT ALL GRAPHS
        with st.expander(f'Week {week_number} - {restaurant} - 2019 vs 2022'):
            c1,c2 = st.columns(2)
            c1.plotly_chart(fig)
            c1.plotly_chart(diff_sph_fig)
            c2.plotly_chart(fig_2019_2022)
            c2.plotly_chart(fig_day_part_)


        
        


