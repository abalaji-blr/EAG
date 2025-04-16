# d_layer.py - decision layer of Agent Architecture
# Handles decision making, planning next steps, and LLM interactions

import asyncio
import logging
from concurrent.futures import TimeoutError
from typing import List, Optional, Dict, Any, Union

from google import genai
from pydantic import BaseModel, Field

# Local imports
from config import Config
from p_layer import PromptFormatter, ResponseParser

class FunctionCall(BaseModel):
    """Model representing a function call parsed from LLM response"""
    name: str 
    params: List[str] = []
    reasoning_type: Optional[str] = None
        
    @classmethod
    def parse(cls, response_text: str):
        """Parse a FUNCTION_CALL: response into a structured object"""
        if not response_text.startswith("FUNCTION_CALL:"):
            return None
                
        _, function_info = response_text.split(":", 1)
        parts = [p.strip() for p in function_info.split("|")]
        func_name = parts[0]
                
        # Handle reasoning comment if present
        reasoning = None
        if "#" in func_name:
            func_name, reasoning_part = func_name.split("#", 1)
            func_name = func_name.strip()
            reasoning = reasoning_part.strip()
            
        # Process parameters
        params = parts[1:]
        clean_params = []
        for param in params:
            # Clean up any trailing comments
            if "#" in param:
                param = param.split("#")[0].strip()
            clean_params.append(param)
    
        return cls(
            name=func_name,
            params=clean_params,
            reasoning_type=reasoning
        )

class LLMClient:
    """Handles interactions with the LLM"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        
    async def generate_with_timeout(self, prompt: str, timeout: int = 10):
        """Generate content with a timeout"""
        print("Starting LLM generation...")
        try:
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None, 
                    lambda: self.client.models.generate_content(
                        model=self.model_name,
                        contents=prompt
                    )
                ),
                timeout=timeout
            )
            print("LLM generation completed")
            return response
        except TimeoutError:
            print("LLM generation timed out!")
            raise
        except Exception as e:
            print(f"Error in LLM generation: {e}")
            raise

class DecisionMaker:
    """Handles decision making and planning next steps"""
    
    def __init__(self, config: Config, llm_client: LLMClient):
        self.config = config
        self.llm_client = llm_client
        self.prompt_formatter = PromptFormatter()
    
    async def get_next_action(self, query: str, iteration_responses: List[str], last_response: Optional[str], tools) -> str:
        """Get the next action from the LLM"""
        current_query = query
        
        # Add context from previous iterations if available
        if iteration_responses:
            current_query = current_query + "\n\n" + " ".join(iteration_responses)
            current_query = current_query + "  What should I do next?"

        # Create prompt and get model's response with timeout
        print("Preparing to generate LLM response...")
        tools_description = self.prompt_formatter.format_tools_description(tools)
        system_prompt = self.prompt_formatter.create_system_prompt(tools_description)
        prompt = f"{system_prompt}\n\nQuery: {current_query}"
        
        logging.info(prompt)

        try:
            response = await self.llm_client.generate_with_timeout(
                prompt, 
                timeout=self.config.llm_timeout
            )
            response_text = response.text.strip()
            print(f"LLM Response: {response_text}")
            
            logging.info(f"LLM Response: {response_text}")
            
            return ResponseParser.extract_action(response_text)
            
        except Exception as e:
            print(f"Failed to get LLM response: {e}")
            raise
    
    def parse_action(self, response_text: str) -> Optional[FunctionCall]:
        """Parse the action from the LLM response"""
        if response_text.startswith("FUNCTION_CALL:"):
            return FunctionCall.parse(response_text)
        return None