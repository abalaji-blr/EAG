# example2-3.py - Defines tools and resources for the MCP server

# basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
import math
import sys
import subprocess
import time
import applescript

# instantiate an MCP server client
mcp = FastMCP("Calculator")

# DEFINE TOOLS

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print("CALLED: add(a: int, b: int) -> int:")
    return int(a + b)

@mcp.tool()
def add_list(l: list) -> int:
    """Add all numbers in a list"""
    print("CALLED: add(l: list) -> int:")
    return sum(l)

@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    print("CALLED: subtract(a: int, b: int) -> int:")
    return int(a - b)

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    print("CALLED: multiply(a: int, b: int) -> int:")
    return int(a * b)

@mcp.tool() 
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    print("CALLED: divide(a: int, b: int) -> float:")
    return float(a / b)

@mcp.tool()
def power(a: int, b: int) -> int:
    """Power of two numbers"""
    print("CALLED: power(a: int, b: int) -> int:")
    return int(a ** b)

@mcp.tool()
def sqrt(a: int) -> float:
    """Square root of a number"""
    print("CALLED: sqrt(a: int) -> float:")
    return float(a ** 0.5)

@mcp.tool()
def cbrt(a: int) -> float:
    """Cube root of a number"""
    print("CALLED: cbrt(a: int) -> float:")
    return float(a ** (1/3))

@mcp.tool()
def factorial(a: int) -> int:
    """Factorial of a number"""
    print("CALLED: factorial(a: int) -> int:")
    return int(math.factorial(a))

@mcp.tool()
def log(a: int) -> float:
    """Log of a number"""
    print("CALLED: log(a: int) -> float:")
    return float(math.log(a))

@mcp.tool()
def remainder(a: int, b: int) -> int:
    """Remainder of two numbers division"""
    print("CALLED: remainder(a: int, b: int) -> int:")
    return int(a % b)

@mcp.tool()
def sin(a: int) -> float:
    """Sin of a number"""
    print("CALLED: sin(a: int) -> float:")
    return float(math.sin(a))

@mcp.tool()
def cos(a: int) -> float:
    """Cos of a number"""
    print("CALLED: cos(a: int) -> float:")
    return float(math.cos(a))

@mcp.tool()
def tan(a: int) -> float:
    """Tan of a number"""
    print("CALLED: tan(a: int) -> float:")
    return float(math.tan(a))

@mcp.tool()
def mine(a: int, b: int) -> int:
    """Special mining tool"""
    print("CALLED: mine(a: int, b: int) -> int:")
    return int(a - b - b)

@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    """Create a thumbnail from an image"""
    print("CALLED: create_thumbnail(image_path: str) -> Image:")
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")

@mcp.tool()
def strings_to_chars_to_int(string: str) -> list[int]:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(string: str) -> list[int]:")
    return [int(ord(char)) for char in string]

@mcp.tool()
def int_list_to_exponential_sum(int_list: list) -> float:
    """Return sum of exponentials of numbers in a list"""
    print("CALLED: int_list_to_exponential_sum(int_list: list) -> float:")
    return sum(math.exp(i) for i in int_list)

@mcp.tool()
def fibonacci_numbers(n: int) -> list:
    """Return the first n Fibonacci Numbers"""
    print("CALLED: fibonacci_numbers(n: int) -> list:")
    if n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:n]

@mcp.tool()
def open_new_pages_document():
    """Opens the Pages application and creates a new document."""
    try:
        script = """
        tell application "Pages"
            activate
            delay 0.5
            make new document
        end tell
        """
        applescript.run(script)
        print("Pages opened and a new document created successfully.")
        return {
            "content": [
                TextContent(
                    type="text",
                    text="Pages opened and a new document created successfully."
                )
            ]
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"An Error while opening Pages: {str(e)}"
                )
            ]
        }

@mcp.tool()
def add_text_to_pages_document(text_to_add: str = "Additional Text"):
    """Adds text to the currently active Pages document."""
    try:
        script = f"""
        tell application "Pages"
            activate
            delay 0.5
            tell application "System Events"
                keystroke "{text_to_add}"
            end tell
        end tell
        """
        applescript.run(script)
        print(f"Text '{text_to_add}' added to Pages document.")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Added text to pages document."
                )
            ]
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"An Error while adding text to Pages: {str(e)}"
                )
            ]
        }

@mcp.tool()
def draw_rectangle_in_existing_pages(width: int = 700, height: int = 700):
    """Draws a rectangle in an already opened Pages document with specified width and height."""
    try:
        check_pages = subprocess.run(["pgrep", "-x", "Pages"], capture_output=True)
        if check_pages.returncode != 0:
            print("Pages is not currently open. Please open Pages manually.")
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Pages is not currently open. Please open Pages manually."
                    )
                ]
            }

        script = f"""
        tell application "Pages" to activate
        delay 0.5

        -- Insert Rectangle
        tell application "System Events"
            tell process "Pages"
                set frontmost to true
                click menu item "Rectangle" of menu "Shape" of menu item "Shape" of menu "Insert" of menu bar 1
            end tell
        end tell

        delay 1

        -- Set dimensions of the new rectangle
        tell application "Pages"
            tell front document
                tell (last shape)
                    set its width to {width}
                    set its height to {height}
                end tell
            end tell
        end tell
        """

        script2 = f"""
        tell application "Pages" to activate
        delay 0.5

        -- Insert Rectangle
        tell application "System Events"
                tell process "Pages"
                        set frontmost to true
                        click menu item "Rectangle" of menu "Shape" of menu item "Shape" of menu "Insert" of menu bar 1
                end tell
        end tell

        delay 1
        """

        applescript.run(script)
        print(f"Rectangle drawn in existing Pages document (width: {width}, height: {height}).")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Rectangle drawn in existing Pages document (width: {width}, height: {height})."
                )
            ]
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"An Error occurred while drawing rectangle in Pages: {str(e)}"
                )
            ]
        }

# DEFINE RESOURCES

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print("CALLED: get_greeting(name: str) -> str:")
    return f"Hello, {name}!"

# DEFINE AVAILABLE PROMPTS

@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
    print("CALLED: review_code(code: str) -> str:")

@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

if __name__ == "__main__":
    print("STARTING")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution