# action.py
import torch
import faiss
import json
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Optional
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables to hold the model and index
# Avoid reloading them on every request
MODEL = None
INDEX = None
URL_MAPPING = None # Will store {index_id: {"url": "...", "text": "..."}}

DIMENSIONS = 768 # Example dimension for nomic-embed-text-v1. Adjust if needed.
MODEL_NAME = "nomic-ai/nomic-embed-text-v1"

def load_embedding_model(model_name: str = MODEL_NAME, trust_remote_code: bool = True) -> SentenceTransformer:
    """Loads the Nomic embedding model."""
    global MODEL
    if MODEL is None:
        logger.info(f"Loading embedding model: {model_name}")
        # Nomic recommends trusting remote code for their model
        MODEL = SentenceTransformer(model_name, trust_remote_code=trust_remote_code)
        logger.info("Embedding model loaded.")
    return MODEL

def load_faiss_index(index_path: str) -> Optional[faiss.Index]:
    """Loads the FAISS index from disk."""
    global INDEX
    if INDEX is None:
        try:
            logger.info(f"Loading FAISS index from: {index_path}")
            INDEX = faiss.read_index(index_path)
            # Ensure the index dimensions match the model
            if INDEX.d != DIMENSIONS:
                 logger.error(f"Index dimension ({INDEX.d}) does not match model dimension ({DIMENSIONS})")
                 INDEX = None # Invalidate index if dimensions mismatch
                 return None
            logger.info(f"FAISS index loaded. Contains {INDEX.ntotal} vectors.")
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}", exc_info=True)
            INDEX = None
    return INDEX

def load_url_mapping(mapping_path: str) -> Optional[dict]:
    """Loads the ID-to-URL mapping from disk."""
    global URL_MAPPING
    if URL_MAPPING is None:
        try:
            logger.info(f"Loading URL mapping from: {mapping_path}")
            with open(mapping_path, 'r') as f:
                # Load and convert keys from string back to int if necessary
                data = json.load(f)
                URL_MAPPING = {int(k): v for k, v in data.items()}
                logger.info(f"URL mapping loaded for {len(URL_MAPPING)} entries.")
        except Exception as e:
            logger.error(f"Failed to load URL mapping: {e}", exc_info=True)
            URL_MAPPING = None
    return URL_MAPPING

def embed_text(text: str) -> Optional[np.ndarray]:
    """Generates an embedding for the given text."""
    model = load_embedding_model()
    if model is None:
        logger.error("Embedding model is not loaded.")
        return None
    try:
        # Nomic expects a prefix for retrieval queries
        # Check documentation for the exact prefix recommended for nomic-embed-text-v1
        # It might be "search_query: "
        query_prefix = "search_query: "
        embeddings = model.encode([query_prefix + text], convert_to_numpy=True)
        # Ensure normalization if required by the model/indexing process
        faiss.normalize_L2(embeddings)
        return embeddings[0].reshape(1, -1) # Return as 2D array for FAISS
    except Exception as e:
        logger.error(f"Failed to embed text: {e}", exc_info=True)
        return None

def search_index(query_embedding: np.ndarray, top_k: int) -> Optional[Tuple[List[float], List[int]]]:
    """Searches the FAISS index for the closest matches."""
    index = load_faiss_index("index.faiss") # Ensure path is correct
    if index is None or index.ntotal == 0:
        logger.error("FAISS index is not loaded or is empty.")
        return None
    if query_embedding is None:
        logger.error("Invalid query embedding provided.")
        return None

    try:
        # Ensure top_k isn't larger than the number of items in the index
        actual_k = min(top_k, index.ntotal)
        if actual_k <= 0:
             logger.warning("Search requested with top_k <= 0 or empty index.")
             return [], []

        logger.info(f"Searching index for top {actual_k} results.")
        distances, indices = index.search(query_embedding, actual_k)

        # distances and indices are 2D arrays (batch size 1), flatten them
        return distances[0].tolist(), indices[0].tolist()
    except Exception as e:
        logger.error(f"Failed to search index: {e}", exc_info=True)
        return None

# --- Functions for Offline Building (Example) ---
# These would typically run in your Colab notebook, not the backend server

def scrape_page(url: str) -> Optional[str]:
    """Basic placeholder for scraping web page text."""
    # In a real scenario, use libraries like requests and BeautifulSoup
    # Handle errors, timeouts, content types, JS rendering etc.
    # This is a highly simplified example.
    try:
        import requests
        from bs4 import BeautifulSoup
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes
        soup = BeautifulSoup(response.content, 'html.parser')
        # Basic text extraction, needs significant improvement for real use
        text_content = ' '.join(p.get_text() for p in soup.find_all('p'))
        return text_content
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return None

def build_index_offline(urls: List[str], index_path: str, mapping_path: str):
    """
    Offline process to scrape URLs, embed content, and build FAISS index.
    (Run this in Colab or locally, not part of the live server).
    """
    logger.info("Starting offline index build process...")
    model = load_embedding_model()
    if not model: return

    all_embeddings = []
    url_map = {}
    doc_id_counter = 0

    # Nomic might have a different prefix for indexing passages
    # Check documentation. Example: "search_passage: "
    passage_prefix = "search_passage: "

    for url in urls:
        logger.info(f"Processing {url}...")
        content = scrape_page(url)
        if content and len(content) > 50: # Basic filter for meaningful content
            try:
                # Note: Nomic works best with chunks <= 512 tokens.
                # Real implementation should chunk long documents.
                # This example embeds the whole (potentially truncated) content.
                embeddings = model.encode([passage_prefix + content], convert_to_numpy=True)
                faiss.normalize_L2(embeddings) # Normalize for cosine similarity
                all_embeddings.append(embeddings[0])
                # Store URL and snippet (e.g., first 500 chars)
                url_map[doc_id_counter] = {
                    "url": url,
                    "text": content[:500] + "..." if len(content) > 500 else content
                }
                doc_id_counter += 1
            except Exception as e:
                 logger.error(f"Failed to process/embed content from {url}: {e}")
        else:
            logger.warning(f"Skipping {url} due to lack of content or scraping error.")

    if not all_embeddings:
        logger.error("No embeddings were generated. Index cannot be built.")
        return

    embeddings_np = np.array(all_embeddings).astype('float32')
    logger.info(f"Generated {embeddings_np.shape[0]} embeddings with dimension {embeddings_np.shape[1]}.")

    # Create FAISS index
    index = faiss.IndexFlatL2(DIMENSIONS) # Use IndexFlatL2 for cosine similarity after normalization
    # Or use a more advanced index like IndexIVFFlat for larger datasets
    # index = faiss.IndexIDMap(index) # If you want to use custom IDs, though sequential is easier here

    index.add(embeddings_np)
    logger.info(f"Added {index.ntotal} embeddings to the FAISS index.")

    # Save index and mapping
    faiss.write_index(index, index_path)
    logger.info(f"FAISS index saved to {index_path}")
    with open(mapping_path, 'w') as f:
        json.dump(url_map, f, indent=4)
    logger.info(f"URL mapping saved to {mapping_path}")
    logger.info("Offline index build complete.")
