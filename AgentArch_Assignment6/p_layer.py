# p_layer.py - perception layer of Agent Architecture
# Handles input and output formatting, including prompt creation, tool descriptions, and result formatting

import os
import asyncio
import logging
from concurrent.futures import TimeoutError
from functools import partial
from typing import List, Optional, Dict, Any, Union

# Third-party imports
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from pydantic import BaseModel, Field, validator, root_validator

# Pydantic models for MCP structures
class ToolParameter(BaseModel):
    name: str 
    type: str 
    description: Optional[str] = None

class Tool(BaseModel):
    name: str 
    description: str 
    parameters: List[ToolParameter] = []
                
    @classmethod
    def from_mcp_tool(cls, tool):
        """Convert MCP tool format to our model"""
        params = []
        if hasattr(tool, 'inputSchema') and 'properties' in tool.inputSchema:
            for param_name, param_info in tool.inputSchema['properties'].items():
                params.append(ToolParameter(
                    name=param_name,
                    type=param_info.get('type', 'string'),
                    description=param_info.get('description', '')
                ))
        return cls(
            name=getattr(tool, 'name', 'unknown_tool'),
            description=getattr(tool, 'description', 'No description'),
            parameters=params
        )

class PromptFormatter:
    """Handles formatting of prompts and tool descriptions"""
    
    @staticmethod
    def format_tools_description(tools) -> str:
        """Format tools into a readable description"""
        tools_models = [Tool.from_mcp_tool(tool) for tool in tools]
        
        tools_description = []
        for i, tool in enumerate(tools_models):
            param_details = []
            for param in tool.parameters:
                param_details.append(f"{param.name}: {param.type}")
            
            params_str = ', '.join(param_details) if param_details else 'no parameters'
            tool_desc = f"{i+1}. {tool.name}({params_str}) - {tool.description}"
            tools_description.append(tool_desc)
            
        return "\n".join(tools_description)
    
    @staticmethod
    def create_system_prompt(tools_description: str) -> str:
        """Create the system prompt with available tools"""
        return f"""You are a math agent solving problems in iterations using internal reasoning and external tools.

Available tools:
{tools_description}

Instructions:
- Internally think step-by-step before you respond.
- Always verify intermediate results before concluding.
- If uncertain or a tool fails, proceed with best-effort reasoning—do not get stuck.
- Do not repeat function calls with the same parameters.
- Tag each response with the type of reasoning used as a comment (e.g., # arithmetic, # logic, # lookup).
- Respond with EXACTLY ONE line in one of these formats (no extra text before or after):

1. FUNCTION_CALL: function_name|param1|param2|...  # reasoning_type
2. FINAL_ANSWER: [number]  # reasoning_type

Only give FINAL_ANSWER when all required calculations are complete and verified.

Examples:
- FUNCTION_CALL: add|5|3  # arithmetic
- FUNCTION_CALL: strings_to_chars_to_int|INDIA  # string
- FINAL_ANSWER: [42]  # arithmetic

DO NOT include any explanations or additional text.
Your entire response should be a single line starting with either FUNCTION_CALL: or FINAL_ANSWER:"""

class ResponseParser:
    """Handles parsing of LLM responses"""
    
    @staticmethod
    def extract_action(response_text: str) -> str:
        """Extract FUNCTION_CALL or FINAL_ANSWER from LLM response"""
        for line in response_text.split('\n'):
            line = line.strip()
            if line.startswith("FUNCTION_CALL:") or line.startswith("FINAL_ANSWER:"):
                return line
        return response_text

class ResultFormatter:
    """Handles formatting of tool call results"""
    
    @staticmethod
    def format_tool_result(result, numeric_precision: Optional[str] = None) -> str:
        """Format the result from a tool call"""
        if hasattr(result, 'content'):
            if isinstance(result.content, list):
                iteration_result = [
                    item.text if hasattr(item, 'text') else str(item)
                    for item in result.content
                ]
            else:
                iteration_result = str(result.content)
        else:
            iteration_result = str(result)
            
        if isinstance(iteration_result, list):
            result_str = f"[{', '.join(str(x) for x in iteration_result)}]"
        else:
            result_str = str(iteration_result)
            
        # Apply numeric precision if specified
        if numeric_precision and result_str.replace('.', '').isdigit():
            if numeric_precision == "2 decimal places":
                result_str = f"{float(result_str):.2f}"
            elif numeric_precision == "4 decimal places":
                result_str = f"{float(result_str):.4f}"
            elif numeric_precision == "Scientific notation":
                result_str = f"{float(result_str):.2e}"
                
        return result_str
    
    @staticmethod
    def format_iteration_response(iteration: int, function_name: str, result_str: str) -> str:
        """Format the response to add to iteration history"""
        return (
            f"In the {iteration} iteration you called {function_name} with parameters, "
            f"and the function returned {result_str}."
        )
    
    @staticmethod
    def format_final_answer(response_text: str) -> str:
        """Format the final answer for display"""
        return f"Final answer received: {response_text}"

class ArgumentsFormatter:
    """Handles preparing arguments for tool calls"""
    
    @staticmethod
    async def prepare_function_arguments(function_call, tools) -> Dict[str, Any]:
        """Prepare function arguments according to the tool's schema"""
        from d_layer import FunctionCall  # Import here to avoid circular dependency
        tool = next((t for t in tools if t.name == function_call.name), None)
        if not tool:
            raise ValueError(f"Unknown tool: {function_call.name}")
        
        arguments = {}
        schema_properties = tool.inputSchema.get('properties', {})
        params = function_call.params.copy()
        
        for param_name, param_info in schema_properties.items():
            if not params:
                raise ValueError(f"Not enough parameters provided for {function_call.name}")
                
            value = params.pop(0)
            param_type = param_info.get('type', 'string')
            
            if param_type == 'integer':
                arguments[param_name] = int(value)
            elif param_type == 'number':
                arguments[param_name] = float(value)
            elif param_type == 'array':
                if isinstance(value, str):
                    value = value.strip('[]').split(',')
                arguments[param_name] = [int(x.strip()) for x in value]
            else:
                arguments[param_name] = str(value)
                
        return arguments

class PreferenceHandler:
    """Handles user preference collection and query enhancement"""
    
    @staticmethod
    async def collect_user_preferences() -> Dict[str, str]:
        """Collect all relevant user preferences"""
        preferences = {}
        print("\n=== Please set your preferences before we begin ===")
    
        # ASCII conversion preferences
        print("\nASCII Output Format:")
        options = ["Comma-separated", "Array notation", "Individual lines"]
        for i, option in enumerate(options):
            print(f"{i+1}. {option}")
        choice = int(input("Enter your preference (number): "))
        preferences["ascii_format"] = options[choice-1]
    
        # Numeric precision preferences
        print("\nNumeric Precision:")
        options = ["2 decimal places", "4 decimal places", "Scientific notation"]
        for i, option in enumerate(options):
            print(f"{i+1}. {option}")
        choice = int(input("Enter your preference (number): "))
        preferences["numeric_precision"] = options[choice-1]
        
        # Rectangle size preferences
        print("\nRectangle Size:")
        options = ["Small (100x100)", "Medium (200x100)", "Large (300x200)"]
        for i, option in enumerate(options):
            print(f"{i+1}. {option}")
        choice = int(input("Enter your preference (number): "))
        preferences["rectangle_size"] = options[choice-1]
        
        # Text style preferences
        print("\nText Style:")
        options = ["Default", "Bold", "Large font"]
        for i, option in enumerate(options):
            print(f"{i+1}. {option}")
        choice = int(input("Enter your preference (number): "))
        preferences["text_style"] = options[choice-1]
        
        return preferences
    
    @staticmethod
    def incorporate_preferences_in_query(query: str, preferences: dict) -> str:
        """Enhance the query with user preferences"""
        rect_size = preferences["rectangle_size"]
        width, height = rect_size.split("(")[1].split(")")[0].split("x")
        
        enhanced_query = f"""{query}
User Preferences:
- ASCII Format: {preferences["ascii_format"]}
- Numeric Precision: {preferences["numeric_precision"]}
- Rectangle Size: Width={width}, Height={height}
- Text Style: {preferences["text_style"]}

Please respect these preferences when executing each step of the task.
"""
        return enhanced_query
    
    @staticmethod
    def apply_preferences(function_call, preferences: dict):
        """Apply user preferences to a function call"""
        from d_layer import FunctionCall  # Import here to avoid circular dependency
        if function_call.name == "draw_rectangle_in_existing_pages" and "rectangle_size" in preferences:
            size_pref = preferences["rectangle_size"]
            if "(" in size_pref:
                dimensions = size_pref.split("(")[1].split(")")[0].split("x")
                if len(dimensions) == 2:
                    function_call.params = dimensions
        return function_call