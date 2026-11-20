from fastapi import FastAPI, HTTPException
from main import generate_answer
from state import State

app = FastAPI()


@app.post("/ask")
def query(query: str):

    try:
        state = State(query=query)

        result = generate_answer(state=state)

        return {
            "answer": result.answer,
            "citations": result.citations
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )