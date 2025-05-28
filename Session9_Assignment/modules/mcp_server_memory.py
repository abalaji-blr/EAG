from mcp.server.fastmcp import FastMCP, Context
from typing import List, Optional, Dict, Any
from datetime import datetime
import yaml
from memory import MemoryManager  # Import MemoryManager to use its path structure
import json
import os
import sys
import signal
from pydantic import BaseModel  # Add this import

# Define input model here
class SearchInput(BaseModel):
    query: str

BASE_MEMORY_DIR = "memory"

# Get absolute path to config file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)  # Go up one level from modules to S9
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "profiles.yaml")

# Load config
try:
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
        MEMORY_CONFIG = config.get("memory", {}).get("storage", {})
        BASE_MEMORY_DIR = MEMORY_CONFIG.get("base_dir", "memory")
except Exception as e:
    print(f"Error loading config from {CONFIG_PATH}: {e}")
    sys.exit(1)

mcp = FastMCP("memory-service")

class MemoryStore:
    def __init__(self):
        self.memory_dir = BASE_MEMORY_DIR
        self.current_session = None
        self.conversation_index = {}  # New: Store semantic index
        os.makedirs(self.memory_dir, exist_ok=True)

    def load_session(self, session_id: str):
        """Load memory manager for a specific session."""
        self.current_session = session_id

    def _list_all_memories(self) -> List[Dict]:
        """Load all memory files using MemoryManager's date-based structure"""
        all_memories = []
        base_path = self.memory_dir  # Use the simple memory_dir path
        
        for year_dir in os.listdir(base_path):
            year_path = os.path.join(base_path, year_dir)
            if not os.path.isdir(year_path):
                continue
                
            for month_dir in os.listdir(year_path):
                month_path = os.path.join(year_path, month_dir)
                if not os.path.isdir(month_path):
                    continue
                    
                for day_dir in os.listdir(month_path):
                    day_path = os.path.join(month_path, day_dir)
                    if not os.path.isdir(day_path):
                        continue
                        
                    for file in os.listdir(day_path):
                        if file.endswith('.json'):
                            try:
                                with open(os.path.join(day_path, file), 'r') as f:
                                    session_memories = json.load(f)
                                    all_memories.extend(session_memories)  # Extend instead of append
                            except Exception as e:
                                print(f"Failed to load {file}: {e}")
        
        return all_memories

    def _get_conversation_flow(self, conversation_id: str = None) -> Dict:
        """Get sequence of interactions in a conversation"""
        if conversation_id is None:
            conversation_id = self.current_session
        
        # Use the session path we already know
        session_path = os.path.join(self.memory_dir, conversation_id)
        if not os.path.exists(session_path):
            return {"error": "Conversation not found"}
        
        interactions = []
        for file in sorted(os.listdir(session_path)):
            if file.endswith('.json'):
                with open(os.path.join(session_path, file), 'r') as f:
                    interactions.append(json.load(f))
        
        return {
            "conversation_flow": [
                {
                    "query": interaction.get("query", ""),
                    "intent": interaction.get("intent", ""),
                    "tool_calls": [
                        {
                            "tool": call["tool"],
                            "args": call["args"],
                            "result_summary": call.get("result_summary", "No summary available")
                        }
                        for call in interaction.get("tool_calls", [])
                    ],
                    "final_answer": interaction.get("final_answer", ""),
                    "tags": interaction.get("tags", [])
                }
                for interaction in interactions
            ],
            "timestamp_start": interactions[0].get("timestamp") if interactions else None,
            "timestamp_end": interactions[-1].get("timestamp") if interactions else None
        }

    def _create_conversation_index(self, memory: Dict) -> Dict:
        """Create a semantic index for a conversation"""
        index_entry = {
            "query": memory.get("user_query", ""),
            "intent": memory.get("intent", ""),
            "final_answer": memory.get("final_answer", ""),
            "timestamp": memory.get("timestamp", ""),
            "tags": memory.get("tags", []),
            "tool_calls": [
                {
                    "tool": call.get("tool", ""),
                    "args": call.get("args", {}),
                    "result": call.get("result", "")
                }
                for call in memory.get("tool_calls", [])
            ]
        }
        return index_entry

    def _update_conversation_index(self):
        """Update the semantic index with all conversations"""
        all_memories = self._list_all_memories()
        for memory in all_memories:
            if memory.get("type") == "run_metadata":
                session_id = memory.get("session_id", "")
                if session_id:
                    self.conversation_index[session_id] = self._create_conversation_index(memory)

    def get_relevant_conversations(self, query: str, limit: int = 5) -> List[Dict]:
        """Get most relevant conversations based on semantic similarity"""
        self._update_conversation_index()
        
        # Calculate relevance scores
        scored_conversations = []
        for session_id, conversation in self.conversation_index.items():
            # Calculate relevance based on query, intent, and tags
            relevance_score = 0
            
            # Query match
            if query.lower() in conversation["query"].lower():
                relevance_score += 0.4
                
            # Intent match
            if query.lower() in conversation["intent"].lower():
                relevance_score += 0.3
                
            # Tag match
            for tag in conversation["tags"]:
                if query.lower() in tag.lower():
                    relevance_score += 0.1
                    
            # Tool result match
            for tool_call in conversation["tool_calls"]:
                if query.lower() in str(tool_call["result"]).lower():
                    relevance_score += 0.2
                    
            scored_conversations.append({
                "session_id": session_id,
                "conversation": conversation,
                "relevance_score": relevance_score
            })
            
        # Sort by relevance and return top matches
        scored_conversations.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_conversations[:limit]

    def get_conversation_context(self, query: str) -> str:
        """Get formatted context from relevant conversations"""
        relevant_convs = self.get_relevant_conversations(query)
        
        if not relevant_convs:
            return "No relevant historical conversations found."
            
        context = []
        for conv in relevant_convs:
            conversation = conv["conversation"]
            context.append(f"Previous Query: {conversation['query']}")
            context.append(f"Intent: {conversation['intent']}")
            context.append(f"Answer: {conversation['final_answer']}")
            context.append(f"Tools Used: {[call['tool'] for call in conversation['tool_calls']]}")
            context.append("---")
            
        return "\n".join(context)

# Initialize global memory store
memory_store = MemoryStore()

def handle_shutdown(signum, frame):
    """Global shutdown handler"""
    sys.exit(0)

@mcp.tool()
async def get_current_conversations(input: Dict) -> Dict[str, Any]:
    """Get current session interactions. Usage: input={"input":{}} result = await mcp.call_tool('get_current_conversations', input)"""
    try:
        # Use absolute paths
        memory_root = os.path.join(ROOT_DIR, "memory")  # ROOT_DIR is already defined at top
        dt = datetime.now()
        
        # List all files in today's directory
        day_path = os.path.join(
            memory_root,
            str(dt.year),
            f"{dt.month:02d}",
            f"{dt.day:02d}"
        )
        
        if not os.path.exists(day_path):
            return {"error": "No sessions found for today"}
            
        # Get most recent session file
        session_files = [f for f in os.listdir(day_path) if f.endswith('.json')]
        if not session_files:
            return {"error": "No session files found"}
            
        latest_file = sorted(session_files)[-1]  # Get most recent
        file_path = os.path.join(day_path, latest_file)
        
        # Read and return contents
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        return {"result": {
                    "session_id": latest_file.replace(".json", ""),
                    "interactions": [
                        item for item in data 
                        if item.get("type") != "run_metadata"
                    ]
                }}
    except Exception as e:
        print(f"[memory] Error: {str(e)}")  # Debug print
        return {"error": str(e)}

@mcp.tool()
async def search_historical_conversations(input: SearchInput) -> Dict[str, Any]:
    """Search conversation memory between user and YOU. Usage: input={"input": {"query": "anmol singh"}} result = await mcp.call_tool('search_historical_conversations', input)"""
    try:
        all_memories = memory_store._list_all_memories()
        search_terms = input.query.lower().split()
        
        matches = []
        for memory in all_memories:
            # Only search in user query, final answer, and intent
            memory_content = " ".join([
                str(memory.get("user_query", "")),
                str(memory.get("final_answer", "")),
                str(memory.get("intent", ""))
            ]).lower()
            
            if all(term in memory_content for term in search_terms):
                # Only keep fields we want to return
                matches.append({
                    "user_query": memory.get("user_query", ""),
                    "final_answer": memory.get("final_answer", ""),
                    "timestamp": memory.get("timestamp", ""),
                    "intent": memory.get("intent", "")
                })

        # Sort by timestamp (most recent last)
        matches.sort(key=lambda x: x.get("timestamp", ""), reverse=False)
        
        # Count total words in matches
        total_words = 0
        filtered_matches = []
        WORD_LIMIT = 10000
        
        for match in matches:
            match_text = " ".join([
                str(match.get("user_query", "")),
                str(match.get("final_answer", ""))
            ])
            words_in_match = len(match_text.split())
            
            if total_words + words_in_match <= WORD_LIMIT:
                filtered_matches.append(match)
                total_words += words_in_match
            else:
                break
        
        return {"result": {
                    "status": "error",
                    "message": str(e)
                }}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def get_conversation_context(input: SearchInput) -> Dict[str, Any]:
    """Get relevant historical conversation context. Usage: input={"input": {"query": "your query"}} result = await mcp.call_tool('get_conversation_context', input)"""
    try:
        context = memory_store.get_conversation_context(input.query)
        return {"result": context}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("Memory MCP server starting...")
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "dev":
            mcp.run()
        else:
            mcp.run(transport="stdio")
    finally:
        print("\nShutting down memory service...")
