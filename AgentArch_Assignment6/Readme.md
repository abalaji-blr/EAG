# AI Agentic Architecture 

## Objective: 
* Refactor the MCP project code and move its logic into its respective AI agentic architecture (Perception, memory, decision making and action layers) files.
* Collect the user preferences before the agentic flow.

## Refactoring
The core part of the Agentic Framework is the following layers:
* **Perception Layer** - Handles all the input and output formatting of data.
* **Decision Layer** - Reasoning and Planning
* **Memory Layer** - Short-term scratchpads / Long-term memory/ vector databases.
* **Action Layer** - API Calls / Run a Python script, etc.

The **orchestration layer** interacts and manages the flow between the layers mentioned above, tools, etc.

In this case:
* [Perception Layer](./p_layer.py) - Uses **Pydantic** to handle the input and output formatting.
```
    def from_mcp_tool(cls, tool):
    def format_tools_description(tools) -> str:
    def create_system_prompt(tools_description: str) -> str:
    def extract_action(response_text: str) -> str:
    def format_tool_result(result, numeric_precision: Optional[str] = None) -> str:
    def format_iteration_response(iteration: int, function_name: str, result_str: str) -> str:
    def format_final_answer(response_text: str) -> str:
    async def prepare_function_arguments(function_call, tools) -> Dict[str, Any]:
    async def collect_user_preferences() -> Dict[str, str]:
    def incorporate_preferences_in_query(query: str, preferences: dict) -> str:
    def apply_preferences(function_call, preferences: dict):
```
* [Decision layer](./d_layer.py) - Reasoning and Planning the next steps.
```
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
    async def generate_with_timeout(self, prompt: str, timeout: int = 10):
    async def get_next_action(self, query: str, iteration_responses: List[str], last_response: Optional[str], tools) -> str:
```
* [Memory Layer](./m_layer.py) - Short term memory
```
    iteration_response: List[str] = Field(default_factory=list)
        default_factory=dict,
    def validate_preferences(cls, v):
    def get_preferences(self) -> Dict[str, str]:
    def set_preferences(self, preferences: Dict[str, str]):
    def reset(self):
```
* [Action Layer](./act_layer.py) - invoke mcp server provided services.
```
async def execute_tool(self, session: ClientSession, function_call: FunctionCall, tools, preferences: Dict[str, str]) -> str:
```
## Handling User Preferences

The second part of the assignment was to collect the user preferences before the agentic flow and handle them.

```
=== Please set your preferences before we begin ===

ASCII Output Format:
1. Comma-separated
2. Array notation
3. Individual lines
Enter your preference (number): 1

Numeric Precision:
1. 2 decimal places
2. 4 decimal places
3. Scientific notation
Enter your preference (number): 2

Rectangle Size:
1. Small (100x100)
2. Medium (200x100)
3. Large (300x200)
Enter your preference (number): 3

Text Style:
1. Default
2. Bold
3. Large font
Enter your preference (number): 1

```

## Output
The complete log file is available [here](./log.log).

## Demo

[![Watch the Demo](https://img.youtube.com/vi/w_8DQ9sAF84/1.jpg)](https://youtu.be/w_8DQ9sAF84)

---

