# Assignment 4: Model Context Protocol (MCP)

## Objective:
The goal is to add certain utilities on the MCP server side, and have the orchestrator direct the LLM (Gemini 2.0 Flash) to use these tools via the MCP client.
 
## Utilities introduced at MCP Server side
Please take a look at file [example2-3.py](./example2-3.py) for the following utilities on the server side.
 * open_new_pages_document
 * draw_rectangle_in_existing_pages
 * add_text_to_pages_document

## Orchestrator
Refer to file [talk2cmp-2.py](./talk2cmp-2.py) for the Orchestractor which directs the LLM to use newly introduced server utilities through MCP client.

## How to Run
$ python3 ./talk2mcp-2.py

## Output / Log file
```
Starting main execution...
Establishing connection to MCP server...
Connection established, creating session...
Session created, initializing...
Requesting tool list...
Processing request of type ListToolsRequest
Successfully retrieved 22 tools
Creating system prompt...
Number of tools: 22
Added description for tool: 1. add(a: integer, b: integer) - Add two numbers
Added description for tool: 2. add_list(l: array) - Add all numbers in a list
Added description for tool: 3. subtract(a: integer, b: integer) - Subtract two numbers
Added description for tool: 4. multiply(a: integer, b: integer) - Multiply two numbers
Added description for tool: 5. divide(a: integer, b: integer) - Divide two numbers
Added description for tool: 6. power(a: integer, b: integer) - Power of two numbers
Added description for tool: 7. sqrt(a: integer) - Square root of a number
Added description for tool: 8. cbrt(a: integer) - Cube root of a number
Added description for tool: 9. factorial(a: integer) - factorial of a number
Added description for tool: 10. log(a: integer) - log of a number
Added description for tool: 11. remainder(a: integer, b: integer) - remainder of two numbers divison
Added description for tool: 12. sin(a: integer) - sin of a number
Added description for tool: 13. cos(a: integer) - cos of a number
Added description for tool: 14. tan(a: integer) - tan of a number
Added description for tool: 15. mine(a: integer, b: integer) - special mining tool
Added description for tool: 16. create_thumbnail(image_path: string) - Create a thumbnail from an image
Added description for tool: 17. strings_to_chars_to_int(string: string) - Return the ASCII values of the characters in a word
Added description for tool: 18. int_list_to_exponential_sum(int_list: array) - Return sum of exponentials of numbers in a list
Added description for tool: 19. fibonacci_numbers(n: integer) - Return the first n Fibonacci Numbers
Added description for tool: 20. open_new_pages_document() - 
Opens the Pages application and creates a new document.

Added description for tool: 21. add_text_to_pages_document(text_to_add: string) - 
Adds text to the currently active Pages document.

Args:
    text_to_add: The text to insert into the Pages document.

Added description for tool: 22. draw_rectangle_in_existing_pages(width: string, height: string) - 
Draws a rectangle in an already opened Pages document with specified width and height.

Args:
    width: The width of the rectangle in points.
    height: The height of the rectangle in points.

Successfully created tools description
Created system prompt...
Starting iteration loop...

--- Iteration 1 ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
LLM Response: FUNCTION_CALL: strings_to_chars_to_int|INDIA
--- Iteration 2 ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
LLM Response: FUNCTION_CALL: int_list_to_exponential_sum|[73, 78, 68, 73, 65]
--- Iteration 3 ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
LLM Response: FUNCTION_CALL: open_new_pages_document
--- Iteration 4 ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
LLM Response: FUNCTION_CALL: draw_rectangle_in_existing_pages|100|50
--- Iteration 5 ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
LLM Response: FUNCTION_CALL: add_text_to_pages_document|7.59982224609308e+33

```
