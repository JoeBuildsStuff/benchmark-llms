import json
import os
import argparse
import re

def load_json_file(file_path):
    """Load and parse a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

# Extract the first part of the question (before options) for matching
def extract_question_text(question_text):
    # Remove "Report Content Errors" and everything after the first option
    cleaned_text = question_text.split("\n\nReport Content Errors")[0].strip()
    return cleaned_text

# Find the matching question in qa_data based on the test name and question text
def find_question_in_qa_data(question_text, qa_data, test_name):
    # Extract test name from the file path (e.g., "cloud-practitioner-clf-c02" from "questions/cloud-practitioner-clf-c02.md")
    test_id = os.path.basename(test_name).split('.')[0]
    
    if test_id not in qa_data:
        return None
        
    clean_question = extract_question_text(question_text)
    
    # Try to find a matching question in the qa_data
    for q in qa_data[test_id]:
        if clean_question in q["question"] or q["question"] in clean_question:
            return q
            
    return None

# Normalize answers to uppercase for comparison
def normalize_answer(answer):
    """Normalize answer format for comparison."""
    if isinstance(answer, list):
        return [a.upper() for a in answer]
    return answer.upper()

def evaluate_answers(llm_results_file, qa_data_file, output_file=None):
    """
    Evaluate LLM answers against the correct answers from qa_data.json.
    
    Args:
        llm_results_file: Path to the LLM results JSON file
        qa_data_file: Path to the qa_data.json file with correct answers
        output_file: Path to save the evaluated results (if None, will modify the original file)
    
    Returns:
        Dictionary with evaluation statistics
    """
    # Load the files
    llm_results = load_json_file(llm_results_file)
    qa_data = load_json_file(qa_data_file)
    
    # Get the test name from metadata
    test_name = llm_results.get("metadata", {}).get("questions_file", "")
    
    # Initialize evaluation summary
    total_questions = 0
    correct_answers = 0
    incorrect_answers = 0
    unanswered_questions = 0
    
    # Process each question/response
    for response in llm_results.get("responses", []):
        total_questions += 1
        question_text = response.get("question", "")
        
        # Find the corresponding question in qa_data
        matching_question = find_question_in_qa_data(question_text, qa_data, test_name)
        
        if not matching_question:
            # Couldn't find matching question
            response["evaluation"] = {
                "status": "unknown",
                "message": "Could not find matching question in qa_data.json"
            }
            continue
            
        # Get the LLM's answer selections
        llm_selections = response.get("answer_selections", [])
        
        # Get the correct answer from qa_data
        correct_answers_list = matching_question.get("correct_answer", [])
        
        # Normalize answers for comparison
        normalized_llm = normalize_answer(llm_selections)
        normalized_correct = normalize_answer(correct_answers_list)
        
        # Create the evaluation data
        evaluation = {
            "correct_answer": correct_answers_list,
            "options": matching_question.get("options", {})
        }
        
        # Determine if the answer is correct
        if len(normalized_llm) == 0:
            evaluation["status"] = "unanswered"
            evaluation["message"] = f"Question was not answered. Correct answer: {', '.join(correct_answers_list)}"
            unanswered_questions += 1
        elif sorted(normalized_llm) == sorted(normalized_correct):
            evaluation["status"] = "correct"
            evaluation["message"] = "Answer is correct"
            correct_answers += 1
        else:
            evaluation["status"] = "incorrect"
            evaluation["message"] = f"Incorrect answer. Selected: {', '.join(llm_selections)}. Correct answer: {', '.join(correct_answers_list)}"
            incorrect_answers += 1
            
        # Add the evaluation to the response
        response["evaluation"] = evaluation
    
    # Add evaluation summary to the results
    accuracy = correct_answers / total_questions if total_questions > 0 else 0
    
    # Add total_correct and total_incorrect to the metadata
    llm_results["metadata"]["total_correct"] = correct_answers
    llm_results["metadata"]["total_incorrect"] = incorrect_answers
    llm_results["metadata"]["accuracy"] = accuracy
    
    # Also add the full evaluation summary
    llm_results["evaluation_summary"] = {
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "incorrect_answers": incorrect_answers,
        "unanswered_questions": unanswered_questions,
        "accuracy": accuracy
    }
    
    # Save the updated results
    output_path = output_file if output_file else llm_results_file
    with open(output_path, 'w') as f:
        json.dump(llm_results, f, indent=4)
        
    return llm_results["evaluation_summary"]

def find_json_files(directory):
    json_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json') and file != 'qa_data.json':
                json_files.append(os.path.join(root, file))
    return json_files

def main():
    parser = argparse.ArgumentParser(description='Evaluate LLM answers against correct answers')
    parser.add_argument('directory', help='Directory containing LLM result JSON files (will search recursively)')
    parser.add_argument('--qa_data', default='outputs/qa_data.json', help='Path to the qa_data.json file')
    parser.add_argument('--output_dir', help='Output directory for evaluated files (if not specified, original files will be modified)')
    
    args = parser.parse_args()
    
    # Find all JSON files in the directory and subdirectories
    json_files = find_json_files(args.directory)
    
    print(f"Found {len(json_files)} JSON files to evaluate")
    
    # Process each file
    for file_path in json_files:
        try:
            output_path = None
            if args.output_dir:
                # Create output directory if it doesn't exist
                os.makedirs(args.output_dir, exist_ok=True)
                
                # Create a similar directory structure in the output directory
                rel_path = os.path.relpath(file_path, args.directory)
                output_path = os.path.join(args.output_dir, rel_path)
                
                # Create parent directories if they don't exist
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            summary = evaluate_answers(file_path, args.qa_data, output_path)
            print(f"Evaluated {file_path}: {summary['correct_answers']}/{summary['total_questions']} correct ({summary['accuracy']:.2%})")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    main() 