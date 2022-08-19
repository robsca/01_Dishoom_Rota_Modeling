import streamlit as st
st.set_page_config(layout='wide',initial_sidebar_state='collapsed')
import pandas as pd
import plotly.graph_objs as go
from main import actual_hours
import datetime
######################
import hydralit_components as hc

# Images
markd = '''
<img src="https://www.dishoom.com/assets/img/roundel-seva.png" width = "120" heigth = "120" >
'''
st.markdown(markd, unsafe_allow_html=True)


# 5. Filter the data (filter by time period, restaurants and measure)
def filter(data, start_date, end_date, res):
    # add 1
    data_filtered = data[(data['Date'] >= start_date) & (data['Date'] <= end_date)]
    # add column with day of week
    data_filtered['Day of Week'] = data_filtered['Date'].apply(get_day_of_week)
    data_filtered = data_filtered[data_filtered['Store_Name'].isin(res)]
    return data_filtered

# get day of week
def get_day_of_week(date):
    day_of_week = datetime.datetime.strptime(date, '%m-%d-%Y').weekday()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    return days[day_of_week]

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
            },]

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


# 1. Import Data 2019, 2022
path1 = "/Users/robertoscalas/Desktop/2019-2022 Dishoom/Aloha_Sales_Data_Export_2019_July.csv"
path2 = "/Users/robertoscalas/Desktop/2019-2022 Dishoom/Aloha_Sales_Data_Export_2022_July.csv"
path3 = "/Users/robertoscalas/Desktop/2019-2022 Dishoom/ActualHoursvRotaHours_2022_Jul.xlsx"
data2019 = pd.read_csv(path1)
data2022 = pd.read_csv(path2)

def Plotter_(plot = True ):
    # 3. Define Restaurants that will be analyzed
    restaurant_col_2019 = data2019['Store_Name'].unique()
    res = st.sidebar.multiselect('Select a restaurant', restaurant_col_2019, default=restaurant_col_2019[0])

    # 4. Define measure to check
    measure = st.sidebar.selectbox('Select a measure', ['Guest_Count', 'Net_Sales', "Gross_Sales"])

    # DATA about Customers
    data_filtered_2019 = filter(data2019, start_date_2019, end_date_2019, res)
    data_filtered_2022 = filter(data2022, start_date_2022, end_date_2022, res)

    # Data about Employees
    data_Hours = actual_hours(path3, res, start_date_2022, end_date_2022) # len() = days in the time period

    # 6. Group by date and restaurant
    from functions import unified
    c1,c2 = st.columns(2)
    with c1:
        unified_data_2019 = unified(data_filtered_2019)
        with st.expander("Unified data 2019"):
            st.write(unified_data_2019)
    with c2:
        unified_data_2022 = unified(data_filtered_2022)
        with st.expander("Unified data 2022"):
            st.write(unified_data_2022)

    x = []
    # 6. Group by date and restaurant -> variation
    from functions import unified_
    unified_data_2019_ = unified_(data_filtered_2019, res[0])
    unified_data_2022_ = unified_(data_filtered_2022, res[0])

    list_of_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
                    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
                    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
                    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for i, day in enumerate(unified_data_2019_):
            day_2022 = unified_data_2022_[i]
            try:
                with st.expander(f'{date_col_2019[i]} - {date_col_2022[i]} - {list_of_days[i]}'):

                    x1 = [i+7 for i in range(len(day))]
                    x2 = [i+7 for i in range(len(day_2022))]
                    # add sublot with secondary axis
                    from plotly.subplots import make_subplots
                    # Create figure with secondary y-axis
                    fig = make_subplots(specs=[[{"secondary_y": True}]])
                    # Add traces
                    fig.add_trace(go.Bar(x =data_Hours[i]['Hour'], y = data_Hours[i]['Count'], name = f'{res[0]} - {date_col_2022[i]} ROTA', opacity=0.6),secondary_y=True)
                    fig.add_trace(go.Scatter(x=x1, y=day[f'{measure} - {res[0]} - {date_col_2019[i]}'], name=f'{res[0]} - {date_col_2019[i]} - {measure}',fill='tozeroy'),secondary_y=False)
                    fig.add_trace(go.Scatter(x=x2, y=day_2022[f'{measure} - {res[0]} - {date_col_2022[i]}'], name=f'{res[0]} - {date_col_2022[i]} - {measure}', fill='tonexty'),secondary_y=False)

##################### Add New Trace with ratio of guest_count data_hours
                    
                    # To do this the len of the lists must be the same
                    new_axes = [guest_count/data_hour if guest_count != 0 and data_hour !=0 else 0 for guest_count, data_hour in zip(day_2022[f'{measure} - {res[0]} - {date_col_2022[i]}'], data_Hours[i]['Count'])]
                    c1,c2 = st.columns(2)

                    with c1:
                        st.write(len(data_Hours[i]['Count']))
                        st.write(data_Hours[i]['Count'])
                    with c2:
                        st.write(len(day_2022[f'{measure} - {res[0]} - {date_col_2022[i]}']))
                        st.write(day_2022[f'{measure} - {res[0]} - {date_col_2022[i]}'])


                    x3 = [i+7 for i in range(len(day_2022[f'{measure} - {res[0]} - {date_col_2022[i]}']))]
                    fig.add_trace(go.Bar(x=x3, y=new_axes, name=f'{res[0]} - {date_col_2022[i]} - {measure}/Labour Hours - {res[0]}'),secondary_y=True)
                    
###############################################################################################
                    # Add figure title
                    fig.update_layout(
                        title_text=f"Double Y Axis {measure} - Labour Hours",
                    )

                    # Set x-axis title
                    fig.update_xaxes(title_text=" Hours")

                    # Set y-axes titles
                    fig.update_yaxes(title_text=f"<b>{measure}</b> yaxis", secondary_y=False)
                    fig.update_yaxes(title_text="<b>Labour Hours</b> yaxis", secondary_y=True)
                    fig.update_layout(legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01
                    ))
                    # modify width and height
                    if plot:
                        st.plotly_chart(fig)
                    # append figure to list
                    x.append(fig)
            except:
                pass
    return x

def Plotter(plot = True ):
    # 3. Define Restaurants that will be analyzed
    restaurant_col_2019 = data2019['Store_Name'].unique()
    res = st.sidebar.multiselect('Select a restaurant', restaurant_col_2019, default=restaurant_col_2019[0])

    # 4. Define measure to check
    measure = st.sidebar.selectbox('Select a measure', ['Guest_Count', 'Net_Sales', "Gross_Sales"])


    # DATA about Customers
    data_filtered_2019 = filter(data2019, start_date_2019, end_date_2019, res)
    data_filtered_2022 = filter(data2022, start_date_2022, end_date_2022, res)

    # Data about Employees
    data_Hours = actual_hours(path3, res, start_date_2022, end_date_2022) # len() = days in the time period

    # 6. Group by date and restaurant
    from functions import unified
    c1,c2 = st.columns(2)
    with c1:
        unified_data_2019 = unified(data_filtered_2019)
        with st.expander("Unified data 2019"):
            st.write(unified_data_2019)
    with c2:
        unified_data_2022 = unified(data_filtered_2022)
        with st.expander("Unified data 2022"):
            st.write(unified_data_2022)

    x = []
    # 6. Group by date and restaurant -> variation
    from functions import unified_
    unified_data_2019_ = unified_(data_filtered_2019, res[0])
    unified_data_2022_ = unified_(data_filtered_2022, res[0])

    list_of_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
                    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
                    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
                    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for i, day in enumerate(unified_data_2019_):
            day_2022 = unified_data_2022_[i]
            try:
                with st.expander(f'{date_col_2019[i]} - {date_col_2022[i]} - {list_of_days[i]}'):

                    x1 = [i+7 for i in range(len(day))]
                    x2 = [i+7 for i in range(len(day_2022))]
                    # add sublot with secondary axis
                    from plotly.subplots import make_subplots
                    # Create figure with secondary y-axis
                    fig = make_subplots(specs=[[{"secondary_y": True}]])
                    # Add traces
                    fig.add_trace(go.Bar(x =data_Hours[i]['Hour'], y = data_Hours[i]['Count'], name = f'{res[0]} - {date_col_2022[i]} ROTA', opacity=0.6),secondary_y=True)
                    fig.add_trace(go.Scatter(x=x1, y=day[f'{measure} - {res[0]} - {date_col_2019[i]}'], name=f'{res[0]} - {date_col_2019[i]} - {measure}',fill='tozeroy'),secondary_y=False)
                    fig.add_trace(go.Scatter(x=x2, y=day_2022[f'{measure} - {res[0]} - {date_col_2022[i]}'], name=f'{res[0]} - {date_col_2022[i]} - {measure}', fill='tonexty'),secondary_y=False)
                    # Add figure title
                    fig.update_layout(
                        title_text=f"Double Y Axis {measure} - Labour Hours",
                    )

                    # Set x-axis title
                    fig.update_xaxes(title_text=" Hours")

                    # Set y-axes titles
                    fig.update_yaxes(title_text=f"<b>{measure}</b> yaxis", secondary_y=False)
                    fig.update_yaxes(title_text="<b>Labour Hours</b> yaxis", secondary_y=True)
                    fig.update_layout(legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01
                    ))
                    # modify width and height
                    if plot:
                        st.plotly_chart(fig)
                    # append figure to list
                    x.append(fig)
            except:
                pass
    return x

#get the id of the menu item clicked
if menu_id == 'TP':
    date_col_2019 = data2019['Date'].unique()[:-3]
    date_col_2022 = data2022['Date'].unique()[3:]
    #'''
    #start_date, end_date = st.sidebar.select_slider(
    #    'Select a time period',
    #    options=date_col_2019,
    #    value=(date_col_2019[0], date_col_2019[-1]),
    #)
    #'''
    # start on monday
    start_date_2019 = date_col_2019[0]
    end_date_2019 = date_col_2019[-1]
    # start on monday
    start_date_2022 = date_col_2022[0]
    end_date_2022 = date_col_2022[-1]

    x = Plotter()

if menu_id == 'Weekly view':
    date_col_2019 = data2019['Date'].unique()[:-3]
    date_col_2022 = data2022['Date'].unique()[3:]

    num_week = st.sidebar.slider('Select a week', 1, (len(date_col_2019)//7)+1, 1)  

    
    # get all the day that are part of that week
    days_2019 = [date_col_2019[(num_week-1)*7:((num_week-1)*7)+7]][0]
    days_2022 = [date_col_2022[(num_week-1)*7:((num_week-1)*7)+7]][0]
    
    date_col_2019 = days_2019
    date_col_2022 = days_2022
    # moodify date_col_2019

    
    start_date_2019 = days_2019[0]
    end_date_2019 = days_2019[-1]
    start_date_2022 = days_2022[0]
    end_date_2022 = days_2022[-1]

    x = Plotter()

if menu_id == 'Monday':
    st.subheader('Mondays')
    date_col_2019 = data2019['Date'].unique()[:-3]
    date_col_2022 = data2022['Date'].unique()[3:]
    start_date_2019 = date_col_2019[0]
    end_date_2019 = date_col_2019[-1]
    start_date_2022 = date_col_2022[0]
    end_date_2022 = date_col_2022[-1]

    x = Plotter_(False)

    # plot every monday
    for i, fig in enumerate(x):
        if i%7 == 0:
            with st.expander(f'{date_col_2019[i]} - {date_col_2022[i]} - Monday'):
                # make fig bigger
                fig.update_layout(
                    height=600,
                    width=800
                )
                st.plotly_chart(fig)
                st.write('---')

elif menu_id == 'Tuesday':
    st.subheader('Tuesdays')
    date_col_2019 = data2019['Date'].unique()[:-3]
    date_col_2022 = data2022['Date'].unique()[3:]

    start_date_2019 = date_col_2019[0]
    end_date_2019 = date_col_2019[-1]

    start_date_2022 = date_col_2022[0]
    end_date_2022 = date_col_2022[-1]

    # plot every tuesday
    x = Plotter_(False)

    for i, fig in enumerate(x):
        if i%7 == 1:
            with st.expander(f'{date_col_2019[i]} - {date_col_2022[i]} - Tuesday'):
                # make fig bigger
                fig.update_layout(
                    height=600,
                    width=800
                )
                st.plotly_chart(fig)
                st.write('---')

elif menu_id == 'Wednesday':
    st.subheader('Wednesdays')
    date_col_2019 = data2019['Date'].unique()[:-3]
    date_col_2022 = data2022['Date'].unique()[3:]

    start_date_2019 = date_col_2019[0]
    end_date_2019 = date_col_2019[-1]

    start_date_2022 = date_col_2022[0]
    end_date_2022 = date_col_2022[-1]
    x = Plotter_(False)

    # plot every wednesday
    for i, fig in enumerate(x):
        if i%7 == 2:
            with st.expander(f'{date_col_2019[i]} - {date_col_2022[i]} - Wednesday'):
                # make fig bigger
                fig.update_layout(
                    height=600,
                    width=800
                )
                st.plotly_chart(fig)
                st.write('---')

elif menu_id == 'Thursday':
    st.subheader('Thursdays')
    date_col_2019 = data2019['Date'].unique()[:-3]
    date_col_2022 = data2022['Date'].unique()[3:]

    start_date_2019 = date_col_2019[0]
    end_date_2019 = date_col_2019[-1]

    start_date_2022 = date_col_2022[0]
    end_date_2022 = date_col_2022[-1]

    # plot every thursday
    x = Plotter_(False)

    for i, fig in enumerate(x):
        if i%7 == 3:
            with st.expander(f'{date_col_2019[i]} - {date_col_2022[i]} - Thursday'):
                # make fig bigger
                fig.update_layout(
                    height=600,
                    width=800
                )
                st.plotly_chart(fig)
                st.write('---')

elif menu_id == 'Friday':
    st.subheader('Fridays')
    date_col_2019 = data2019['Date'].unique()[:-3]
    date_col_2022 = data2022['Date'].unique()[3:]

    start_date_2019 = date_col_2019[0]
    end_date_2019 = date_col_2019[-1]

    start_date_2022 = date_col_2022[0]
    end_date_2022 = date_col_2022[-1]

    # plot every friday
    x = Plotter_(False)

    for i, fig in enumerate(x):
        if i%7 == 4:
            with st.expander(f'{date_col_2019[i]} - {date_col_2022[i]} - Friday'):
                # make fig bigger
                fig.update_layout(
                    height=600,
                    width=800
                )
                st.plotly_chart(fig)
                st.write('---')

elif menu_id == 'Saturday':
    st.subheader('Saturdays')
    date_col_2019 = data2019['Date'].unique()[:-3]
    date_col_2022 = data2022['Date'].unique()[3:]

    start_date_2019 = date_col_2019[0]
    end_date_2019 = date_col_2019[-1]

    start_date_2022 = date_col_2022[0]
    end_date_2022 = date_col_2022[-1]

    # plot every saturday
    x = Plotter_(False)

    for i, fig in enumerate(x):
        if i%7 == 5:
            with st.expander(f'{date_col_2019[i]} - {date_col_2022[i]} - Saturday'):
                # make fig bigger
                fig.update_layout(
                    height=600,
                    width=800
                )
                st.plotly_chart(fig)
                st.write('---')

elif menu_id == 'Sunday':
    st.subheader('Sundays')
    date_col_2019 = data2019['Date'].unique()[:-3]
    date_col_2022 = data2022['Date'].unique()[3:]

    start_date_2019 = date_col_2019[0]
    end_date_2019 = date_col_2019[-1]

    start_date_2022 = date_col_2022[0]
    end_date_2022 = date_col_2022[-1]

    # plot every sunday
    x = Plotter_(False)

    for i, fig in enumerate(x):
        if i%7 == 6:
            with st.expander(f'{date_col_2019[i]} - {date_col_2022[i]} - Sunday'):
                # make fig bigger
                fig.update_layout(
                    height=600,
                    width=800
                )
                st.plotly_chart(fig)
                st.write('---')

else:
    st.write('Please select a day')


# get only the data for the selected restaurant
    
def plot_whole_thing():
    # 7. Plot data
    fig = go.Figure()
    for r in res:
        x_1 = [x for x in range(len(unified_data_2019[f'{measure} - {r}']))]
        x_2 = [x for x in range(len(unified_data_2022[f'{measure} - {r}']))]
        fig.add_trace(go.Line(x=x_1, y=unified_data_2019[f'{measure} - {r}'], name=f'{r} 2019'))
        fig.add_trace(go.Line
                        (x=x_2, y=unified_data_2022[f'{measure} - {r}'], name=f'{r} 2022'))


    fig.update_layout(title='Sales per restaurant', xaxis_title='Date', yaxis_title='Sales')
    st.plotly_chart(fig)