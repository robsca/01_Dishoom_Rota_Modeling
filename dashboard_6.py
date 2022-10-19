import streamlit as st
import pandas as pd
st.set_page_config(layout='wide')
from helper_functions import *

#
path = 'data_download/Aug - 2019 FOH Hours.xlsx'
# open the file
df = pd.read_excel(path)
st.write(df)

