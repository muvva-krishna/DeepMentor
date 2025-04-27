import os
import time
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pinecone import ServerlessSpec
from main import create_documents_with_labels

load_dotenv()
#change the api key for pinecone, index_name, and host
pinecone_api_key = "pcsk_3UiVd2_RegBBzyog3P6EytzRbocmt7ttGt5SwrDWtW6z9EmTNRg67byxaGeDhFw7jQPE5e"
openai_api_key = "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"

pc = Pinecone(api_key=pinecone_api_key)

index_name = "test" #indexname

pcindex = pc.Index(name = index_name,host="https://test-a604i2v.svc.aped-4627-b74a.pinecone.io")# change the host name

embeddings = OpenAIEmbeddings(api_key=openai_api_key,model = "text-embedding-3-large")
vectorstore = PineconeVectorStore(index= pcindex,embedding= embeddings)

text_splitter = RecursiveCharacterTextSplitter()

def create_embeddings(documents):
    return embeddings.embed_documents([doc.page_content for doc in documents])

def store_embeddings(documents, embeddings, batch_size=100):
    pinecone_data = [
        {
            "id": doc.metadata["label"],
            "values": embedding,
            "metadata": {"text": doc.page_content}
        }
        for doc, embedding in zip(documents, embeddings)
    ]

    # Process in batches
    for i in range(0, len(pinecone_data), batch_size):
        batch = pinecone_data[i:i + batch_size]
        pcindex.upsert(vectors=batch)

if __name__ == "__main__":
    try:
        pdf_paths = ["dataset/probability.pdf"]
        labeled_chunks = create_documents_with_labels(pdf_paths)
        chunk_documents = labeled_chunks
        chunk_embeddings = create_embeddings(chunk_documents)
        store_embeddings(chunk_documents, chunk_embeddings, batch_size=100)
        print("All documents stored in Pinecone with labels.")
    except Exception as e:
        print(f"❌ Error while storing documents: {e}")
