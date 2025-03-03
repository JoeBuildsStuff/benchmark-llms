import json
import os
import glob
from openai import OpenAI
from tqdm import tqdm
import argparse
import concurrent.futures

client = OpenAI()

def extract_answer_selections(model_response):
    """
    Send the model's response to GPT-4o to extract the selected answer(s).
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that analyzes multiple choice question responses. Extract only the letter(s) of the selected answer(s) from the provided response."
                },
                {
                    "role": "user",
                    "content": f"Extract the selected answer letter(s) (A, B, C, D, E, F, G, H, or I) from this response to a multiple choice question: \n\n{model_response}"
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "multiple_choice_response",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "selected_answers": {
                                "type": "array",
                                "description": "An array of selected letter answers from the provided response to a multiple choice question.",
                                "items": {
                                    "type": "string",
                                    "enum": ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
                                }
                            }
                        },
                        "required": ["selected_answers"],
                        "additionalProperties": False
                    }
                }
            },
            temperature=0,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error extracting answer selections: {e}")
        return {"selected_answers": []}

def process_json_file(file_path):
    """
    Process a single JSON file, extract answer selections for each question,
    and update the JSON with the selections.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated = False
        
        # Check if the file has the structure with "responses" array
        if isinstance(data, dict) and "responses" in data:
            for item in tqdm(data["responses"], desc=f"Processing {os.path.basename(file_path)}"):
                if "response" in item and "answer_selections" not in item:
                    content = item["response"]["choices"][0]["message"]["content"]
                    selections = extract_answer_selections(content)
                    item["answer_selections"] = selections["selected_answers"]
                    updated = True
        # Check if it's a batch file with multiple questions
        elif isinstance(data, list):
            for item in tqdm(data, desc=f"Processing {os.path.basename(file_path)}"):
                if "response" in item and "answer_selections" not in item:
                    content = item["response"]["choices"][0]["message"]["content"]
                    selections = extract_answer_selections(content)
                    item["answer_selections"] = selections["selected_answers"]
                    updated = True
        # Check if it's a single question file
        elif isinstance(data, dict) and "response" in data and "answer_selections" not in data:
            content = data["response"]["choices"][0]["message"]["content"]
            selections = extract_answer_selections(content)
            data["answer_selections"] = selections["selected_answers"]
            updated = True
            
        if updated:
            # Save the updated data back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            
            return f"Updated {file_path}"
        else:
            return f"No updates needed for {file_path}"
            
    except Exception as e:
        return f"Error processing {file_path}: {e}"

def process_directory(directory_path, max_workers=5):
    """
    Process all JSON files in the specified directory.
    """
    json_files = glob.glob(os.path.join(directory_path, "**/*.json"), recursive=True)
    
    if not json_files:
        print(f"No JSON files found in {directory_path}")
        return
    
    print(f"Found {len(json_files)} JSON files to process")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_json_file, json_files))
    
    for result in results:
        print(result)

def main():
    parser = argparse.ArgumentParser(description="Extract answer selections from model responses in JSON files")
    parser.add_argument("directory", help="Directory containing JSON files to process")
    parser.add_argument("--workers", type=int, default=5, help="Number of worker threads (default: 5)")
    args = parser.parse_args()
    
    process_directory(args.directory, args.workers)

if __name__ == "__main__":
    main()