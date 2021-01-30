"""FastAPI server."""
from fastapi import FastAPI

from .parse import parse_question

app = FastAPI()


@app.post("/to_trapi")
def to_trapi(
        question: str,
):
    """Convert English to TRAPI."""
    return parse_question(question)
