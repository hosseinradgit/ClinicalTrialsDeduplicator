import streamlit as st
import pandas as pd
import re
from file_convertor import *
from concatenate_files import *

st.set_page_config(
    page_title="Clinical Trials Deduplicator",
    page_icon="",
    layout="centered"
)
 
st.title("Clinical Trials Deduplicator")


# Tabs for the main content
tab1, tab2, tab3 = st.tabs(["Home", "Data Summary", "Export Data"])
with tab1:
        st.markdown("""
    
    ### Using This Tool
    
    1. **Upload Data**: Navigate to the "Upload Data" section in the sidebar.
    
    2. **Select Your Files**: Upload your RIS, CSV, or XML data files.
    
    3. **View Results**: Review the processed information in the "Data Summary" and "Export Data" tabs.
    
    
    """)
# Data Uploaders in the sidebar
with st.sidebar:
    st.header("Upload Your Data")
    
    # Section 1: Cochrane CENTRAL
    st.subheader("1. Cochrane Central")
    uploaded_ris_file1 = st.file_uploader(
        "Choose your RIS file...",
        type=["ris"],
        key="ris_uploader1" 
    )
    if uploaded_ris_file1 is not None:
        st.success("Cochrane Central data uploaded successfully!")
    
        # create central ids list
        m3_pattern = re.compile(r'M3\s+-\s+Trial registry record', re.MULTILINE)
        a1_pattern = re.compile(r'A1\s+-\s+(.*)', re.MULTILINE)
        central = uploaded_ris_file1.read().decode("utf-8")
        central = central.split("ER  -")[:-1]
        st.write(f"🎉 Successfully parsed **{len(central)}** records from Cochrane Central.")
        central_ids = []
        for i, record in enumerate(central):
            if m3_pattern.search(record):
                a1_authors = a1_pattern.findall(record)
                if a1_authors:
                    for author in a1_authors:
                        if author.strip()[-1] == ',':
                            central_ids.append (author.strip()[:-1])
                        else:
                            pass
                            central_ids.append (author.strip())
        if central_ids:
            # st.write(f"🎉 Successfully detected **{len(central_ids)}** trial records from Cochrane Central.")
            st.session_state['Central_IDs'] = central_ids
            st.session_state['Central_df'] =  central
            
        else:
            st.warning("No trial records were identified from Cochrane CENTRAL.")
    
    
    st.markdown("---") 
    
    # Section 2: Embase data
    st.subheader("2. Embase")
    uploaded_ris_file2 = st.file_uploader(
        "Choose your RIS file...",
        type=["ris"],
        key="ris_uploader2"
    )
    if uploaded_ris_file2 is not None:
        st.success("Embase data uploaded successfully!")
    
        # create embase ids list
        db_pattern = re.compile(r'DB\s+-\s+Embase Clinical Trials',re.MULTILINE)
        an_pattern = re.compile(r'AN\s+-\s+(.*)', re.MULTILINE)
        embase = uploaded_ris_file2.read().decode("utf-8")
        embase = embase.split("ER  -")[:-1]
        st.write(f"🎉 Successfully parsed **{len(embase)}** records from Embase.")
        embase_ids = []
        for i, record in enumerate(embase):
            if db_pattern.search(record):
                an_authors = an_pattern.findall(record)
                if an_authors:
                    for author in an_authors:
                        embase_ids.append(author.strip())
    
        if embase_ids:
            # st.write(f"🎉 Successfully detected **{len(embase_ids)}** trial records from Embase.")
            st.session_state['Embase_IDs'] = embase_ids
            st.session_state['Embase_df'] =  embase
        else:
            st.warning("No trial records were identified from Embase.")
        # st.info(f"File name: {uploaded_ris_file2.name}")
    
    st.markdown("---") 

    
    # ClinicalTrials.gov data
    st.subheader("3. ClinicalTrials.gov")
    uploaded_csv_file = st.file_uploader(
        "Choose your CSV file...",
        type=["csv"],
        key="csv_uploader1",
        accept_multiple_files=True
    )
    # if uploaded_csv_file is not None:
    #     st.success("ClinicalTrials data uploaded successfully!")
    if uploaded_csv_file:
        st.success("ClinicalTrials data uploaded successfully!")
        try: 
            df_ct = concatenate_files (uploaded_csv_file, 'csv')
            st.write(f"🎉 Successfully parsed **{(df_ct.shape[0])}** records from ClinicalTrials.gov.")
            ct_ids = []
            for i in df_ct['NCT Number']:
                ct_ids.append(str(i).strip())
            ct_ids_final = list(set(ct_ids))
            if ct_ids_final:
                # st.write(f"🎉 Successfully detected **{len(ct_ids_final)}** unique trial records from ClinicalTrials.gov.")
                st.session_state['CT_IDs'] = ct_ids_final
                st.session_state['CT_df'] =  df_ct
            else:
                st.warning("No trial records were identified from ClinicalTrials.gov.")
        
        except Exception as e:
            st.error(f"Error during concatenation: {e}")

    st.markdown("---")
       
                

   
    
    # ScanMedicine data
    st.subheader("4. ScanMedicine")
    uploaded_csv_file1 = st.file_uploader(
        "Choose your CSV file...",
        type=["csv"], 
        key="csv_uploader2",
        accept_multiple_files=True
    )
    if uploaded_csv_file1:
        st.success(f"ScanMedicine data uploaded successfully!")
        try:
            df_scanmedicine = concatenate_files (uploaded_csv_file1, 'csv')
            st.write(f"🎉 Successfully parsed **{(df_scanmedicine.shape[0])}** records from ScanMedicine.")
            # create scanmedicine ids list
            scanmedicine_ids = []
            for i in df_scanmedicine['MainID']:
                scanmedicine_ids.append(str(i).strip())
            scanmedicine_ids_final = list(set(scanmedicine_ids))
            if scanmedicine_ids_final:
                # st.write(f"🎉 Successfully detected **{len(scanmedicine_ids_final)}** unique trial records from ScanMedicine")
                st.session_state['SM_IDs'] = scanmedicine_ids_final
                st.session_state['SM_df'] =  df_scanmedicine
                
            else:
                st.warning("No trial records were identified from ScanMedicine.")
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")    
    
    st.markdown("---")
    
    # WHO ICTRP data
    st.subheader("5. WHO ICTRP")
    uploaded_xml_file = st.file_uploader(
        "Choose your XML file...",
        type=["xml"],
        key="xml_uploader",
        accept_multiple_files=True
    )
    if uploaded_xml_file:
        st.success("WHO ICTRP data uploaded successfully!")
    
        try:
            df_ictrp = concatenate_files (uploaded_xml_file, 'xml')
            st.write(f"🎉 Successfully parsed **{(df_ictrp.shape[0])}** records from WHO ICTRP.")
            # create ictrp ids list
            ictrp_ids = []
            for i in df_ictrp['TrialID']:
                ictrp_ids.append(str(i).strip())
            ictrp_ids_final = list(set(ictrp_ids))
            if ictrp_ids_final:
                st.session_state['ICTRP_IDs'] = ictrp_ids_final
                st.session_state['ICTRP_df'] =  df_ictrp
                # st.write(f"🎉 Successfully detected **{len(st.session_state['ICTRP_IDs'])}** unique trial records from WHO ICTRP.")
            else:
                st.warning("No trial records were identified from WHO ICTRP.")
            
        except Exception as e:
            st.error(f"Error reading XML file: {e}")
        
    st.markdown("---") 
    

   
    with tab2:
        
        
        ## Central data and ids
        if 'Central_IDs' in st.session_state:
            central_ids = st.session_state['Central_IDs']
        else: 
            central_ids = []
        if 'Central_df' in st.session_state:
            central = st.session_state['Central_df']
        else: 
            central = None
        
        ## embase data and ids
        if 'Embase_IDs' in st.session_state:
            embase_ids = st.session_state['Embase_IDs']
        else: 
            embase_ids = []
        if 'Embase_df' in st.session_state:
            embase = st.session_state['Embase_df']
        else: 
            embase = None
        
        ## ClinicalTirals.gov data and ids
        if 'CT_IDs' in st.session_state: 
            ct_ids_final = st.session_state['CT_IDs']
        else:
            ct_ids_final = []
        if 'CT_df' in st.session_state:
            ct = st.session_state['CT_df']
        else: 
            ct = None
            
        ## WHO ICTRP data and ids
        if 'ICTRP_IDs' in st.session_state:
            ictrp_ids_final = st.session_state['ICTRP_IDs']
        else: 
            ictrp_ids_final = []
        if 'ICTRP_df' in st.session_state:
            ictrp = st.session_state['ICTRP_df']
        else: 
            ictrp = None
        
        ## ScanMedidince data and ids
        if 'SM_IDs' in st.session_state:
            scanmedicine_ids_final = st.session_state['SM_IDs']
        else: 
            scanmedicine_ids_final = []
        if 'SM_df' in st.session_state:
            scanmedicine = st.session_state['SM_df']
        else: 
            scanmedicine = None
        
        
        def detecting_duplicates():
            # detecting id duplication between clinicaltrials.gov and ICTRP
            ct_ictrp = []
            for i in ictrp_ids_final:
                if i in ct_ids_final:
                    ct_ictrp.append(i)
            
            # detecting id duplication between clinicaltrials.gov and ScanMedicine
            ct_scanmedicine = []
            for i in scanmedicine_ids_final:
                if i in ct_ids_final:
                    ct_scanmedicine.append(i)
            
            # detecting id duplication between ICTRP and ScanMedicine
            ictrp_scanmedicine = []
            for i in scanmedicine_ids_final:
                if i in ictrp_ids_final:
                    ictrp_scanmedicine.append(i)
            
            #Remove duplicates between three registries
            ictrp_ids_final1 = list(set(ictrp_ids_final) - set(ct_ictrp))
            scanmedicine_ids_final1 = list(set(scanmedicine_ids_final) - set(ct_scanmedicine))
            scanmedicine_ids_final2 = list(set(scanmedicine_ids_final1) - set(ictrp_scanmedicine))
            
            # create list of all unique ids with the name of each registry
            combined_ct_ictrp_sm = []
            for i in ct_ids_final:
                combined_ct_ictrp_sm.append(("ct", i))
            for i in ictrp_ids_final1:
                combined_ct_ictrp_sm.append(("ictrp", i))
            for i in  scanmedicine_ids_final2:
                combined_ct_ictrp_sm.append(("sm", i))
            
            # matching three registry records with cochrane central records and embase trials
            combined_central_embase = []
            for (i,j) in combined_ct_ictrp_sm:
                if (j in central_ids) or (j in embase_ids):
                    combined_central_embase.append((i,j))
            # st.write ("Total number of duplicate records between three registries and Cochrane Central/embase trials: ", len(combined_central_embase))
            
            # Determining the number of records of each source (ClinicalTrials.gov)
            ct_filter = []
            for i, j in combined_ct_ictrp_sm:
                if i == "ct":
                    ct_filter.append(j)
            
            # Determining the number of records of each source (ICTRP)
            ictrp_filter = []
            for i, j in combined_ct_ictrp_sm:
                if i == "ictrp":
                    ictrp_filter.append(j)
            
            # Determining the number of records of each source (ScanMedicine)
            scanmedicine_filter = []
            for i, j in combined_ct_ictrp_sm:
                if i == "sm":
                    scanmedicine_filter.append(j)
            
            # create dataframe for each registry after remove duplicates
            if ct is not None:
                ct_df = ct.drop_duplicates(subset=['NCT Number'])
                ct_toexport = ct_df[ct_df['NCT Number'].str.strip().isin(ct_filter)]
            else: 
                ct_toexport = None
            if ictrp is not None: 
                ictrp_df = ictrp.drop_duplicates(subset = ['TrialID'])
                ictrp_toexport = ictrp_df[ictrp_df['TrialID'].str.strip().isin(ictrp_filter)]
            else:
                ictrp_toexport = None
            if scanmedicine is not None:
                scanmedicine_df = scanmedicine.drop_duplicates(subset = ['MainID'])
                scanmedicine_toexport = scanmedicine_df[scanmedicine_df['MainID'].str.strip().isin(scanmedicine_filter)]
                # st.write(scanmedicine_toexport)
            else:
                scanmedicine_toexport = None
            
            # Determining the number of duplicates of each source with central and embase records (ClinicalTrials)
            ct_filter_final = []
            for i, j in combined_central_embase:
                if i == "ct":
                    ct_filter_final.append(j)
            
            # Determining the number of duplicates of each source with central and embase records (ICTRP)
            ictrp_filter_final = []
            for i, j in combined_central_embase:
                if i == "ictrp":
                    ictrp_filter_final.append(j)
            
            # Determining the number of duplicates of each source with central and embase records (ScanMedicine)
            scanmedicine_filter_final = []
            for i, j in combined_central_embase:
                if i == "sm":
                    scanmedicine_filter_final.append(j)
            
            # create dataframe for each registry after remove duplicates with cochrane central
            data_summary = {"Source Name":[], "Total Records":[], "Unique Records (in Source)":[], "Deduplicated Records":[]}
            try:
                ct_toexport_final = ct_toexport[~ct_toexport['NCT Number'].isin(ct_filter_final)]
                data_summary["Total Records"].append(df_ct.shape[0])
                data_summary["Unique Records (in Source)"].append(len(ct_ids_final))
                data_summary["Deduplicated Records"].append(len(ct_toexport_final))
                data_summary["Source Name"].append("ClinicalTrials.gov")
                st.session_state['ct_export'] = ct_toexport_final

                # Tab3 for exporting data
                with tab3: 
                    ct_file = ct_toexport_final.to_csv(index=False)
                    st.subheader("ClinicalTrials.gov")
                    st.markdown(" ")
                    col1, col2 = st.columns(2)
                    with col1:
                        # Download button
                        st.download_button(
                        label="📥 CSV",
                        data=ct_file,
                        file_name='ClinicalTrials.csv',
                        mime='text/csv',
                        )
                    with col2:
                        st.download_button(
                        label="📥 RIS",
                        data=CT_RIS(ct_toexport_final),
                        file_name='ClinicalTrials.gov.ris',
                        mime='text/RIS',
                        )
                    st.markdown("---")
                    
            except:
                pass
                
            try: 
                ictrp_toexport_final = ictrp_toexport[~ictrp_toexport['TrialID'].isin(ictrp_filter_final)]
                data_summary["Total Records"].append(df_ictrp.shape[0])
                data_summary["Unique Records (in Source)"].append(len(ictrp_ids_final))
                data_summary["Deduplicated Records"].append(len(ictrp_toexport_final))
                data_summary["Source Name"].append("WHO ICTRP")
                st.session_state['ictrp_export'] = ictrp_toexport_final
                with tab3: 
                    ## WHO ICTRP to export
                    ictrp_file = ictrp_toexport_final.to_csv(index=False)
                    st.subheader("WHO ICTRP")
                    st.markdown(" ")
                    col1, col2 = st.columns(2)
                    with col1:
                        # Download button
                        st.download_button(
                        label="📥 XML",
                        data=ictrp_file,
                        file_name='ICTRP_WHO.xml',
                        mime='text/xml',
                        )
                    with col2:
                        st.download_button(
                        label="📥 RIS",
                        data=ICTRP_RIS(ictrp_toexport_final),
                        file_name='WHO ICTRP.ris',
                        mime='text/RIS',
                        )
                    st.markdown("---")
            except:
                pass
                
            try:
                scanmedicine_toexport_final = scanmedicine_toexport[~scanmedicine_toexport['MainID'].isin(scanmedicine_filter_final)]
                data_summary["Total Records"].append(df_scanmedicine.shape[0])
                data_summary["Unique Records (in Source)"].append(len(scanmedicine_ids_final))
                data_summary["Deduplicated Records"].append(len(scanmedicine_toexport_final))
                data_summary["Source Name"].append("ScanMedicine")
                st.session_state['sm_export'] = scanmedicine_toexport_final
                with tab3: 
                    scanmedicine_file = scanmedicine_toexport_final.to_csv(index=False)
                    st.subheader("ScanMedicine")
                    st.markdown(" ")
                    col1, col2 = st.columns(2)
                    with col1:
                        # Download button
                        st.download_button(
                        label="📥 CSV",
                        data=scanmedicine_file,
                        file_name='ScanMedicine.csv',
                        mime='text/csv',
                        )
                    with col2:
                        st.download_button(
                        label="📥 RIS",
                        data=SM_RIS(scanmedicine_toexport_final),
                        file_name='ScanMedicine.ris',
                        mime='text/RIS',
                        )
                    st.markdown("---")
            except:
                pass
            
            return st.dataframe(data_summary)

        detecting_duplicates()
