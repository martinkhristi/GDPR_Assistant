import streamlit as st
import google.generativeai as genai
from PIL import Image
import base64
from PyPDF2 import PdfReader

# Function to get API key
def get_api_key():
    encoded_key = "GEMINI_API_KEY"  # Example encoded key
    return base64.b64decode(encoded_key).decode('utf-8')

# Initialize Gemini model
def initialize_gemini():
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name="gemini-2.0-flash-exp")

# Extract clauses from PDF
def extract_clauses_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    return text.split("\n\n")  # Assuming clauses are separated by double newlines

# Check GDPR compliance for each clause
def check_gdpr_compliance(model, clauses):
    compliance_results = []
    for clause in clauses:
        prompt = (
            f"Review the following clause for GDPR compliance:\n\n"
            f"Clause: {clause}\n\n"
            f"Output: Indicate whether the clause is compliant or non-compliant and provide reasoning."
        )
        response = model.generate_content([prompt])
        compliance_results.append({
            "clause": clause,
            "result": response.text
        })
    return compliance_results

# Set up the Streamlit app
st.set_page_config(
    page_title="GDPR Agreement Review",
    layout="wide"
)
st.title("GDPR Agreement Review 🛡️")
st.caption("Upload an agreement to analyze its clauses for GDPR compliance. By Martin Khristi 🌟")

# Initialize the AI model
try:
    model = initialize_gemini()
except Exception as e:
    st.error("Failed to initialize the AI model. Please check your API key.")
    st.stop()

# Sidebar for document upload
with st.sidebar:
    st.title("Upload Agreement")
    uploaded_file = st.file_uploader(
        "Upload a document (PDF only)...",
        type=["pdf"]
    )

if uploaded_file:
    st.sidebar.success("Document uploaded successfully.")
    st.sidebar.info("Processing document to extract clauses...")
    
    # Extract clauses
    try:
        clauses = extract_clauses_from_pdf(uploaded_file)
        if not clauses:
            raise ValueError("No text could be extracted.")
    except Exception as e:
        st.error("Failed to extract clauses. Please ensure the PDF contains readable text.")
        st.stop()

    st.success(f"Extracted {len(clauses)} clauses from the document.")
    st.write("### Extracted Clauses")
    for i, clause in enumerate(clauses):
        st.write(f"**Clause {i+1}:** {clause}")

    # Perform GDPR compliance check
    if st.button("Check GDPR Compliance"):
        with st.spinner("Analyzing clauses for GDPR compliance..."):
            try:
                results = check_gdpr_compliance(model, clauses)
                compliant_clauses = [
                    res for res in results if "compliant" in res["result"].lower()
                ]
                non_compliant_clauses = [
                    res for res in results if "compliant" not in res["result"].lower()
                ]

                # Display results
                st.write("### GDPR Compliance Results")
                
                st.write("#### Compliant Clauses")
                if compliant_clauses:
                    for item in compliant_clauses:
                        st.write(f"**Clause:** {item['clause']}")
                        st.write(f"**Result:** {item['result']}")
                        st.write("---")
                else:
                    st.info("No compliant clauses found.")

                st.write("#### Non-Compliant Clauses")
                if non_compliant_clauses:
                    for item in non_compliant_clauses:
                        st.write(f"**Clause:** {item['clause']}")
                        st.write(f"**Result:** {item['result']}")
                        st.write("---")
                else:
                    st.success("No non-compliant clauses found.")

                # Conclusion
                if non_compliant_clauses:
                    st.error(
                        f"The agreement has {len(non_compliant_clauses)} non-compliant clauses. "
                        f"It is not fully GDPR compliant."
                    )
                else:
                    st.success("The agreement is fully GDPR compliant!")
            except Exception as e:
                st.error("Error during GDPR compliance analysis. Please try again.")
else:
    st.info("Upload a PDF document to begin.")

