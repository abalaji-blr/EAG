# Session9 Assignment

## Objective:
Start with the code shared. Your task is

1.Fix an "error" in the framework, which will not allow you to run other queries shared in "agent.py"
2. Write 10 Heuristics that run on the query and results. Think of "removing banned words", etc.
3. Index your Past Historical Conversation and provide it to Your Agent. Do this very smartly, a lot of scores for this. 
4. decision_prompt_conservative.txt has 729 words. Reduce it to less than 300 without breaking performance. 

## Submission
1. The error was for the queries - the tool always gets into FURTHER_PROCESSING_REQUIRED. So, the fix is in loop.py,
   along with the user_input provide **user_input_override**. This will help in multi-step iterative processing.
   The following are the outputs for the queries.
   1. Find the ASCII values of characters in INDIA and then return sum of exponentials of those values.
      The Complete [log file is available here](./log/q1.log).
      ```
      Final Answer: 7.599822246093079e+33
      ```
   2. How much Anmol singh paid for his DLF apartment via Capbridge?
      The complete [log file is available here](./log/q2.log)
      ```
      [plan] import json
      async def solve():
          # FUNCTION_CALL: 1
          input = {"input": {"query": "Anmol Singh DLF apartment Capbridge payment", "max_results": 5} }
          result = await mcp.call_tool('duckduckgo_search_results', input)
          search_results = json.loads(result.content[0].text)["result"]
          if "42.94 crore" in search_results:
              return f"FINAL_ANSWER: 42.94 crore"
          else:
              return f"FURTHER_PROCESSING_REQUIRED: {search_results}"
      [loop] Detected solve() plan — running sandboxed...
      [action] 🔍 Entered run_python_sandbox()
      [05/28/25 17:46:23] INFO     Processing request of type CallToolRequest                                                                                                                        server.py:551
      [05/28/25 17:46:24] INFO     HTTP Request: POST https://html.duckduckgo.com/html "HTTP/1.1 200 OK"                                                                                           _client.py:1740
      
      💡 Final Answer: 42.94 crore
      ```
   4. What do you know about Don Tapscott and Anthony Williams?
   5. What is the relationship between Gensol and Go-Auto?
   6. which course are we teaching on Canvas LMS? "/Users/abalaji/mydata/EAG/Session9/S9/documents/How to use Canvas LMS.pdf"
   7. Summarize this page: https://theschoolof.ai/
   8. What is the log value of the amount that Anmol singh paid for his DLF apartment via Capbridge? 

   9. Find the sum of all even number in the fibonacci sequence up to the 10th term.
   10. What is the current year and how many days are in it? 
   11. Take the first paragraph of the School of AI website, count the frequency of each word, and identify the three most common words that       are longer than 4 letters. www.theschoolof.ai

   
