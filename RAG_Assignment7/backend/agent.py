# agent.py
from flask import Flask, request, jsonify
import logging
from werkzeug.exceptions import BadRequest

from perception import SearchQueryInput, SearchResultsOutput
from memory import AgentMemory
from decision import decide_search_action
#from . import action # To potentially call build_index_offline if needed via a dev endpoint
import action

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize memory (loads model, index, mapping) when the app starts
# Make sure index.faiss and url_mapping.json are in the correct path
try:
    agent_memory = AgentMemory(index_path="index.faiss", mapping_path="url_mapping.json")
except Exception as e:
    logger.error(f"Failed to initialize AgentMemory: {e}", exc_info=True)
    # Decide how to handle catastrophic failure - exit, or run with limited functionality?
    # For now, we'll let it potentially fail requests.
    agent_memory = None

@app.route('/search', methods=['POST'])
def handle_search():
    """API endpoint to handle search requests."""
    if agent_memory is None or action.INDEX is None or action.MODEL is None:
         logger.error("Search endpoint called but agent memory/components not initialized.")
         return jsonify({"error": "Service not ready, initialization failed."}), 503 # Service Unavailable

    try:
        # Validate input using Pydantic
        query_data = SearchQueryInput(**request.json)
    except Exception as e:
        logger.error(f"Invalid search input: {e}", exc_info=True)
        return jsonify({"error": f"Invalid input: {e}"}), 400 # Bad Request

    # Use the decision module to process the search
    results: Optional[SearchResultsOutput] = decide_search_action(query_data, agent_memory)

    if results is None:
        logger.error(f"Search failed for query: {query_data.query}")
        # Decide on error response - could be 500 Internal Server Error
        return jsonify({"error": "Search processing failed."}), 500

    logger.info(f"Returning {len(results.results)} results for query: '{query_data.query}'")
    # Return results using Pydantic model's dict representation
    return jsonify(results.dict())

# Optional: Add a health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    if agent_memory and action.MODEL and action.INDEX and action.URL_MAPPING:
        return jsonify({
            "status": "OK",
            "model_loaded": True,
            "index_loaded": True,
            "index_size": action.INDEX.ntotal,
            "mapping_loaded": True,
            "mapping_size": len(action.URL_MAPPING)
            }), 200
    else:
        return jsonify({"status": "ERROR", "message": "One or more components failed to load."}), 503


# Example for triggering offline build (for development)
# Be careful exposing this in production!
@app.route('/build-index', methods=['POST'])
def trigger_build():
    data = request.json
    urls = data.get('urls')
    if not urls or not isinstance(urls, list):
        return jsonify({"error": "Missing or invalid 'urls' list in request body"}), 400

    try:
        # Run the offline build process (synchronously for simplicity here)
        # In a real app, you'd run this asynchronously (e.g., Celery task)
        action.build_index_offline(
            urls=urls,
            index_path="index.faiss",
            mapping_path="url_mapping.json"
        )
        # Re-initialize memory after building
        global agent_memory
        agent_memory = AgentMemory(index_path="index.faiss", mapping_path="url_mapping.json")
        return jsonify({"message": "Index build process completed and memory reloaded."}), 200
    except Exception as e:
        logger.error(f"Offline build failed: {e}", exc_info=True)
        return jsonify({"error": f"Index build failed: {e}"}), 500

if __name__ == '__main__':
    # Make sure to set host='0.0.0.0' to be accessible externally if needed
    # Use a proper WSGI server like Gunicorn or uWSGI for production
    app.run(host='127.0.0.1', port=5000, debug=True) # Debug=True for development only
