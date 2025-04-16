# act_layer.py - action layer of Agent Architecture
# Handles execution of tools and interaction with the MCP server

import asyncio
import logging
from typing import Dict, Any, List

from mcp import ClientSession
from pydantic import BaseModel

# Local imports
from d_layer import FunctionCall
from p_layer import ArgumentsFormatter, ResultFormatter, PreferenceHandler

class ActionExecutor:
    """Handles execution of tools and interaction with the MCP server"""
    
    def __init__(self):
        self.args_formatter = ArgumentsFormatter()
        self.result_formatter = ResultFormatter()
    
    async def execute_tool(self, session: ClientSession, function_call: FunctionCall, tools, preferences: Dict[str, str]) -> str:
        """Execute a tool and return the result"""
        try:
            # Apply user preferences if available
            if preferences:
                function_call = PreferenceHandler.apply_preferences(function_call, preferences)
            
            # Prepare arguments according to the tool's input schema
            arguments = await self.args_formatter.prepare_function_arguments(function_call, tools)
            print(f"DEBUG: Final arguments: {arguments}")
            
            # Call the tool
            result = await session.call_tool(function_call.name, arguments=arguments)
            
            # Format the result with preferences
            return self.result_formatter.format_tool_result(
                result, 
                preferences.get("numeric_precision", None)
            )
        
        except Exception as e:
            print(f"DEBUG: Error in tool execution: {str(e)}")
            import traceback
            traceback.print_exc()
            raise