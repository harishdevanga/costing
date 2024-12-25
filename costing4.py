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
        df5 = pd.read_excel(uploaded_file_simulation_db, sheet_name='Assumptions')

        # File uploader for Excel/CSV/XLSM files
        uploaded_file = st.file_uploader("Choose Process Maping Excel/CSV/XLSM file", type=["xlsx", "csv", "xlsm"])

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
            else:
                # Initialize df4 with loaded data
                st.session_state['df4'] = df4
            processmapping_col1, processmapping_col2 = st.columns(2)
            if isinstance(df4, dict):
                with processmapping_col1:
                    sheet_name = st.selectbox("Select the sheet", df4.keys())

                if sheet_name in st.session_state.edited_sheets:
                    st.session_state.df = st.session_state.edited_sheets[sheet_name]
                else:
                    selected_data = df4[sheet_name]
                    st.session_state.df = pd.DataFrame(selected_data)  # Load original data from file

                with processmapping_col2:
                    stages = ['MK0', 'MK1', 'MK2', 'MK3', 'X1', 'X1.1', 'X1.2']  # Add more stages if needed
                    selected_stage = st.selectbox("Select the product development stage", stages)

                    # Display data in a table (unique key based on sheet name)
                    st.subheader("Data Table")
                edited_data = st.data_editor(st.session_state.df, key=f"data_editor_{sheet_name}")
                
                # Compute VA MC Cost based on EMS MMR (using edited data)
                @st.cache_data
                def merge_data(df, df3):
                    return df.merge(df3, left_on='Stage', right_on='Process Name', how='left')

                # Ensure 'MMR' exists in df3
                if 'MMR' not in df3.columns:
                    st.error("'MMR' column not found in 'MMR-EMS' sheet. Please check the input file.")
                else:
                    # Perform merge only if 'MMR' is present
                    edited_data = df.merge(df3, left_on='Stage', right_on='Process Name', how='left')

                    # Fill NaN values in 'MMR' with 0
                    edited_data['MMR'] = edited_data['MMR'].fillna(0)

                    # Add necessary columns with default values
                    edited_data['VA MC Cost'] = np.nan
                    edited_data['Batch Set up Cost'] = np.nan
                    edited_data['Labour cost/Hr'] = np.nan

                    # Calculate VA MC Cost
                    edited_data['VA MC Cost'] = edited_data['Process Cycle Time'] * edited_data['MMR']
                    edited_data['VA MC Cost'] = edited_data['VA MC Cost'].fillna(0)

                    try:
                        labour_cost_hr = df5.loc[0, 'Labour cost/Hr']
                        idl_cost_hr = df5.loc[0, 'Idl Cost/Hr']
                        months_per_year = 12
                        batch_qty = annual_volume / months_per_year if annual_volume > 0 else 1  # Avoid division by zero

                        # Calculate Batch Set up Cost
                        edited_data['Batch Set up Cost'] = (
                            (((edited_data['Batch Set up Time'] * labour_cost_hr) / 3600) * 1.15) / batch_qty
                        ) * edited_data['FTE for Batch Set up']
                        
                        # Calculate Labour Cost
                        edited_data['Labor Cost'] = (
                            ((((edited_data['Process Cycle Time'] * labour_cost_hr) / 3600) * 1.15) * edited_data['DL FTE']) + 
                            ((((edited_data['Process Cycle Time'] * idl_cost_hr) / 3600) * 1.15) * edited_data['IDL FTE'])
                        )

                        # Fill NaN values with 0
                        edited_data['Batch Set up Cost'] = edited_data['Batch Set up Cost'].fillna(0)
                        edited_data['Labour cost/Hr'] = edited_data['Labor Cost'].fillna(0)

                        # Update session state
                        st.session_state.edited_sheets[sheet_name] = edited_data

                    except KeyError as e:
                        st.error(f"Error in calculation: Missing column {e}. Please check the input data.")
                # Display the updated DataFrame
                st.data_editor(edited_data, key=f"data_editor_{sheet_name}_updated")

                st.header("Consumable Costing")
                
                st.subheader("RTV Glue")
                rtv_col1, rtv_col2, rtv_col3, rtv_col4, rtv_col5, rtv_col6 = st.columns(6)

                # Glue Wt/Board input
                with rtv_col1:
                    glue_wt_per_board = st.text_input('Glue Wt/Board', value="", disabled=False)

                # Wastage % input
                with rtv_col2:
                    wastage_percentage_per_board = st.text_input('RTV Wastage %', value="", disabled=False)

                # RTV Glue Cost input
                with rtv_col3:
                    rtv_glue_cost = st.text_input('RTV Glue Cost', value="", disabled=False)

                with rtv_col4:
                    specific_gravity_of_solder = st.text_input('Specific Gravity Of Solder', value="", disabled=False)

                # Convert inputs to float safely
                try:
                    glue_wt_per_board = float(glue_wt_per_board) if glue_wt_per_board else 0.0
                    wastage_percentage_per_board = float(wastage_percentage_per_board) if wastage_percentage_per_board else 0.0
                    rtv_glue_cost = float(rtv_glue_cost) if rtv_glue_cost else 0.0
                    specific_gravity_of_solder = float(specific_gravity_of_solder) if specific_gravity_of_solder else 0.0
                except ValueError:
                    st.error("Please enter valid numbers for Glue Wt/Board, Wastage %, and RTV Glue Cost.")
                    glue_wt_per_board = 0.0
                    wastage_percentage_per_board = 0.0
                    rtv_glue_cost = 0.0
                    specific_gravity_of_solder = 0.0

                # Calculate Wt per board including wastage
                with rtv_col5:
                    wt_per_board_inlcuding_wastage_percentage_value = (
                        (glue_wt_per_board * specific_gravity_of_solder ) * (1 + (wastage_percentage_per_board / 100))
                    )
                    wt_per_board_inlcuding_wastage_percentage = st.text_input(
                        'Wt per board (including wastage %)', 
                        value=f"{wt_per_board_inlcuding_wastage_percentage_value:.4f}", 
                        disabled=True
                    )

                # Calculate Cost Per Board
                with rtv_col6:
                    cost_per_board_value = (
                        wt_per_board_inlcuding_wastage_percentage_value * rtv_glue_cost
                    )
                    cost_per_board = st.text_input(
                        'RTV Cost Per Board', 
                        value=f"{cost_per_board_value:.4f}", 
                        disabled=True
                    )
                
                st.subheader("Solder Paste - Top")
                sp_col1, sp_col2, sp_col3 = st.columns(3)
                sp_col4, sp_col5, sp_col6 = st.columns(3)
                sp_col7, sp_col8, sp_col9 = st.columns(3)
                sp_col10, sp_col11 = st.columns(2)
                with sp_col1:
                    board_length = st.text_input('Board Length(mm)', value="", disabled=False)
                with sp_col2:
                    board_width = st.text_input('Board Width(mm)', value="", disabled=False)
                with sp_col3:
                    solder_paste_thickness = st.text_input('Solder paste Thickness(mm)', value="", disabled=False)
                with sp_col7:
                    top_weight_estimate_percentage = st.text_input('Top Weight Estimate %', value="", disabled=False)
                with sp_col8:
                    top_sp_wastage_percentage = st.text_input('Top Solder Paste Wastage %', value="", disabled=False)
                with sp_col4:
                    paste_specific_gravity_value = 7.31
                    paste_specific_gravity = st.text_input('Paste Specific Gravity(g/cc)', value= paste_specific_gravity_value, disabled=True)
                with sp_col6:
                    cost_of_solder_bar_value = 0.065
                    cost_of_solder_bar = st.text_input('Cost of Solder Bar($/g)', value= cost_of_solder_bar_value, disabled=True)

                # Safe conversion
                try:
                    board_length = float(board_length) if board_length else 0.0
                    board_width = float(board_width) if board_width else 0.0
                    top_weight_estimate_percentage = float(top_weight_estimate_percentage) if top_weight_estimate_percentage else 0.0
                    top_sp_wastage_percentage = float(top_sp_wastage_percentage) if top_sp_wastage_percentage else 0.0
                    solder_paste_thickness = float(solder_paste_thickness) if solder_paste_thickness else 0.0
                    paste_specific_gravity = float(paste_specific_gravity) if paste_specific_gravity else 0.0
                    cost_of_solder_bar = float(cost_of_solder_bar) if cost_of_solder_bar else 0.0
                except ValueError:
                    st.error("Please enter valid numbers for the fields.")
                    board_length = 0.0
                    board_width = 0.0
                    weight_estimate_percentage = 0.0
                    sp_wastage_percentage = 0.0
                    solder_paste_thickness = 0.0
                    paste_specific_gravity = 0.0
                    cost_of_solder_bar = 0.0

                with sp_col5:
                    weight_of_solder_paste_for_100percentage_wt_value = (
                        (board_length * board_width * solder_paste_thickness * paste_specific_gravity)/1000
                    )
                    weight_of_solder_paste_for_100percentage_wt = st.text_input('Weight of solder paste for 100%(g)', value=weight_of_solder_paste_for_100percentage_wt_value, disabled=True)

                with sp_col9:
                    # Ensure weight_estimate_percentage and sp_wastage_percentage are scaled correctly
                    top_weight_estimate_percentage = top_weight_estimate_percentage / 100  # Convert from percentage to fraction
                    top_sp_wastage_percentage = top_sp_wastage_percentage / 100           # Convert from percentage to fraction
                    top_weight_of_solder_paste_for_wt_estimate_value = (
                        weight_of_solder_paste_for_100percentage_wt_value * top_weight_estimate_percentage * (1+(top_sp_wastage_percentage))
                    )
                    top_weight_of_solder_paste_for_wt_estimate = st.text_input('Weight of solder paste for Weight Estimate(g) - Top Side', value=top_weight_of_solder_paste_for_wt_estimate_value, disabled=True)

                with sp_col10:
                    top_side_cost_per_board_value = top_weight_of_solder_paste_for_wt_estimate_value * cost_of_solder_bar
                    top_side_cost_per_board = st.text_input('Top Side Cost Per Board($)', value= top_side_cost_per_board_value, disabled=True)

                st.subheader("Solder Paste - Bottom")                
                sp_col12, sp_col13, sp_col14  = st.columns(3)
                sp_col15, sp_col16  = st.columns(2)

                with sp_col12:
                    bot_weight_estimate_percentage = st.text_input('Bottom Weight Estimate %', value="", disabled=False)
                with sp_col13:
                    bot_sp_wastage_percentage = st.text_input('Bottom Solder Paste Wastage %', value="", disabled=False)
                bot_weight_estimate_percentage = float(bot_weight_estimate_percentage) if bot_weight_estimate_percentage else 0.0
                bot_sp_wastage_percentage = float(bot_sp_wastage_percentage) if bot_sp_wastage_percentage else 0.0                

                with sp_col14:
                    # Ensure weight_estimate_percentage and sp_wastage_percentage are scaled correctly
                    bot_weight_estimate_percentage = bot_weight_estimate_percentage / 100  # Convert from percentage to fraction
                    bot_sp_wastage_percentage = bot_sp_wastage_percentage / 100           # Convert from percentage to fraction
                    bot_weight_of_solder_paste_for_wt_estimate_value = (
                        weight_of_solder_paste_for_100percentage_wt_value * bot_weight_estimate_percentage * (1+(bot_sp_wastage_percentage))
                    )
                    bot_weight_of_solder_paste_for_wt_estimate = st.text_input('Weight of solder paste for Weight Estimate(g) - Bottom Side', value=bot_weight_of_solder_paste_for_wt_estimate_value, disabled=True)

                with sp_col15:
                    bot_side_cost_per_board_value = bot_weight_of_solder_paste_for_wt_estimate_value * cost_of_solder_bar                    
                    bot_side_cost_per_board = st.text_input('Bottom Side Cost Per Board($)', value=bot_side_cost_per_board_value, disabled=True)
                

                st.subheader("Flux Wave Soldering")
                flux_col1, flux_col2, flux_col3, flux_col4, flux_col5 = st.columns(5)

                with flux_col1:
                    flux_wastage_percentage = st.text_input('Flux Wastage %', value="", disabled=False)
                with flux_col2:
                    flux_cost_value = 0.0055
                    flux_cost = st.text_input('Flux cost($/ml)', value=flux_cost_value, disabled=True)
                with flux_col3:
                    flux_board_area_value = board_length * board_width
                    flux_board_area = st.text_input('Board Area(mm^2)', value=flux_board_area_value, disabled=True)

                # Convert inputs to float safely
                try:
                    flux_wastage_percentage = float(flux_wastage_percentage) if flux_wastage_percentage else 0.0
                    flux_cost = float(flux_cost) if flux_cost else 0.0
                    flux_board_area = float(flux_board_area) if flux_board_area else 0.0
                except ValueError:
                    st.error("Please enter valid numeric values for Flux inputs.")
                    flux_wastage_percentage = 0.0
                    flux_cost = 0.0
                    flux_board_area = 0.0
                
                with flux_col4:
                    flux_wastage_percentage = flux_wastage_percentage / 100           # Convert from percentage to fraction
                    flux_spread_area_value = ((flux_board_area_value/100)*0.1)*(1+flux_wastage_percentage)
                    flux_spread_area = st.text_input('Flux Spread Area(mm^2)', value=flux_spread_area_value, disabled=True)
                with flux_col5:
                    flux_cost_per_board_value = flux_spread_area_value * flux_cost_value
                    flux_cost_per_board = st.text_input('Flux Cost Per Board($)', value=flux_cost_per_board_value, disabled=True)

                st.subheader("Cost Summary")
                st.write("Material Cost Input")
                cost_col1, cost_col2, cost_col3, cost_col4, cost_col5 = st.columns(5)

                with cost_col1:
                    cost_pcb = st.text_input('PCB ($)', value="", disabled=False)
                with cost_col2:
                    cost_electronics_components = st.text_input('Electronics Component ($)', value="", disabled=False)
                with cost_col3:
                    cost_mech_components = st.text_input('Mechanical Component ($)', value="", disabled=False)
                with cost_col4:
                    cost_nre = st.text_input('NRE ($)', value="", disabled=False)
                with cost_col5:
                    cost_consumables = st.text_input('Consumables ($)', value="", disabled=False)

                # Convert inputs to float safely
                try:
                    cost_pcb = float(cost_pcb) if cost_pcb else 0.0
                    cost_electronics_components = float(cost_electronics_components) if cost_electronics_components else 0.0
                    cost_mech_components = float(cost_mech_components) if cost_mech_components else 0.0
                    cost_nre = float(cost_nre) if cost_nre else 0.0
                    cost_consumables = float(cost_consumables) if cost_consumables else 0.0
                except ValueError:
                    st.error("Please enter valid numeric values for PCB, Electronics Comp, Mech Comp, NRE & Consumable.")
                    cost_pcb = 0.0
                    cost_electronics_components = 0.0
                    cost_mech_components = 0.0
                    cost_nre = 0.0
                    cost_consumables = 0.0

                st.write("OHP % Input & Cost Output")
                ohp_col1, ohp_col2, ohp_col3, ohp_col4, ohp_col5, ohp_col6, ohp_col7 = st.columns(7)
                ohp_col8, ohp_col9, ohp_col10, ohp_col11  = st.columns(4)
                ohp_col12, ohp_col13, ohp_col14, ohp_col15, ohp_col16, ohp_col17 = st.columns(6)
                ohp_col18, ohp_col19, ohp_col20 = st.columns(3)

                with ohp_col1:
                    moh_percentage = st.text_input('MOH %', value="", disabled=False)
                with ohp_col2:
                    foh_percentage = st.text_input('FOH %', value="", disabled=False)
                with ohp_col3:
                    profit_on_rm_percentage = st.text_input('Profit on RM %', value="", disabled=False)
                with ohp_col4:
                    profit_on_va_percentage = st.text_input('Profit on VA %', value="", disabled=False)
                with ohp_col5:
                    r_n_d_percentage = st.text_input('R&D %', value="", disabled=False)
                with ohp_col6:
                    warranty_percentage = st.text_input('Warranty %', value="", disabled=False)
                with ohp_col7:
                    sg_and_a_percentage = st.text_input('SG&A %', value="", disabled=False)


                # Convert inputs to float safely
                try:
                    moh_percentage = float(moh_percentage) if moh_percentage else 0.0
                    foh_percentage = float(foh_percentage) if foh_percentage else 0.0
                    profit_on_rm_percentage = float(profit_on_rm_percentage) if profit_on_rm_percentage else 0.0
                    profit_on_va_percentage = float(profit_on_va_percentage) if profit_on_va_percentage else 0.0
                    r_n_d_percentage = float(r_n_d_percentage) if r_n_d_percentage else 0.0
                    warranty_percentage = float(warranty_percentage) if warranty_percentage else 0.0
                    sg_and_a_percentage = float(sg_and_a_percentage) if sg_and_a_percentage else 0.0

                except ValueError:
                    st.error("Please enter valid numeric values for .")
                    moh_percentage = 0.0
                    foh_percentage = 0.0
                    profit_on_rm_percentage = 0.0
                    profit_on_va_percentage = 0.0
                    r_n_d_percentage = 0.0
                    warranty_percentage = 0.0
                    sg_and_a_percentage = 0.0

                with ohp_col8:
                    moh_percentage = moh_percentage / 100           # Convert from percentage to fraction
                    pcb_comp_mech_cost = cost_pcb + cost_electronics_components + cost_mech_components
                    moh_cost_value = pcb_comp_mech_cost * moh_percentage
                    moh_cost = st.text_input('MOH ($)', value=moh_cost_value, disabled=True)
                with ohp_col9:
                    foh_percentage = foh_percentage / 100           # Convert from percentage to fraction
                    total_factory_overheads_batchsetup = edited_data['Batch Set up Cost'].sum()
                    total_factory_overheads_vamachine = edited_data['VA MC Cost'].sum()
                    total_factory_overheads_labour = edited_data['Labour cost/Hr'].sum()
                    foh_cost_value = (total_factory_overheads_batchsetup + total_factory_overheads_vamachine + total_factory_overheads_labour) * foh_percentage
                    foh_cost = st.text_input('FOH ($)', value=foh_cost_value, disabled=True)
                with ohp_col10:
                    profit_on_rm_percentage = profit_on_rm_percentage / 100
                    profit_on_rm_cost_value = pcb_comp_mech_cost * profit_on_rm_percentage
                    profit_on_rm_cost = st.text_input('Profit on RM ($)', value=profit_on_rm_cost_value, disabled=True)
                with ohp_col11:
                    profit_on_va_percentage = profit_on_va_percentage / 100
                    profit_on_va_cost_value = (total_factory_overheads_batchsetup + total_factory_overheads_vamachine + total_factory_overheads_labour) * profit_on_va_percentage
                    profit_on_va_cost = st.text_input('Profit on VA ($)', value=profit_on_va_cost_value, disabled=True)

                with ohp_col12:
                    total_material_cost_value = pcb_comp_mech_cost + nre_per_unit + cost_per_board_value
                    total_material_cost = st.text_input('Material Cost ($)', value=total_material_cost_value, disabled=True)
                with ohp_col13:
                    total_manufacturing_cost_value = (total_factory_overheads_batchsetup + total_factory_overheads_vamachine + total_factory_overheads_labour)
                    total_manufacturing_cost = st.text_input('Manufacturing Cost ($)', value=total_manufacturing_cost_value, disabled=True)
                with ohp_col14:
                    total_ohp_cost_value = moh_cost_value + foh_cost_value + profit_on_rm_cost_value + profit_on_va_cost_value
                    total_ohp_cost = st.text_input('OH&P ($)', value=total_ohp_cost_value, disabled=True)


                with ohp_col15:
                    r_n_d_percentage = r_n_d_percentage / 100
                    r_n_d_cost_value = (total_material_cost_value + total_manufacturing_cost_value) * r_n_d_percentage
                    r_n_d_cost = st.text_input('R&D ($)', value=r_n_d_cost_value, disabled=True)
                with ohp_col16:
                    warranty_percentage = warranty_percentage / 100
                    warranty_cost_value = (total_material_cost_value + total_manufacturing_cost_value) * warranty_percentage
                    warranty_cost = st.text_input('Warranty ($)', value=warranty_cost_value, disabled=True)
                with ohp_col17:
                    sg_and_a_percentage = sg_and_a_percentage / 100
                    sg_and_a_cost_value = (total_material_cost_value + total_manufacturing_cost_value) * sg_and_a_percentage
                    sg_and_a_cost = st.text_input('SG&A ($)', value=sg_and_a_cost_value, disabled=True)

                with ohp_col18:
                    grand_total_cost_value = ((total_material_cost_value + total_manufacturing_cost_value) + moh_cost_value + 
                                                foh_cost_value + profit_on_rm_cost_value + profit_on_va_cost_value +
                                                r_n_d_cost_value + warranty_cost_value + sg_and_a_cost_value )
                    grand_total_cost = st.text_input('Total Cost ($)', value=grand_total_cost_value, disabled=True)
                with ohp_col19:
                    rm_cost_value = total_material_cost_value
                    rm_cost = st.text_input('RM Cost ($)', value=rm_cost_value, disabled=True)
                with ohp_col20:
                    conversion_cost_value = grand_total_cost_value - total_material_cost_value
                    conversion_cost = st.text_input('Conversion Cost ($)', value=conversion_cost_value, disabled=True)


# Example to show how the existing_analysis would be implemented
if existing_analysis:
    st.subheader("Existing Analysis")
    # Implement logic for existing analysis here
    st.write("Feature under development.")
