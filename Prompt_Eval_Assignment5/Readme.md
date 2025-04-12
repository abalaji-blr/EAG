# Prompt Evaluation

**Objective**: 

Redo the MCP assignment (#4), evaluate the prompts using the prompt evaluator, and modify the code as required.

Click the following link for the [prompt evaluator](./prompt_of_prompts.md) using any LLM.

---
## Demo

[![Watch the Demo](https://img.youtube.com/vi/a31ZPl43ZWY/0.jpg)](https://www.youtube.com/watch?v=a31ZPl43ZWY)


---

## Prompts
* **Original System Prompt:**
```
system_prompt = f"""You are a math agent solving problems in iterations. You have access to various mathematical tools.

Available tools:
{tools_description}

You must respond with EXACTLY ONE line in one of these formats (no additional text):
1. For function calls:
   FUNCTION_CALL: function_name|param1|param2|...
   
2. For final answers:
   FINAL_ANSWER: [number]

Important:
- When a function returns multiple values, you need to process all of them
- Only give FINAL_ANSWER when you have completed all necessary calculations
- Do not repeat function calls with the same parameters

Examples:
- FUNCTION_CALL: add|5|3
- FUNCTION_CALL: strings_to_chars_to_int|INDIA
- FINAL_ANSWER: [42]

DO NOT include any explanations or additional text.
Your entire response should be a single line starting with either FUNCTION_CALL: or FINAL_ANSWER:"""
```


* **Modified System Prompt**:
```
system_prompt = f"""You are a math agent solving problems in iterations using internal reasoning and external tools.

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
- FUNCTION_CALL: add|5|3  # 'arithmetic'
- FUNCTION_CALL: strings_to_chars_to_int|INDIA  # 'string'
- FINAL_ANSWER: [42]  # 'arithmetic'

DO NOT include any explanations or additional text.
Your entire response should be a single line starting with either FUNCTION_CALL: or FINAL_ANSWER:"""
```

* **LLM Evaluation Result:**
```
{
  "explicit_reasoning": true,
  "structured_output": true,
  "tool_separation": true,
  "conversation_loop": true,
  "instructional_framing": true,
  "internal_self_checks": true,
  "reasoning_type_awareness": true,
  "fallbacks": true,
  "overall_clarity": "Excellent prompt—fully aligned with best practices for tool-assisted reasoning. Structured, self-aware, and robust against uncertainty."
}
```
---

* **Original Query**:
```
query = """Find the ASCII values of characters in INDIA and then return sum of exponentials of those values.
Open a new doucment using Pages, draw a rectangle on that and finally paste the resulted ASCII values as text.
"""
```
* **Modified Query**:
```
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
```
* **LLM Evaluation Result:**
```
 {
  "explicit_reasoning": true,
  "structured_output": true,
  "tool_separation": true,
  "conversation_loop": true,
  "instructional_framing": true,
  "internal_self_checks": true,
  "reasoning_type_awareness": true,
  "fallbacks": true,
  "overall_clarity": "Very clear, step-by-step task prompt with structured output and strong error handling. Well suited for multi-modal reasoning with both math and GUI tools."
}
```
