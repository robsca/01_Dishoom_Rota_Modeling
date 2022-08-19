'''
author: Roberto Scalas
date: 2022-07-14
---
EXPERIMENTIG WITH DATA ANALYSIS
---
ideas to implement:
-   Time series analysis - Net sales, Gross sales, Void total, Item sales, Guest count
-   Service time distribution - by day
-   Average Spending for customer
-   Average time spent by customer in the restaurant
-   Measure the variation in sales between week days and weekends [Not Done]
---
Observations:
-   Kings cross voided a lot more than other restaurants with similar sales,
    it seems obvius that the guest count is influencing the value positively.(see D3 and D1)
-   Something is wrong with the check_time, or close_time, 16 hours cannot be right.
    # Might be the time when the check is been register in the system, at the closing time?
        
'''
import streamlit as st
import hydralit_components as hc
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from plotting_rota import rota_tion
from dtbs import *


st.set_page_config(layout='wide',initial_sidebar_state='collapsed')

# Write some functions 

        
def get_store_data(store_):
    figs, Xs, Ys = rota_tion() # kings cross rotations graph

    import plotly.graph_objs as go
    st.subheader(f'{store_}')
    df = pd.read_csv('Dishoom_/myReport - 2022-07-13T120124.897 copy.csv')

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

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    options = ['Net_Sales', 'Gross_Sales', 'Void_Total', 'Item_Sales', 'Guest_Count']

    selected_graph = st.selectbox('Graph', options, key = 1)
    c10, c11 = st.columns(2)
    with c10:
        # Average time spent by customer in the restaurant
        st.write('Average Time Spent On Restaurant') 
        check_in_time = df['Check_Time']
        check_out_time = df['Close_Time']
        permanence = check_out_time - check_in_time

        fig = px.histogram(df, x=permanence)
        st.plotly_chart(fig)
        average = permanence.mean()
        st.write(f'Average permanence: {average//60} hours')
    with c11:        
        # create a pie chart
        st.write('Distribution of Sales by Day Part')
        breakfast_lunch_pie = px.pie(df, values=f'{selected_graph}', names='Day_Part_Name', color = 'Day_Part_Name')
        fig = go.Figure(data=breakfast_lunch_pie)
        fig.update_layout(legend_orientation="h")
        st.plotly_chart(fig)
    tot_cost_labour_ = 0
    tot_net_sales_ = 0
    for i, df_ in enumerate(table_by_date):
        with st.expander(f'{dates[i]} - {days[i]}'):
            #st.write(df)

            # breakfast, lunch, afternoon, dinner
            breakfast = df_[df_['Day_Part_Name'] == 'Breakfast']
            breakfast_total = breakfast[f'{selected_graph}'].sum()

            lunch = df_[df_['Day_Part_Name'] == 'Lunch']
            lunch_total = lunch[f'{selected_graph}'].sum()

            afternoon = df_[df_['Day_Part_Name'] == 'Afternoon']
            afternoon_total = afternoon[f'{selected_graph}'].sum()

            dinner = df_[df_['Day_Part_Name'] == 'Dinner']
            dinner_total = dinner[f'{selected_graph}'].sum()
            tot = breakfast_total + lunch_total + afternoon_total + dinner_total
            st.write(f'Total of the day - {tot.round(2)}')
            

            c1,c2 = st.columns(2)
            with c1:
                pie = px.pie(df_, values=f'{selected_graph}', names='Day_Part_Name', color = 'Day_Part_Name')
                # put legend in the middle of the pie
                fig = go.Figure(data=pie)
                fig.update_layout(legend_orientation="h")
                st.plotly_chart(fig)
            with c2:
                bar = px.bar(df_, x='Day_Part_Name', y=f'{selected_graph}', color = 'Day_Part_Name',width = 500)
                fig = go.Figure(data=bar)
                # take off the legend
                fig.update_layout(legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01)
                    )           
                st.plotly_chart(fig)

            # group by hour
            data_ = df_.groupby('Hour').sum()
            

            #plot
            hour_net_sales = px.line(x=data_.index, y=data_['Net_Sales'], title='Hourly Net Sales', width=1000, height=600)
            hour_gross_sales = px.line(x=data_.index, y=data_['Gross_Sales'], title='Hourly Gross Sales', width=1000, height=600)
            hour_void_total = px.line(x=data_.index, y=data_['Void_Total'],     title='Hourly Void Total', width=1000, height=600) 
            hour_item_sales = px.line(x=data_.index, y=data_['Item_Sales'], title = 'Hourly Item Sales',    width=1000, height=600)
            hour_guest_count = px.line(x=data_.index, y=data_['Guest_Count'], title = 'Hourly Guest Count')

            import plotly.graph_objs as go
            fig = go.Figure()
            fig.add_trace(go.Scatter
                (x=data_.index, y=data_['Guest_Count'], name='Guest Count',))
            fig.add_trace(go.Scatter(x=data_.index, y=Ys[i], name='Employee Count'))
            y_coeff_one_to_ten = [e*10 for e in Ys[i]]
            

            fig.add_trace(go.Scatter(x=data_.index, y=y_coeff_one_to_ten, name='Coefficient 1 to 10'))
            fig.update_layout(title='Employee vs Guest Count', xaxis_title='Hour', yaxis_title='Gross Sales')
            
            # plot revenue and cost_labour
            net_sales = data_['Net_Sales']
            cost_labour = [int(e*9.5) for e in Ys[i]]
            #st.write(y_coeff_one_to_ten)
            #st.write(cost_labour)

            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=data_.index, y=data_['Net_Sales'], name='Net Sales'))

            fig2.add_trace(go.Scatter(x=data_.index, y=cost_labour, name='Cost_labour'))
            fig2.update_layout(title='Net Sales vs Cost Labour', xaxis_title='Hour', yaxis_title='Gross Sales')

            # plot totals 
            tot_net_sales = data_['Net_Sales'].sum()
            tot_cost_labour = sum([int(e*9.5) for e in Ys[i]])
            tot_cost_labour_ += tot_cost_labour
            tot_net_sales_ += tot_net_sales


            # create bar graph with totals
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(x=['Net Sales', 'Cost Labour'], y=[tot_net_sales, tot_cost_labour]))
            fig3.update_layout(title='Totals', xaxis_title='', yaxis_title='Gross Sales')

            # plot piechart with totals
            fig4 = go.Figure()
            fig4.add_trace(go.Pie(labels=['Net Sales', 'Cost Labour'], values=[tot_net_sales, tot_cost_labour]))
            fig4.update_layout(title='Totals', xaxis_title='', yaxis_title='Gross Sales')
           
            # plot all in same graph
            if selected_graph == 'Net_Sales':
                st.plotly_chart(hour_net_sales)
            elif selected_graph == 'Gross_Sales':
                st.plotly_chart(hour_gross_sales)
            elif selected_graph == 'Void_Total':
                st.plotly_chart(hour_void_total)
            elif selected_graph == 'Item_Sales':
                st.plotly_chart(hour_item_sales)
            elif selected_graph == 'Guest_Count':
                c1,c2 = st.columns(2)

                with c1:
                    st.plotly_chart(fig3)
                    st.plotly_chart(fig4)


                with c2:
                    st.plotly_chart(fig)
                    st.plotly_chart(fig2)
    st.write(f'Total cost labour - {tot_cost_labour_}')
    st.write(f'Total net sales - {tot_net_sales_}')
    # plot totals
    c1,c2 = st.columns(2)
    fig5 = go.Figure()
    # bar graph of net sales and cost labour
    fig5.add_trace(go.Bar(x=['Net Sales', 'Cost Labour'], y=[tot_net_sales_, tot_cost_labour_]))
    fig5.update_layout(title='Totals', xaxis_title='', yaxis_title='Gross Sales')
    with c1:
        st.plotly_chart(fig5)
    # pie chart of net sales and cost labour
    fig6 = go.Figure()
    fig6.add_trace(go.Pie(labels=['Net Sales', 'Cost Labour'], values=[tot_net_sales_, tot_cost_labour_]))
    fig6.update_layout(title='Totals', xaxis_title='', yaxis_title='Gross Sales')
    with c2:
        st.plotly_chart(fig6)

def unified_table_(df):
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

        # check average spendings
        average_spending = df['Net_Sales'].mean()
        average_spending = round(average_spending, 2)
        st.write(f'In average every customers spend {average_spending}£')
        return df_unified

markd = '''
<img src="https://www.dishoom.com/assets/img/roundel-seva.png" width = "120" heigth = "120" >
'''

st.markdown(markd, unsafe_allow_html=True)
# specify the primary menu definition
menu_data = [
    {'id': 'Dashboard','icon': "fas fa-tachometer-alt", 'label':"Dashboard",'ttip':"I'm the Dashboard tooltip!"}, #can add a tooltip message
    {'id': 'Rota_Checker', 'label':"Rota",'ttip':"I'm the Rota Dashboard tooltip!"}, #
    {'id':'Weekly view','label':"Weekly view"},
    {'icon': "",'label':"Employees", 
                'submenu':[
                    {'id':'Employees', 'label':"List Employees"},
                    {'id':'ADD', 'label':"Add Employees"},
                ]},
    {'icon': "",'label':"Restaurants", 
                'submenu':[
                    {'id':'D1', 'label':"Dishoom Covent Garden"},
                    {'id':'D2', 'label':"Dishoom Shoreditch"},
                    {'id':'D3', 'label':"Dishoom Kings Cross"},
                    {'id':'D4', 'label':"Dishoom Carnaby"},
                    {'id':'D5', 'label':"Dishoom Edinburgh"},
                    {'id':'D6', 'label':"Dishoom Kensington"},
                    {'id':'D7', 'label':"Dishoom Manchester"},
                    {'id':'D8', 'label':"Dishoom Birmingham"},
                    ]},

    {'icon': "",'label':"Delivery Kitchens", 
                'submenu':[
                    {'id':'D101', 'label':"Dishoom Battersea"},
                    {'id':'D102', 'label':"Dishoom Whitechapel"},
                    {'id':'D103', 'label':"Dishoom Swiss Cottage"},
                    {'id':'D104', 'label':"Dishoom Park Royal"},
                    {'id':'D105', 'label':"Dishoom Islington"},
                    {'id':'D106', 'label':"Dishoom Blackwall"},
                    {'id':'D107', 'label':"Dishoom Brighton"},
                    {'id':'D108', 'label':"Dishoom Cambridge"},
                    {'id':'D109', 'label':"Dishoom Wandsworth"},
                    {'id':'D110', 'label':"Dishoom Bermondsey"},
                    {'id':'D111', 'label':"Dishoom Acton"},
                    {'id':'D112', 'label':"Dishoom Dulwich"},
                    ]},
    {'id':'ML','label':"Machine Learning"},
                   ]

# specify the theme
over_theme = {'menu_background': '#ebd2b9',
                'txc_inactive': '#6e7074' ,
                'txc_active':'#6e7074'}

menu_id = hc.nav_bar(
    menu_definition=menu_data,
    override_theme=over_theme,
    hide_streamlit_markers=True, #will show the st hamburger as well as the navbar now!
    sticky_nav=False, #at the top or not
    sticky_mode='sticky', #jumpy or not-jumpy, but sticky or pinned
)
#get the id of the menu item clicked
if menu_id == 'Weekly view':

    # open csv file
    df = pd.read_csv('Dishoom_/myReport - 2022-07-13T120124.897 copy.csv')
    stores = df['Store_Name'].unique()

    # Clean from useless values
    df = df.drop(df[df['Item_Sales'] == 0].index)
    df = df.drop(df[df['Net_Sales'] == df['Void_Total']].index) # might be better to use the gross sales

    # Set options for the plot
    # ---
    c11, c22 = st.columns(2)
    with c11:
        shops = st.multiselect('Select a shop', stores)
    with c22:
        measure = st.selectbox('Select: ', ['Item_Sales', 'Net_Sales', 'Void_Total', 'Gross_Sales', 'Guest_Count'])
    # ---

    df_unified = unified_table_(df)
    # group by date
    df_ = df.groupby('Date').sum()

    # Create the line and the bar graph with totals
    fig1= go.Figure()
    for shop in shops:
        #fig.add_trace(go.Scatter(x=df_unified.index, y=df_unified[f'{measure} - {shop}'], name=f'{measure} - {shop}'))
        fig1.add_trace(go.Bar(x=df_unified.index, y=df_unified[f'{measure} - {shop}'], name=f'{measure} - {shop}'))
    fig1.update_layout(legend_orientation="h", width = 1250, height = 600)
    st.plotly_chart(fig1) 
elif menu_id == 'Dashboard':
        # open csv file
    df = pd.read_csv('Dishoom_/myReport - 2022-07-13T120124.897 copy.csv')

    # Clean from 0 values
    df = df.drop(df[df['Item_Sales'] == 0].index)
    df = df.drop(df[df['Net_Sales'] == df['Void_Total']].index)

    # divide data by store
    stores = df['Store_Name'].unique()
    table_by_store = []

    for store in stores:
        table_by_store.append(pd.DataFrame(df[df['Store_Name'] == store])) 

    # Create a different table for each date
    dates = df['Date'].unique()
    table_by_date = []
    for date in dates:
        table_by_date.append(pd.DataFrame(df[df['Date'] == date])) 

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    options = ['Net_Sales', 'Gross_Sales', 'Void_Total', 'Item_Sales', 'Guest_Count']

    selected_graph = st.selectbox('Graph', options, key = 1)

    for i, df_ in enumerate(table_by_date):
        with st.expander(f'{dates[i]} - {days[i]}'):
            #st.write(df)

            # breakfast, lunch, afternoon, dinner
            breakfast = df_[df_['Day_Part_Name'] == 'Breakfast']
            breakfast_total = breakfast[f'{selected_graph}'].sum()

            lunch = df_[df_['Day_Part_Name'] == 'Lunch']
            lunch_total = lunch[f'{selected_graph}'].sum()

            afternoon = df_[df_['Day_Part_Name'] == 'Afternoon']
            afternoon_total = afternoon[f'{selected_graph}'].sum()

            dinner = df_[df_['Day_Part_Name'] == 'Dinner']
            dinner_total = dinner[f'{selected_graph}'].sum()

            st.text(f'Total: {breakfast_total + lunch_total + afternoon_total + dinner_total}')

            c1,c2 = st.columns(2)
            with c1:
                pie = px.pie(df_, values=f'{selected_graph}', names='Day_Part_Name', color = 'Day_Part_Name')
                # put legend in the middle of the pie
                fig = go.Figure(data=pie)
                fig.update_layout(legend_orientation="h")
                st.plotly_chart(fig)
            with c2:
                bar = px.bar(df_, x='Day_Part_Name', y=f'{selected_graph}', color = 'Day_Part_Name',width = 500)
                fig = go.Figure(data=bar)
                # take off the legend
                fig.update_layout(legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01)
                    )           
                st.plotly_chart(fig)

            # group by hour
            data_ = df_.groupby('Hour').sum()
            

            #plot
            hour_net_sales = px.line(x=data_.index, y=data_['Net_Sales'], title='Hourly Net Sales', width=1000, height=600)
            hour_gross_sales = px.line(x=data_.index, y=data_['Gross_Sales'], title='Hourly Gross Sales', width=1000, height=600)
            hour_void_total = px.line(x=data_.index, y=data_['Void_Total'],     title='Hourly Void Total', width=1000, height=600) 
            hour_item_sales = px.line(x=data_.index, y=data_['Item_Sales'], title = 'Hourly Item Sales',    width=1000, height=600)
            hour_guest_count = px.line(x=data_.index, y=data_['Guest_Count'], title = 'Hourly Guest Count', width=1000, height=600)
            import plotly.graph_objs as go
            # plot all in same graph
        
            if selected_graph == 'Net_Sales':
                st.plotly_chart(hour_net_sales)
            elif selected_graph == 'Gross_Sales':
                st.plotly_chart(hour_gross_sales)
            elif selected_graph == 'Void_Total':
                st.plotly_chart(hour_void_total)
            elif selected_graph == 'Item_Sales':
                st.plotly_chart(hour_item_sales)
            elif selected_graph == 'Guest_Count':
                st.plotly_chart(hour_guest_count)
# Restaurants
elif menu_id == 'D1':
    store_ = 'D1 - Dishoom Covent Garden'
    get_store_data(store_)
elif menu_id == 'D2':
    store_ = 'D2 - Dishoom Shoreditch'
    get_store_data(store_)
elif menu_id == 'D3':
    store_ = 'D3 - Dishoom Kings Cross'
    get_store_data(store_)
elif menu_id == 'D4':
    store_ = 'D4 - Dishoom Carnaby'
    get_store_data(store_)
elif menu_id == 'D5':
    store_ = 'D5 - Dishoom Edinburgh'
    get_store_data(store_)
elif menu_id == 'D6':
    store_ = 'D6 - Dishoom Kensington'
    get_store_data(store_)
elif menu_id == 'D7':
    store_ = 'D7 - Dishoom Manchester'
    get_store_data(store_)
elif menu_id == 'D8':
    store_ = 'D8 - Dishoom Birmingham'
    get_store_data(store_)
# Delivery Kitchens
elif menu_id == 'D101':
    store_ = 'D101 - Dishoom Battersea'
    get_store_data(store_)
elif menu_id == 'D102':
    store_ = 'D102 - Dishoom Whitechapel'
    get_store_data(store_)
elif menu_id == 'D103':
    store_ = 'D103 - Dishoom Swiss Cottage'
    get_store_data(store_)
elif menu_id == 'D104':
    store_ = 'D104 - Dishoom Park Royal'
    get_store_data(store_)
elif menu_id == 'D105':
    store_ = 'D105 - Dishoom Islington'
    get_store_data(store_)
elif menu_id == 'D106':
    store_ = 'D106 - Dishoom Blackwall'
    get_store_data(store_)
elif menu_id == 'D107':
    store_ = 'D107 - Dishoom Brighton'
    get_store_data(store_)
elif menu_id == 'D108':
    store_ = 'D108 - Dishoom Cambridge'
    get_store_data(store_)
elif menu_id == 'D109':
    store_ = 'D109 - Dishoom Wandsworth'
    get_store_data(store_)
elif menu_id == 'D110':
    store_ = 'D110 - Dishoom Bermondsey'
    get_store_data(store_)
elif menu_id == 'D111':
    store_ = 'D111 - Dishoom Acton'
    get_store_data(store_)
elif menu_id == 'D112':
    store_ = 'D112 - Dishoom Dulwich'
    get_store_data(store_)
# rota checker
elif menu_id == 'Rota_Checker':
    st.title('Rota Checker')
    from Cover_Predictor_ARIMA import Arima
    from Cover_Predictor_LSTM import LSTM
    from Cover_Predictor_LSTM_ import LSTM_

    from genetic_algorithm import GeneticAlgorithm
    from main import Esteban
    import pandas as pd

    st.sidebar.title('Generating Rota')

    tech = st.sidebar.selectbox('Technique', ['Genetic Algorithm', 'AlgoEsteban'])
    if tech == 'Genetic Algorithm':
        GeneticAlgorithm()
    elif tech == 'AlgoEsteban':
        Esteban()

        if st.checkbox('Assign Shifts'):
            st.write('Assigning Shifts')

elif menu_id == 'Employees':
    all_employees = get_all_employees()
    if all_employees is not None:
        # Show employees list and edit UI   
        for e in all_employees:
            with st.expander("%s %s" % (e[1], e[2])):
                st.write("Shifts: %s" % e[3])
                if st.checkbox("Edit", key = e[0]):
                    name = st.text_input("EDIT Name", e[1])
                    role = st.text_input("EDIT Role", e[2])
                    shifts = st.text_input("EDIT Shifts", e[3])
                    if st.button("Save", key = e[0]):
                        # modify employee in the database
                        update_employee(e[0], name, role, shifts)
                        st.success("Employee updated")
                if st.button("Delete",key = e[0]):
                    if st.button("Confirm", key = e[0]):
                        delete_employee(e[0])
                        st.success("Employee deleted")
    else:
        st.write("No employees found")

elif menu_id == 'ADD':
    st.sidebar.title("Employee Database")
    create_employees_table()

    # Delete All
    if st.sidebar.button('Delete all'):
        delete_all_employees()
        st.success("All employees deleted")
        
    # Add employee
    with st.expander("Add Employee"):
        name = st.text_input("Name")
        role = st.text_input("Role")
        shifts = st.text_input("Shifts")
        if st.button("Confirm"):
            # add employee to the database
            done = add_employee(name, role, shifts)
            if done:
                st.success("Employee added")
            else:
                st.error("Employee already exists")
            # refresh the page

    all_employees = get_all_employees()

    for e in all_employees:
        with st.expander("%s %s" % (e[1], e[2])):
            st.write("Shifts: %s" % e[3])
            if st.checkbox("Edit", key = e[0]):
                name = st.text_input("EDIT Name", e[1])
                role = st.text_input("EDIT Role", e[2])
                shifts = st.text_input("EDIT Shifts", e[3])
                if st.button("Save", key = e[0]):
                    # modify employee in the database
                    update_employee(e[0], name, role, shifts)
                    st.success("Employee updated")
            if st.button("Delete",key = e[0]):
                if st.button("Confirm", key = e[0]):
                    delete_employee(e[0])
                    st.success("Employee deleted")

elif menu_id == 'ML':
    from Cover_Predictor_ARIMA import Arima
    from Cover_Predictor_LSTM import LSTM
    from Cover_Predictor_LSTM_ import LSTM_

    from genetic_algorithm import GeneticAlgorithm
    from main import Esteban
    import pandas as pd
    import numpy as np
    import pydeck as pdk

    guest_count = 1000
    lat = 51.537430
    long = -0.125250
    n = guest_count

    df = pd.read_csv("Dishoom_/myReport - 2022-07-13T120124.897 copy.csv")
    #
    restaurants = [
    'D1 - Dishoom Covent Garden',
    'D2 - Dishoom Shoreditch',
    'D3 - Dishoom Kings Cross',
    'D4 - Dishoom Carnaby',
    'D5 - Dishoom Edinburgh',
    'D6 - Dishoom Kensington',
    'D7 - Dishoom Manchester',
    'D8 - Dishoom Birmingham',
    ]
    df = df[df['Store_Name'].isin(restaurants)]
    df = df.groupby('Store_Name').count()
    # sort restaurants by length of name

    lats_log = [
        [51.512383, -0.127173],   # Covent Garden 1
        [51.52454, -0.076682],    # Shoreditch 2
        [51.53613, -0.125694],    # KX 3
        [51.5130843, -0.1397679], # Carnaby 4
        [55.953572, -3.1926045],  # Edinburgh 
        [51.501264, -0.191075],   # Kensigton
        [53.4810344, -2.2501745], # Manchester
        [52.4799, -1.897],        # Birmingham
    ]
    cols = ['Guest_Count', 'Net_Sales','Gross_Sales','Item_Sales']
    indicator = st.selectbox('Select a indicator', cols)

    data_ = list(df[indicator])
    data = df[indicator]
    lats_log = pd.DataFrame(lats_log, columns=['lat', 'lon'], index = restaurants)
    
    # merge the two dataframes
    df = pd.merge(data, lats_log, left_index=True, right_index=True)

    frame = []
    for i in range(len(restaurants)-1):
        lat_ = lats_log.iloc[i]['lat']
        lon_ = lats_log.iloc[i]['lon']
        restaurant = restaurants[i]
        count = int(data_[i]/2)
       
        df = pd.DataFrame(
            np.random.randn(count, 2) / [2000, 2000] + [lat_, lon_],
            columns=['lat', 'lon'])
        frame.append(df)

    df = pd.concat(frame)

    def create_map(df):
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=pdk.ViewState(
                latitude=lat,
                longitude=long,
                zoom=12,
                pitch=50,
            ),
            layers=[
                pdk.Layer(
                    'HexagonLayer',
                    data=df,
                    get_position='[lon, lat]',
                    radius=20,
                    elevation_scale=4,
                    elevation_range=[0, 200],
                    pickable=True,
                    extruded=True,
                ),
                pdk.Layer(
                    'ScatterplotLayer',
                    data=df,
                    get_position='[lon, lat]',
                    get_color='[200, 30, 0, 160]',
                    get_radius=10,
                ),
            ],
        ))

    map = True
    if map:
        with st.expander('Map'):
            create_map(df)
    
    st.sidebar.title('Machine Learning - Cover Predict')
    with st.sidebar.expander('Upload Data'):
        uploaded_file = st.file_uploader("Choose a file")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        store = st.sidebar.selectbox('Select Store', df['Store_Name'].unique())
        map = False

        # Filter out the data that we don't need, keep only KX
        df = df[df['Store_Name'] == store]

        # Transform the data into the right form -> # get hour_by_hour data
        def unified():
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
  
        # transform the guest_count into a series of integers
        data = unified()
        data = data[f'Guest_Count - {store}'].apply(lambda x: int(x))

        model = st.sidebar.selectbox('Model', ['LSTM', 'ARIMA', 'LSTM Weekly sequence'])

        if model == 'LSTM':
            LSTM(data)
        elif model == 'ARIMA':
            Arima(data)
        elif model == 'LSTM Weekly sequence':
            LSTM_(data)
    
if __name__ == '__main__':
    if not st._is_running_with_streamlit:
        import os
        os.system('streamlit run Dishoom_/home.py')