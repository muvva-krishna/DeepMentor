import os
import re
from pdf2image import convert_from_path
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
from pdfminer.high_level import extract_text
import base64
import io
import concurrent.futures
from tqdm import tqdm
from dotenv import load_dotenv
from pdf2image import convert_from_path
from openai import OpenAI
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from asset import system_prompt  # assuming you have this prompt file
load_dotenv()

api_key = "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"
client = OpenAI(api_key=api_key)

# New technique: Convert PDF pages to images
def convert_doc_to_images(path):
    return convert_from_path(path)

def get_img_uri(img):
    png_buffer = io.BytesIO()
    img.save(png_buffer, format="PNG")
    png_buffer.seek(0)
    return f"data:image/png;base64,{base64.b64encode(png_buffer.read()).decode('utf-8')}"

def analyze_image(data_uri):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [{"type": "image_url", "image_url": {"url": data_uri}}]},
            ],
            max_tokens=1000,
            temperature=0.1,
            top_p=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def analyze_doc_image(img):
    return analyze_image(get_img_uri(img))

def extract_content_with_vision(pdf_paths):
    all_docs = []
    for i, pdf_path in enumerate(pdf_paths):
        print(f"Processing PDF: {os.path.basename(pdf_path)}")
        images = convert_doc_to_images(pdf_path)

        chunks = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(analyze_doc_image, img) for img in images]
            with tqdm(total=len(images), desc=f"Analyzing {os.path.basename(pdf_path)}") as pbar:
                for j, future in enumerate(futures):
                    result = future.result()
                    if result.strip():
                        chunks.append(Document(
                            page_content=result,
                            metadata={"label": f"pdf_{i}_page_{j}"}
                        ))
                    pbar.update(1)
        all_docs.extend(chunks)
    return all_docs

# You can still use a text splitter if needed
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

def create_documents_with_labels(pdf_paths):
    raw_docs = extract_content_with_vision(pdf_paths)
    split_docs = []

    for doc in raw_docs:
        chunks = text_splitter.split_text(doc.page_content)
        for i, chunk in enumerate(chunks):
            split_docs.append(Document(
                page_content=chunk,
                metadata={"label": doc.metadata["label"] + f"_chunk_{i}"}
            ))
    return split_docs

# Example usage
pdf_paths = ["dataset/probability.pdf"]
documents = create_documents_with_labels(pdf_paths)
print(f"Total processed chunks: {len(documents)}")
