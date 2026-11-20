
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from state import State


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_FOLDER = BASE_DIR / "DATA"

if not DATA_FOLDER.exists():
    raise FileNotFoundError(f"Folder not found: {DATA_FOLDER}")

CONNECTION_STRING = os.getenv("CONNECTION_STRING")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not CONNECTION_STRING:
    raise ValueError("CONNECTION_STRING is missing from .env")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing from .env")

CONNECTION_NAME = "state_of_union_vector"

engine = create_engine(CONNECTION_STRING)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = PGVector(
    embeddings=embeddings,
    collection_name=CONNECTION_NAME,
    connection=CONNECTION_STRING,
)

# Create a table to track processed filenames
with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS processed_files (
            id SERIAL PRIMARY KEY,
            file_name VARCHAR(255) UNIQUE NOT NULL
        )
    """))


# --------------------------------------------------
# 3. File ingestion function
# --------------------------------------------------

def ingest_files(data_folder: Path, db: PGVector):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80
    )

    for file_path in data_folder.iterdir():

        if file_path.suffix.lower() not in [".pdf", ".txt"]:
            continue

        # Check whether filename already exists
        with engine.connect() as conn:
            exists = conn.execute(
                text("""
                    SELECT EXISTS (
                        SELECT 1 FROM processed_files
                        WHERE file_name = :file_name
                    )
                """),
                {"file_name": file_path.name}
            ).scalar()

        if exists:
            print(f"Already processed: {file_path.name}")
            continue

        try:
            # Load PDF or TXT
            if file_path.suffix.lower() == ".pdf":
                loader = PyPDFLoader(str(file_path))
            else:
                loader = TextLoader(
                    str(file_path),
                    encoding="utf-8"
                )

            documents = loader.load()

            # Add filename to metadata
            for doc in documents:
                doc.metadata["source"] = file_path.name

            # Generate chunks
            chunks = text_splitter.split_documents(documents)

            if not chunks:
                print(f"No content found: {file_path.name}")
                continue

            # Generate embeddings and store chunks
            db.add_documents(documents=chunks)

            # Save filename after successful storage
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO processed_files (file_name)
                        VALUES (:file_name)
                    """),
                    {"file_name": file_path.name}
                )

            print(f"Successfully stored: {file_path.name}")
            print(f"Total chunks: {len(chunks)}")

        except Exception as e:
            print(f"Failed to process {file_path.name}: {e}")


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.3,
    api_key=GROQ_API_KEY
)


from flashrank import Ranker, RerankRequest

# Initialize FlashRank once
ranker = Ranker(
    model_name="ms-marco-MiniLM-L-12-v2"
)


def reRanker(query: str, retrieved_docs, top_n=4):
    """
    Re-rank retrieved documents using FlashRank.
    """

    passages = []

    for i, doc in enumerate(retrieved_docs):
        passages.append({
            "id": str(i),
            "text": doc.page_content,
            "meta": doc.metadata
        })

    rerank_request = RerankRequest(
        query=query,
        passages=passages
    )

    reranked_results = ranker.rerank(rerank_request)

    # Select top N relevant documents
    top_results = reranked_results[:top_n]

    print("\nRe-ranking Results:")

    reranked_docs = []

    for i, result in enumerate(top_results, start=1):

        doc = retrieved_docs[int(result["id"])]

        print(
            f"[{i}] Score: {result['score']:.4f}"
        )

        reranked_docs.append(doc)

    return reranked_docs


def generate_answer(state: State, db: PGVector= db) -> State:

    # STEP 1: Retrieve more candidates from vector DB
    retrieved_docs = db.similarity_search(
        query=state.query,
        k=10
    )

    print(f"\nRetrieved {len(retrieved_docs)} chunks.")

    # STEP 2: Re-rank retrieved documents
    reranked_docs = reRanker(
        query=state.query,
        retrieved_docs=retrieved_docs,
        top_n=4
    )

    print(f"Selected {len(reranked_docs)} chunks after reranking.")

    context_parts = []
    citations = []

    for i, doc in enumerate(reranked_docs, start=1):

        source = doc.metadata.get("source", "Unknown source")
        page = doc.metadata.get("page", "N/A")

        citation = f"[{i}] Source: {source}, Page: {page}"

        context_parts.append(
            f"{doc.page_content}\nCitation: {citation}"
        )

        citations.append(citation)

    context = "\n\n".join(context_parts)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a helpful RAG assistant.

            Answer the user's question using ONLY the
            provided context.

            If the answer is not available in the context,
            clearly say that you don't have enough information.

            IMPORTANT:
            - Add inline citations for factual claims.
            - Use citation format [1], [2], etc.
            - Only cite sources provided in the context.
            - Do not invent citations.

            Context:
            {context}
            """
        ),
        ("human", "{query}")
    ])

    chain = prompt | llm

    response = chain.invoke({
        "context": context,
        "query": state.query
    })

    state.answer = response.content

    print("\nAnswer:")
    print(state.answer)

    print("\nSources:")

    for citation in citations:
        print(citation)
        state.citations.append(citation)

    return state


if __name__ == "__main__":

    print("Starting file ingestion...")
    print("Reading files from:", DATA_FOLDER)

    # Process only new files
    ingest_files(DATA_FOLDER, db)

    print("\nFile ingestion completed!")

    # Ask a question
    state = State(
        query="What is the main topic of the documents?"
    )

    result = generate_answer(state, db)

    print("\nQuestion:", result.query)
    print("Answer:", result.answer)
