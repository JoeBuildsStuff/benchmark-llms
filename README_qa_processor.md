# Question-Answer Processor

This script processes question and answer markdown files into a structured JSON format. It's designed to work with pairs of files:

1. Question files (e.g., `exam-name-question.md`) containing questions and multiple-choice options
2. Answer files (e.g., `exam-name-answers.md`) containing the correct answers

## Features

- Automatically matches question files with their corresponding answer files
- Supports multiple naming conventions for answer files
- Handles questions with multiple correct answers
- Preserves the structure of questions and their options
- Generates a unique ID for each question
- Outputs a structured JSON file for easy processing

## Usage

```bash
python process_qa_to_json.py [--input INPUT_DIR] [--output OUTPUT_FILE]
```

### Arguments

- `--input`, `-i`: Directory containing question and answer files (default: "questions")
- `--output`, `-o`: Output JSON file path (default: "outputs/qa_data.json")

### Example

```bash
python process_qa_to_json.py --input my_questions --output results/exam_data.json
```

## File Format Requirements

### Question Files

- Must end with `-question.md` or `_question.md`
- Questions should be separated by `----` delimiters
- Each question should include "Report Content Errors" text to separate the question from the options
- Options should be formatted as:
  ```
  A
  Option text here
  
  B
  Another option text
  ```

### Answer Files

- Should match the base name of the question file with `-answers.md`, `-answer.md`, `_answers.md`, or `_answer.md` suffix
- Each line should contain the letter(s) of the correct answer(s)
- For multiple correct answers, separate letters with commas (e.g., "a, c")
- The number of answers should match the number of questions

## Output Format

The script generates a JSON file with the following structure:

```json
{
  "exam-name": [
    {
      "id": "exam-name-1",
      "question": "Question text here?",
      "options": {
        "A": "First option",
        "B": "Second option",
        "C": "Third option",
        "D": "Fourth option"
      },
      "correct_answer": ["b"]
    },
    {
      "id": "exam-name-2",
      "question": "Another question with multiple correct answers?",
      "options": {
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D",
        "E": "Option E"
      },
      "correct_answer": ["a", "c"]
    }
  ]
}
``` 