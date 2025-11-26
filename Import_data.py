import streamlit as st
import pandas as pd
import re


def RIS_To_DataFrame (ris_data):
    tag_map = {
    'TY': 'Reference_Type',
    'TI': 'Title', 'T1': 'Title',
    'AN': 'Acession_Number',
    'AB': 'Abstract', 'N2': 'Abstract',
    'AU': 'Author', 'A1': 'Author',
    'JA': 'Source', 'SO': 'Source', 'JF':'Source',
    'PY': 'Year', 'Y1': 'Year', 'YR':'Year',
    'DO': 'DOI', 'DI': 'DOI',
    'C3': 'Trial Source',
    'M3': 'Note', 'CY': 'Note',
    'KW':'Keywords',
    'UR': 'URL',
    'DB': 'Database',
    'PT': 'Publication_Type'}
    standard_columns = set(tag_map.values())
    record_splitter = r'ER\s{2}-\s*'
    line_parser = r'^([A-Z0-9]{2})\s{2}-\s+(.*)'
    
    parsed_records = []
    ris_records = re.split(record_splitter, ris_data.strip())
    for record_str in ris_records:
        if not record_str.strip():
            continue
            
        record_dict = {}
        for line in record_str.strip().split('\n'):
            match = re.search(line_parser, line.strip())
            if match:
                ris_tag = match.group(1).strip()
                ris_value = match.group(2).strip()
                
                standard_tag = tag_map.get(ris_tag)
    
                if standard_tag:
                    if standard_tag in record_dict:
                        record_dict[standard_tag] += f"; {ris_value}"
                    else:
                        record_dict[standard_tag] = ris_value
        
        parsed_records.append(record_dict)
    df = pd.DataFrame(parsed_records, columns=sorted(list(standard_columns)))
    object_cols = df.select_dtypes(include=['object']).columns
    df[object_cols] = df[object_cols].where(pd.notna, None)
    df['Author'] = df['Author'].str.rstrip(',')
    return df




def CENTRAL_Parse (data):
    m3_pattern = re.compile(r'M3\s+-\s+Trial registry record', re.MULTILINE)
    a1_pattern = re.compile(r'A1\s+-\s+(.*)', re.MULTILINE)
    try:
        central = data
        central = central.split("ER  -")[:-1]
        st.write(f"🎉 Successfully parsed **{len(central)}** records.")               
        CENTRAL_Dataframe = RIS_To_DataFrame (data)
        central_ids = []
        for i, record in enumerate(central):
            if m3_pattern.search(record):
                a1_authors = a1_pattern.findall(record)
                if a1_authors:
                    for author in a1_authors:
                        if author.strip()[-1] == ',':
                            central_ids.append (author.strip()[:-1])
                        else:
                            central_ids.append (author.strip())
        if central_ids:
            central_ids = list (set(central_ids))
            filtered_CENTRAL_Dataframe = CENTRAL_Dataframe[CENTRAL_Dataframe['Author'].isin(central_ids)]
            st.session_state['Central_IDs'] = central_ids
            st.session_state['Central_df'] =  filtered_CENTRAL_Dataframe
            return filtered_CENTRAL_Dataframe           
            
        else:
            st.warning("No trial records were identified. Please double check the uploaded data.")
            # uploaded_ris_file1.seek(0) 
    except Exception as e:
        st.error(f"Error reading RIS file: {e}. Please check the uploaded data.")


    


def Embase_Parse (data):
    db_pattern = re.compile(r'DB\s+-\s+Embase Clinical Trials',re.MULTILINE)
    an_pattern = re.compile(r'AN\s+-\s+(.*)', re.MULTILINE)
    # create embase ids list
    try:
        embase = data
        embase = embase.split("ER  -")[:-1]
        st.write(f"🎉 Successfully parsed **{len(embase)}** records.")
        EMBASE_Dataframe = RIS_To_DataFrame (data)
        embase_ids = []
        for i, record in enumerate(embase):
            if db_pattern.search(record):
                an_authors = an_pattern.findall(record)
                if an_authors:
                    for author in an_authors:
                        embase_ids.append(author.strip())
    
        if embase_ids:
            embase_ids = list (set(embase_ids))
            filtered_EMBASE_Dataframe = EMBASE_Dataframe[EMBASE_Dataframe['Acession_Number'].isin(embase_ids)]
            embase_urls = []
            year_cleaned = []
            for idx in range(len(filtered_EMBASE_Dataframe)):
                url_splited = filtered_EMBASE_Dataframe['URL'][idx].split("; ")
                if len (url_splited)>1:
                    embase_urls.append (url_splited[0])
                else:
                    embase_urls.append (url_splited)
            filtered_EMBASE_Dataframe['URL'] = embase_urls 
            filtered_EMBASE_Dataframe['Year'] = filtered_EMBASE_Dataframe['Year'].str.rstrip('//')
            st.session_state['Embase_IDs'] = embase_ids
            st.session_state['Embase_df'] =  filtered_EMBASE_Dataframe
            return filtered_EMBASE_Dataframe
        else:
            st.warning("No trial records were identified. Please double check the uploaded data.")
    except Exception as e:
        st.error(f"Error reading RIS file: {e}. Please check the uploaded data.")

    

def ClinicalTrialsGov_Parse (data):
    try:
        df_ct = data
        ct_ids = []
        for i in df_ct['NCT Number']:
            ct_ids.append(str(i).strip())
        ct_ids_final = list(set(ct_ids))
        if ct_ids_final:
            st.session_state['CT_IDs'] = ct_ids_final
            st.session_state['CT_df'] =  df_ct
            return df_ct
            
        else:
            st.warning("No trial records were identified from ClinicalTrials.gov.")
    except Exception as e:
        st.error(f"Error reading CSV file: {e}. Please check the uploaded data.")

def WHO_ICTRP_Parse (data):
    try:
        df_ictrp = data
        df_ictrp['TrialID'] = df_ictrp['TrialID'].str.strip()
        # create ictrp ids list
        ictrp_ids = []
        for i in df_ictrp['TrialID']:
            ictrp_ids.append(str(i).strip())
        ictrp_ids_final = list(set(ictrp_ids))
        if ictrp_ids_final:
            st.session_state['ICTRP_IDs'] = ictrp_ids_final
            st.session_state['ICTRP_df'] =  df_ictrp
            return df_ictrp
        else:
            st.warning("No trial records were identified from WHO ICTRP.")
            
    except Exception as e:
        st.error(f"Error reading XML file: {e}. Please check the uploaded data.")


def ScanMedicine_Parse (data):
    try:
        df_scanmedicine = data
        # create scanmedicine ids list
        scanmedicine_ids = []
        for i in df_scanmedicine['MainID']:
            scanmedicine_ids.append(str(i).strip())
        scanmedicine_ids_final = list(set(scanmedicine_ids))
        if scanmedicine_ids_final:
            st.session_state['SM_IDs'] = scanmedicine_ids_final
            st.session_state['SM_df'] =  df_scanmedicine
            return df_scanmedicine
            
        else:
            st.warning("No trial records were identified from ScanMedicine.")
    except Exception as e:
        st.error(f"Error reading CSV file: {e}. Please check the uploaded data.")  
        
    