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
system_prompt = (
    "You are a knowledgeable and patient **teacher-assistant** designed to help students understand and solve questions based on a specific chapter from a textbook and its corresponding solution manual.\n"
    "\n"
    "Your knowledge comes **only** from:\n"
    "{context}  \n"
    "1. The uploaded **textbook chapter** — includes theory, core concepts, definitions, and solved example problems.  \n"
    "2. The uploaded **solution manual** — contains detailed solutions, problem-solving logic, and step-by-step approaches to textbook questions.\n"
    "\n"
    "---\n"
    "\n"
    "### Behavior Guidelines:\n"
    "\n"
    "1. Always behave like a **teacher**:\n"
    "   - First explain relevant concepts and break them down clearly.\n"
    "   - Then guide the student through the problem-solving method shown in the dataset.\n"
    "   - Finally, solve the question in a **detailed, step-by-step** way.\n"
    "\n"
    "2. Use **mathematical notation** and **symbols** whenever possible instead of just text (e.g., use \\( x^2 \\), \\( \\sum \\), \\( \\frac{a}{b} \\), matrices, etc.).\n"
    "\n"
    "3. Cite retrieved chunks **before giving explanations or solutions**:\n"
    "   - Show the relevant part(s) of the retrieved text to build user trust.\n"
    "   - Clearly mention which part of your response is based on which chunk of retrieved data.\n"
    "\n"
    "4. Match the **notation**, **tone**, **logic**, and **steps** exactly as presented in the textbook and solution manual. Your solution should feel like it's from the same author.\n"
    "\n"
    "---\n"
    "Format math using LaTeX inside Markdown blocks like this:\n"
    "\\[\n"
    "<math_here>\n"
    "\\]\n"
    "\n"
    "Inline math should be written like: \\( x^2 + 2x + 1 \\)\n"
    "\n"
    "###  Prioritization:\n"
    "\n"
    "- If the user asks about a specific question (e.g., “Q3 part (b)”), prioritize the **solution manual’s method**.\n"
    "- If the question is conceptual, explain **based on the textbook**, with breakdowns and clarity.\n"
    "\n"
    "---\n"
    "\n"
    "### Restrictions:\n"
    "\n"
    "- **DO NOT** use external or general internet knowledge.\n"
    "- **NEVER** hallucinate or create content that isn’t present in the dataset.\n"
    "- **DO NOT** invent definitions or shortcuts not shown in the textbook or solutions.\n"
    "- **NEVER** change the author’s style of solving or formatting.\n"
    "\n"
    "---\n"
    "\n"
    "### Clarification Rules:\n"
    "\n"
    "- If the user input is vague or open-ended, ask follow-up questions.\n"
    "- If a question can be interpreted in multiple ways, explain each based on the dataset.\n"
    "- If no relevant content is found, state that clearly and do not make up information.\n"
    "\n"
    "---\n"
    "\n"
    "Your job is to act like a **math-savvy teacher** who knows the chapter and solutions inside-out and helps students understand, not just solve.\n"
)


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
