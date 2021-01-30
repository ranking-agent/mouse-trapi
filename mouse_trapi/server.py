"""FastAPI server."""
from fastapi import Body, FastAPI

from .parse import parse_question

app = FastAPI(
    title="Mouse-TRAPI",
    version="1.0.0",
)


@app.post("/to_trapi")
def to_trapi(
        question: str = Body(..., example="What drugs treat asthma?"),
):
    """Convert English to TRAPI."""
    return parse_question(question)
