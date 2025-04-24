# perception.py
from pydantic import BaseModel
from typing import List, Optional

class SearchQueryInput(BaseModel):
    """Schema for incoming search queries."""
    query: str
    top_k: Optional[int] = 5

class SearchResultItem(BaseModel):
    """Schema for a single search result item."""
    url: str
    score: float
    text_snippet: Optional[str] = None # Optional: Include snippet used for indexing

class SearchResultsOutput(BaseModel):
    """Schema for the list of search results."""
    results: List[SearchResultItem]

# Optional: Schema if you were to add online indexing
# class PageDataInput(BaseModel):
#     url: str
#     content: str
