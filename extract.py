import os
import glob
import json
import pdfplumber
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

pdf_paths = ["dataset\\probability.pdf",
            "dataset\\Ch-16_Probability.pdf",
             
            ]

def extract_content_pdfplumber(pdf_paths): 
    all_content = []
    for pdf_path in pdf_paths:  
        combined_data = ""  
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                combined_data += page_text
        all_content.append(combined_data)
    return all_content

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)

def create_documents_with_labels():
    all_text_chunks = []
    content_pdf = extract_content_pdfplumber(pdf_paths)
    for i, text in enumerate(content_pdf):
        split_text_chunks = text_splitter.split_text(text)
        print(f"Extracted {len(split_text_chunks)} chunks from PDF {i}")
        all_text_chunks += [
            Document(page_content=chunk, metadata={"label": f"pdf_content_{i}_chunk_{j}"})
            for j, chunk in enumerate(split_text_chunks)
        ]
    return all_text_chunks

