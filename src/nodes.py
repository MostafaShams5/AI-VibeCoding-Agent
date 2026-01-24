import subprocess
import tempfile
import os
import sys
from langchain_core.messages import SystemMessage, HumanMessage
from src.utils import extract_code

def coder_node(state, llm):
    print(f"   Writing Code (Attempt {state['iteration'] + 1})...")
    
    system_prompt = """You are an expert Python programmer.
    1. You will be given a function signature and a docstring.
    2. Complete the function implementation.
    3. Use standard Python libraries only.
    4. Output ONLY the code.
    """
    
    if state.get("error"):
        user_msg = f"""
        The code you wrote failed the unit tests.
        FUNCTION PROMPT: {state['prompt']}
        YOUR PREVIOUS CODE: {state['code']}
        ERROR MESSAGE: {state['error']}
        Please rewrite the code to fix this error.
        """
    else:
        user_msg = f"""
        Complete the following Python function. 
        IMPORTANT: Your output must start with the function definition provided below.
        {state['prompt']}
        """

    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_msg)])
    code = extract_code(response.content)
    return {"code": code, "iteration": state["iteration"]}

def executor_node(state):
    print(f"   Running Tests...")
    
    full_script = f"""
from typing import List, Tuple, Dict, Any, Optional
import math

# --- GENERATED SOLUTION ---
{state['code']}

# --- HUMAN EVAL TEST HARNESS ---
{state['test_code']}

# --- RUN CHECK ---
try:
    check({state['entry_point']})
    print("TEST_PASSED")
except AssertionError as e:
    print(f"TEST_FAILED: Assertion Error")
    raise e
except Exception as e:
    print(f"TEST_FAILED: {{e}}")
    raise e
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py', encoding='utf-8') as f:
        f.write(full_script)
        script_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True, text=True, timeout=5
        )
        
        output = result.stdout + result.stderr
        
        if "TEST_PASSED" in output:
            print("    Tests Passed")
            return {"error": None, "success": True, "iteration": state["iteration"] + 1}
        else:
            error_msg = result.stderr if result.stderr else output
            error_msg = error_msg[-2000:] 
            print(f"    Tests Failed")
            return {"error": error_msg, "success": False, "iteration": state["iteration"] + 1}

    except Exception as e:
        return {"error": str(e), "success": False, "iteration": state["iteration"] + 1}
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)
