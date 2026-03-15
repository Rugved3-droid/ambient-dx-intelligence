"""Pydantic request/response models for API endpoints."""

from pydantic import BaseModel


class TranscriptInput(BaseModel):
    speaker: str
    text: str
    phase: int = 0


class QueryInput(BaseModel):
    question: str
    speaker: str = "Judge"
