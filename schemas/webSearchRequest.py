from pydantic_core import BaseModel, Field

#this is it
class WebSearchRequest(BaseModel):
    query: str = Field(..., description="The search query string.")
    num_results: int = Field(5, description="Number of search results to return.", ge=1, le=10)
