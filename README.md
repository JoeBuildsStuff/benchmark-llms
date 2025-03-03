# LLM Benchmarking Framework

A comprehensive framework for benchmarking Large Language Models (LLMs) on multiple-choice question answering tasks. This project allows you to evaluate and compare the performance of different LLMs on standardized question sets.

Current Results:

<div style="overflow-x: auto;">
<table>
  <thead>
    <tr>
      <th>test_name</th>
      <th>model</th>
      <th>total_questions</th>
      <th>total_correct</th>
      <th>total_incorrect</th>
      <th>accuracy</th>
      <th>total_duration_seconds</th>
      <th>total_cost</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>cloud-practitioner-clf-c02</td>
      <td>gpt-3.5-turbo-0125</td>
      <td>65</td>
      <td>61</td>
      <td>4</td>
      <td>93.85%</td>
      <td>37.8541</td>
      <td>0.005078</td>
    </tr>
    <tr>
      <td>cloud-practitioner-clf-c02</td>
      <td>gpt-4-0613</td>
      <td>65</td>
      <td>64</td>
      <td>1</td>
      <td>98.46%</td>
      <td>53.7187</td>
      <td>0.17715</td>
    </tr>
    <tr>
      <td>cloud-practitioner-clf-c02</td>
      <td>gpt-4-turbo-2024-04-09</td>
      <td>65</td>
      <td>64</td>
      <td>1</td>
      <td>98.46%</td>
      <td>299.324</td>
      <td>0.36475</td>
    </tr>
    <tr>
      <td>cloud-practitioner-clf-c02</td>
      <td>gpt-4o-2024-11-20</td>
      <td>65</td>
      <td>65</td>
      <td>0</td>
      <td>100.00%</td>
      <td>183.454</td>
      <td>0.13905</td>
    </tr>
    <tr>
      <td>cloud-practitioner-clf-c02</td>
      <td>gpt-4o-mini-2024-07-18</td>
      <td>65</td>
      <td>63</td>
      <td>2</td>
      <td>96.92%</td>
      <td>122.595</td>
      <td>0.004728</td>
    </tr>
    <tr>
      <td>cloud-practitioner-clf-c02</td>
      <td>o1-2024-12-17</td>
      <td>65</td>
      <td>58</td>
      <td>6</td>
      <td>89.23%</td>
      <td>214.659</td>
      <td>0.710865</td>
    </tr>
    <tr>
      <td>cloud-practitioner-clf-c02</td>
      <td>o1-2024-12-17</td>
      <td>65</td>
      <td>57</td>
      <td>6</td>
      <td>87.69%</td>
      <td>296.697</td>
      <td>1.28422</td>
    </tr>
    <tr>
      <td>cloud-practitioner-clf-c02</td>
      <td>o1-mini-2024-09-12</td>
      <td>65</td>
      <td>65</td>
      <td>0</td>
      <td>100.00%</td>
      <td>288.638</td>
      <td>0.145175</td>
    </tr>
    <tr>
      <td>cloud-practitioner-clf-c02</td>
      <td>o3-mini-2025-01-31</td>
      <td>65</td>
      <td>63</td>
      <td>2</td>
      <td>96.92%</td>
      <td>346.619</td>
      <td>0.197295</td>
    </tr>
    <tr>
      <td>cloud-practitioner-clf-c02</td>
      <td>o3-mini-2025-01-31</td>
      <td>65</td>
      <td>60</td>
      <td>5</td>
      <td>92.31%</td>
      <td>189.791</td>
      <td>0.0514217</td>
    </tr>
    <tr>
      <td>solutions-architect-associate-saa-c03</td>
      <td>gpt-3.5-turbo-0125</td>
      <td>65</td>
      <td>53</td>
      <td>12</td>
      <td>81.54%</td>
      <td>57.0788</td>
      <td>0.011824</td>
    </tr>
    <tr>
      <td>solutions-architect-associate-saa-c03</td>
      <td>gpt-4-0613</td>
      <td>65</td>
      <td>61</td>
      <td>4</td>
      <td>93.85%</td>
      <td>103.803</td>
      <td>0.45126</td>
    </tr>
    <tr>
      <td>solutions-architect-associate-saa-c03</td>
      <td>gpt-4-turbo-2024-04-09</td>
      <td>65</td>
      <td>62</td>
      <td>3</td>
      <td>95.38%</td>
      <td>654.962</td>
      <td>0.90569</td>
    </tr>
    <tr>
      <td>solutions-architect-associate-saa-c03</td>
      <td>gpt-4o-2024-11-20</td>
      <td>65</td>
      <td>63</td>
      <td>2</td>
      <td>96.92%</td>
      <td>388.828</td>
      <td>0.287567</td>
    </tr>
    <tr>
      <td>solutions-architect-associate-saa-c03</td>
      <td>gpt-4o-mini-2024-07-18</td>
      <td>65</td>
      <td>60</td>
      <td>5</td>
      <td>92.31%</td>
      <td>304.82</td>
      <td>0.0126082</td>
    </tr>
    <tr>
      <td>solutions-architect-associate-saa-c03</td>
      <td>o1-2024-12-17</td>
      <td>65</td>
      <td>58</td>
      <td>7</td>
      <td>89.23%</td>
      <td>705.665</td>
      <td>3.94299</td>
    </tr>
    <tr>
      <td>solutions-architect-associate-saa-c03</td>
      <td>o1-2024-12-17</td>
      <td>65</td>
      <td>58</td>
      <td>6</td>
      <td>89.23%</td>
      <td>393.679</td>
      <td>1.96041</td>
    </tr>
    <tr>
      <td>solutions-architect-associate-saa-c03</td>
      <td>o1-mini-2024-09-12</td>
      <td>65</td>
      <td>65</td>
      <td>0</td>
      <td>100.00%</td>
      <td>423.585</td>
      <td>0.268451</td>
    </tr>
    <tr>
      <td>solutions-architect-associate-saa-c03</td>
      <td>o3-mini-2025-01-31</td>
      <td>65</td>
      <td>63</td>
      <td>2</td>
      <td>96.92%</td>
      <td>539.455</td>
      <td>0.344227</td>
    </tr>
    <tr>
      <td>solutions-architect-associate-saa-c03</td>
      <td>o3-mini-2025-01-31</td>
      <td>65</td>
      <td>64</td>
      <td>1</td>
      <td>98.46%</td>
      <td>203.692</td>
      <td>0.0811162</td>
    </tr>
    <tr>
      <td>solutions-architect-professional-sap-c02</td>
      <td>gpt-3.5-turbo-0125</td>
      <td>75</td>
      <td>33</td>
      <td>42</td>
      <td>44.00%</td>
      <td>87.5845</td>
      <td>0.0215195</td>
    </tr>
    <tr>
      <td>solutions-architect-professional-sap-c02</td>
      <td>gpt-4-0613</td>
      <td>75</td>
      <td>53</td>
      <td>22</td>
      <td>70.67%</td>
      <td>174.844</td>
      <td>0.91485</td>
    </tr>
    <tr>
      <td>solutions-architect-professional-sap-c02</td>
      <td>gpt-4-turbo-2024-04-09</td>
      <td>75</td>
      <td>53</td>
      <td>22</td>
      <td>70.67%</td>
      <td>888.426</td>
      <td>1.26631</td>
    </tr>
    <tr>
      <td>solutions-architect-professional-sap-c02</td>
      <td>gpt-4o-2024-11-20</td>
      <td>75</td>
      <td>56</td>
      <td>19</td>
      <td>74.67%</td>
      <td>437.607</td>
      <td>0.42255</td>
    </tr>
    <tr>
      <td>solutions-architect-professional-sap-c02</td>
      <td>gpt-4o-mini-2024-07-18</td>
      <td>75</td>
      <td>54</td>
      <td>21</td>
      <td>72.00%</td>
      <td>431.361</td>
      <td>0.0189192</td>
    </tr>
    <tr>
      <td>solutions-architect-professional-sap-c02</td>
      <td>o1-2024-12-17</td>
      <td>75</td>
      <td>66</td>
      <td>9</td>
      <td>88.00%</td>
      <td>655.529</td>
      <td>3.69163</td>
    </tr>
    <tr>
      <td>solutions-architect-professional-sap-c02</td>
      <td>o1-2024-12-17</td>
      <td>75</td>
      <td>68</td>
      <td>7</td>
      <td>90.67%</td>
      <td>1330.82</td>
      <td>8.23868</td>
    </tr>
    <tr>
      <td>solutions-architect-professional-sap-c02</td>
      <td>o1-mini-2024-09-12</td>
      <td>75</td>
      <td>62</td>
      <td>13</td>
      <td>82.67%</td>
      <td>595.887</td>
      <td>0.403484</td>
    </tr>
    <tr>
      <td>solutions-architect-professional-sap-c02</td>
      <td>o3-mini-2025-01-31</td>
      <td>75</td>
      <td>59</td>
      <td>16</td>
      <td>78.67%</td>
      <td>265.384</td>
      <td>0.134382</td>
    </tr>
    <tr>
      <td>solutions-architect-professional-sap-c02</td>
      <td>o3-mini-2025-01-31</td>
      <td>75</td>
      <td>66</td>
      <td>9</td>
      <td>88.00%</td>
      <td>1051.07</td>
      <td>0.720844</td>
    </tr>
  </tbody>
</table>
</div>

## Project Overview

This framework provides a complete pipeline for:
1. Sending questions to various LLM models
2. Calculating the costs of API calls
3. Extracting answer selections from model responses
4. Processing question and answer files into a structured format
5. Evaluating model accuracy against correct answers
6. Summarizing and comparing results across models

## Components

The project consists of several Python scripts that work together:

1. **[get-llm-answers.py](README_get-llm-answers.md)**: Sends questions to LLM models and collects responses
2. **[calculate_costs.py](README_calculate_costs.md)**: Calculates token usage costs for each model response
3. **[analyze_model_answers.py](README_analyze_model_answers.md)**: Extracts answer selections from model responses
4. **[process_qa_to_json.py](README_process_qa_to_json.md)**: Processes question and answer files into a structured JSON format
5. **[evaluate_llm_answers.py](README_evaluate_llm_answers.md)**: Evaluates model answers against correct answers
6. **[summarize_llm_results.py](README_summarize_llm_results.md)**: Generates summary tables and statistics

## Workflow

The typical workflow for using this framework is:

1. **Prepare Questions**: Create or obtain question and answer files in markdown format
2. **Process Q&A Files**: Convert question and answer files to structured JSON
   ```bash
   python process_qa_to_json.py --input questions/ --output outputs/qa_data.json
   ```
3. **Run Models**: Send questions to various LLM models
   ```bash
   python get-llm-answers.py --questions questions/exam-name.md --models gpt-4o-2024-11-20 o1-2024-12-17
   ```
4. **Calculate Costs**: Add cost information to the response files
   ```bash
   python calculate_costs.py outputs/ --recursive
   ```
5. **Analyze Answers**: Extract answer selections from model responses
   ```bash
   python analyze_model_answers.py outputs/
   ```
6. **Evaluate Accuracy**: Compare model answers with correct answers
   ```bash
   python evaluate_llm_answers.py outputs/ --qa_data outputs/qa_data.json
   ```
7. **Summarize Results**: Generate summary tables and statistics
   ```bash
   python summarize_llm_results.py --directory outputs/
   ```

## Directory Structure

```
benchmark-llms/
├── get-llm-answers.py           # Script to send questions to LLMs
├── calculate_costs.py           # Script to calculate token usage costs
├── analyze_model_answers.py     # Script to extract answer selections
├── process_qa_to_json.py        # Script to process Q&A files
├── evaluate_llm_answers.py      # Script to evaluate model accuracy
├── summarize_llm_results.py     # Script to generate summary statistics
├── questions/                   # Directory for question and answer files
│   ├── exam-name-question.md    # Question file
│   └── exam-name-answers.md     # Answer file
└── outputs/                     # Directory for output files
    ├── qa_data.json             # Processed Q&A data
    └── model_timestamp.json     # Model response files
```

## Requirements

- Python 3.8+
- OpenAI API key (set as environment variable `OPENAI_API_KEY`)
- Required Python packages:
  - openai
  - tqdm
  - pandas
  - tabulate
  - argparse
  - concurrent.futures

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/benchmark-llms.git
   cd benchmark-llms
   ```

2. Install required packages:
   ```bash
   pip install openai tqdm pandas tabulate
   ```

3. Set up your OpenAI API key:
   ```bash
   export OPENAI_API_KEY='your-api-key'
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the API access
- Anthropic for Claude models
- Contributors to the question datasets 