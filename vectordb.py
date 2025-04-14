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
pinecone_api_key = os.getenv("pinecone_api")
openai_api_key = os.getenv("openai_api")

pc = Pinecone(api_key=pinecone_api_key)

index_name = "manimdemo"

pcindex = pc.Index(name = index_name,host="https://manimdemo-vd1mwjl.svc.aped-4627-b74a.pinecone.io")

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
        labeled_chunks = create_documents_with_labels()
        chunk_documents = labeled_chunks  # Use directly
        chunk_embeddings = create_embeddings(chunk_documents)
        store_embeddings(chunk_documents, chunk_embeddings, batch_size=100)
        print("All documents stored in Pinecone with labels.")
    except Exception as e:
        print(f"❌ Error while storing documents: {e}")

