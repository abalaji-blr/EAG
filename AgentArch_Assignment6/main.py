# main.py

import asyncio
from dotenv import load_dotenv

# Local imports
#import m_layermemory
from config import Config, get_config  # Import Config from config.py
from talk2mcp import MCPAgent

async def main():
    # Load environment variables from .env file
    load_dotenv()
        
    # Create configuration and agent
    try:
        config = get_config()
        agent = MCPAgent(config)
            
        query = """Your task consists of four steps using both computation and GUI tools:
Step 1: Convert each character in the string "INDIA" to its ASCII value.
Step 2: For each ASCII value, compute its exponential.
Step 3: Sum all the exponential values.
Step 4: Open a document using Pages
Step 5: Draw a rectangle
Step 6: Paste the exponential value as text inside the rectangle.

Instructions:
- Think through the problem step-by-step before responding.
- Use FUNCTION_CALL format for all tool-related actions:
  FUNCTION_CALL: tool_name|param1|param2|...
- Use FINAL_ANSWER only after all calculations are complete and verified:
  FINAL_ANSWER: [result]  # arithmetic
- Only one line should be output at a time—either a FUNCTION_CALL or FINAL_ANSWER.
- Add an inline comment (e.g., # arithmetic, # gui) to identify the reasoning or action type.
- If a GUI tool fails or is unavailable, skip that step and continue.
- Do not include any explanations or text beyond the required output format.
"""
        await agent.run(query)
            
    except Exception as e:
        print(f"Error in main function: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

