import streamlit as st
import pandas as pd
import docx
import PyPDF2
import openai

# Load the OpenAI API key from secrets
openai.api_key = st.secrets["openai_api_key"]

def check_openai_connection():
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt="Hello, OpenAI!",
            max_tokens=5
        )
        return f"Connection successful! Response: {response.choices[0].text.strip()}"
    except Exception as e:
        return f"Connection failed! Error: {e}"

def read_docx(file):
    doc = docx.Document(file)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def read_pdf(file):
    pdf_reader = PyPDF2.PdfFileReader(file)
    text = ""
    for page in range(pdf_reader.numPages):
        text += pdf_reader.getPage(page).extract_text()
    return text

def read_txt(file):
    return file.read().decode("utf-8")

def read_excel(file):
    df = pd.read_excel(file)
    return df.to_string()

def process_file(file):
    if file.type == "application/pdf":
        return read_pdf(file)
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return read_docx(file)
    elif file.type == "text/plain":
        return read_txt(file)
    elif file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        return read_excel(file)
    else:
        return "Unsupported file type"

def main():
    st.title("Document Question Answering App")

    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt", "xlsx"])

    if uploaded_file is not None:
        document_text = process_file(uploaded_file)
        st.write("Document content:", document_text)

        question = st.text_input("Ask a question about the document")
        if question:
            response = openai.Completion.create(
                engine="davinci",
                prompt=f"Document: {document_text}\n\nQuestion: {question}\n\nAnswer:",
                max_tokens=150
            )
            st.write("Answer:", response.choices[0].text.strip())

    if st.button("Check OpenAI Connection"):
        connection_status = check_openai_connection()
        st.write(connection_status)

if __name__ == "__main__":
    main()
