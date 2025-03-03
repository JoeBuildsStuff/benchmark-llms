import json
import os
import time
import datetime
from openai import OpenAI

client = OpenAI()

# Define the model to use
MODEL_NAME = "gpt-4o-mini"  # You can change this to any model you want to use

#function to parse questions from a markdown file separated by ----
def parse_questions(file_path):
    """Parse questions from a markdown file separated by ----"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    questions = content.split('----')
    return [q.strip() for q in questions if q.strip()]

#function to send questions to openai
def send_questions_to_openai(question):
    """Send questions to OpenAI"""
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": question}
        ]
    )
    return completion

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

# run the script
if __name__ == "__main__":
    # Create a timestamp for the file name (use a format suitable for filenames)
    script_start_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    script_start_time_iso = datetime.datetime.now().isoformat()
    
    # Create a directory for outputs if it doesn't exist
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Questions file path
    questions_file = "questions/cloud-practitioner-clf-c02.md"
    
    # Create output file name with model name and timestamp
    sanitized_model_name = MODEL_NAME.replace("-", "_")
    output_file = f"{output_dir}/{sanitized_model_name}_{script_start_time}.json"
    
    print(f"Responses will be saved to: {output_file}")
    
    questions = parse_questions(questions_file)
    total_questions = len(questions)
    print(f"Loaded {total_questions} questions")
    
    # Create metadata dictionary
    metadata = {
        "model": MODEL_NAME,
        "questions_file": questions_file,
        "total_questions": total_questions,
        "test_start_time": script_start_time_iso,
        "test_id": f"{sanitized_model_name}_{script_start_time}"
    }
    
    # Process each question and save responses
    for i, question in enumerate(questions):
        print(f"Processing question {i+1}/{total_questions}")
        
        # Record start time
        start_time = time.time()
        start_time_str = datetime.datetime.fromtimestamp(start_time).isoformat()
        
        # Send request to OpenAI
        response = send_questions_to_openai(question)
        
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
        
        # Save response with timing information
        save_to_json(question, response, timing_info, output_file, metadata)
        
    print(f"All responses have been saved to {output_file}")

