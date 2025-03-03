# LLM Answer Analyzer

This script analyzes the responses from LLM models to multiple-choice questions and extracts the selected answer choices (A, B, C, D, etc.). It uses GPT-4o to interpret the model's responses and determine which options were selected.

## Features

- Automatically extracts answer selections from free-text model responses
- Uses GPT-4o to interpret responses and identify selected options
- Handles various response formats and styles
- Processes multiple JSON files in parallel
- Updates the original JSON files with extracted answer selections
- Supports concurrent processing for efficiency

## Usage

```bash
python analyze_model_answers.py DIRECTORY [--workers WORKERS]
```

### Arguments

- `DIRECTORY`: Directory containing JSON files to process (will search recursively)
- `--workers`: Number of worker threads for parallel processing (default: 5)

### Example

```bash
# Process all JSON files in the outputs directory with default settings
python analyze_model_answers.py outputs/

# Process files with more worker threads for faster processing
python analyze_model_answers.py outputs/ --workers 10
```

## How It Works

1. The script searches for all JSON files in the specified directory (recursively)
2. For each file, it extracts the model's response text for each question
3. It sends the response to GPT-4o with a prompt to extract the selected answer letter(s)
4. GPT-4o returns a structured JSON response with the selected answers
5. The script adds the extracted answer selections to the original JSON data
6. The updated data is saved back to the original file

## Output Format

The script adds an `answer_selections` field to each response in the JSON file:

```json
"answer_selections": ["A", "C"]
```

This field contains an array of the letter choices that were selected by the model.

## Dependencies

- openai
- json
- os
- glob
- tqdm
- argparse
- concurrent.futures 