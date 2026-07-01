import asyncio

import structlog
from duckduckgo_search import AsyncDDGS
from pydantic import BaseModel, ConfigDict, Field

from ..base import BaseTool, ToolResult

logger = structlog.get_logger(__name__)


class SearchResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    title: str
    url: str
    snippet: str


class WebSearchTool(BaseTool):
    """Tool to search the web using DuckDuckGo."""

    name = "web_search"
    description = "Searches the web using DuckDuckGo. No API key required."

    class Input(BaseModel):
        query: str = Field(description="Search query string", min_length=1)
        num_results: int = Field(default=5, ge=1, le=10)

    class Output(BaseModel):
        model_config = ConfigDict(frozen=True)

        results: list[SearchResult]
        query_used: str
        results_count: int

    input_schema = Input
    output_schema = Output
    required_permissions = []

    async def execute(self, input: BaseModel) -> ToolResult:  # noqa: A002
        if not isinstance(input, self.Input):
            raise TypeError("Invalid input type")
        query_log = input.query if len(input.query) <= 100 else input.query[:97] + "..."
        logger.info("executing_web_search", query=query_log, num_results=input.num_results)

        try:
            results = await asyncio.wait_for(
                self._perform_search(input.query, input.num_results), timeout=10.0
            )

            output = self.Output(
                results=results, query_used=input.query, results_count=len(results)
            )

            return ToolResult(success=True, data=output.model_dump())

        except TimeoutError:
            return ToolResult(success=False, error="Search timed out", error_code="SEARCH_TIMEOUT")
        except Exception as e:
            return ToolResult(success=False, error=f"Search failed: {str(e)}")

    async def _perform_search(self, query: str, max_results: int) -> list[SearchResult]:
        async with AsyncDDGS() as ddgs:
            raw_results = await ddgs.atext(query, max_results=max_results)

            parsed_results = []
            for r in raw_results:
                parsed_results.append(
                    SearchResult(
                        title=r.get("title", ""), url=r.get("href", ""), snippet=r.get("body", "")
                    )
                )
            return parsed_results
