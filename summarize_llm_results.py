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
        
        # Extract other metadata
        result = {
            'file': os.path.basename(json_file),
            'test_name': test_name,
            'model': metadata.get('model', 'unknown'),
            'total_questions': metadata.get('total_questions', 0),
            'total_correct': metadata.get('total_correct', 'N/A'),
            'total_incorrect': metadata.get('total_incorrect', 'N/A'),
            'accuracy': metadata.get('accuracy', 'N/A'),
            'total_duration_seconds': metadata.get('total_duration_seconds', 0),
            'total_cost': metadata.get('costs', {}).get('total_cost', 0)
        }
        
        # Format accuracy as percentage if it exists
        if result['accuracy'] != 'N/A':
            result['accuracy'] = f"{result['accuracy']:.2%}"
            
        return result
    except Exception as e:
        print(f"Error processing {json_file}: {e}")
        return None

def summarize_results(directory):
    """Summarize results from all JSON files in the directory."""
    json_files = find_json_files(directory)
    
    if not json_files:
        print(f"No JSON files found in {directory}")
        return
    
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
    
    # Select columns to display
    display_columns = [
        'test_name', 
        'model', 
        'total_questions', 
        'total_correct', 
        'total_incorrect', 
        'accuracy', 
        'total_duration_seconds', 
        'total_cost'
    ]
    
    # Display the table
    print("\nSummary of LLM Results:")
    print(tabulate(df[display_columns], headers='keys', tablefmt='grid', showindex=False))
    
    # Calculate and display averages by model
    print("\nAverages by Model:")
    model_avg = df.groupby('model').agg({
        'total_questions': 'mean',
        'total_duration_seconds': 'mean',
        'total_cost': 'mean'
    }).reset_index()
    
    # Add accuracy calculation for models that have it
    accuracy_data = []
    for model in model_avg['model']:
        model_files = df[df['model'] == model]
        if 'N/A' not in model_files['accuracy'].values:
            # Convert percentage strings back to floats for calculation
            accuracies = [float(acc.strip('%'))/100 for acc in model_files['accuracy']]
            avg_accuracy = sum(accuracies) / len(accuracies)
            accuracy_data.append((model, f"{avg_accuracy:.2%}"))
    
    # Add accuracy column to model_avg if we have data
    if accuracy_data:
        accuracy_df = pd.DataFrame(accuracy_data, columns=['model', 'avg_accuracy'])
        model_avg = model_avg.merge(accuracy_df, on='model', how='left')
    
    print(tabulate(model_avg, headers='keys', tablefmt='grid', showindex=False))

def main():
    parser = argparse.ArgumentParser(description='Summarize LLM results from JSON files')
    parser.add_argument('--directory', default='outputs', help='Directory containing LLM result JSON files')
    
    args = parser.parse_args()
    
    summarize_results(args.directory)

if __name__ == "__main__":
    main() 