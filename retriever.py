import os
import openai
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from asset import teaching_prompt

load_dotenv()
pinecone_api_key = os.getenv("pinecone_api")
openai_api_key = os.getenv("openai_api")

os.environ["OPENAI_API_KEY"] = openai_api_key
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("langsmith_api_key")
os.environ["LANGCHAIN_PROJECT"] = "rag"

# Initialize Pinecone and set up Pinecone VectorStore retriever
pc = Pinecone(api_key=pinecone_api_key)
index_name = "manimdemo"
pcindex = pc.Index(name=index_name, host="https://manimdemo-vd1mwjl.svc.aped-4627-b74a.pinecone.io")

# Create the OpenAI embedding and vector store retriever
embeddings = OpenAIEmbeddings(api_key=openai_api_key, model="text-embedding-3-large")
vectorstore = PineconeVectorStore(index=pcindex, embedding=embeddings)
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

# Initialize the language model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
llm_adv = ChatOpenAI(model="gpt-4o", temperature = 0.2)
output_parser = StrOutputParser()

# System prompt for guiding the responses
system_prompt = teaching_prompt

# Setup for contextualizing question prompts
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question which might reference context in the chat history, "
    "formulate a standalone question which can be understood without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)



# History-aware retriever setup
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

# Define chat prompt template with history
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# Set up question-answer chain
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# Store for chat session history
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Chain with message history
conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)

# Function to handle user queries
def handle_query(input_prompt, session_id):
    # Invoke the RAG chain with the input prompt and session_id
    response = conversational_rag_chain.invoke(
        {"input": input_prompt},
        {"configurable": {"session_id": session_id}}
    )
    
    # Print the assistant's response
    return response["answer"]

# Continuous interaction loop
if __name__ == "__main__":
    session_id = "unique_session_identifier"
    while True:
        user_input = input("You| ")
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Ending the conversation. Goodbye!")
            break
        handle_query(user_input, session_id)
