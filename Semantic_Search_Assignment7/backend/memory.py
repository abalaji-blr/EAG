# memory.py
from typing import Optional, List, Dict, Any
import logging
#from . import action # Use relative import
import action

logger = logging.getLogger(__name__)

class AgentMemory:
    """Manages the state, including the index and mappings."""

    def __init__(self, index_path: str = "index.faiss", mapping_path: str = "url_mapping.json"):
        self.index_path = index_path
        self.mapping_path = mapping_path
        self._initialize_memory()

    def _initialize_memory(self):
        """Loads the necessary components into memory."""
        logger.info("Initializing agent memory...")
        action.load_embedding_model()
        action.load_faiss_index(self.index_path)
        action.load_url_mapping(self.mapping_path)
        if action.MODEL is None or action.INDEX is None or action.URL_MAPPING is None:
            logger.error("Memory initialization failed. Check logs for details.")
            # You might want to raise an exception here or handle it downstream
        else:
            logger.info("Agent memory initialized successfully.")


    def get_url_mapping(self, index_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves URL and associated data for a given index ID."""
        if action.URL_MAPPING is None:
             logger.error("URL Mapping is not loaded.")
             return None
        return action.URL_MAPPING.get(index_id)

    # Add other methods if needed to interact with or update memory state
    # For this use case, loading is the primary function.
