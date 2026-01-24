# Autonomous Self-Healing Coding Agent

This project implements an autonomous AI agent capable of generating Python code, executing it, and automatically fixing errors without human intervention. It utilizes a state machine architecture to create a feedback loop between the Large Language Model (LLM) and the Python runtime environment.

The system is designed to improve code generation reliability by allowing the model to "see" its own errors (such as syntax errors or failed unit tests) and attempt to correct them iteratively.

## Project Overview

Standard code generation models often fail when they produce code that looks correct but contains subtle bugs. This project solves that problem by wrapping the model in a "Reflexion" loop.

**Key Architecture:**
1.  **Coder Node:** An LLM (Qwen-2.5-Coder-7B) generates a Python function based on a prompt.
2.  **Executor Node:** The system executes the generated code against rigorous unit tests in a secure sandbox.
3.  **Reflexion Loop:** If the code fails, the error message (stderr) is captured and fed back to the Coder Node. The model analyzes the error and regenerates the code.

This architecture transforms a static generation process into a dynamic, self-correcting workflow.

## Performance & Validation

We validated this agent against the **HumanEval Benchmark**, the industry standard for evaluating code generation models.

### Results
*   **Base Model Performance:** The Qwen2.5-Coder-7B model typically achieves a pass rate of approximately **61%** on HumanEval (0-shot), as referenced in recent research papers (e.g., [ArXiv:2409.12186](https://arxiv.org/pdf/2409.12186)).
*   **Agent Performance:** By implementing the self-healing loop, this agent achieved a pass rate of **89.0%** on the same benchmark.

**Evidence:**
You can view the full execution logs, methodology, and verified results in this Kaggle Notebook:
[View Benchmark Results on Kaggle](https://www.kaggle.com/code/shamsccs/humaneval-grade-ai-agent-kaggle-version?scriptVersionId=293582845)

This significant improvement (from ~61% to 89%) demonstrates the power of agentic workflows over simple prompting.

## Technical Architecture

The codebase is modular and designed for production deployment.

### File Structure
*   `src/agent.py`: Defines the state machine graph using LangGraph. This manages the flow between writing code and testing it.
*   `src/nodes.py`: Contains the specific logic for the Coder (LLM interaction) and Executor (Python subprocess handling) nodes.
*   `tests/benchmark.py`: A script to run the agent against the HumanEval dataset and calculate the final pass rate.
*   `Dockerfile`: Configuration for containerizing the application.
*   `.github/workflows`: Automation pipelines for Continuous Integration.

## Automation & CI/CD

To ensure the agent remains reliable, we implemented a robust pipeline:

### 1. Continuous Integration (GitHub Actions)
Every time code is pushed to the repository, a GitHub Actions workflow is triggered. This workflow:
*   Sets up a Python environment.
*   Installs dependencies (LangChain, Ollama).
*   Runs a subset of the HumanEval benchmark (5 problems) to ensure the agent's logic is fundamentally sound.
*   Fails the deployment if the success rate drops below a quality threshold (80%).

### 2. MLOps (MLflow)
We use MLflow to track every experiment. Each run logs:
*   The prompt used.
*   The number of retries required to solve a problem.
*   The final success/failure status.
This allows us to analyze whether changes to the system prompt improve or degrade performance over time.

## Installation and Usage

### Prerequisites
*   Python 3.9 or higher
*   Docker (optional, for sandboxed execution)
*   Ollama (must be installed locally to serve the LLM)

### Running Locally
1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Ensure Ollama is running:**
    ```bash
    ollama serve
    ```
    (In a separate terminal, pull the model: `ollama pull qwen2.5-coder:7b`)

3.  **Run the benchmark:**
    ```bash
    python tests/benchmark.py
    ```

### Running with Docker
We provide a Docker image that encapsulates the entire environment, including the LLM server and the testing framework.

1.  **Build the image:**
    ```bash
    docker build -t self-healing-agent .
    ```

2.  **Run the container:**
    *   *Note: Running LLMs requires significant resources. GPU passthrough is recommended on Linux.*
    ```bash
    docker run -it self-healing-agent
    ```

This container will automatically start the Ollama server, download the model, and execute the benchmark suite, printing the results to your console.
