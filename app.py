import streamlit as st
import pandas as pd
import PyPDF2
import docx
import openai
import json
import os
from datetime import datetime

# Function to read PDF files
def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to read DOCX files
def read_docx(file):
    doc = docx.Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

# Function to read Excel files
def read_excel(file):
    df = pd.read_excel(file)
    return df.to_string()

# Function to read TXT files
def read_txt(file):
    return file.read().decode("utf-8")

# Function to handle file upload and extract text
def extract_text(file):
    if file.type == "application/pdf":
        return read_pdf(file)
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return read_docx(file)
    elif file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        return read_excel(file)
    elif file.type == "text/plain":
        return read_txt(file)
    else:
        return "Unsupported file type"

# Load request count
def load_request_count():
    if os.path.exists("request_count.json"):
        with open("request_count.json", "r") as f:
            return json.load(f)
    return {"date": str(datetime.now().date()), "count": 0}

# Save request count
def save_request_count(data):
    with open("request_count.json", "w") as f:
        json.dump(data, f)

# Streamlit app layout
st.title("Document Question Answering App")

# Load the current request count
request_data = load_request_count()
current_date = str(datetime.now().date())

if request_data["date"] != current_date:
    request_data = {"date": current_date, "count": 0}
    save_request_count(request_data)

# Display the remaining requests
st.write(f"Remaining requests for today: {20 - request_data['count']}")

uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "xlsx", "txt"])

if uploaded_file is not None:
    document_text = extract_text(uploaded_file)
    st.text_area("Document Text", document_text, height=300)

    question = st.text_input("Ask a question about the document")

    if st.button("Get Answer"):
        if question:
            if request_data["count"] < 20:
                try:
                    openai.api_key = st.secrets["openai_api_key"]
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": f"Document text: {document_text}\n\nQuestion: {question}"}
                        ],
                        max_tokens=150
                    )
                    answer = response.choices[0].message['content'].strip()
                    st.write(f"Answer: {answer}")
                    
                    # Increment and save the request count
                    request_data["count"] += 1
                    save_request_count(request_data)
                except KeyError:
                    st.error("The API key was not found in Streamlit secrets.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.error("You have reached the maximum number of requests for today.")
        else:
            st.write("Please ask a question.")
