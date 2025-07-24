# MentraX AI 🧠

MentraX AI is a powerful, interactive learning platform designed to help students understand complex mathematical concepts. It combines a knowledgeable AI tutor with an automated animation engine to provide a rich, multi-modal learning experience.

## Features

  - **AI-Powered Study Assistant**: Get detailed, step-by-step explanations for textbook questions. The AI tutor's knowledge is strictly limited to the provided textbook and solution manual, ensuring accurate and relevant answers.
  - **Automated Mathematical Animations**: Visualize complex mathematical concepts with automatically generated Manim animations. The system takes a mathematical explanation and creates a corresponding video to illustrate the logic.
  - **Interactive Chat Interface**: Engage with the AI tutor through an intuitive, chat-like interface built with Streamlit.
  - **RAG-Powered Responses**: The AI leverages a Retrieval-Augmented Generation (RAG) pipeline with Pinecone's vector database to pull in the most relevant information from the source material.
  - **Extensible and Modular**: The codebase is organized into logical modules, making it easy to extend or modify.

## Architecture

The application is built on a modular architecture that combines several key technologies:

  - **Frontend**: A user-friendly web interface created with **Streamlit** (`app.py`).
  - **AI and Language Models**: The core logic for generating explanations and animation plans is powered by the **Groq API** (`codegen.py`), which provides fast inference for large language models.
  - **Animation Engine**: Mathematical animations are generated using the **Manim Community Edition** library. The `codegen.py` script produces Manim code, which is then executed by `manim_runner.py`.
  - **Retrieval-Augmented Generation (RAG)**: The AI's responses are grounded in the provided educational materials using a RAG pipeline.
  - **Vector Database**: **Pinecone** is used to store and retrieve vector embeddings of the textbook content, ensuring that the AI can quickly find the most relevant information to answer a user's query (`vectordb.py`, `retriever.py`).
  - **PDF Content Extraction**: The `extract.py` script processes PDF documents, converting them into a format that can be used to build the vector database.

## File Descriptions

| File | Description |
|---|---|
| `app.py` | The main Streamlit application. It handles the user interface, chat history, and orchestrates calls to the other modules. |
| `codegen.py` | Contains the `AnimationGenerator` class, which uses the Groq API to generate animation plans and Manim code. |
| `manim_runner.py` | A utility to execute Manim code and find the path to the most recently rendered video. |
| `retriever.py` | Implements the RAG pipeline. It uses Pinecone and LangChain to retrieve relevant document chunks and generate a response. |
| `vectordb.py`| A script to create and store vector embeddings from the source PDFs into the Pinecone database. |
| `extract.py`| A utility for extracting content from PDF files, preparing it for the vector database. |
| `asset.py` | Stores prompt templates and other assets used by the AI models. |
| `requirements.txt` | A list of all the Python dependencies required to run the project. |
| `Dockerfile` | A Dockerfile to containerize the application and its dependencies for easy deployment. |
| `.env` | A file to store environment variables, such as API keys. |

## Setup and Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/muvva-krishna/manim.git
    cd manim
    ```

2.  **Install system dependencies:**
    The application requires FFmpeg and a LaTeX distribution. These are included in the Docker setup.

3.  **Install Python dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the root directory and add your API keys:

    ```
    GROQ_API_KEY="your_groq_api_key"
    LANGCHAIN_API_KEY="your_langchain_api_key"
    PINECONE_API_KEY="your_pinecone_api_key"
    OPENAI_API_KEY="your_openai_api_key"
    ```

5.  **Prepare the Vector Database:**
    Run the `vectordb.py` script to populate your Pinecone index with the content from the provided PDF(s).

    ```bash
    python vectordb.py
    ```

## How to Run

To start the application, run the following command in your terminal:

```bash
streamlit run app.py
```

This will launch the Streamlit web server, and you can access the application in your browser at `http://localhost:8501`.

## Dependencies

  - **Streamlit**: For the web interface.
  - **Groq**: For fast language model inference.
  - **Manim**: For creating mathematical animations.
  - **OpenAI**: For generating embeddings.
  - **LangChain**: For building the RAG pipeline.
  - **Pinecone**: For the vector database.
  - **python-dotenv**: For managing environment variables.
  - **pdf2image**: For extracting content from PDFs.
