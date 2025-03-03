import json
import os
import argparse
from glob import glob
from datetime import datetime

def calculate_costs(response_data, model_info):
    """Calculate costs for a single response based on token usage"""
    usage = response_data.get("response", {}).get("usage", {})
    
    # Extract token counts
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    reasoning_tokens = usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
    
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

def get_model_info(model_name):
    """Get model pricing information"""
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
    
    for model in MODELS:
        if model["name"] == model_name:
            return model
    
    # Default values if model not found
    return {"input": 0, "output": 0}

def process_json_file(file_path, output_dir=None):
    """Process a single JSON file to add cost information"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Get model info for pricing
        model_name = data.get("metadata", {}).get("model", "")
        model_info = get_model_info(model_name)
        
        # Calculate costs for each response and add to the data
        total_prompt_cost = 0
        total_completion_cost = 0
        total_reasoning_cost = 0
        total_cost = 0
        total_duration = 0
        
        for response_data in data.get("responses", []):
            # Calculate costs
            costs = calculate_costs(response_data, model_info)
            
            # Add costs to the response
            response_data["costs"] = costs
            
            # Add to totals
            total_prompt_cost += costs["prompt_cost"]
            total_completion_cost += costs["completion_cost"]
            total_reasoning_cost += costs["reasoning_cost"]
            total_cost += costs["prompt_cost"] + costs["completion_cost"]
            
            # Add to total duration
            duration = response_data.get("timing", {}).get("duration_seconds", 0)
            total_duration += duration
        
        # Add total duration and costs to metadata
        if "metadata" in data:
            data["metadata"]["total_duration_seconds"] = total_duration
            data["metadata"]["costs"] = {
                "total_prompt_cost": total_prompt_cost,
                "total_completion_cost": total_completion_cost,
                "total_reasoning_cost": total_reasoning_cost,
                "total_cost": total_cost
            }
        
        # Determine output path
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.basename(file_path)
            output_path = os.path.join(output_dir, filename)
        else:
            # Overwrite the original file
            output_path = file_path
        
        # Write the updated data
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"Processed {file_path} -> {output_path}")
        return True
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Calculate and add cost information to LLM response JSON files")
    parser.add_argument("input_path", help="Path to JSON file or directory containing JSON files")
    parser.add_argument("--output-dir", help="Directory to save processed files (if not specified, original files will be overwritten)")
    parser.add_argument("--recursive", action="store_true", help="Process JSON files in subdirectories recursively")
    
    args = parser.parse_args()
    
    # Process files
    if os.path.isfile(args.input_path):
        # Process a single file
        process_json_file(args.input_path, args.output_dir)
    else:
        # Process a directory
        pattern = os.path.join(args.input_path, "**/*.json" if args.recursive else "*.json")
        files = glob(pattern, recursive=args.recursive)
        
        if not files:
            print(f"No JSON files found at {args.input_path}")
            return
        
        print(f"Found {len(files)} JSON files to process")
        success_count = 0
        for file_path in files:
            if process_json_file(file_path, args.output_dir):
                success_count += 1
        
        print(f"Processed {success_count} of {len(files)} files successfully")

if __name__ == "__main__":
    main()