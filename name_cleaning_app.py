import streamlit as st
import pandas as pd
from nameparser import HumanName
import io

# 1. Page Configuration
st.set_page_config(page_title="Name Parser Pro", layout="wide")
st.title("🏷️ Professional Name Splitter")
st.markdown("""
Upload an Excel or CSV file to automatically split full names into 
**First, Middle, Last, Suffix, and Nicknames**.
""")

# 2. File Uploader
uploaded_file = st.file_uploader("Upload your file", type=['csv', 'xlsx'])

if uploaded_file:
    # Load the data based on file extension
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
    
    st.write("### Data Preview")
    st.dataframe(df.head(10))

    # 3. User selects the column to parse
    # Using 'name_column' consistently as the variable name
    name_column = st.selectbox("Which column contains the Full Names?", df.columns)

    if st.button("🚀 Process Names"):
        # The internal function to handle name parsing logic
        def parse_names_logic(val):
            # Convert to string and handle potential nulls
            name_str = str(val) if pd.notnull(val) else ""
            name_obj = HumanName(name_str)
            
            # Return list of components in a specific order
            return [
                name_obj.first, 
                name_obj.middle, 
                name_obj.last, 
                name_obj.suffix, 
                name_obj.nickname
            ]

        with st.spinner('Parsing names...'):
            # Define new column names
            new_cols = ['First Name', 'Middle Name', 'Last Name', 'Suffix', 'Nickname']
            
            # Apply the logic: use 'name_column' to find the data
            # and expand the returned list into the 'new_cols'
            df[new_cols] = df[name_column].apply(lambda x: pd.Series(parse_names_logic(x)))
            
        st.success("Success! Names have been split into new columns.")
        st.dataframe(df.head())

        # 4. Excel Export Logic
        # This creates the file in memory so it can be downloaded via browser
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Cleaned Names')
        
        st.download_button(
            label="📥 Download Cleaned Excel File",
            data=output.getvalue(),
            file_name=f"parsed_{uploaded_file.name.split('.')[0]}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )