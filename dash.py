import streamlit as st
st.set_page_config(layout='wide',initial_sidebar_state='collapsed')

import hydralit_components as hc

def menu():
    # Images
    markd = '''
    <img src="https://www.dishoom.com/assets/img/roundel-seva.png" width = "120" heigth = "120" >
    '''
    st.markdown(markd, unsafe_allow_html=True)

    # Menu
    menu_data = [
        {'id':'heatmap','label':"Heatmap"},
        {'id':'Comparison','label':"Comparison"},
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
choosen = menu()
if choosen == 'heatmap':
    from Dashboard_3 import one
    one()
    
elif choosen == 'Comparison':
    from Dashboard_4 import two
    two()

