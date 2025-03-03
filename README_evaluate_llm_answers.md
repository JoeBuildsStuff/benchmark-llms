# LLM Answer Evaluator

This script evaluates the accuracy of LLM responses to multiple-choice questions by comparing the model's selected answers against the correct answers from a reference dataset.

## Features

- Automatically matches questions with their reference answers
- Evaluates the correctness of each answer selection
- Handles multiple correct answers
- Calculates overall accuracy statistics
- Processes multiple JSON files in a directory
- Preserves directory structure when saving output files
- Adds detailed evaluation data to each response

## Usage

```bash
python evaluate_llm_answers.py DIRECTORY [--qa_data QA_DATA_FILE] [--output_dir OUTPUT_DIR]
```

### Arguments

- `DIRECTORY`: Directory containing LLM result JSON files (will search recursively)
- `--qa_data`: Path to the qa_data.json file with correct answers (default: "outputs/qa_data.json")
- `--output_dir`: Output directory for evaluated files (if not specified, original files will be modified)

### Example

```bash
# Evaluate all files in the outputs directory using the default qa_data.json
python evaluate_llm_answers.py outputs/

# Evaluate files using a specific reference file and save to a new directory
python evaluate_llm_answers.py outputs/ --qa_data reference/qa_data.json --output_dir evaluated_results/
```

## How It Works

1. The script loads the LLM result files and the reference qa_data.json file
2. For each question in the LLM results, it finds the matching question in the reference data
3. It compares the model's answer selections with the correct answers
4. It adds evaluation data to each response, including:
   - The correct answer
   - Whether the model's answer was correct, incorrect, or unanswered
   - A message explaining the evaluation
5. It calculates overall statistics (total correct, incorrect, accuracy)
6. It saves the updated data to the original file or a new file in the output directory

## Output Format

The script adds an `evaluation` field to each response in the JSON file:

```json
"evaluation": {
  "status": "correct",
  "message": "Answer is correct",
  "correct_answer": ["B"],
  "options": {
    "A": "Option A text",
    "B": "Option B text",
    "C": "Option C text",
    "D": "Option D text"
  }
}
```

It also adds evaluation summary data to the metadata section:

```json
"total_correct": 42,
"total_incorrect": 8,
"accuracy": 0.84
```

## Dependencies

- json
- os
- argparse
- re 