import streamlit as st
import pandas as pd
import plotly.graph_objects as go
st.set_page_config(layout="wide")

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
    uploaded_file_1 = st.file_uploader("extract")

# open the file
if uploaded_file_1 is not None:
    # read
    df = pd.read_excel(uploaded_file_1, engine='openpyxl')
    # transform in csv
    df.to_csv('data.csv', index=False)
    # read csv
    df = pd.read_csv('data.csv')
    # replace NaN with 0
    df = df.fillna(0)
    # replace "HOL" with 0
    df = df.replace('HOL', 0)
    # replace "Absence" with 0
    df = df.replace('Authorised Absence (no SSP or CSP)', 0)
    # replace Unauthorised Absence (no SSP or CSP) with 0
    df = df.replace('Unauthorised Absence (no SSP or CSP)', 0)
    # replace Sickness Self Certified (SSP Only) with 0
    df = df.replace('Sickness Self Certified (SSP Only)', 0)
    st.write('This need to be modified')
    st.write(df)

    # open the file
    correct_format_data = pd.read_excel('August_Actual_Hours.xlsx', engine='openpyxl')
    st.write('Correct format data')
    st.write(correct_format_data)
