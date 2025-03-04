# LLM Benchmark Tool

A comprehensive benchmarking tool for evaluating Large Language Models (LLMs) on multiple-choice question answering tasks. This tool measures accuracy, response time, token usage, and costs across different models.

## Overview

This tool automates the process of:
1. Loading multiple-choice questions from a JSON file
2. Sending these questions to various LLM models
3. Extracting and evaluating the answers
4. Calculating token usage and associated costs
5. Generating detailed performance reports

## Features

- **Multi-model Support**: Test multiple LLMs side-by-side (Claude, GPT-4, etc.)
- **Parallel Processing**: Process questions in configurable batch sizes for efficiency
- **Reasoning Effort Control**: Adjust reasoning effort for models that support it
- **Cost Calculation**: Track token usage and calculate costs based on model pricing
- **Comprehensive Reporting**: Generate detailed JSON reports with:
  - Accuracy metrics
  - Response timing
  - Token usage statistics
  - Cost analysis
  - Individual question evaluations

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/benchmark-llms.git
cd benchmark-llms

# Install dependencies
pip install openai tqdm
```

## Usage

### Basic Usage

```bash
python generate_comprehensive_report.py --model MODEL_NAME --qa-data path/to/qa_data.json --output path/to/output
```

### Evaluate All Available Models

```bash
python generate_comprehensive_report.py --all-models --qa-data path/to/qa_data.json --output path/to/output
```

### Command Line Arguments

| Argument | Description |
|----------|-------------|
| `--model MODEL_NAME` | Specific model to evaluate (e.g., "o3-mini-2025-01-31") |
| `--all-models` | Run evaluation on all available models |
| `--qa-data PATH` | Path to the question-answer JSON file (required) |
| `--output PATH` | Path to save the output report (required) |
| `--test-id ID` | Process only a specific test from the qa_data.json file |
| `--batch-size N` | Number of questions to process in parallel (default: 10) |
| `--reasoning-effort {low,medium,high}` | Set reasoning effort for models that support it |

## Input Data Format

The script expects a JSON file with the following structure:

```json
{
  "test_id_1": [
    {
      "id": "q1",
      "question": "What is the capital of France?",
      "options": {
        "A": "London",
        "B": "Paris",
        "C": "Berlin",
        "D": "Madrid"
      },
      "correct_answer": ["B"]
    },
    // More questions...
  ],
  "test_id_2": [
    // Another set of questions...
  ]
}
```

## How It Works

### Workflow

1. **Load Questions**: The script loads questions from the specified JSON file.
2. **Process Questions**: Questions are processed in parallel batches:
   - Each question is formatted with its options
   - The formatted question is sent to the specified LLM
   - Response timing is recorded
3. **Extract Answers**: A separate GPT-4o call extracts the letter selections (A, B, C, etc.) from the model's response.
4. **Evaluate Answers**: The selected answers are compared to the correct answers.
5. **Calculate Costs**: Token usage is analyzed to calculate costs based on model pricing.
6. **Generate Report**: A comprehensive JSON report is created with all the collected data.

### Key Components

- **Question Processing**: The `process_question` function handles sending questions to the LLM and collecting responses.
- **Answer Extraction**: The `extract_answer_selections` function uses GPT-4o to extract letter selections from free-text responses.
- **Cost Calculation**: The `calculate_costs` function computes costs based on token usage and model pricing.
- **Answer Evaluation**: The `evaluate_answer` function compares selected answers against correct answers.
- **Report Generation**: The `generate_comprehensive_report` function orchestrates the entire process and creates the final report.

## Output Format

The script generates a JSON report with the following structure:

```json
{
  "metadata": {
    "model": "model-name",
    "questions_file": "qa_data.json",
    "total_questions": 100,
    "test_start_time": "2023-01-01T12:00:00",
    "test_id": "model_name_20230101_120000",
    "batch_size": 10,
    "total_duration_seconds": 120.5,
    "costs": {
      "total_prompt_cost": 0.05,
      "total_completion_cost": 0.03,
      "total_reasoning_cost": 0.01,
      "total_cost": 0.09
    },
    "total_correct": 85,
    "total_incorrect": 15,
    "accuracy": 0.85
  },
  "responses": [
    {
      "question": "What is the capital of France?...",
      "response": { /* Full API response */ },
      "timing": {
        "start_time": "2023-01-01T12:00:01",
        "end_time": "2023-01-01T12:00:02",
        "duration_seconds": 1.2
      },
      "costs": {
        "prompt_cost": 0.0005,
        "completion_cost": 0.0003,
        "reasoning_cost": 0.0001,
        "total_cost": 0.0009
      },
      "answer_selections": ["B"],
      "evaluation": {
        "correct_answer": ["B"],
        "options": { /* Question options */ },
        "status": "correct",
        "message": "Answer is correct"
      }
    },
    // More responses...
  ],
  "evaluation_summary": {
    "total_questions": 100,
    "correct_answers": 85,
    "incorrect_answers": 15,
    "unanswered_questions": 0,
    "accuracy": 0.85
  }
}
```

## Supported Models

The script supports various LLM models, configured in the `MODELS` list at the top of the script:

- Claude models (o3-mini, o1, o1-mini)
- GPT models (gpt-4o, gpt-4o-mini, gpt-4, gpt-4-turbo, gpt-3.5-turbo)

Each model entry includes:
- Name
- Whether reasoning is required/supported
- Default reasoning effort (if applicable)
- Input and output costs per million tokens

## Adding New Models

To add a new model, add an entry to the `MODELS` list:

```python
{
    "name": "model-name",
    "reasoning_required": True/False,
    "default_effort": "low/medium/high",  # Only for models with reasoning
    "input": 1.0,  # Cost per million input tokens
    "output": 2.0  # Cost per million output tokens
}
```

## License

[Your License Here]

## Contributing

[Your Contribution Guidelines Here] 