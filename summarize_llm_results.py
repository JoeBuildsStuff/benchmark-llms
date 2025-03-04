import json
import os
import argparse
from tabulate import tabulate
import pandas as pd

def load_json_file(file_path):
    """Load and parse a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def find_json_files(directory):
    """Find all JSON files in a directory and its subdirectories."""
    json_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json') and file != 'qa_data.json':
                json_files.append(os.path.join(root, file))
    return json_files

def extract_metadata(json_file):
    """Extract relevant metadata from a JSON file."""
    try:
        data = load_json_file(json_file)
        metadata = data.get('metadata', {})
        
        # Extract the test name from questions_file
        questions_file = metadata.get('questions_file', '')
        test_name = os.path.basename(questions_file).split('.')[0] if questions_file else 'unknown'
        
        # Get the model name and append reasoning effort if available
        model_name = metadata.get('model', 'unknown')
        reasoning_effort = metadata.get('reasoning_effort')
        if reasoning_effort:
            model_name = f"{model_name} ({reasoning_effort})"
        
        # Extract other metadata
        result = {
            'file': os.path.basename(json_file),
            'test_name': test_name,
            'model': model_name,
            'total_questions': metadata.get('total_questions', 0),
            'total_correct': metadata.get('total_correct', 'N/A'),
            'total_incorrect': metadata.get('total_incorrect', 'N/A'),
            'accuracy': metadata.get('accuracy', 'N/A'),
            'total_duration_seconds': metadata.get('total_duration_seconds', 0),
            'total_cost': metadata.get('costs', {}).get('total_cost', 0)
        }
        
        # Format accuracy as percentage if it exists
        if result['accuracy'] != 'N/A':
            result['accuracy_formatted'] = f"{result['accuracy']:.2%}"
        else:
            result['accuracy_formatted'] = 'N/A'
            
        return result
    except Exception as e:
        print(f"Error processing {json_file}: {e}")
        return None

def save_results_as_json(results_data, model_averages, output_file):
    """Save the results and model averages as JSON."""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Convert DataFrame to list of dictionaries for JSON serialization
    results_list = results_data.to_dict(orient='records')
    model_averages_list = model_averages.to_dict(orient='records')
    
    # Create the output structure
    output_data = {
        'summary': results_list,
        'model_averages': model_averages_list
    }
    
    # Save to file
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nResults saved to {output_file}")

def summarize_results(directory, json_output=None, print_output=True):
    """Summarize results from all JSON files in the directory."""
    json_files = find_json_files(directory)
    
    if not json_files:
        print(f"No JSON files found in {directory}")
        return
    
    if print_output:
        print(f"Found {len(json_files)} JSON files to summarize")
    
    # Extract metadata from each file
    results = []
    for file_path in json_files:
        metadata = extract_metadata(file_path)
        if metadata:
            results.append(metadata)
    
    if not results:
        print("No valid metadata found in any files")
        return
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(results)
    
    # Sort by test_name and model
    df = df.sort_values(['test_name', 'model'])
    
    # Try to create the accuracy_formatted column if accuracy exists
    if 'accuracy' in df.columns:
        df['accuracy_formatted'] = df['accuracy'].apply(
            lambda x: f"{float(x):.2%}" if isinstance(x, (int, float)) or (isinstance(x, str) and x.replace('.', '', 1).isdigit()) else 'N/A'
        )
    
    # Define desired display columns
    desired_columns = [
        'test_name', 
        'model', 
        'total_questions', 
        'total_correct', 
        'total_incorrect', 
        'accuracy_formatted', 
        'total_duration_seconds', 
        'total_cost'
    ]
    
    # Only include columns that actually exist in the DataFrame
    display_columns = [col for col in desired_columns if col in df.columns]
    
    # If accuracy_formatted doesn't exist but accuracy does, use accuracy instead
    if 'accuracy_formatted' not in display_columns and 'accuracy' in df.columns:
        display_columns = [col if col != 'accuracy_formatted' else 'accuracy' for col in display_columns]
    
    # Create a display version of the DataFrame
    display_df = df.copy()
    
    # Display the table
    print("\nSummary of LLM Results:")
    print(tabulate(display_df[display_columns], headers='keys', tablefmt='grid', showindex=False))
    
    # Calculate and display averages by model
    print("\nAverages by Model:")
    numeric_columns = ['total_questions', 'total_duration_seconds', 'total_cost']
    available_numeric_columns = [col for col in numeric_columns if col in df.columns]
    
    if available_numeric_columns:
        model_avg = df.groupby('model')[available_numeric_columns].mean().reset_index()
    else:
        model_avg = df.groupby('model').size().reset_index(name='count')
    
    # Add accuracy calculation for models that have it
    if 'accuracy' in df.columns:
        accuracy_data = []
        for model in model_avg['model']:
            model_files = df[df['model'] == model]
            # Use the original accuracy values for calculation
            accuracies = [float(acc) for acc in model_files['accuracy'] 
                         if isinstance(acc, (int, float)) or 
                         (isinstance(acc, str) and acc.replace('.', '', 1).isdigit())]
            if accuracies:
                avg_accuracy = sum(accuracies) / len(accuracies)
                accuracy_data.append((model, avg_accuracy, f"{avg_accuracy:.2%}"))
        
        # Add accuracy column to model_avg if we have data
        if accuracy_data:
            accuracy_df = pd.DataFrame(accuracy_data, columns=['model', 'avg_accuracy', 'avg_accuracy_formatted'])
            model_avg = model_avg.merge(accuracy_df, on='model', how='left')
    
    # Display the model averages
    print(tabulate(model_avg, headers='keys', tablefmt='grid', showindex=False))
    
    # Save results as JSON if requested
    if json_output:
        save_results_as_json(df, model_avg, json_output)

def main():
    from datetime import datetime
    parser = argparse.ArgumentParser(description='Summarize LLM results from JSON files')
    parser.add_argument('--directory', default='outputs', help='Directory containing LLM result JSON files')
    parser.add_argument('--json', default=os.path.join('outputs', 'summary.json'), 
                        help='Output file path for JSON results (default: outputs/summary.json)')
    
    args = parser.parse_args()
    
    summarize_results(args.directory, args.json, not args.no_print)

if __name__ == "__main__":
    main() 