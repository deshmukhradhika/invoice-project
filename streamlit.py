import streamlit as st
import pytesseract
from PIL import Image
import re
import os
path=r"C:\Program Files\Tesseract-OCR\tesseract"
pytesseract.pytesseract.tesseract_cmd=path
# Define regex patterns
patterns = {
    'pan_no': r"[A-Z]{5}\d{4}[A-Z]",
    'mail_id': r"[\w]{1,36}[@][a-z.]{8,14}",
    'phone_no': r"[9][1][-]\d{10}",
    'GSTIN_no': r"\d{2}[A-Z]{5}\d{4}[A-Z]\d[A-Z]{2}",
    'customer_Account_no': r"[0]\d{11}",
    'IFSC_Code': r"[A-Z]{4}\d{7}"
}

# Function to extract patterns from text using regex
def extract_patterns(text):
    results = {}
    for pattern_name, pattern in patterns.items():
        results[pattern_name] = re.findall(pattern, text)
    return results

# Main function to run the Streamlit app
def main():
    st.title('Invoice Information Extraction from Images')
    
    # Upload image file
    uploaded_file = st.file_uploader("Upload an invoice image", type=['jpg', 'png', 'jpeg'])
    
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
            for pattern_name, pattern_results in extracted_results.items():
                if pattern_results:
                    st.write(f"- {pattern_name}: {', '.join(pattern_results)}")
                else:
                    st.write(f"- {pattern_name}: No match found")
        
        except Exception as e:
            st.error(f"Error processing image: {e}")

# Run the app
if __name__ == '__main__':
    main()