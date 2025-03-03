import os
import json
import re
import argparse
from pathlib import Path

def parse_question_file(file_path):
    """Parse a question file and extract questions with options."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split the content by the delimiter
    question_blocks = content.split('----')
    
    # Remove empty blocks
    question_blocks = [block.strip() for block in question_blocks if block.strip()]
    
    questions = []
    for block in question_blocks:
        # Skip blocks that don't contain actual questions
        if "Report Content Errors" not in block:
            continue
        
        # Extract the question text (everything before "Report Content Errors")
        question_parts = block.split("Report Content Errors", 1)
        if len(question_parts) < 2:
            continue
        
        question_text = question_parts[0].strip()
        
        # Extract options
        options = {}
        option_pattern = re.compile(r'\n([A-Z])\n(.*?)(?=\n\n[A-Z]\n|\Z)', re.DOTALL)
        option_matches = option_pattern.findall(block)
        
        for option_letter, option_text in option_matches:
            options[option_letter] = option_text.strip()
        
        questions.append({
            "question": question_text,
            "options": options
        })
    
    return questions

def parse_answer_file(file_path):
    """Parse an answer file and extract answers."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by newlines and remove empty lines
    answers = [line.strip().lower() for line in content.split('\n') if line.strip()]
    
    # Process answers to handle multiple correct options (e.g., "a, b")
    processed_answers = []
    for answer in answers:
        if ',' in answer:
            # Split by comma and remove whitespace
            options = [opt.strip() for opt in answer.split(',')]
            processed_answers.append(options)
        else:
            processed_answers.append([answer])
    
    return processed_answers

def find_answer_file(directory_path, base_name):
    """Find the corresponding answer file for a question file."""
    # Try different naming conventions
    possible_names = [
        f"{base_name}-answers.md",
        f"{base_name}-answer.md",
        f"{base_name}_answers.md",
        f"{base_name}_answer.md",
        f"{base_name.replace('-', '_')}-answers.md",
        f"{base_name.replace('-', '_')}-answer.md",
        f"{base_name.replace('-', '_')}_answers.md",
        f"{base_name.replace('-', '_')}_answer.md"
    ]
    
    for name in possible_names:
        answer_file = directory_path / name
        if answer_file.exists():
            return answer_file
    
    return None

def process_qa_files(directory):
    """Process all question-answer file pairs in the directory."""
    directory_path = Path(directory)
    
    # Find all question files
    question_files = list(directory_path.glob('*-question.md')) + list(directory_path.glob('*_question.md'))
    
    all_qa_data = {}
    
    for question_file in question_files:
        # Determine the base name (without the -question suffix)
        base_name = question_file.stem
        if '-question' in base_name:
            base_name = base_name.replace('-question', '')
        elif '_question' in base_name:
            base_name = base_name.replace('_question', '')
        
        # Find the corresponding answer file
        answer_file = find_answer_file(directory_path, base_name)
        
        if not answer_file:
            print(f"Warning: No matching answer file found for {question_file}")
            continue
        
        # Parse the files
        questions = parse_question_file(question_file)
        answers = parse_answer_file(answer_file)
        
        # Ensure we have the same number of questions and answers
        if len(questions) != len(answers):
            print(f"Warning: Mismatch in number of questions ({len(questions)}) and answers ({len(answers)}) for {base_name}")
            # Use the minimum length to avoid index errors
            min_length = min(len(questions), len(answers))
            questions = questions[:min_length]
            answers = answers[:min_length]
        
        # Combine questions and answers
        qa_pairs = []
        for i, (question, answer) in enumerate(zip(questions, answers)):
            qa_pair = {
                "id": f"{base_name}-{i+1}",
                "question": question["question"],
                "options": question["options"],
                "correct_answer": answer
            }
            qa_pairs.append(qa_pair)
        
        all_qa_data[base_name] = qa_pairs
    
    return all_qa_data

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Process question and answer markdown files into JSON.')
    parser.add_argument('--input', '-i', default='questions', help='Directory containing question and answer files (default: questions)')
    parser.add_argument('--output', '-o', default='outputs/qa_data.json', help='Output JSON file path (default: outputs/qa_data.json)')
    args = parser.parse_args()
    
    # Process the files
    qa_data = process_qa_files(args.input)
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_dir = output_path.parent
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Save the combined data to a JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(qa_data, f, indent=2)
    
    print(f"Processed {sum(len(qa_pairs) for qa_pairs in qa_data.values())} questions from {len(qa_data)} files")
    print(f"Output saved to {output_path}")

if __name__ == "__main__":
    main() 