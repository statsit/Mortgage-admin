from datetime import date 
import asyncio
import streamlit as st
from PIL import Image
from data_process import (
            read_api_df_filter_year, 
            create_payment, 
            create_payment_async,
            read_api_df_filter_year_async
        )
from ocr import OCR, load_model

# OCR
model = load_model()
ocr = OCR(model)


st.title("Mortgage Repayment Admin")

repayment, download, simulate = st.tabs(
    [
        "Create New Mortgage Repayment", 
        "Mortgage Repayment Data", 
        "Stimulation"
    ]
)

with repayment:
    # with st.expander("Create New Mortgage Repayment using Form"):
    st.subheader("Create New Mortgage Repayment")

    extracted_info = None
    created = date.today()
    amount_sent = 0.0

    uploaded_file = st.file_uploader("**:green[Upload Recept]**")

    with st.spinner("Processing Image..."):
        if uploaded_file is not None:
            bytes_data = uploaded_file.getvalue()
            result = ocr.detect(bytes_data)
            extracted_info = ocr.extract_info()
            st.image(result, caption='Uploaded Image.', use_column_width=True, clamp=True)
            if len(extracted_info) > 0:
                created = extracted_info['created']
                amount_sent = extracted_info['amount_sent']
    
        
    with st.form(key="my_form", clear_on_submit=True):
        

        rate = st.slider("Interest Rate", 0.0, 1.0, 0.15) 
        log_date = st.date_input("Enter date", created)
        exchange = st.number_input("Enter exchange value", min_value=580)
        repayment = st.number_input("Enter repayment value", min_value=0.0, value=amount_sent)


        submit_button = st.form_submit_button(label="Submit")
        if submit_button:
            
            with st.spinner("Writing to database..."):
            
                payload = {
                    'amount': int(repayment),
                    "exchange_rate": exchange,
                    "interest_rate": rate,
                }
                # create_payment(payload)
                asyncio.run(create_payment_async(payload))
            st.success("Successfully created new repayment")
            st.balloons()


with download:
    st.subheader("Download Mortgages Payment Data")
    years = ['All', 2021, 2022, 2023, 2024, 2025]
    selected = st.selectbox("Select What Year", years, index=3)
    df = asyncio.run(read_api_df_filter_year_async(selected))
    
    st.dataframe(df, hide_index=True)
    
    
    st.download_button(
        label="Download Data",
        data=df.to_csv().encode("utf-8"),
        file_name=f"mortages_{selected}.csv",
        mime="text/csv",
    )