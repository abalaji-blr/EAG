import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()

class Config(BaseModel):
    """Application configuration"""
    gemini_api_key: str
    max_iterations: int = 5
    llm_timeout: int = 10
    model_name: str = "gemini-2.0-flash"

# Load the config in your main function
def get_config():
    # Ensure environment variables are loaded
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not found")
    
    return Config(
        gemini_api_key=api_key,
        max_iterations=int(os.getenv("MAX_ITERATIONS","5" )),
        llm_timeout=int(os.getenv("LLM_TIMEOUT", "10")),
        model_name=os.getenv("MODEL_NAME", "gemini-2.0-flash")
    )

# Then in your main function:
# config = get_config()
