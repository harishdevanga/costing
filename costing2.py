import streamlit as st
import pandas as pd
import openpyxl
import numpy as np
from openpyxl.utils.dataframe import dataframe_to_rows

# Set the page layout to wide
st.set_page_config(layout="wide")

# Title of the app
st.title(":bar_chart: Process Mapping & :hourglass: Cycle Time Simulation")

# Sidebar configuration
st.sidebar.header("Category")

# Create an expander for "Offers"
with st.sidebar.expander("Analysis"):
    # Create checkboxes for each offer
    new_analysis = st.checkbox("New")
    existing_analysis = st.checkbox("Existing")

# Display selected analysis
if new_analysis:
    st.subheader("New Analysis")

    # File uploader for the first Excel file (simulation_db.xlsx, sheet 'Process_CT')
    uploaded_file_simulation_db = st.file_uploader("Upload the simulation_db.xlsx file", type=["xlsx"])
    
    # Load data if the file is uploaded
    if uploaded_file_simulation_db:
        # Load the specific sheet from simulation_db.xlsx for 'Process_CT'
        df = pd.read_excel(uploaded_file_simulation_db, sheet_name='Process_CT')

        # Extract the required values
        shift_hr_day = df.at[0, 'Shift Hr/day']
        days_week = df.at[0, 'Days/Week']
        weeks_year = df.at[0, 'Weeks/Year']
        hr_year_shift = shift_hr_day * days_week * weeks_year
        overall_labor_efficiency = df.at[0, 'Overall Labor Efficiency']
        
        # Hide the dataframe
        st.write("")

        # Create text inputs for each value
        col1, col2, col3 = st.columns(3)

        with col1:
            shift_hr_day_input = st.text_input('Shift Hr/day', value=shift_hr_day, disabled=True)

        with col2:
            days_week_input = st.text_input('Days/Week', value=days_week, disabled=True)

        with col3:
            overall_labor_efficiency_input = st.text_input('Overall Labor Efficiency', value=overall_labor_efficiency, disabled=True)

        # Load the specific sheet from simulation_db.xlsx for 'NRE'
        df2 = pd.read_excel(uploaded_file_simulation_db, sheet_name='NRE')

        st.write("-------------------")

        # # Print column names to verify
        # st.write("Columns in 'NRE' sheet:", df2.columns.tolist())
        # st.write("First few rows of 'NRE' sheet:")
        # st.dataframe(df2.head())

        # Create an empty DataFrame with the defined columns
        initial_df = pd.DataFrame(columns=['Item', 'Unit Price (₹)', 'Life Cycle (Boards)', 'Qty for LCV', "Extended Price (₹)"])

        # Initialize session state variables
        if 'data' not in st.session_state:
            st.session_state['data'] = initial_df

        if 'filtered_data' not in st.session_state:
            st.session_state['filtered_data'] = initial_df

        # Initialize dropdown values if not set
        if 'item' not in st.session_state:
            st.session_state['item'] = ''

        if 'unit_price' not in st.session_state:
            st.session_state['unit_price'] = ''

        if 'life_cycle_boards' not in st.session_state:
            st.session_state['life_cycle_boards'] = ''

        if 'qty_for_lcv' not in st.session_state:
            st.session_state['qty_for_lcv'] = ''

        if 'ext_price' not in st.session_state:
            st.session_state['ext_price'] = ''

        if 'reset_selectbox' not in st.session_state:
            st.session_state['reset_selectbox'] = 0

        # Display the headings
        header_cols = st.columns(5)
        header_cols[0].markdown("<h6 style='text-align: center;'>Item</h6>", unsafe_allow_html=True)
        header_cols[1].markdown("<h6 style='text-align: center;'>Unit Price (₹)</h6>", unsafe_allow_html=True)
        header_cols[2].markdown("<h6 style='text-align: center;'>Life Cycle (Boards)</h6>", unsafe_allow_html=True)
        header_cols[3].markdown("<h6 style='text-align: center;'>Qty for LCV</h6>", unsafe_allow_html=True)
        header_cols[4].markdown("<h6 style='text-align: center;'>Extended Price (₹)</h6>", unsafe_allow_html=True)

        # Function to display a row
        def display_row():
            row_cols = st.columns(5)
            
            # Select boxes to select the “Item”
            item = row_cols[0].selectbox('', [''] + list(df2['Item'].unique()), key=f'item_{st.session_state.reset_selectbox}')
            unit_price = df2[df2['Item'] == item]['Unit Price (₹)'].values[0] if item else ''
            life_cycle_boards = df2[df2['Item'] == item]['Life Cycle (Boards)'].values[0] if item else ''
            qty_for_lcv = df2[df2['Item'] == item]['Qty for LCV'].values[0] if item else ''
            ext_price = df2[df2['Item'] == item]['Extended Price (₹)'].values[0] if item else ''
            
            with row_cols[1]:
                unit_price_input = st.text_input('', value=unit_price, key=f'unit_price_{st.session_state.reset_selectbox}')

            with row_cols[2]:
                life_cycle_boards_input = st.text_input('', value=life_cycle_boards, key=f'life_cycle_boards_{st.session_state.reset_selectbox}')

            with row_cols[3]:
                qty_for_lcv_input = st.text_input('', value=qty_for_lcv, key=f'qty_for_lcv_{st.session_state.reset_selectbox}')

            with row_cols[4]:
                ext_price_input = st.text_input('', value=ext_price, key=f'ext_price_{st.session_state.reset_selectbox}')

        # Display the row
        display_row()


        # Add Save, Clear, and Delete buttons
        save_col, clear_col, delete_col3, delete_col4 = st.columns(4)
        with save_col:
            if st.button('Save'):
                # Save the current selection to session state data
                item = st.session_state[f'item_{st.session_state.reset_selectbox}']
                unit_price = st.session_state[f'unit_price_{st.session_state.reset_selectbox}']
                life_cycle_boards = st.session_state[f'life_cycle_boards_{st.session_state.reset_selectbox}']
                qty_for_lcv = st.session_state[f'qty_for_lcv_{st.session_state.reset_selectbox}']
                ext_price = st.session_state[f'ext_price_{st.session_state.reset_selectbox}']

                if item:
                    new_row = {
                        'Item': item,
                        'Unit Price (₹)': unit_price,                        
                        'Life Cycle (Boards)': life_cycle_boards,
                        'Qty for LCV': qty_for_lcv,
                        'Extended Price (₹)': ext_price
                    }
                    if not st.session_state['filtered_data']['Item'].eq(item).any():
                        st.session_state['filtered_data'] = pd.concat([st.session_state['filtered_data'], pd.DataFrame([new_row])], ignore_index=True)
                        st.success("Record added successfully. Select Your Next Side & Stage")
                    else:
                        st.warning("Record Already Exists in the Table")

        with clear_col:
            if st.button('Clear'):
                # Increment the key to reset the select boxes
                st.session_state['reset_selectbox'] += 1

        # Display the updated dataframe with a header
        st.markdown("## NRE Mapping")
        st.dataframe(st.session_state['filtered_data'], use_container_width=True)
