"""FastAPI server."""
from fastapi import Body, FastAPI, HTTPException

from .parse import parse_question, ParseError

app = FastAPI(
    title="Mouse-TRAPI",
    version="1.0.0",
)


@app.post("/to_trapi")
def to_trapi(
        question: str = Body(..., example="What drugs treat asthma?"),
):
    """Convert English to TRAPI."""
    try:
        return parse_question(question)
    except ParseError as err:
        raise HTTPException(status_code=400, detail=str(err))
