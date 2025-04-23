import streamlit as st
import pytesseract
from PIL import Image
import re
import csv


# Path to Tesseract executable
path = r"C:\Program Files\Tesseract-OCR\tesseract"
pytesseract.pytesseract.tesseract_cmd = path

# Define regex patterns for extraction (you can adjust as per your needs)
patterns = {
    'pan_no': r"[A-Z]{5}\d{4}[A-Z]",
    'mail_id': r"[\w]{1,36}[@][a-z.]{8,14}",
    'phone_no': r"[9][1][-]\d{10}",
    'GSTIN_no': r"[A-Z]{1}\d{1}[A-Z]{5}\d{4}[A-Z]{1}\d{2}[A-Z]",
    'customer_Account_no': r"[0]\d{11}",
    'IFSC_Code': r"\d{1}[A-Z]{1}\d{1}[A-Z]{1}[0-9]{7}" 
}

# Function to extract patterns from text using regex
def extract_patterns(text):
    results = {}
    for pattern_name, pattern in patterns.items():
        results[pattern_name] = re.findall(pattern, text)
    return results

# Function to save data to CSV file
def save_to_csv(extracted_info, submitted_info):
    csv_filename = 'invoice_information.csv'
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write headers for extracted information
        writer.writerow(['Category', 'Information', 'Source'])
        
        # Write extracted information
        for category, info_list in extracted_info.items():
            for info in info_list:
                writer.writerow([category, info, 'Extracted'])
        
        # Write submitted information
        for info in submitted_info:
            category, data = info.split(': ', 1)
            writer.writerow([category, data, 'Manual'])
    
    return csv_filename

# Main function to run the Streamlit app
def main():
    st.title('Invoice Information Extraction from Images')
    
    # Sidebar for invoice details
    st.sidebar.title("Invoice Details")
    invoice_number = st.sidebar.text_input("Invoice Number")
    invoice_date = st.sidebar.date_input("Invoice Date")
    send_amount=st.sidebar.number_input("Send Amount",min_value=0.0)
    total_amount=st.sidebar.number_input("Total Ammount",min_value=0.0)
    payment_terms = st.sidebar.selectbox("Payment Terms", ("Net 30 Days", "Net 60 Days", "Other"))
    
    # Upload image file
    uploaded_file = st.file_uploader("Upload an invoice image", type=['jpg', 'png', 'jpeg'])
    
    # Initialize variables for manual input
    customer_name = ""
    address = ""
    state = ""
    pincode = ""
    received_amount = 0.0
    pending_amount = 0.0
    
    if uploaded_file is not None:
        try:
            # Read image file
            img = Image.open(uploaded_file)
            
            # Perform OCR on the image
            ocr_text = pytesseract.image_to_string(img)
            
            # Display the extracted text
            st.write("### Extracted Text:")
            st.write(ocr_text)
            
            # Extract information using regex patterns
            extracted_results = extract_patterns(ocr_text)
            
            # Display extracted information
            st.write("### Extracted Information:")
            extracted_info_rows = []
            for pattern_name, pattern_results in extracted_results.items():
                if pattern_results:
                    extracted_info_rows.append(f"- {pattern_name}: {', '.join(pattern_results)}")
                else:
                    extracted_info_rows.append(f"- {pattern_name}: No match found")
            st.markdown("\n".join(extracted_info_rows))
            
            # Display a form-like structure for manual entries
            st.write("### Information:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                customer_name = st.text_input("Customer Name")
                address = st.text_area("Address")
                total_amount = st.number_input("Total Amount", value=0.0)
            
            with col2:
                state = st.text_input("State")
                pincode = st.text_input("Pincode")
                received_amount = st.number_input("Received Amount", value=0.0)
                pending_amount = total_amount - received_amount
            
            # Highlight pending amount based on value
            if pending_amount > 0:
                st.markdown(f"<p style='font-weight:bold; font-size:1.2em; color:green;'>Pending Amount: {pending_amount}</p>", unsafe_allow_html=True)
            elif pending_amount < 0:
                st.markdown(f"<p style='font-weight:bold; font-size:1.2em; color:red;'>Pending Amount: {pending_amount}</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"Pending Amount: {pending_amount}")
            
            if st.button("Submit"):
                # Process manual entries if submitted
                submitted_info_rows = []
                if customer_name:
                    submitted_info_rows.append(f"Customer Name: {customer_name}")
                if address:
                    submitted_info_rows.append(f"Address: {address}")
                if state:
                    submitted_info_rows.append(f"State: {state}")
                if pincode:
                    submitted_info_rows.append(f"Pincode: {pincode}")
                if total_amount:
                    submitted_info_rows.append(f"Total Amount: {total_amount}")
                if received_amount:
                    submitted_info_rows.append(f"Received Amount: {received_amount}")
                if pending_amount:
                    submitted_info_rows.append(f"Pending Amount: {pending_amount}")
                
                # Display side by side
                col1, col2 = st.columns(2)
                with col1:
                    st.write("### Extracted Information:")
                    st.markdown("\n".join(extracted_info_rows))
                
                with col2:
                    st.write("### Submitted Information:")
                    st.markdown("\n".join(submitted_info_rows))
                
                # Save data to CSV file
                csv_filename = save_to_csv(extracted_results, submitted_info_rows)
                
                # Display success message and download link
                st.success(f"CSV file successfully created! Click below to download.")
                st.markdown(get_download_link(csv_filename), unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Error processing image: {e}")

def get_download_link(csv_filename):
    href = f'<a href="/download/{csv_filename}" download="{csv_filename}">Download CSV File</a>'
    return href

# Run the app
if __name__ == '__main__':
    main()