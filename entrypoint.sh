#!/bin/bash

ollama serve &

echo " Waiting for Ollama to start..."
sleep 5

# 3. Pull the model (if not already cached)
# In production, you'd bake the model into the image to save time, 
# but for now we pull it at runtime.
echo " Pulling Model..."
ollama pull qwen2.5-coder:7b

# 4. Run the benchmark
echo " Running Benchmark..."
python tests/benchmark.py 5
