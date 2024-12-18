import streamlit as st
import pandas as pd
import openpyxl
import numpy as np
from openpyxl.utils.dataframe import dataframe_to_rows
import matplotlib
import os
import tempfile
import io


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
        try:
            df = pd.read_excel(uploaded_file_simulation_db, sheet_name='Process_CT')
            # st.write("File successfully read. Preview below:")
            # st.dataframe(df.head())
        except Exception as e:
            st.error(f"Error while reading the file: {e}")
            
        # Extract the required values
        shift_hr_day = df.at[0, 'Shift Hr/day']
        days_week = df.at[0, 'Days/Week']
        weeks_year = df.at[0, 'Weeks/Year']
        hr_year_shift = shift_hr_day * days_week * weeks_year
        overall_labor_efficiency = df.at[0, 'Overall Labor Efficiency']
        
        # Hide the dataframe
        st.write("")

        # Create text inputs for each value
        col1, col2, col3, vol_col1, vol_col2, vol_col3 = st.columns(6)

        with col1:
            shift_hr_day_input = st.text_input('Shift Hr/day', value=shift_hr_day, disabled=True)

        with col2:
            days_week_input = st.text_input('Days/Week', value=days_week, disabled=True)

        with col3:
            overall_labor_efficiency_input = st.text_input('Overall Labor Efficiency', value=overall_labor_efficiency, disabled=True)

        # Load the specific sheet from simulation_db.xlsx for 'NRE'
        df2 = pd.read_excel(uploaded_file_simulation_db, sheet_name='NRE')

        st.write("-------------------")

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

        # Define the Product Volume from the 'Process_CT' sheet
        # vol_col1, vol_col2, vol_col3 = st.columns(3)

        # Text inputs for Annual Volume and Product Life
        with vol_col1:
            annual_volume = st.text_input('Annual Volume', value="", disabled=False)

        with vol_col2:
            product_life = st.text_input('Product Life', value="", disabled=False)

        # Safely convert inputs to float, defaulting to 0 if conversion fails
        try:
            annual_volume = float(annual_volume) if annual_volume else 0.0
        except ValueError:
            annual_volume = 0.0
            st.warning("Invalid input for 'Annual Volume'. Please enter a number.")

        try:
            product_life = float(product_life) if product_life else 0.0
        except ValueError:
            product_life = 0.0
            st.warning("Invalid input for 'Product Life'. Please enter a number.")

        # Perform the calculation for Annual Volume
        product_volume = annual_volume * product_life

        # Display results
        with vol_col3:
            st.text_input('Product Volume', value=product_volume, disabled=True)
              
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
            
            # Apply the formula for Qty for LCV
            qty_for_lcv = 1 * (max(product_volume, life_cycle_boards) / life_cycle_boards) if life_cycle_boards else ''
            ext_price = unit_price * qty_for_lcv if unit_price and qty_for_lcv else ''

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

        totalcost_col1, toolmaintenance_col2, totalextendedprice_col3, nreperunit_col4 = st.columns(4)

        with totalcost_col1:
            # Convert the 'Extended Price (₹)' column to numeric
            st.session_state['filtered_data']['Extended Price (₹)'] = pd.to_numeric(st.session_state['filtered_data']['Extended Price (₹)'], errors='coerce')            
            # Calculate the total cost
            total_cost = st.session_state['filtered_data']['Extended Price (₹)'].sum()
            total_cost_value = float(total_cost)
            st.text_input('Total Cost (₹)', value=total_cost, disabled=True)

        with toolmaintenance_col2:
            tool_maintenance_rate = st.text_input('Tool Maintenance Rate (%)', value="", disabled=False)
            tool_maintenance_rate_value = float(tool_maintenance_rate) / 100 if tool_maintenance_rate else 0.0

        with totalextendedprice_col3:
            tool_maintenance_cost = total_cost_value * tool_maintenance_rate_value
            total_extended_price = total_cost_value + tool_maintenance_cost
            st.text_input('Total Extended Price (₹)', value=total_extended_price, disabled=True)

        with nreperunit_col4:
            nre_per_unit = total_extended_price / product_volume if product_volume else 0
            st.text_input('NRE per Unit (₹)', value=nre_per_unit, disabled=True)

        # Provide inputs for file name, sheet name, and path
        st.markdown("### Save Data to Excel")

        # Provide inputs for file name and sheet name only (without path)
        file_name = st.text_input("Enter the Excel file name (with .xlsx extension):")
        sheet_name = st.text_input("Enter the sheet name:")

        # Add a button to save the entire DataFrame
        if st.button("Save DataFrame to Excel"):
            with tempfile.TemporaryDirectory() as tmpdirname:
                full_path = os.path.join(tmpdirname, file_name)

                # Write data to Excel file
                with pd.ExcelWriter(full_path, engine='openpyxl') as writer:
                    # Prepare the DataFrame for saving
                    final_df = st.session_state['filtered_data'].copy()
                    
                    # Add the additional fields in the first row
                    for col, value in zip(
                        ['Annual Volume', 'Product Life', 'Product Volume', 'Total Cost (₹)', 'Tool Maintenance Rate (%)', 
                        'Extended Price (₹)', 'NRE Per Unit ($)'],
                        [annual_volume, product_life, product_volume, total_cost, tool_maintenance_rate_value, 
                        total_extended_price, nre_per_unit]):
                        final_df.at[0, col] = value
                    final_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Load the saved file and create a download link
                with open(full_path, "rb") as f:
                    st.download_button(
                        label="Download Excel file",
                        data=f,
                        file_name=file_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        st.write("-------------------")

        # Load the specific sheet from simulation_db.xlsx for 'MMR-EMS'
        df3 = pd.read_excel(uploaded_file_simulation_db, sheet_name='MMR-EMS')

        # File uploader for Excel/CSV/XLSM files
        uploaded_file = st.file_uploader("Choose an Excel/CSV/XLSM file", type=["xlsx", "csv", "xlsm"])

        if uploaded_file:
            # Load data from the uploaded file
            @st.cache_data
            def load_data(file):
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file, sheet_name=None)
                return df

            df4 = load_data(uploaded_file)

            # Initialize session state to store edited data for each sheet
            if 'edited_sheets' not in st.session_state:
                st.session_state.edited_sheets = {}

            processmapping_col1, processmapping_col2 = st.columns(2)
            if isinstance(df4, dict):
                with processmapping_col1:
                    sheet_name = st.selectbox("Select the sheet", df4.keys())

                # Check if the sheet has been edited before; if so, load the edited version
                if sheet_name in st.session_state.edited_sheets:
                    st.session_state.df = st.session_state.edited_sheets[sheet_name]
                else:
                    selected_data = df4[sheet_name]
                    st.session_state.df = pd.DataFrame(selected_data)  # Load original data from file

                # 1. Provide an option to select the product development stage
                with processmapping_col2:            
                    stages = ['MK0', 'MK1', 'MK2', 'MK3', 'X1', 'X1.1', 'X1.2']  # Add more stages if needed
                    selected_stage = st.selectbox("Select the product development stage", stages)

                # Display data in a table
                st.subheader("Data Table")
                edited_data = st.data_editor(st.session_state.df4)



# Example to show how the existing_analysis would be implemented
if existing_analysis:
    st.subheader("Existing Analysis")
    # Implement logic for existing analysis here
    st.write("Feature under development.")


