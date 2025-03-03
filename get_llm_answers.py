import json
import os
import time
import datetime
from openai import OpenAI
import concurrent.futures
from tqdm import tqdm
import argparse

client = OpenAI()

# Define the models to use
MODELS = [
    {"name": "o3-mini-2025-01-31", "reasoning_required": True, "default_effort": "low", "input": 1.10, "output": 4.4},
    {"name": "o3-mini-2025-01-31", "reasoning_required": True, "default_effort": "high", "input": 1.10, "output": 4.4},
    {"name": "o1-2024-12-17", "reasoning_required": True, "default_effort": "low", "input": 15, "output": 60},
    {"name": "o1-2024-12-17", "reasoning_required": True, "default_effort": "high", "input": 15, "output": 60},
    {"name": "o1-mini-2024-09-12", "reasoning_required": False, "input": 1.1, "output": 4.4},
    {"name": "gpt-4o-2024-11-20", "reasoning_required": False, "input": 2.5, "output": 10},
    {"name": "gpt-4o-mini-2024-07-18", "reasoning_required": False, "input": 0.15, "output": .60},
    {"name": "gpt-4-0613", "reasoning_required": False, "input": 30, "output": 60},
    {"name": "gpt-4-turbo-2024-04-09", "reasoning_required": False, "input": 10, "output": 30},
    {"name": "gpt-3.5-turbo-0125", "reasoning_required": False, "input": 0.5, "output": 1.5}
]

# Default batch size
BATCH_SIZE = 10  # Number of questions to process in parallel

#function to parse questions from a markdown file separated by ----
def parse_questions(file_path):
    """Parse questions from a markdown file separated by ----"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    questions = content.split('----')
    return [q.strip() for q in questions if q.strip()]

#function to send questions to openai
def send_questions_to_openai(question, model_info):
    """Send questions to OpenAI"""
    model_name = model_info["name"]
    
    # Base parameters for the API call
    params = {
        "model": model_name,
        "response_format": {"type": "text"},
        "messages": [
            {"role": "user", "content": question}
        ]
    }
    
    # Add reasoning_effort parameter if the model requires it
    if model_info.get("reasoning_required", False):
        reasoning_effort = model_info.get("reasoning_effort", model_info.get("default_effort", "medium"))
        params["reasoning_effort"] = reasoning_effort
    else:
        # Only add temperature for non-reasoning models and not o1-mini
        if model_name != "o1-mini-2024-09-12":
            params["temperature"] = 0.0
    
    completion = client.chat.completions.create(**params)
    return completion

#function to process a single question and return the result
def process_question(question, model_info):
    """Process a single question and return the result"""
    # Record start time
    start_time = time.time()
    start_time_str = datetime.datetime.fromtimestamp(start_time).isoformat()
    
    # Send request to OpenAI
    response = send_questions_to_openai(question, model_info)
    
    # Record end time and calculate duration
    end_time = time.time()
    end_time_str = datetime.datetime.fromtimestamp(end_time).isoformat()
    duration = end_time - start_time
    
    # Create timing info dictionary
    timing_info = {
        "start_time": start_time_str,
        "end_time": end_time_str,
        "duration_seconds": duration
    }
    
    return {
        "question": question,
        "response": response,
        "timing_info": timing_info
    }

#function to save the response to a json file
def save_to_json(question, response, timing_info, output_file, metadata=None):
    """
    Save a question and its response to a JSON file.
    If the file exists, it will append to it; otherwise, it will create a new file.
    
    Parameters:
    - question: The question text
    - response: The model response object
    - timing_info: Dictionary containing start_time, end_time, and duration
    - output_file: Path to the output JSON file
    - metadata: Dictionary containing metadata about the test run
    """
    # Create the data structure for this QA pair
    qa_pair = {
        "question": question,
        "response": response.model_dump(),
        "timing": timing_info
    }
    
    # Check if file exists and load existing data
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                # If file is empty or invalid JSON
                data = {"metadata": metadata, "responses": []}
    else:
        data = {"metadata": metadata, "responses": []}
    
    # Append new response
    data["responses"].append(qa_pair)
    
    # Write back to file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"Response saved to {output_file}")

#function to save batch results to json
def save_batch_to_json(results, output_file, metadata=None):
    """Save a batch of results to a JSON file"""
    # Check if file exists and load existing data
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                # If file is empty or invalid JSON
                data = {"metadata": metadata, "responses": []}
    else:
        data = {"metadata": metadata, "responses": []}
    
    # Append new responses
    for result in results:
        qa_pair = {
            "question": result["question"],
            "response": result["response"].model_dump(),
            "timing": result["timing_info"]
        }
        data["responses"].append(qa_pair)
    
    # Write back to file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"{len(results)} responses saved to {output_file}")

def process_model(model_info, questions_file, batch_size):
    """Process all questions for a specific model"""
    # Create a timestamp for the file name (use a format suitable for filenames)
    script_start_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    script_start_time_iso = datetime.datetime.now().isoformat()
    
    # Create a directory for outputs if it doesn't exist
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create output file name with model name and timestamp
    model_name = model_info["name"]
    sanitized_model_name = model_name.replace("-", "_")
    
    # Add reasoning effort to the filename if applicable
    if model_info.get("reasoning_required", False):
        reasoning_effort = model_info.get("reasoning_effort", model_info.get("default_effort", "medium"))
        output_file = f"{output_dir}/{sanitized_model_name}_{reasoning_effort}_{script_start_time}.json"
    else:
        output_file = f"{output_dir}/{sanitized_model_name}_{script_start_time}.json"
    
    print(f"\n{'='*50}")
    print(f"Processing model: {model_name}")
    if model_info.get("reasoning_required", False):
        print(f"Reasoning effort: {model_info.get('reasoning_effort', model_info.get('default_effort', 'medium'))}")
    print(f"{'='*50}")
    print(f"Responses will be saved to: {output_file}")
    
    questions = parse_questions(questions_file)
    total_questions = len(questions)
    print(f"Loaded {total_questions} questions")
    
    # Create metadata dictionary
    metadata = {
        "model": model_name,
        "questions_file": questions_file,
        "total_questions": total_questions,
        "test_start_time": script_start_time_iso,
        "test_id": f"{sanitized_model_name}_{script_start_time}",
        "batch_size": batch_size
    }
    
    # Add reasoning effort to metadata if applicable
    if model_info.get("reasoning_required", False):
        metadata["reasoning_effort"] = model_info.get("reasoning_effort", model_info.get("default_effort", "medium"))
    
    # Process questions in batches
    with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
        for i in range(0, total_questions, batch_size):
            batch = questions[i:i+batch_size]
            batch_size_actual = len(batch)
            print(f"Processing batch of {batch_size_actual} questions ({i+1}-{i+batch_size_actual}/{total_questions})")
            
            # Submit all questions in the batch to the executor
            future_to_question = {executor.submit(process_question, question, model_info): question for question in batch}
            
            # Collect results as they complete
            batch_results = []
            for future in tqdm(concurrent.futures.as_completed(future_to_question), total=batch_size_actual, desc="Processing"):
                try:
                    result = future.result()
                    batch_results.append(result)
                except Exception as exc:
                    question = future_to_question[future]
                    print(f"Question generated an exception: {question[:50]}... - {exc}")
            
            # Save batch results
            save_batch_to_json(batch_results, output_file, metadata)
    
    print(f"All responses for model {model_name} have been saved to {output_file}")
    return output_file

# run the script
if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run LLM benchmarking with multiple models")
    parser.add_argument("--questions", default="questions/solutions-architect-professional-sap-c02.md", 
                        help="Path to the questions file")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, 
                        help="Number of questions to process in parallel")
    parser.add_argument("--models", nargs="+", 
                        help="List of model names to run (if not specified, all models will be run)")
    parser.add_argument("--reasoning-effort", choices=["low", "medium", "high"], default=None,
                        help="Reasoning effort for models that support it (o1, o3 families)")
    
    args = parser.parse_args()
    
    # Filter models if specific ones were requested
    models_to_run = MODELS
    if args.models:
        models_to_run = [model for model in MODELS if model["name"] in args.models]
        if not models_to_run:
            print(f"Error: None of the specified models {args.models} were found in the available models list.")
            exit(1)
    
    # Set reasoning effort if specified
    if args.reasoning_effort:
        for model in models_to_run:
            if model.get("reasoning_required", False):
                model["reasoning_effort"] = args.reasoning_effort
    
    # Process each model
    output_files = []
    for model_info in models_to_run:
        try:
            output_file = process_model(model_info, args.questions, args.batch_size)
            output_files.append(output_file)
        except Exception as e:
            print(f"Error processing model {model_info['name']}: {e}")
    
    print("\nAll models have been processed. Output files:")
    for file in output_files:
        print(f"- {file}")

