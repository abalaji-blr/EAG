# Session9 Assignment

## Objective:
Start with the code shared. Your task is

1.Fix an "error" in the framework, which will not allow you to run other queries shared in "agent.py"
2. Write 10 Heuristics that run on the query and results. Think of "removing banned words", etc.
3. Index your Past Historical Conversation and provide it to Your Agent. Do this very smartly, a lot of scores for this. 
4. decision_prompt_conservative.txt has 729 words. Reduce it to less than 300 without breaking performance. 

## Submission
1. The error was for the queries, the tool always gets into FURTHER_PROCESSING_REQUIRED. So, the fix is in loop.py,
   along with the user_input provide **user_input_override**. This will help in multi step iterative processing.
   
