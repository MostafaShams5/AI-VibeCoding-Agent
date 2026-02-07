import os
from typing import TypedDict, Optional
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from src.nodes import coder_node, executor_node

MODEL_NAME = os.getenv("LLM_MODEL", "qwen2.5-coder:7b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

class AgentState(TypedDict):
    task_id: str
    prompt: str      
    test_code: str   
    entry_point: str 
    code: str        
    error: Optional[str]
    iteration: int
    success: bool

def build_agent():
    # Allow connecting to remote Ollama (essential for Docker Compose)
    llm = ChatOllama(
        model=MODEL_NAME, 
        temperature=0,
        base_url=OLLAMA_BASE_URL
    )

    def coder_wrapper(state):
        return coder_node(state, llm)

    def should_continue(state):
        max_retries = int(os.getenv("MAX_RETRIES", 2))
        if state["success"]: return "end"
        if state["iteration"] > max_retries: return "end"
        return "retry"

    workflow = StateGraph(AgentState)
    workflow.add_node("coder", coder_wrapper)
    workflow.add_node("executor", executor_node)

    workflow.set_entry_point("coder")
    workflow.add_edge("coder", "executor")
    workflow.add_conditional_edges("executor", should_continue, {"end": END, "retry": "coder"})
    
    return workflow.compile()
