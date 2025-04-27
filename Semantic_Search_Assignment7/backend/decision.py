# decision.py
from typing import Optional, List
from perception import SearchQueryInput, SearchResultItem, SearchResultsOutput
from action import embed_text, search_index
from memory import AgentMemory # Assuming you might pass the memory instance
import logging

logger = logging.getLogger(__name__)

def decide_search_action(query_input: SearchQueryInput, memory: AgentMemory) -> Optional[SearchResultsOutput]:
    """Processes a search query and decides on the search action."""

    logger.info(f"Received search query: '{query_input.query}' with top_k={query_input.top_k}")

    # 1. Embed the query
    query_embedding = embed_text(query_input.query)
    if query_embedding is None:
        logger.error("Failed to generate query embedding.")
        return None # Or return an empty result/error message

    # 2. Search the index
    search_result = search_index(query_embedding, query_input.top_k)
    if search_result is None:
        logger.error("Failed to perform index search.")
        return None # Or return an empty result/error message

    distances, indices = search_result
    logger.info(f"Found {len(indices)} results.")

    # 3. Format the results
    output_results: List[SearchResultItem] = []
    for i, index_id in enumerate(indices):
        mapping = memory.get_url_mapping(index_id)
        if mapping:
            output_results.append(
                SearchResultItem(
                    url=mapping.get("url", "URL not found"),
                    score=float(distances[i]), # FAISS L2 distance; smaller is better. Can convert to similarity if needed.
                    text_snippet=mapping.get("text", None) # Include the snippet
                )
            )
        else:
             logger.warning(f"No URL mapping found for index ID: {index_id}")


    return SearchResultsOutput(results=output_results)
