import streamlit as st
st.set_page_config(layout='wide',initial_sidebar_state='auto')
import pandas as pd
import plotly.graph_objects as go
from helper_functions import *

with st.sidebar.expander('Import data'):
    uploaded_file_1 = st.file_uploader("2019")
    uploaded_file_2 = st.file_uploader("2022")

def get_SPH(df1,df2):
    # take off guest_count 0
    df1 = df1[df1['Guest_Count'] != 0]
    df2 = df2[df2['Guest_Count'] != 0]
    # take off guest_count > 25
    df1 = df1[df1['Guest_Count'] <= 25]
    df2 = df2[df2['Guest_Count'] <= 25]
    
    # create a new columns calls Spent per head
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

if uploaded_file_1 is not None and uploaded_file_2 is not None:
    df1 = pd.read_csv(uploaded_file_1)
    df2 = pd.read_csv(uploaded_file_2)

    # take off guest_count 0
    df1 = df1[df1['Guest_Count'] != 0]
    df2 = df2[df2['Guest_Count'] != 0]

    SPH_2019, SPH_2022 = get_SPH(df1,df2)

    with st.expander('SPH'):
        # plot the data
        fig_2019 = go.Figure()
        for restaurant in SPH_2019['Store_Name'].unique():
            fig_2019.add_trace(go.Bar
                            (x=SPH_2019[SPH_2019['Store_Name'] == restaurant]['Day_Part_Name'],
                            y=SPH_2019[SPH_2019['Store_Name'] == restaurant]['Spent_per_head'],
                            name=restaurant))
        fig_2019.update_layout(title='SPH 2019')
        st.plotly_chart(fig_2019, use_container_width=True)

        #---
        fig_2022 = go.Figure()
        for restaurant in SPH_2022['Store_Name'].unique():
            fig_2022.add_trace(go.Bar
                            (x=SPH_2022[SPH_2022['Store_Name'] == restaurant]['Day_Part_Name'],
                            y=SPH_2022[SPH_2022['Store_Name'] == restaurant]['Spent_per_head'],
                            name=restaurant))
        fig_2022.update_layout(title='SPH 2022')
        st.plotly_chart(fig_2022, use_container_width=True)

    # add spent per head to the original dataframes store name and day part
    df1 = df1.merge(SPH_2019, on=['Store_Name', 'Day_Part_Name'])
    df2 = df2.merge(SPH_2022, on=['Store_Name', 'Day_Part_Name'])


    # if guest_count is > 25 divide sales by SPH of the restaurant
    df1['Guest_Count'] = df1.apply(lambda x: x['Net_Sales']//x['Spent_per_head'] if x['Guest_Count'] > 25 else x['Guest_Count'], axis=1)
    df2['Guest_Count'] = df2.apply(lambda x: x['Net_Sales']//x['Spent_per_head'] if x['Guest_Count'] > 25 else x['Guest_Count'], axis=1)

    #---
    with st.expander('Data 1st Processing'):
        st.write(df1)
        st.write(df2)

    # modify
    covers2019 = create_timeries_covers(df1)
    covers2022 = create_timeries_covers(df2)

    with st.expander('Data 2nd Processing'):
        st.write(covers2019)
        st.write(covers2022)

    # select restarants
    # create a list of restaurants
    restaurants = covers2019['Store_Name'].unique()
    # add all restaurants to the list
    import numpy as np
    restaurants = np.append(restaurants, 'All Restaurants')

    restaurant = st.sidebar.selectbox('Select restaurant', restaurants)
    if restaurant is not 'All Restaurant':
        # filter out restaurant not choosen
        covers2019 = covers2019[covers2019['Store_Name'] == restaurant]
        covers2022 = covers2022[covers2022['Store_Name'] == restaurant]
    # ----------------- #
    # CREATE HEATMAP 2019 and 2022
    # Filter out hours < 9 and > 23
    covers2019 = covers2019[(covers2019.index.hour >= 9) & (covers2019.index.hour < 23)]
    covers2022 = covers2022[(covers2022.index.hour >= 9) & (covers2022.index.hour < 23)]
    
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
    with st.expander('Heatmap_data'):
        st.write(data_guest_heatmap_2019)
        st.write(data_guest_heatmap_2022)

    #--- PLOT THE DATA
    # HEATMAP 2019
    import plotly.express as px
    z = data_guest_heatmap_2019
    z = z.values.tolist()
    fig = px.imshow(z, text_auto=True, title='Heatmap 2019')
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
        ticktext=data_guest_heatmap_2019.index[::-1],
        tickvals=list(range(len(data_guest_heatmap_2019.index[::-1]))),
        tickangle=0,
        tickfont=dict(
            family="Rockwell",
            size=14,
        )
    )
     # modify size
    fig.update_layout(
        autosize=False,
        width=1400,
        height=600,
    )

    st.plotly_chart(fig, use_container_width=True)
    # ------
    # HEATMAP 2022
    z = data_guest_heatmap_2022
    z = z.values.tolist()
    fig = px.imshow(z, text_auto=True, title='Heatmap 2022')
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
        ticktext=data_guest_heatmap_2022.index[::-1],
        tickvals=list(range(len(data_guest_heatmap_2022.index[::-1]))),
        tickangle=0,
        tickfont=dict(
            family="Rockwell",
            size=14,
        )
    )
     # modify size
    fig.update_layout(
        autosize=False,
        width=1400,
        height=600,
    )
    st.plotly_chart(fig, use_container_width=True)
    # ----------------- #
    # DIFFERENCE HEATMAP
    difference_between_years = data_guest_heatmap_2022 - data_guest_heatmap_2019
    # express difference in %
    difference_between_years = difference_between_years/data_guest_heatmap_2019 * 100
    # round to 2 decimal
    difference_between_years = difference_between_years.round(2)
    z = difference_between_years
    # transform in list of list
    z = z.values.tolist()
    fig = px.imshow(z, text_auto=True, title='Difference between 2019 and 2022')
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
        ticktext=difference_between_years.index[::-1],
        tickvals=list(range(len(difference_between_years.index[::-1]))),
        tickangle=0,
        tickfont=dict(
            family="Rockwell",
            size=14,
        )
    )
    # modify size
    fig.update_layout(
        autosize=False,
        width=1400,
        height=600,
    )

    st.plotly_chart(fig, use_container_width=True)