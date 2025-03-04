import json
import os
import argparse
import datetime
import time
from openai import OpenAI
import concurrent.futures
from tqdm import tqdm

client = OpenAI()

# Define the models to use
MODELS = [
    {"name": "o3-mini-2025-01-31", "reasoning_required": True, "default_effort": "low", "input": 1.10, "output": 4.4},
    # {"name": "o3-mini-2025-01-31", "reasoning_required": True, "default_effort": "high", "input": 1.10, "output": 4.4},
    # {"name": "o1-2024-12-17", "reasoning_required": True, "default_effort": "low", "input": 15, "output": 60},
    # {"name": "o1-2024-12-17", "reasoning_required": True, "default_effort": "high", "input": 15, "output": 60},
    # {"name": "o1-mini-2024-09-12", "reasoning_required": False, "input": 1.1, "output": 4.4},
    # {"name": "gpt-4o-2024-11-20", "reasoning_required": False, "input": 2.5, "output": 10},
    # {"name": "gpt-4o-mini-2024-07-18", "reasoning_required": False, "input": 0.15, "output": .60},
    # {"name": "gpt-4-0613", "reasoning_required": False, "input": 30, "output": 60},
    # {"name": "gpt-4-turbo-2024-04-09", "reasoning_required": False, "input": 10, "output": 30},
    # {"name": "gpt-3.5-turbo-0125", "reasoning_required": False, "input": 0.5, "output": 1.5}
]

# Default batch size
BATCH_SIZE = 10  # Number of questions to process in parallel

def load_qa_data(file_path):
    """Load the qa_data.json file"""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            # Try to find the file in common locations
            possible_paths = [
                file_path,
                os.path.join(os.getcwd(), file_path),
                os.path.join(os.getcwd(), "outputs", os.path.basename(file_path)),
                os.path.join("outputs", os.path.basename(file_path))
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    file_path = path
                    break
            else:
                raise FileNotFoundError(f"Could not find qa_data.json file at any of these locations: {possible_paths}")
        
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {file_path} is not a valid JSON file.")
        exit(1)
    except Exception as e:
        print(f"Error loading qa_data.json: {e}")
        print("Please check that the file exists and is accessible.")
        exit(1)

def extract_questions_from_qa_data(qa_data, test_id=None):
    """Extract questions from qa_data.json"""
    questions = []
    
    # If test_id is specified, only extract questions from that test
    if test_id:
        if test_id in qa_data:
            for q in qa_data[test_id]:
                question_text = format_question_with_options(q)
                questions.append({
                    "text": question_text,
                    "id": q.get("id", ""),
                    "correct_answer": q.get("correct_answer", []),
                    "options": q.get("options", {})
                })
        else:
            print(f"Warning: Test ID '{test_id}' not found in qa_data.json")
    else:
        # Extract questions from all tests
        for test_id, test_questions in qa_data.items():
            for q in test_questions:
                question_text = format_question_with_options(q)
                questions.append({
                    "text": question_text,
                    "id": q.get("id", ""),
                    "correct_answer": q.get("correct_answer", []),
                    "options": q.get("options", {})
                })
    
    return questions

def format_question_with_options(question_data):
    """Format a question with its options for sending to the model"""
    question_text = question_data.get("question", "")
    options = question_data.get("options", {})
    
    formatted_question = question_text + "\n\nReport Content Errors\n\n"
    
    for option_key, option_text in options.items():
        formatted_question += f"{option_key}\n{option_text}\n\n\n"
    
    return formatted_question

def normalize_answer(answer):
    """Normalize answer format for comparison"""
    if isinstance(answer, list):
        return [a.upper() for a in answer]
    return answer.upper()

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

def process_question(question_data, model_info):
    """Process a single question and return the result"""
    # Record start time
    start_time = time.time()
    start_time_str = datetime.datetime.fromtimestamp(start_time).isoformat()
    
    # Send request to OpenAI
    response = send_questions_to_openai(question_data["text"], model_info)
    
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
        "question_data": question_data,
        "response": response,
        "timing_info": timing_info
    }

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
            max_tokens=100,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error extracting answer selections: {e}")
        return {"selected_answers": []}

def calculate_costs(response_data, model_info):
    """Calculate costs for a single response based on token usage"""
    try:
        # Get the response object
        response_obj = response_data.get("response", None)
        
        # Extract usage data based on the response structure
        usage = None
        
        # If response is already a dictionary (from model_dump())
        if isinstance(response_obj, dict) and "usage" in response_obj:
            usage = response_obj["usage"]
        # If response is the original API response object
        elif hasattr(response_obj, "usage"):
            usage = response_obj.usage
        # If response is in the result dictionary
        elif "response" in response_data and hasattr(response_data["response"], "usage"):
            usage = response_data["response"].usage
        
        # If we still don't have usage data, try to access it from the model_dump
        if usage is None and isinstance(response_obj, dict):
            # Try to find usage in the response structure
            if "usage" in response_obj:
                usage = response_obj["usage"]
        
        # If we still don't have usage, create a default
        if usage is None:
            print(f"Warning: Could not find usage data in response. Creating default values.")
            usage = {"prompt_tokens": 0, "completion_tokens": 0}
        
        # Extract token counts
        prompt_tokens = usage.get("prompt_tokens", 0) if isinstance(usage, dict) else getattr(usage, "prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0) if isinstance(usage, dict) else getattr(usage, "completion_tokens", 0)
        
        # Handle reasoning tokens
        reasoning_tokens = 0
        if isinstance(usage, dict) and "completion_tokens_details" in usage:
            if isinstance(usage["completion_tokens_details"], dict):
                reasoning_tokens = usage["completion_tokens_details"].get("reasoning_tokens", 0)
        elif hasattr(usage, "completion_tokens_details"):
            reasoning_tokens = getattr(usage.completion_tokens_details, "reasoning_tokens", 0)
        
        # Calculate costs (convert from dollars per million tokens to dollars)
        prompt_cost = (prompt_tokens * model_info["input"]) / 1000000
        completion_cost = (completion_tokens * model_info["output"]) / 1000000
        reasoning_cost = (reasoning_tokens * model_info["output"]) / 1000000
        total_cost = prompt_cost + completion_cost
        
        # Create costs object
        costs = {
            "prompt_cost": prompt_cost,
            "completion_cost": completion_cost,
            "reasoning_cost": reasoning_cost,
            "total_cost": total_cost
        }
        
        return costs
    except Exception as e:
        print(f"Error calculating costs: {e}")
        import traceback
        traceback.print_exc()
        
        # Return default costs
        return {
            "prompt_cost": 0,
            "completion_cost": 0,
            "reasoning_cost": 0,
            "total_cost": 0
        }

def evaluate_answer(response, llm_selections):
    """Evaluate a single answer against the correct answer"""
    question_data = response.get("question_data", {})
    correct_answers_list = question_data.get("correct_answer", [])
    
    # Normalize answers for comparison
    normalized_llm = normalize_answer(llm_selections)
    normalized_correct = normalize_answer(correct_answers_list)
    
    # Create the evaluation data
    evaluation = {
        "correct_answer": correct_answers_list,
        "options": question_data.get("options", {})
    }
    
    # Determine if the answer is correct
    if len(normalized_llm) == 0:
        evaluation["status"] = "unanswered"
        evaluation["message"] = f"Question was not answered. Correct answer: {', '.join(correct_answers_list)}"
        return evaluation, "unanswered"
    elif sorted(normalized_llm) == sorted(normalized_correct):
        evaluation["status"] = "correct"
        evaluation["message"] = "Answer is correct"
        return evaluation, "correct"
    else:
        evaluation["status"] = "incorrect"
        evaluation["message"] = f"Incorrect answer. Selected: {', '.join(llm_selections)}. Correct answer: {', '.join(correct_answers_list)}"
        return evaluation, "incorrect"

def generate_comprehensive_report(model_info, qa_data_file, output_file, test_id=None, batch_size=BATCH_SIZE):
    """
    Generate a comprehensive report for a model on questions from qa_data.json.
    This combines the functionality of get_llm_answers.py, analyze_model_answers.py,
    calculate_costs.py, and evaluate_llm_answers.py.
    """
    # Create a timestamp for the file name
    script_start_time = datetime.datetime.now()
    script_start_time_str = script_start_time.strftime("%Y%m%d_%H%M%S")
    script_start_time_iso = script_start_time.isoformat()
    
    # Load qa_data.json
    qa_data = load_qa_data(qa_data_file)
    
    # Create a directory for outputs if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Create model name for metadata
    model_name = model_info["name"]
    sanitized_model_name = model_name.replace("-", "_")
    
    # Extract questions from qa_data.json
    questions = extract_questions_from_qa_data(qa_data, test_id)
    total_questions = len(questions)
    
    if total_questions == 0:
        print(f"Error: No questions found in qa_data.json" + (f" for test ID '{test_id}'" if test_id else ""))
        exit(1)
    
    print(f"Loaded {total_questions} questions from qa_data.json")
    
    # Create metadata dictionary
    metadata = {
        "model": model_name,
        "questions_file": f"qa_data.json" + (f":{test_id}" if test_id else ""),
        "total_questions": total_questions,
        "test_start_time": script_start_time_iso,
        "test_id": f"{sanitized_model_name}_{script_start_time_str}",
        "batch_size": batch_size
    }
    
    # Add reasoning effort to metadata if applicable
    if model_info.get("reasoning_required", False):
        reasoning_effort = model_info.get("reasoning_effort", model_info.get("default_effort", "medium"))
        metadata["reasoning_effort"] = reasoning_effort
    
    # Initialize the results structure
    results = {
        "metadata": metadata,
        "responses": []
    }
    
    # Initialize counters for evaluation summary
    total_duration = 0
    total_prompt_cost = 0
    total_completion_cost = 0
    total_reasoning_cost = 0
    total_cost = 0
    correct_answers = 0
    incorrect_answers = 0
    unanswered_questions = 0
    
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
                    print(f"Question generated an exception: {question['id']} - {exc}")
            
            # Process each result in the batch
            for result in batch_results:
                try:
                    # Extract answer selections
                    content = result["response"].choices[0].message.content
                    selections = extract_answer_selections(content)
                    
                    # Convert the response to a dictionary for JSON serialization
                    response_dict = result["response"].model_dump()
                    
                    # Calculate costs
                    costs = calculate_costs({"response": response_dict}, model_info)
                    
                    # Create the response object
                    response = {
                        "question": result["question_data"]["text"],
                        "response": response_dict,
                        "timing": result["timing_info"],
                        "costs": costs,
                        "answer_selections": selections["selected_answers"]
                    }
                    
                    # Evaluate the answer
                    evaluation, status = evaluate_answer(result, selections["selected_answers"])
                    response["evaluation"] = evaluation
                    
                    # Update counters
                    total_duration += result["timing_info"]["duration_seconds"]
                    total_prompt_cost += costs["prompt_cost"]
                    total_completion_cost += costs["completion_cost"]
                    total_reasoning_cost += costs["reasoning_cost"]
                    total_cost += costs["total_cost"]
                    
                    if status == "correct":
                        correct_answers += 1
                    elif status == "incorrect":
                        incorrect_answers += 1
                    elif status == "unanswered":
                        unanswered_questions += 1
                    
                    # Add the response to the results
                    results["responses"].append(response)
                except Exception as e:
                    print(f"Error processing result: {e}")
                    import traceback
                    traceback.print_exc()
    
    # Update metadata with totals
    results["metadata"]["total_duration_seconds"] = total_duration
    results["metadata"]["costs"] = {
        "total_prompt_cost": total_prompt_cost,
        "total_completion_cost": total_completion_cost,
        "total_reasoning_cost": total_reasoning_cost,
        "total_cost": total_cost
    }
    
    # Add evaluation summary to metadata
    accuracy = correct_answers / total_questions if total_questions > 0 else 0
    results["metadata"]["total_correct"] = correct_answers
    results["metadata"]["total_incorrect"] = incorrect_answers
    results["metadata"]["accuracy"] = accuracy
    
    # Add full evaluation summary
    results["evaluation_summary"] = {
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "incorrect_answers": incorrect_answers,
        "unanswered_questions": unanswered_questions,
        "accuracy": accuracy
    }
    
    # Save the results to the output file
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
    
    print(f"\nComprehensive report saved to {output_file}")
    print(f"Accuracy: {correct_answers}/{total_questions} correct ({accuracy:.2%})")
    
    return results

def get_model_info_by_name(model_name):
    """Get model info by name"""
    for model in MODELS:
        if model["name"] == model_name:
            return model
    return None

def main():
    parser = argparse.ArgumentParser(description="Generate a comprehensive LLM evaluation report")
    parser.add_argument("--model", help="Model name to use")
    parser.add_argument("--all-models", action="store_true", help="Run evaluation on all available models")
    parser.add_argument("--qa-data", required=True, help="Path to the qa_data.json file")
    parser.add_argument("--output", required=True, help="Path to save the output JSON file")
    parser.add_argument("--test-id", help="Specific test ID to process from qa_data.json")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="Number of questions to process in parallel")
    parser.add_argument("--reasoning-effort", choices=["low", "medium", "high"], help="Reasoning effort for models that support it")
    
    args = parser.parse_args()
    
    # Print current working directory for debugging
    print(f"Current working directory: {os.getcwd()}")
    
    # Check if either --model or --all-models is provided
    if not args.model and not args.all_models:
        print("Error: Either --model or --all-models must be specified")
        parser.print_help()
        exit(1)
    
    # If --all-models is specified, run evaluation for all models
    if args.all_models:
        print(f"Running evaluation on all {len(MODELS)} available models")
        
        # Create a list to store results for all models
        all_results = []
        
        # Process each model
        for model_info in MODELS:
            model_name = model_info["name"]
            
            # Skip duplicate model entries with different reasoning efforts
            # We'll handle reasoning effort separately
            if args.all_models and model_name in [result.get("model_name") for result in all_results]:
                continue
                
            print(f"\n{'='*80}\nProcessing model: {model_name}\n{'='*80}")
            
            # Set reasoning effort if specified and applicable
            if args.reasoning_effort and model_info.get("reasoning_required", False):
                model_info = model_info.copy()  # Create a copy to avoid modifying the original
                model_info["reasoning_effort"] = args.reasoning_effort
            
            # Add timestamp to output file
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create model-specific output filename
            if "." in os.path.basename(args.output):
                base, ext = os.path.splitext(args.output)
                output_file = f"{base}_{model_name.replace('-', '_')}_{timestamp}{ext}"
            else:
                output_file = f"{args.output}_{model_name.replace('-', '_')}_{timestamp}.json"
            
            try:
                # Generate the comprehensive report for this model
                result = generate_comprehensive_report(
                    model_info=model_info,
                    qa_data_file=args.qa_data,
                    output_file=output_file,
                    test_id=args.test_id,
                    batch_size=args.batch_size
                )
                
                # Store basic result info
                all_results.append({
                    "model_name": model_name,
                    "output_file": output_file,
                    "accuracy": result["evaluation_summary"]["accuracy"],
                    "total_cost": result["metadata"]["costs"]["total_cost"]
                })
                
            except Exception as e:
                print(f"Error generating report for model {model_name}: {e}")
                import traceback
                traceback.print_exc()
        
        # Print summary of all model results
        print("\n\n" + "="*80)
        print("SUMMARY OF ALL MODEL RESULTS")
        print("="*80)
        print(f"{'Model':<30} {'Accuracy':<10} {'Total Cost':<15}")
        print("-"*80)
        
        for result in all_results:
            print(f"{result['model_name']:<30} {result['accuracy']:.2%} ${result['total_cost']:.6f}")
    
    else:
        # Get model info for a single model
        model_info = get_model_info_by_name(args.model)
        if not model_info:
            print(f"Error: Model '{args.model}' not found in the available models list.")
            print("Available models:")
            for model in MODELS:
                print(f"- {model['name']}")
            exit(1)
        
        # Set reasoning effort if specified
        if args.reasoning_effort and model_info.get("reasoning_required", False):
            model_info["reasoning_effort"] = args.reasoning_effort
        
        # Add timestamp to output file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = args.output
        
        # Check if the output file has an extension
        if "." in os.path.basename(output_file):
            base, ext = os.path.splitext(output_file)
            output_file = f"{base}_{timestamp}{ext}"
        else:
            output_file = f"{output_file}_{timestamp}.json"
        
        # Generate the comprehensive report
        try:
            generate_comprehensive_report(
                model_info=model_info,
                qa_data_file=args.qa_data,
                output_file=output_file,
                test_id=args.test_id,
                batch_size=args.batch_size
            )
        except Exception as e:
            print(f"Error generating comprehensive report: {e}")
            import traceback
            traceback.print_exc()
            exit(1)

if __name__ == "__main__":
    main() 