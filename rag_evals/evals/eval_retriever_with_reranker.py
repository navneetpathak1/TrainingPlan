import json
import re
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

from deepeval import evaluate
from deepeval.models import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    ContextualRecallMetric,
    ContextualPrecisionMetric,
    AnswerRelevancyMetric,
    FaithfulnessMetric,
)

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(PROJECT_ROOT))
from langchain_groq import ChatGroq

from main import (
    db,
    llm,
    reRanker,
    generate_answer,
    ingest_files,
    DATA_FOLDER,
    GROQ_API_KEY,
)

from state import State

load_dotenv()

GOLDEN_PATH = Path(__file__).resolve().parents[1] / "Golden_data" / "retriever_goldens.json"

JUDGE_MODEL_NAME = "openai/gpt-oss-120b"
THRESHOLD = 0.6

RETRIEVE_K = 10      # db.similarity_search(k=10)
RERANK_TOP_N = 4     # reRanker(top_n=4)

# Set True to also run the generator and score the answers
EVALUATE_GENERATION = False


class GroqJudge(DeepEvalBaseLLM):
    def __init__(self):
        self.model = ChatGroq(
            model=JUDGE_MODEL_NAME,
            temperature=0,
            api_key=GROQ_API_KEY,
        )

    def load_model(self):
        return self.model

    @staticmethod
    def _parse(text: str, schema: type[BaseModel]):
        match = re.search(r"\{.*\}", text, re.DOTALL)
        return schema(**json.loads(match.group(0) if match else text))

    def generate(self, prompt: str, schema: type[BaseModel] | None = None):
        if schema is None:
            return self.model.invoke(prompt).content
        try:
            return self.model.with_structured_output(schema).invoke(prompt)
        except Exception:
            text = self.model.invoke(prompt + "\n\nRespond with valid JSON only.").content
            return self._parse(text, schema)

    async def a_generate(self, prompt: str, schema: type[BaseModel] | None = None):
        if schema is None:
            return (await self.model.ainvoke(prompt)).content
        try:
            return await self.model.with_structured_output(schema).ainvoke(prompt)
        except Exception:
            text = (await self.model.ainvoke(prompt + "\n\nRespond with valid JSON only.")).content
            return self._parse(text, schema)

    def get_model_name(self):
        return JUDGE_MODEL_NAME


judge = GroqJudge()

def retrieve(query: str):
    candidates = db.similarity_search(query=query, k=RETRIEVE_K)
    return reRanker(query=query, retrieved_docs=candidates, top_n=RERANK_TOP_N)

with open(GOLDEN_PATH, encoding="utf-8") as f:
    goldens = json.load(f)


ingest_files(DATA_FOLDER, db)

test_cases = []

for g in goldens:
    query = g["query"]

    retrieved = retrieve(query)
    retrieval_context = [doc.page_content for doc in retrieved]

    if EVALUATE_GENERATION:
        state = generate_answer(State(query=query), db)
        actual_output = state.answer
    else:
        actual_output = "(generator not evaluated in this run)"

    test_cases.append(
        LLMTestCase(
            input=query,
            expected_output=g["ideal_answer"],
            retrieval_context=retrieval_context,
            actual_output=actual_output,
        )
    )


metrics = [
    ContextualRecallMetric(threshold=THRESHOLD, model=judge, include_reason=True, async_mode=False),
    ContextualPrecisionMetric(threshold=THRESHOLD, model=judge, include_reason=True, async_mode=False),
]

if EVALUATE_GENERATION:
    metrics += [
        AnswerRelevancyMetric(threshold=THRESHOLD, model=judge, include_reason=True),
        FaithfulnessMetric(threshold=THRESHOLD, model=judge, include_reason=True),
    ]

evaluate(
    test_cases=test_cases,
    metrics=metrics,
    hyperparameters={
        "model": "openai/gpt-oss-120b",
        "prompt template": "RAG retrieval evaluation",
        "retriever": f"similarity_k{RETRIEVE_K}+flashrank_top{RERANK_TOP_N}",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "reranker": "ms-marco-MiniLM-L-12-v2",
        "chunk_size": 500,
        "chunk_overlap": 80,
        "top_k": RERANK_TOP_N,
        "generator_model": "openai/gpt-oss-120b",
        "judge_model": JUDGE_MODEL_NAME,
        "golden_set": GOLDEN_PATH.name,
    },
)