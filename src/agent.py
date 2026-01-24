from typing import TypedDict, Optional
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from src.nodes import coder_node, executor_node

class AgentState(TypedDict):
    task_id: str
    prompt: str      
    test_code: str   
    entry_point: str 
    code: str        
    error: Optional[str]
    iteration: int
    success: bool

def build_agent(model_name="qwen2.5-coder:7b", max_retries=2):
    llm = ChatOllama(model=model_name, temperature=0)

    def coder_wrapper(state):
        return coder_node(state, llm)

    def should_continue(state):
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
