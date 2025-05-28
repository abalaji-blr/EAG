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
   2. How much Anmol singh paid for his DLF apartment via Capbridge? 
   3. What do you know about Don Tapscott and Anthony Williams?
   4. What is the relationship between Gensol and Go-Auto?
   5. which course are we teaching on Canvas LMS? "/Users/abalaji/mydata/EAG/Session9/S9/documents/How to use Canvas LMS.pdf"
   6. Summarize this page: https://theschoolof.ai/
   7. What is the log value of the amount that Anmol singh paid for his DLF apartment via Capbridge? 

   8. Find the sum of all even number in the fibonacci sequence up to the 10th term.
   9. What is the current year and how many days are in it? 
   10. Take the first paragraph of the School of AI website, count the frequency of each word, and identify the three most common words that       are longer than 4 letters. www.theschoolof.ai

   
