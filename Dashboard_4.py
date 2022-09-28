import streamlit as st
import pandas as pd
import numpy as np

def two():

    with st.sidebar.expander('Import data'):
        uploaded_file_1 = st.file_uploader("Data 1")
        uploaded_file_2 = st.file_uploader("Data 2")

    if uploaded_file_1 is not None:
        with st.expander('Data 1'):
            data1 = pd.read_csv(uploaded_file_1)
            # translate data1['Date'] to datetime
            data1['Date'] = pd.to_datetime(data1['Date'])
            # set index
            data1.set_index('Date', inplace=True)
            
            # get ratio
            data1['Ratio'] = data1['Guest_Count'] / data1['Employees_Count']


            st.write(data1)
        
            # create a list of restaurants
            restaurants = data1['Store_Name'].unique()
            # add all restaurants to the list        
            restaurants = np.append(restaurants, 'All Restaurants')

            selected = st.sidebar.selectbox('Select a restaurant', restaurants)
            if selected == 'All Restaurants':
                # drop the column 'Store_Name'
                data1 = data1.drop(columns=['Store_Name'])
                # group by hour
                data1 = data1.groupby(data1.index).sum()
                # create a new column 'Hours'
                data1['Hour'] = data1.index.hour
                # add a column 'Day'
                data1['Day_of_week'] = data1.index.day_name()
                #st.write(data1)
                st.subheader('Employees Data - All Restaurants')
            # get the df for that restaurant
            else:
                data1 = data1[data1['Store_Name'] == selected]
                st.subheader(f'Employees Data - {selected}')
                #st.write(data1)
            # ----------------- #
            # plot
            import plotly.graph_objects as go
            fig_timeries = go.Figure()
            fig_timeries.add_trace(go.Scatter(x=data1.index, y=data1['Guest_Count'], name='Guest Count', fill='tozeroy'))
            fig_timeries.add_trace(go.Scatter(x=data1.index, y=data1['Employees_Count'], name='Employees Count', fill='tozeroy'))
            fig_timeries.update_layout(
                title="Guest Count vs Employees",
                xaxis_title="Date",
                yaxis_title="Count",
                legend_title="Legend Title",
                font=dict(
                    family="Courier New, monospace",
                    color="#7f7f7f"
                )
            )

            # ----------------- #
            # CREATE HEATMAP
            # Filter out hours < 9 and > 23
            data1 = data1[(data1.index.hour >= 9) & (data1.index.hour < 23)]
            
            # group by day making average of the guests and employees
            days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            frame = []
            for day in days_of_week:
                # filter by day
                data1_day = data1[data1['Day_of_week'] == day]
                data1_day = data1_day.groupby(data1['Hour']).mean()
                # modify guest count as ratio
                data1_day['Guest_Count'] = data1_day['Guest_Count'] / data1_day['Employees_Count']        
                # drop hour column
                data1_day = data1_day.drop(columns=['Hour'])
                # drop employees count
                data1_day = data1_day.drop(columns=['Employees_Count'])
                # rename guest count
                data1_day = data1_day.rename(columns={'Guest_Count': day})
                transposed_day = data1_day.T
                # add to list
                frame.append(transposed_day)

            data1s_heat = pd.concat(frame)
            #st.write(data1s_heat)
            
            st.plotly_chart(fig_timeries, use_container_width=True)

            # plot heatmap
            import plotly.express as px
            fig = px.imshow(data1s_heat, labels=dict(x="Hour", y="Day of week", color="Guests per employee"))
            # from red to green
            

            fig.update_layout(
                title="Guests per employee",
                xaxis_title="Hour",
                yaxis_title="Day of week",
                legend_title="Legend Title",
                font=dict(
                    family="Courier New, monospace",
                    color="#7f7f7f"
                )
            )
            #st.plotly_chart(fig, use_container_width=True)

            # plot as go
            import plotly.graph_objects as go
            fig = go.Figure(data=go.Heatmap(    
                z=data1s_heat.values,
                x=data1s_heat.columns,
                y=data1s_heat.index[::-1],
                colorscale='Turbo',
                # set as min of the whole dataset
                zmin=data1s_heat.values.min(),
                # set as max of the whole df
                zmax=data1s_heat.values.max(),
                colorbar=dict(
                    title="Guests per employee",
                    titleside="right",
                    tickmode="array",
                    tickvals=[data1s_heat.values.min(), 2.0, data1s_heat.values.max()],
                    ticktext=["Over-Staffed", "Ideal", "Under-Staffed"],
                    ticks="outside"
                )
            ))
            fig.update_layout(
                title="Guests per employee",
                xaxis_title="Hour",
                yaxis_title="Day of week",
                legend_title="Legend Title",
                font=dict(
                    family="Courier New, monospace",
                    color="#7f7f7f"
                )
            )
            st.plotly_chart(fig, use_container_width=True)

    if uploaded_file_2 is not None:
        with st.expander('Data 2'):
            data2 = pd.read_csv(uploaded_file_2)
            # translate data1['Date'] to datetime
            data2['Date'] = pd.to_datetime(data2['Date'])
            # set index
            data2.set_index('Date', inplace=True)

            # get ratio
            data2['Ratio'] = data2['Guest_Count'] / data2['Employees_Count']
            st.write(data2)


            # create a list of restaurants
            restaurants = data2['Store_Name'].unique()
            # add all restaurants to the list
            restaurants = np.append(restaurants, 'All Restaurants')

            selected = st.sidebar.selectbox('Select a restaurant', restaurants, key='2')
            if selected == 'All Restaurants':
                # drop the column 'Store_Name'
                data2 = data2.drop(columns=['Store_Name'])
                # group by hour
                data2 = data2.groupby(data2.index).sum()
                # create a new column 'Hours'
                data2['Hour'] = data2.index.hour
                # add a column 'Day'
                data2['Day_of_week'] = data2.index.day_name()
                #st.write(data1)
                st.subheader('Employees Data - All Restaurants')
            # get the df for that restaurant
            else:
                data2 = data2[data2['Store_Name'] == selected]
                st.subheader(f'Employees Data - {selected}')
                #st.write(data1)
            # ----------------- #
            # plot
            import plotly.graph_objects as go
            fig_timeries = go.Figure()
            fig_timeries.add_trace(go.Scatter(x=data2.index, y=data2['Guest_Count'], name='Guest Count', fill='tozeroy'))
            fig_timeries.add_trace(go.Scatter(x=data2.index, y=data2['Employees_Count'], name='Employees Count', fill='tozeroy'))
            fig_timeries.update_layout(
                title="Guest Count vs Employees",
                xaxis_title="Date",
                yaxis_title="Count",
                legend_title="Legend Title",
                font=dict(
                    family="Courier New, monospace",
                    color="#7f7f7f"
                )
            )

            # ----------------- #
            # CREATE HEATMAP
            # Filter out hours < 9 and > 23
            data2 = data2[(data2.index.hour >= 9) & (data2.index.hour < 23)]
            
            # group by day making average of the guests and employees
            days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            frame = []
            for day in days_of_week:
                # filter by day
                data2_day = data2[data2['Day_of_week'] == day]
                data2_day = data2_day.groupby(data2['Hour']).mean()
                # modify guest count as ratio
                data2_day['Guest_Count'] = data2_day['Guest_Count'] / data2_day['Employees_Count']        
                # drop hour column
                data2_day = data2_day.drop(columns=['Hour'])
                # drop employees count
                data2_day = data2_day.drop(columns=['Employees_Count'])
                # rename guest count
                data2_day = data2_day.rename(columns={'Guest_Count': day})
                transposed_day = data2_day.T
                # add to list
                frame.append(transposed_day)

            data2s_heat = pd.concat(frame)
            #st.write(data1s_heat)
            
            st.plotly_chart(fig_timeries, use_container_width=True)

            # plot heatmap
            import plotly.express as px
            fig = px.imshow(data2s_heat, labels=dict(x="Hour", y="Day of week", color="Guests per employee"))
            # from red to green
            

            fig.update_layout(
                title="Guests per employee",
                xaxis_title="Hour",
                yaxis_title="Day of week",
                legend_title="Legend Title",
                font=dict(
                    family="Courier New, monospace",
                    color="#7f7f7f"
                )
            )
            #st.plotly_chart(fig, use_container_width=True)

            # plot as go
            import plotly.graph_objects as go
            fig = go.Figure(data=go.Heatmap(    
                z=data2s_heat.values,
                x=data2s_heat.columns,
                y=data2s_heat.index[::-1],
                colorscale='Turbo',
                # set as min of the whole dataset
                zmin=data2s_heat.values.min(),
                # set as max of the whole df
                zmax=data2s_heat.values.max(),
                colorbar=dict(
                    title="Guests per employee",
                    titleside="right",
                    tickmode="array",
                    tickvals=[data2s_heat.values.min(), 2.0, data2s_heat.values.max()],
                    ticktext=["Over-Staffed", "Ideal", "Under-Staffed"],
                    ticks="outside"
                )
            ))
            fig.update_layout(
                title="Guests per employee",
                xaxis_title="Hour",
                yaxis_title="Day of week",
                legend_title="Legend Title",
                font=dict(
                    family="Courier New, monospace",
                    color="#7f7f7f"
                )
            )
            st.plotly_chart(fig, use_container_width=True)


    try:
        # plot ratio data1
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data1.index, y=data1['Ratio'], name='Ratio', fill='tozeroy'))
        fig.update_layout(
            title="Ratio",
            xaxis_title="Date",
            yaxis_title="Ratio",
            legend_title="Legend Title",
            font=dict(
                family="Courier New, monospace",
                color="#7f7f7f"
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        # plot ratio
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data2.index, y=data2['Ratio'], name='Ratio', fill='tozeroy'))
        fig.update_layout(
            title="Ratio",
            xaxis_title="Date",
            yaxis_title="Ratio",
            legend_title="Legend Title",
            font=dict(
                family="Courier New, monospace",
                color="#7f7f7f"
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    except:
        pass

two()