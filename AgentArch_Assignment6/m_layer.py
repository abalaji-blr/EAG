# m_layer.py - memory layer of Agent Architecture
# Manages memory-related functionality, such as storing state across iterations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator

class Memory(BaseModel):
    """Global memory state for the agent."""
    max_iterations: int = 5
    iteration: int = 0
    last_response: Optional[Any] = None
    iteration_response: List[str] = Field(default_factory=list)
    user_preferences: Dict[str, str] = Field(
        default_factory=dict,
        description="User preferences for formatting and GUI tasks (e.g., 'ascii_format', 'numeric_precision', 'rectangle_size', 'text_style')."
    )
    
    @validator("user_preferences")
    def validate_preferences(cls, v):
        """Ensure only valid preference keys are used."""
        valid_keys = {"ascii_format", "numeric_precision", "rectangle_size", "text_style"}
        for key in v.keys():
            if key not in valid_keys:
                raise ValueError(f"Invalid preference key: {key}")
        return v
    
    def get_preferences(self) -> Dict[str, str]:
        """Get the current user preferences."""
        return self.user_preferences
    
    def set_preferences(self, preferences: Dict[str, str]):
        """Set user preferences with validation."""
        valid_keys = {"ascii_format", "numeric_precision", "rectangle_size", "text_style"}
        for key in preferences.keys():
            if key not in valid_keys:
                raise ValueError(f"Invalid preference key: {key}")
        self.user_preferences = preferences
    
    def reset(self):
        """Reset all state variables."""
        self.iteration = 0
        self.last_response = None
        self.iteration_response = []
        self.user_preferences = {}

# Create a global instance that will be imported by other modules
memory_state = Memory()
