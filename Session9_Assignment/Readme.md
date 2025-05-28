# Session9 Assignment

## Objective:
Start with the code shared. Your task is: <br>
   1. Fix an "error" in the framework, which will not allow you to run other queries shared in "agent.py" <br>
   2. Write 10 Heuristics that run on the query and results. Think of "removing banned words", etc. <br>
   3. Index your Past Historical Conversation and provide it to Your Agent. Do this very smartly, a lot of scores for this. <br>
   4. decision_prompt_conservative.txt has 729 words. Reduce it to less than 300 without breaking performance. <br>

## Submission
### Bug Fix
1. The error was for the queries - the tool always gets into FURTHER_PROCESSING_REQUIRED. So, the fix is in loop.py,
   along with the user_input provide **user_input_override**. This will help in multi-step iterative processing.
   
   The code changes are [available here](./core/loop.py). <br>
   
   The following are the outputs for the queries. <br>
   1. Find the ASCII values of characters in INDIA and then return sum of exponentials of those values.<br>
      The Complete [log file is available here](./log/q1.log).
      ```
      Final Answer: 7.599822246093079e+33
      ```
   2. How much Anmol singh paid for his DLF apartment via Capbridge? <br>
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
   3. What do you know about Don Tapscott and Anthony Williams? <br>
      The complete [log file is available here](./log/q3.log).
      ```
      [loop] Detected solve() plan — running sandboxed...
      [action] 🔍 Entered run_python_sandbox()
      [05/28/25 17:59:27] INFO     Processing request of type CallToolRequest                                                   
      [05/28/25 17:59:28] INFO     HTTP Request: POST https://html.duckduckgo.com/html "HTTP/1.1 200 OK"                                                                                            
      Final Answer: Don Tapscott and Anthony Williams are best known for co-authoring the book Wikinomics: How Mass Collaboration Changes    Everything.
      ```
   4. What is the relationship between Gensol and Go-Auto? <br>
      The Complete [log file is available here](./log/q4.log).
      
      ```
      [loop] Detected solve() plan — running sandboxed...
      [action] 🔍 Entered run_python_sandbox()
      [05/28/25 18:00:48] INFO     Processing request of type CallToolRequest                                                                                                                        server.py:551
      [05/28/25 18:00:50] INFO     HTTP Request: POST https://html.duckduckgo.com/html "HTTP/1.1 200 OK"                                                                                           _client.py:1740

      💡 Final Answer: Gensol and Go-Auto are related through business dealings involving the purchase of EVs. Go-Auto supplied EVs to Gensol. There are also indications of financial irregularities and funds moving between the two companies.
      ```
   5. which course are we teaching on Canvas LMS? "/Users/abalaji/mydata/EAG/Session9/S9/documents/How to use Canvas LMS.pdf" <br>
      The Complete [log file is available here](./log/q5.log).<br>

   6. Summarize this page: https://theschoolof.ai/ <br>
      The Complete [log file is available here](./log/q6.log).<br>
      ```
      [plan] import json
      async def solve():
          # FUNCTION_CALL: 1
          """Summarize this page: https://theschoolof.ai/"""
          return f"FINAL_ANSWER: This document is a markdown representation of the \"The School of AI\" website. It provides information on various AI/ML courses offered by TSAI, including Agentic AI (EAG), Full-Stack AI (ERA), and MLOps (EMLO). It outlines the curriculum, key features, and schedules for these courses, also including student and instructor feedback."
      [loop] Detected solve() plan — running sandboxed...
      [action] 🔍 Entered run_python_sandbox()
      
      💡 Final Answer: This document is a markdown representation of the "The School of AI" website. It provides information on various AI/ML courses offered by TSAI, including Agentic AI (EAG), Full-Stack AI (ERA), and MLOps (EMLO). It outlines the curriculum, key features, and schedules for these courses, also including student and instructor feedback.

      ```
   7. What is the log value of the amount that Anmol singh paid for his DLF apartment via Capbridge? <br>
       The Complete [log file is available here](./log/q7.log).<br>
      
      ```
      [plan] import json
      import math
      
      async def solve():
          # FUNCTION_CALL: 1
          """Extract the amount Anmol Singh paid for his DLF apartment. The search results indicate the amount is 42.94 crore. We need to calculate the log value of this amount. First, convert crore to a numerical value. 1 crore = 10 million = 10,000,000. Therefore, 42.94 crore = 42.94 * 10,000,000 = 429,400,000. Now, calculate the log value (base 10) of 429,400,000."""
          amount = 429400000
          log_value = math.log10(amount)
          return f"FINAL_ANSWER: {log_value}"
      [loop] Detected solve() plan — running sandboxed...
      [action] 🔍 Entered run_python_sandbox()
      
      💡 Final Answer: 8.63286204010023
      ```

   8. **Find the sum of all even number in the fibonacci sequence up to the 10th term.** <br>
        The Complete [log file is available here](./log/q8.log).<br>
      ```
      [plan] import json
      async def solve():
          # FUNCTION_CALL: 1
          """Generate first n Fibonacci numbers. Usage: input={"input": {"n": 10}}"""
          input = {"input": {"n": 10}}
          result = await mcp.call_tool('fibonacci_numbers', input)
          fibonacci_numbers = json.loads(result.content[0].text)["result"]
          
          even_sum = 0
          for number in fibonacci_numbers:
              if number % 2 == 0:
                  even_sum += number
                  
          return f"FINAL_ANSWER: {even_sum}"
      [loop] Detected solve() plan — running sandboxed...
      [action] 🔍 Entered run_python_sandbox()
      [05/28/25 18:15:43] INFO     Processing request of type CallToolRequest                                                                                                                        server.py:551
      
      💡 Final Answer: 44
      ```
      
   9. **What is the current year and how many days are in it?** <br>
       The Complete [log file is available here](./log/q9.log).<br>
      ```
      [plan] import json
      import datetime
      
      async def solve():
          current_year = datetime.datetime.now().year
          if (current_year % 4 == 0 and current_year % 100 != 0) or (current_year % 400 == 0):
              days_in_year = 366
          else:
              days_in_year = 365
          return f"FINAL_ANSWER: The current year is {current_year} and it has {days_in_year} days."
      [loop] Detected solve() plan — running sandboxed...
      [action] 🔍 Entered run_python_sandbox()
      
      💡 Final Answer: The current year is 2025 and it has 365 days.
      ```
   10. **Take the first paragraph of the School of AI website, count the frequency of each word, and identify the three most common words that       are longer than 4 letters. www.theschoolof.ai** <br>
        The Complete [log file is available here](./log/q10.log).<br>
      ```
      | Session 15: Introduction to Browser Automation Tools - Surveys Selenium, Puppeteer, and Playwright, focusing on bridging them with agentic frameworks. |
      | Session 16: Intelligent Goal Interpretation - Explores designing agents that align web automation tasks with user-defined objectives. |
      | Session 17: Multi-Agent Systems and Collaboration - Demonstrates how multiple agents can coordinate across different browser tasks or subtasks. |
      | Session 18: Managing Uncertainty and Error Correction - Equips you with strategies for handling dynamic web structures, unexpected failures, and retries. |
      | Session 19: Advanced Task Orchestration - Guides you through synchronizing tasks, tabs, and user interactions in real time. |
      | Session 20: Capstone – (Probably) Autonomous Browser Assistant - Challenges you to design, build, and demo a fully functioning browser-based AI with advanced features. |"""
          
          # Clean the text
          text = re.sub(r'[^\w\s]', '', text).lower()
          
          # Split into words and filter out words with length <= 4
          words = [word for word in text.split() if len(word) > 4]
          
          # Count word frequencies
          word_counts = Counter(words)
          
          # Get the three most common words
          most_common_words = word_counts.most_common(3)
          
          return f"FINAL_ANSWER: {most_common_words}"
      [loop] Detected solve() plan — running sandboxed...
      [action] 🔍 Entered run_python_sandbox()
      
      💡 Final Answer: [('session', 21), ('agents', 14), ('students', 6)]

      ```

   
