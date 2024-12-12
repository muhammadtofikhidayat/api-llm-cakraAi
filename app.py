import streamlit as st
import requests
import json
from PyPDF2 import PdfReader

# Fungsi untuk memuat dokumen
def load_document(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type == "application/pdf":
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    else:
        st.error("Format file tidak didukung. Unggah file TXT atau PDF.")
        return None

# Fungsi untuk mengirimkan data ke API LLM cakra.ai
def generate_questions(api_key, text, num_questions=5):
    url = "https://saas.cakra.ai/genv2/llms"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model_name": "brain-v2",
        "messages": [
            {"role": "system", "content": "Anda adalah asisten AI yang membantu membuat soal pilihan ganda."},
            {"role": "user", "content": f"Buatlah {num_questions} soal pilihan ganda berdasarkan teks berikut. Format setiap soal adalah: \nSoal: [Pertanyaan]\nA) [Pilihan 1]\nB) [Pilihan 2]\nC) [Pilihan 3]\nD) [Pilihan 4]\nJawaban: [Pilihan yang benar].\n\nTeks:\n{text}"}
        ],
        "max_new_tokens": 500,
        "do_sample": False,
        "temperature": 0.7,
        "top_k": 50,
        "top_p": 1.0
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None

# Streamlit UI
st.title("Soal Pilihan Ganda Generator")

api_key = st.text_input("Masukkan API Key", type="password")
uploaded_file = st.file_uploader("Unggah Dokumen (TXT atau PDF)", type=["txt", "pdf"])

if uploaded_file and api_key:
    document_text = load_document(uploaded_file)

    if document_text and st.button("Generate Soal"):
        with st.spinner("Menghasilkan soal..."):
            result = generate_questions(api_key, document_text)

            if result:
                st.success("Soal berhasil dihasilkan!")
                choices = result.get("choices", [])
                for i, choice in enumerate(choices, 1):
                    st.markdown(choice.get("content"))
