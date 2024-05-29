import streamlit as st
import openai
import pandas as pd
from PyPDF2 import PdfReader
import docx2txt
import textract
from datetime import datetime, timedelta

# Load the OpenAI API key
def load_api_key():
    try:
        return st.secrets["general"]["OPENAI_API_KEY"]
    except KeyError:
        st.error("API key not found. Please check your secrets.toml file.")
        return None

# Set up the OpenAI API key
api_key = load_api_key()
if api_key:
    openai.api_key = api_key

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_word(file):
    text = docx2txt.process(file)
    return text

def extract_text_from_excel(file):
    df = pd.read_excel(file)
    text = df.to_string()
    return text

def extract_text_from_txt(file):
    text = textract.process(file).decode("utf-8")
    return text

def get_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_word(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        return extract_text_from_excel(uploaded_file)
    elif uploaded_file.type == "text/plain":
        return extract_text_from_txt(uploaded_file)
    else:
        return "Unsupported file type."

def get_answer_from_gpt3(question, document_text):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": document_text},
        {"role": "user", "content": question},
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150,
        temperature=0.7,
    )
    answer = response.choices[0].message["content"].strip()
    return answer

# Initialize session state variables
if "questions_asked" not in st.session_state:
    st.session_state.questions_asked = 0
    st.session_state.start_time = datetime.now()

def check_question_limit():
    if st.session_state.questions_asked >= 20:
        st.error("You have reached the limit of 20 questions for today.")
        return False
    if datetime.now() - st.session_state.start_time > timedelta(days=1):
        st.session_state.questions_asked = 0
        st.session_state.start_time = datetime.now()
    return True

st.title("Document-based Q&A with GPT-3")

uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "xlsx", "txt"])

if uploaded_file is not None:
    document_text = get_text_from_file(uploaded_file)
    st.write("Document text extracted. You can now ask questions based on the document.")
    
    question = st.text_input("Ask a question about the document:")
    
    if question and api_key:
        if check_question_limit():
            answer = get_answer_from_gpt3(question, document_text)
            st.session_state.questions_asked += 1
            st.write("Answer:", answer)
        else:
            st.warning("You have reached your daily limit of 20 questions. Please come back tomorrow.")
