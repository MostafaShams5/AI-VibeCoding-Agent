# Autonomous Self-Healing Coding Agent

This project implements an autonomous AI agent capable of generating Python code, executing it, and automatically fixing errors without human intervention. It utilizes a state machine architecture to create a feedback loop between the Large Language Model (LLM) and the Python runtime environment.

The system is designed to improve code generation reliability by allowing the model to "see" its own errors (such as syntax errors or failed unit tests) and attempt to correct them iteratively.

## Project Overview

Standard code generation models often fail when they produce code that looks correct but contains subtle bugs. This project solves that problem by wrapping the model in a "Reflexion" loop.

**Key Architecture:**
1.  **Coder Node:** An LLM (Qwen-2.5-Coder) generates a Python function based on a prompt.
2.  **Executor Node:** The system executes the generated code against rigorous unit tests.
3.  **Reflexion Loop:** If the code fails, the error message (stderr) is captured and fed back to the Coder Node. The model analyzes the error and regenerates the code.

This architecture transforms a static generation process into a dynamic, self-correcting workflow.

## Performance & Validation

We validated this agent against the **HumanEval Benchmark**, the industry standard for evaluating code generation models.

### What is HumanEval?
HumanEval is a rigorous benchmark released by OpenAI consisting of **164 programming problems**. Each problem includes a function signature, docstring, body, and several unit tests. To "pass," a model must generate code that satisfies **all** unit tests for a given problem (Pass@1).

### Our Results
* **Base Model (Verified):** We verified that the raw Qwen2.5-Coder-7B model achieves a pass rate of approximately **61%** on HumanEval (0-shot), which aligns with findings in recent research papers (e.g., [ArXiv:2409.12186](https://arxiv.org/pdf/2409.12186)).
* **Agent Performance:** By implementing the self-healing loop, this agent achieved a pass rate of **89.0%** on the same benchmark.

### Comparison to SOTA LLMs
By implementing an agentic "Reflexion" loop, our local 7B model bridges the gap between open-source and state-of-the-art proprietary models. 

Below is a comparison of our agent against top-tier closed-source models (data sourced from [LLM-Stats](https://llm-stats.com/benchmarks/humaneval?utm_source=chatgpt.com)):

| Rank | Model | Type | Pass@1 (HumanEval) |
| :--- | :--- | :--- | :--- |
| 1 | Claude 3.5 Sonnet | Proprietary | 93.7% |
| 2 | GPT-5 | Proprietary | 93.4% |
| 3 | GPT-4o | Proprietary | 90.2% |
| **4** | **VibeCoding Agent (Ours)** | **Open Source (7B)** | **89.0%** |
| 5 | Claude 3.5 Haiku | Proprietary | 88.1% |
| 6 | GPT-4.5 | Proprietary | 88.0% |
| 7 | Qwen2.5-Coder-7B (Base) | Open Source | 61.6% |

**Key Takeaway:** Our agent, running locally on a standard consumer CPU/GPU, **outperforms GPT-4.5 and Claude 3.5 Haiku**, proving that *Agentic Workflows* > *Raw Parameter Count*.

**Evidence:**
You can view the full execution logs, methodology, and verified results in this Kaggle Notebook:
👉 **[View Benchmark Results on Kaggle](https://www.kaggle.com/code/shamsccs/humaneval-grade-ai-agent-kaggle-version?scriptVersionId=293582845)**

## Technical Architecture

The codebase follows a **Microservices Architecture**, separating the inference engine from the application logic.

### File Structure
* `src/agent.py`: Defines the state machine graph using LangGraph. This manages the flow between writing code and testing it.
* `src/nodes.py`: Contains the specific logic for the Coder (LLM interaction) and Executor (Python subprocess handling) nodes.
* `tests/benchmark.py`: A script to run the agent against the HumanEval dataset and calculate the final pass rate.
* `docker-compose.yml`: Orchestrates the multi-container environment (Agent + Ollama).
* `.github/workflows`: Automation pipelines for Continuous Integration.

## Installation and Usage

### Prerequisites
* Docker & Docker Compose (Recommended)
* *Alternatively:* Python 3.9+ and Ollama installed locally

### Running with Docker (Recommended)
This project uses **Docker Compose** to orchestrate the Agent and the LLM as separate microservices. This ensures modularity and allows for easy scaling.

1.  **Start the Cluster:**
    This command builds the agent and starts the Ollama inference server in a dedicated container.
    ```bash
    docker compose up -d --build
    ```

2.  **Initialize the Model (First Run Only):**
    Since the inference server is fresh, we need to pull the specific model we want to use. We use the **1.5B parameter model** for CPU efficiency during local testing, but you can pull `7b` if you have a GPU.
    ```bash
    docker exec -it ollama_service ollama pull qwen2.5-coder:1.5b
    ```

3.  **Run the Benchmark:**
    Execute the test suite inside the running agent container.
    ```bash
    docker exec -it vibe_agent python tests/benchmark.py
    ```

## Configuration

The agent is designed to be model-agnostic and fully configurable via environment variables in `docker-compose.yml`.

| Variable | Default | Description |
| :--- | :--- | :--- |
| `LLM_MODEL` | `qwen2.5-coder:7b` | The specific Ollama model tag to use (e.g., `qwen2.5-coder:1.5b` for CPU). |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL of the inference server. In Docker, this is `http://ollama:11434`. |
| `MAX_RETRIES` | `2` | Number of self-healing attempts allowed before giving up. |

## Automation & CI/CD

To ensure the agent remains reliable, we implemented a robust pipeline:

### 1. Continuous Integration (GitHub Actions)
Every time code is pushed to the repository, a GitHub Actions workflow is triggered. This workflow:
* Sets up a Python environment.
* Installs dependencies (LangChain, Ollama).
* Runs a subset of the HumanEval benchmark to ensure the agent's logic is fundamentally sound.
* Fails the deployment if the success rate drops below a quality threshold (80%).

### 2. MLOps (MLflow)
We use MLflow to track every experiment. Each run logs the prompt used, the number of retries required, and the final success status. This allows us to analyze whether changes to the system prompt improve or degrade performance over time.

##  Security & Architecture Note

**Current Implementation:**
For demonstration purposes, this agent executes generated Python code using a local `subprocess`.

**Production Requirement:**
In a real-world production environment, executing arbitrary LLM-generated code poses a security risk. To make this system production-ready, the `executor_node` should be refactored to use a secure, ephemeral sandbox such as **gVisor** or **Firecracker MicroVMs**. This ensures that any flawed code generated by the LLM is strictly isolated from the host infrastructure.
