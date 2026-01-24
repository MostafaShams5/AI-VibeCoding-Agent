# Self-Healing Autonomous Coding Agent

An LLM-based agent that writes Python code, executes it against unit tests, and autonomously fixes errors using a feedback loop.

## Architecture
- **LangGraph:** Orchestrates the state machine (Coder -> Executor -> Reflexion).
- **Ollama:** Local inference engine running Qwen-2.5-Coder.
- **MLflow:** Tracks experiment metrics (Pass@k, Retry Rate).
- **Docker:** Provides sandboxed execution environment.

## Installation
```bash
pip install -r requirements.txt
