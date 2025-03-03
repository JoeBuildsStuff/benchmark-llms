# LLM Answer Generator

This script sends multiple-choice questions to various LLM models and collects their responses. It's designed to benchmark different models on standardized question sets.

## Features

- Supports multiple OpenAI models (Claude, GPT-4, GPT-3.5, etc.)
- Handles model-specific parameters like reasoning_effort for Claude models
- Processes questions in parallel batches for efficiency
- Records detailed timing and response information
- Saves results in structured JSON format for further analysis

## Usage

```bash
python get-llm-answers.py [--questions QUESTIONS_FILE] [--batch-size BATCH_SIZE] [--models MODEL_NAMES] [--reasoning-effort {low,medium,high}]
```

### Arguments

- `--questions`: Path to the markdown file containing questions (default: "questions/solutions-architect-professional-sap-c02.md")
- `--batch-size`: Number of questions to process in parallel (default: 10)
- `--models`: List of specific model names to run (if not specified, all models will be run)
- `--reasoning-effort`: Reasoning effort for models that support it (Claude family)

### Example

```bash
# Run all models on the default question set
python get-llm-answers.py

# Run specific models with high reasoning effort
python get-llm-answers.py --models o1-2024-12-17 o3-mini-2025-01-31 --reasoning-effort high

# Use a different question file with a smaller batch size
python get-llm-answers.py --questions questions/cloud-practitioner-clf-c02.md --batch-size 5
```

## Input Format

The script expects questions in a markdown file separated by `----` delimiters. Each question should include the question text and multiple-choice options.

## Output

Results are saved to the `outputs` directory with filenames that include the model name and timestamp. Each output file contains:

- Metadata about the test run (model, questions file, timestamp, etc.)
- An array of responses, each containing:
  - The original question text
  - The model's complete response
  - Timing information (start time, end time, duration)

## Dependencies

- openai
- concurrent.futures
- tqdm
- argparse
- json
- os
- time
- datetime 