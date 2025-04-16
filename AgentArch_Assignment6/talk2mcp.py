# talk2mcp.py - Main agent class for handling MCP interactions

import os
import asyncio
import logging
from concurrent.futures import TimeoutError
from typing import List, Optional, Dict, Any, Union

# Third-party imports
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import BaseModel, Field

# Local imports
from config import Config, get_config
from m_layer import memory_state
from d_layer import LLMClient, DecisionMaker, FunctionCall
from act_layer import ActionExecutor
from p_layer import ResultFormatter, PreferenceHandler

# Configure logging
logging.basicConfig(
    filename='log.log',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.info("Logging to a file!")

class MCPAgent:
    """Main agent class for handling MCP interactions"""
    
    def __init__(self, config: Config):
        self.config = config
        self.llm_client = LLMClient(
            api_key=config.gemini_api_key,
            model_name=config.model_name
        )
        self.decision_maker = DecisionMaker(config, self.llm_client)
        self.action_executor = ActionExecutor()
        self.result_formatter = ResultFormatter()
        self.state = memory_state
    
    async def run_iteration(self, query: str, session: ClientSession, tools) -> bool:
        """Run a single iteration of the agent loop"""
        try:
            # Get the next action from the decision maker
            response_text = await self.decision_maker.get_next_action(
                query, 
                self.state.iteration_response, 
                self.state.last_response, 
                tools
            )
            
            # Check if we have a final answer
            if response_text.startswith("FINAL_ANSWER:"):
                formatted_answer = self.result_formatter.format_final_answer(response_text)
                print(formatted_answer)
                self.state.iteration_response.append(formatted_answer)
                return False  # End iteration loop on final answer
                
            # Parse function call if available
            if response_text.startswith("FUNCTION_CALL:"):
                function_call = self.decision_maker.parse_action(response_text)
                if not function_call:
                    print("Failed to parse function call")
                    return False
                    
                print(f"\nDEBUG: Parsed function call: {function_call.dict()}")
                
                try:
                    # Execute the tool call with preferences
                    result_str = await self.action_executor.execute_tool(
                        session, 
                        function_call, 
                        tools, 
                        self.state.get_preferences()  # Pass preferences
                    )
                    
                    # Update state with the result
                    iteration_response = self.result_formatter.format_iteration_response(
                        self.state.iteration + 1,
                        function_call.name,
                        result_str
                    )
                    self.state.iteration_response.append(iteration_response)
                    self.state.last_response = result_str
                    
                    return True
                    
                except Exception as e:
                    print(f"DEBUG: Error details: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    self.state.iteration_response.append(f"Error in iteration {self.state.iteration + 1}: {str(e)}")
                    return False
            
            # If we get here, we didn't get a proper response format
            print(f"Invalid response format received: {response_text}")
            return False
                
        except Exception as e:
            print(f"Error in iteration: {e}")
            return False
    
    async def run(self, query: str):
        """Main agent execution loop"""
        self.state.reset()
        print("Starting main execution...")
        
        try:
            # Collect user preferences before starting
            user_preferences = await PreferenceHandler.collect_user_preferences()
            self.state.set_preferences(user_preferences)
            
            # Update the query with the user preferences
            enhanced_query = PreferenceHandler.incorporate_preferences_in_query(query, self.state.get_preferences())

            print(f"""{enhanced_query}""")
            logging.info(enhanced_query)

            # Create a single MCP server connection
            print("Establishing connection to MCP server...")
            server_params = StdioServerParameters(
                command="python3",
                args=["example2-3.py"]
            )

            async with stdio_client(server_params) as (read, write):
                print("Connection established, creating session...")
                async with ClientSession(read, write) as session:
                    print("Session created, initializing...")
                    await session.initialize()
                    
                    # Get available tools
                    print("Requesting tool list...")
                    tools_result = await session.list_tools()
                    tools = tools_result.tools
                    print(f"Successfully retrieved {len(tools)} tools")
                    
                    # Run iterations
                    print("Starting iteration loop...")
                    while self.state.iteration < self.state.max_iterations:
                        print(f"\n--- Iteration {self.state.iteration + 1} ---")
                        success = await self.run_iteration(enhanced_query, session, tools)
                        if not success:
                            break
                            
                        logging.info(f"---------------------------------------------")
                        self.state.iteration += 1

        except Exception as e:
            print(f"Error in main execution: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.state.reset()

if __name__ == "__main__":
    load_dotenv()
    config = get_config()
    agent = MCPAgent(config)
    asyncio.run(agent.run("Your query here"))