# modules/loop.py

import asyncio
from modules.perception import run_perception
from modules.decision import generate_plan
from modules.action import run_python_sandbox
from modules.model_manager import ModelManager
from core.session import MultiMCP
from core.strategy import select_decision_prompt_path
from core.context import AgentContext
from modules.tools import summarize_tools
import re
import urllib.parse

try:
    from agent import log
except ImportError:
    import datetime
    def log(stage: str, msg: str):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] [{stage}] {msg}")

def check_content_length(text: str, min_length: int = 10, max_length: int = 30000) -> bool:
    """Ensure content is neither too short nor too long"""
    return min_length <= len(text) <= max_length

def filter_banned_words(text: str, banned_words: set) -> str:
    """Remove or replace banned/inappropriate words"""
    words = text.split()
    filtered_words = [word if word.lower() not in banned_words else "[REDACTED]" for word in words]
    return " ".join(filtered_words)

def validate_url(url: str) -> bool:
    """Check if URL is safe and follows proper format"""
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except:
        return False

def classify_query_intent(query: str) -> str:
    """Classify query into categories like: mathematical, informational, financial, educational"""
    # Use existing intent classification from perception.py
    return intent

def calculate_relevance_score(query: str, result: str) -> float:
    """Calculate how relevant the result is to the original query"""
    # Use semantic similarity or keyword matching
    score = 0.5
    return score

def check_rate_limit(user_id: str, query_type: str) -> bool:
    """Ensure user isn't making too many requests"""
    # Use existing RateLimiter class logic
    is_allowed = True
    return is_allowed

def validate_content_type(content: str, expected_type: str) -> bool:
    """Ensure content matches expected type (text, number, URL, etc.)"""
    if expected_type == "number":
        return content.replace(".", "").isdigit()
    elif expected_type == "url":
        return validate_url(content)
    return True

def filter_sensitive_info(text: str) -> str:
    """Remove or mask sensitive information like phone numbers, emails, etc."""
    # Remove phone numbers
    #text = re.sub(r'\d{3}[-.]?\d{3}[-.]?\d{4}', '[PHONE]', text)
    # Remove emails
    text = re.sub(r'[\w\.-]+@[\w\.-]+', '[EMAIL]', text)
    return text

def check_query_complexity(query: str) -> int:
    """Rate query complexity to determine processing approach"""
    # Count number of operations/conditions
    complexity = 0
    if "and" in query.lower(): complexity += 1
    if "or" in query.lower(): complexity += 1
    if "not" in query.lower(): complexity += 1
    return complexity

def check_source_consistency(sources: list) -> float:
    """
    Check if multiple sources agree on the information.
    Returns a score between 0 and 1 indicating how consistent the sources are.
    """
    if not sources or len(sources) == 1:
        return 1.0  # Single source or no sources is considered fully consistent
        
    # Extract key information from each source
    source_info = []
    for source in sources:
        # Extract main points or key facts from the source
        # This is a simplified version - you might want to use more sophisticated extraction
        key_points = set(source.lower().split())
        source_info.append(key_points)
    
    # Calculate pairwise similarity between sources
    total_similarity = 0
    comparisons = 0
    
    for i in range(len(source_info)):
        for j in range(i + 1, len(source_info)):
            set1 = source_info[i]
            set2 = source_info[j]
            
            # Calculate Jaccard similarity
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            
            if union > 0:  # Avoid division by zero
                similarity = intersection / union
                total_similarity += similarity
                comparisons += 1
    
    # Return average similarity if we made any comparisons
    return total_similarity / comparisons if comparisons > 0 else 0.0

def calculate_confidence_score(result: str, sources: list) -> float:
    """Calculate confidence in the result based on sources and consistency"""
    # Check number of sources
    source_count = len(sources)
    # Check if sources agree
    consistency = check_source_consistency(sources)
    return (source_count * 0.3) + (consistency * 0.7)

class AgentLoop:
    def __init__(self, context: AgentContext):
        self.context = context
        self.mcp = self.context.dispatcher
        self.model = ModelManager()
        self.banned_words = set(['inappropriate', 'banned', 'words'])  # Add your banned words here

    async def apply_heuristics(self, query: str, result: str = None) -> tuple[bool, str]:
        """Apply all heuristics to query and result if provided"""
        # Apply query heuristics
        if not check_content_length(query):
            return False, "Query length is outside acceptable range"
            
        query = filter_banned_words(query, self.banned_words)
        
        if not validate_content_type(query, "text"):
            return False, "Invalid query content type"
            
        complexity = check_query_complexity(query)
        if complexity > 3:  # Adjust threshold as needed
            return False, "Query is too complex"
            
        # Apply result heuristics if result is provided
        if result:
            if not check_content_length(result):
                return False, "Result length is outside acceptable range"
                
            result = filter_sensitive_info(result)
            result = filter_banned_words(result, self.banned_words)
            
            if not validate_content_type(result, "text"):
                return False, "Invalid result content type"
                
            relevance = calculate_relevance_score(query, result)
            if relevance < 0.5:  # Adjust threshold as needed
                return False, "Result is not relevant enough to the query"
        
        return True, result if result else query

    async def run(self):
        max_steps = self.context.agent_profile.strategy.max_steps

        for step in range(max_steps):
            print(f"🔁 Step {step+1}/{max_steps} starting...")
            self.context.step = step
            lifelines_left = self.context.agent_profile.strategy.max_lifelines_per_step

            while lifelines_left >= 0:
                # === Perception ===
                user_input_override = getattr(self.context, "user_input_override", None)
                current_input = user_input_override or self.context.user_input
                
                # Apply heuristics to input
                is_valid, processed_input = await self.apply_heuristics(current_input)
                if not is_valid:
                    log("loop", f"⚠️ Input validation failed: {processed_input}")
                    break
                
                perception = await run_perception(context=self.context, user_input=processed_input)

                print(f"[perception] {perception}")

                selected_servers = perception.selected_servers
                selected_tools = self.mcp.get_tools_from_servers(selected_servers)
                if not selected_tools:
                    log("loop", "⚠️ No tools selected — aborting step.")
                    break

                # === Planning ===
                tool_descriptions = summarize_tools(selected_tools)
                prompt_path = select_decision_prompt_path(
                    planning_mode=self.context.agent_profile.strategy.planning_mode,
                    exploration_mode=self.context.agent_profile.strategy.exploration_mode,
                )

                plan = await generate_plan(
                    user_input=processed_input,
                    perception=perception,
                    memory_items=self.context.memory.get_session_items(),
                    tool_descriptions=tool_descriptions,
                    prompt_path=prompt_path,
                    step_num=step + 1,
                    max_steps=max_steps,
                )
                print(f"[plan] {plan}")

                # === Execution ===
                if re.search(r"^\s*(async\s+)?def\s+solve\s*\(", plan, re.MULTILINE):
                    print("[loop] Detected solve() plan — running sandboxed...")

                    self.context.log_subtask(tool_name="solve_sandbox", status="pending")
                    result = await run_python_sandbox(plan, dispatcher=self.mcp)

                    success = False
                    if isinstance(result, str):
                        result = result.strip()
                        if result.startswith("FINAL_ANSWER:"):
                            # Apply heuristics to result
                            is_valid, processed_result = await self.apply_heuristics(current_input, result)
                            if not is_valid:
                                log("loop", f"⚠️ Result validation failed: {processed_result}")
                                lifelines_left -= 1
                                continue
                                
                            success = True
                            self.context.final_answer = processed_result
                            self.context.update_subtask_status("solve_sandbox", "success")
                            self.context.memory.add_tool_output(
                                tool_name="solve_sandbox",
                                tool_args={"plan": plan},
                                tool_result={"result": result},
                                success=True,
                                tags=["sandbox"],
                            )
                            return {"status": "done", "result": self.context.final_answer}
                        elif result.startswith("FURTHER_PROCESSING_REQUIRED:"):
                            content = result.split("FURTHER_PROCESSING_REQUIRED:")[1].strip()
                            self.context.user_input_override  = (
                                f"Original user task: {self.context.user_input}\n\n"
                                f"Your last tool produced this result:\n\n"
                                f"{content}\n\n"
                                f"If this fully answers the task, return:\n"
                                f"FINAL_ANSWER: your answer\n\n"
                                f"Otherwise, return the next FUNCTION_CALL."
                            )
                            log("loop", f"📨 Forwarding intermediate result to next step:\n{self.context.user_input_override}\n\n")
                            log("loop", f"🔁 Continuing based on FURTHER_PROCESSING_REQUIRED — Step {step+1} continues...")
                            break  # Step will continue
                        elif result.startswith("[sandbox error:"):
                            success = False
                            self.context.final_answer = "FINAL_ANSWER: [Execution failed]"
                        else:
                            success = True
                            self.context.final_answer = f"FINAL_ANSWER: {result}"
                    else:
                        self.context.final_answer = f"FINAL_ANSWER: {result}"

                    if success:
                        self.context.update_subtask_status("solve_sandbox", "success")
                    else:
                        self.context.update_subtask_status("solve_sandbox", "failure")

                    self.context.memory.add_tool_output(
                        tool_name="solve_sandbox",
                        tool_args={"plan": plan},
                        tool_result={"result": result},
                        success=success,
                        tags=["sandbox"],
                    )

                    if success and "FURTHER_PROCESSING_REQUIRED:" not in result:
                        return {"status": "done", "result": self.context.final_answer}
                    else:
                        lifelines_left -= 1
                        log("loop", f"🛠 Retrying... Lifelines left: {lifelines_left}")
                        continue
                else:
                    log("loop", f"⚠️ Invalid plan detected — retrying... Lifelines left: {lifelines_left-1}")
                    lifelines_left -= 1
                    continue

        log("loop", "⚠️ Max steps reached without finding final answer.")
        self.context.final_answer = "FINAL_ANSWER: [Max steps reached]"
        return {"status": "done", "result": self.context.final_answer}
