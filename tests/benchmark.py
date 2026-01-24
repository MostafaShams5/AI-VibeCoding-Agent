import pandas as pd
import mlflow
from datasets import load_dataset
from src.agent import build_agent
import sys

# Limit number of problems for CI/CD speed
NUM_PROBLEMS = 5 
if len(sys.argv) > 1:
    NUM_PROBLEMS = int(sys.argv[1])

print(f"Starting Benchmark on {NUM_PROBLEMS} problems...")

app = build_agent()
ds = load_dataset("openai_humaneval")
test_data = ds['test'].select(range(NUM_PROBLEMS))
results = []

mlflow.set_experiment("CI_Pipeline_Benchmark")

for item in test_data:
    task_id = item['task_id']
    print(f"\n🔹 Working on: {task_id}")
    
    inputs = {
        "task_id": task_id,
        "prompt": item['prompt'],
        "test_code": item['test'],
        "entry_point": item['entry_point'],
        "code": "",
        "error": None,
        "iteration": 0,
        "success": False
    }
    
    with mlflow.start_run(run_name=task_id):
        final_state = app.invoke(inputs)
        mlflow.log_metric("success", 1 if final_state['success'] else 0)
        
        results.append({
            "Task ID": task_id,
            "Success": final_state['success'],
            "Retries": final_state['iteration'] - 1
        })

df = pd.DataFrame(results)
pass_rate = df['Success'].mean() * 100
print(f"\nFinal Pass Rate: {pass_rate:.1f}%")

if pass_rate < 80:
    print(" Failed Quality Gate (<80%)")
    sys.exit(1)
else:
    print(" Passed Quality Gate")
    sys.exit(0)
