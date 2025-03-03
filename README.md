# LLM Benchmarking Framework

A comprehensive framework for benchmarking Large Language Models (LLMs) on multiple-choice question answering tasks. This project allows you to evaluate and compare the performance of different LLMs on standardized question sets.

## Project Overview

This framework provides a complete pipeline for:
1. Sending questions to various LLM models
2. Calculating the costs of API calls
3. Extracting answer selections from model responses
4. Processing question and answer files into a structured format
5. Evaluating model accuracy against correct answers
6. Summarizing and comparing results across models

## Components

The project consists of several Python scripts that work together:

1. **[get-llm-answers.py](README_get-llm-answers.md)**: Sends questions to LLM models and collects responses
2. **[calculate_costs.py](README_calculate_costs.md)**: Calculates token usage costs for each model response
3. **[analyze_model_answers.py](README_analyze_model_answers.md)**: Extracts answer selections from model responses
4. **[process_qa_to_json.py](README_process_qa_to_json.md)**: Processes question and answer files into a structured JSON format
5. **[evaluate_llm_answers.py](README_evaluate_llm_answers.md)**: Evaluates model answers against correct answers
6. **[summarize_llm_results.py](README_summarize_llm_results.md)**: Generates summary tables and statistics

## Workflow

The typical workflow for using this framework is:

1. **Prepare Questions**: Create or obtain question and answer files in markdown format
2. **Process Q&A Files**: Convert question and answer files to structured JSON
   ```bash
   python process_qa_to_json.py --input questions/ --output outputs/qa_data.json
   ```
3. **Run Models**: Send questions to various LLM models
   ```bash
   python get-llm-answers.py --questions questions/exam-name.md --models gpt-4o-2024-11-20 o1-2024-12-17
   ```
4. **Calculate Costs**: Add cost information to the response files
   ```bash
   python calculate_costs.py outputs/ --recursive
   ```
5. **Analyze Answers**: Extract answer selections from model responses
   ```bash
   python analyze_model_answers.py outputs/
   ```
6. **Evaluate Accuracy**: Compare model answers with correct answers
   ```bash
   python evaluate_llm_answers.py outputs/ --qa_data outputs/qa_data.json
   ```
7. **Summarize Results**: Generate summary tables and statistics
   ```bash
   python summarize_llm_results.py --directory outputs/
   ```

## Directory Structure

```
benchmark-llms/
├── get-llm-answers.py           # Script to send questions to LLMs
├── calculate_costs.py           # Script to calculate token usage costs
├── analyze_model_answers.py     # Script to extract answer selections
├── process_qa_to_json.py        # Script to process Q&A files
├── evaluate_llm_answers.py      # Script to evaluate model accuracy
├── summarize_llm_results.py     # Script to generate summary statistics
├── questions/                   # Directory for question and answer files
│   ├── exam-name-question.md    # Question file
│   └── exam-name-answers.md     # Answer file
└── outputs/                     # Directory for output files
    ├── qa_data.json             # Processed Q&A data
    └── model_timestamp.json     # Model response files
```

## Requirements

- Python 3.8+
- OpenAI API key (set as environment variable `OPENAI_API_KEY`)
- Required Python packages:
  - openai
  - tqdm
  - pandas
  - tabulate
  - argparse
  - concurrent.futures

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/benchmark-llms.git
   cd benchmark-llms
   ```

2. Install required packages:
   ```bash
   pip install openai tqdm pandas tabulate
   ```

3. Set up your OpenAI API key:
   ```bash
   export OPENAI_API_KEY='your-api-key'
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the API access
- Anthropic for Claude models
- Contributors to the question datasets 