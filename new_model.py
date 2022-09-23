'''
1. Use historic covers/sales data to predict covers by date and hour across given period of time (start with 1 month).
2. Prepose IDEAL Covers per Hour ratio per date / DoW and Hour - we use this variable as our 'demand' elasticity
3. Use current team sizes to propose TOTAL hours that should be worked, given our Covers per Hour ratio

P.S.: Eventually consider data like part of two different buckets: FOH and BOH.
'''
import pandas as pd
import streamlit as st
st.set_page_config(layout="wide")

# title
st.sidebar.title('Rota Modeling')
# choose ratio - Guest vs
ratio = st.sidebar.slider('Ratio', 0.0, 5.0, 2.0, 0.25)

with st.sidebar.expander('Import data'):
    uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # 1. Merge time and dates
    df['Date'] = df.apply(lambda x: x['Date'] + ' ' + str(str(x['Hour']) + ':' + '00'), axis=1)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 2. Get unique restaurants
    restaurants = df['Store_Name'].unique()
    frame = []
    for restaurant in restaurants:
        # filter data for each restaurant
        df_restaurant = df[df['Store_Name'] == restaurant]
        # group by date
        df_restaurant = df_restaurant.groupby('Date').sum()
        # add a column for the ideal number of employees 
        df_restaurant['Ideal'] = df_restaurant['Guest_Count'] / ratio
        # add store name
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

    # Choose the column that you want to visualize
    features = ['Guest_Count', 'Ideal', 'Store_Name', 'Hour', 'Part_of_day', 'Day_of_week']
    st.write(df[features])

    @st.cache # cache the function
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

    with st.sidebar.expander('Download data'):
        csv = convert_df(df)
        name = st.text_input('File name', 'data')
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f'{name}.csv',
            mime='text/csv',
        )

    # Visualize the data
    import plotly.graph_objects as go
    figure = go.Figure()
    figure.add_trace(go.Bar(x=df.index, y=df['Guest_Count'], name='Guest Count'))
    figure.add_trace(go.Bar(x=df.index, y=df['Ideal'], name='Ideal'))
    st.plotly_chart(figure, use_container_width=True)