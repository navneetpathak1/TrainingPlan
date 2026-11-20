
import os
from pathlib import Path

from dotenv import load_dotenv

from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from pathlib import Path

from state import State

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent


DATA_FOLDER = BASE_DIR / "DATA"

if not DATA_FOLDER.exists():
    raise FileNotFoundError(f"Folder not found: {DATA_FOLDER}")

print("Reading files from:", DATA_FOLDER)

# 2. Load all TXT and PDF files
documents = []

for file_path in DATA_FOLDER.iterdir():

    if file_path.suffix.lower() == ".txt":
        loader = TextLoader(
            str(file_path),
            encoding="utf-8"
        )

    elif file_path.suffix.lower() == ".pdf":
        loader = PyPDFLoader(str(file_path))

    else:
        continue

    try:
        loaded_docs = loader.load()

        # Add source filename to metadata
        for doc in loaded_docs:
            doc.metadata["source"] = file_path.name

        documents.extend(loaded_docs)

        print(f"Loaded: {file_path.name}")

    except Exception as e:
        print(f"Failed: {file_path.name} - {e}")


print(f"\nTotal documents loaded: {len(documents)}")
print(documents)


# 3. Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=80
)

texts = text_splitter.split_documents(documents)

print(f"Total chunks generated: {len(texts)}")


# 4. Generate embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector = embeddings.embed_query("Testing the embedding model")

print("Vector dimensions:", len(vector))


# 5. PostgreSQL connection
CONNECTION_STRING = os.getenv("CONNECTION_STRING")

if not CONNECTION_STRING:
    raise ValueError("CONNECTION_STRING is missing from .env")


CONNECTION_NAME = "state_of_union_vector"


# 6. Store chunks in PGVector
db = PGVector.from_documents(
    embedding=embeddings,
    documents=texts,
    collection_name=CONNECTION_NAME,
    connection=CONNECTION_STRING,
)

print("Successfully stored documents in PGVector!")

  # 3. Create ChatGroq model
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_answer(state: State, db: PGVector) -> State:

    retrieved_docs = db.similarity_search(
        query=state.query,
        k=4
    )

    context = "\n\n".join(
        doc.page_content for doc in retrieved_docs
    )

    # 4. Create prompt
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a helpful RAG assistant.

            Answer the user's question using ONLY the
            provided context.

            If the answer is not available in the context,
            clearly say that you don't have enough information.

            Context:
            {context}
            """
        ),
        ("human", "{query}")
    ])

    # Generate answer
    chain = prompt | llm

    response = chain.invoke({
        "context": context,
        "query": state.query
    })

    state.answer = response.content

    return state


state = State(
    query="What is the main topic of the documents?"
)

result = generate_answer(state, db)

print("Question:", result.query)
print("Answer:", result.answer)

