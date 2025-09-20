import pandas as pd
import streamlit as st

def concatenate_files(uploaded_files, data_type): #data type could be csv or xml
        """Reads and concatenates a list of uploaded CSV or xmls files."""
        if not uploaded_files:
            return None
        all_dfs = []
        for file in uploaded_files:
            try:
                if data_type == 'csv':
                    df = pd.read_csv(file)
                    all_dfs.append(df)
                elif data_type == 'xml':
                    df = pd.read_xml(file)
                    all_dfs.append(df)
            except Exception as e:
                st.error(f"Error reading {file.name}: {e}")
                return None
        try:
            concatenated_df = pd.concat(all_dfs, ignore_index=True)
            return concatenated_df
        except Exception as e:
            st.error(f"Error concatenating files: {e}")
            return None