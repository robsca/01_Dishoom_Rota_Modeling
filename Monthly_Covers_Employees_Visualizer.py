import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
from helper_functions import *

# title
st.sidebar.title('Rota Modeling')

with st.sidebar.expander('Import data'):
    uploaded_file_1 = st.file_uploader("Select Employees Data")
    uploaded_file_2 = st.file_uploader("Select Covers Data")

if uploaded_file_1 is not None and uploaded_file_2 is not None:

    data_employee = create_final_timeseries(uploaded_file_1,uploaded_file_2)
    
    with st.expander('Data'):
        st.write(data_employee)

    with st.sidebar.expander('Download data'):
        @st.cache # cache the function
        def convert_df(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv().encode('utf-8')
        
        csv = convert_df(data_employee)
        name = st.text_input('File name', 'data')
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f'{name}.csv',
            mime='text/csv',
        )
        
    # create a list of restaurants
    restaurants = data_employee['Store_Name'].unique()

    selected = st.selectbox('Select a restaurant', restaurants)
    # get the df for that restaurant
    data_employee = data_employee[data_employee['Store_Name'] == selected]

    # ----------------- #
    # plot
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_employee.index, y=data_employee['Guest_Count'], name='Guest Count'))
    fig.add_trace(go.Scatter(x=data_employee.index, y=data_employee['Employees_Count'], name='Employees'))
    fig.update_layout(
        title="Guest Count vs Employees",
        xaxis_title="Date",
        yaxis_title="Count",
        legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            color="#7f7f7f"
        )
    )
    st.plotly_chart(fig, use_container_width=True)