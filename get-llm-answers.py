
#function to parse questions from a markdown file separated by ----
def parse_questions(file_path):
    """Parse questions from a markdown file separated by ----"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    questions = content.split('----')
    return [q.strip() for q in questions if q.strip()]


# run the script
if __name__ == "__main__":
    questions = parse_questions("questions/cloud-practitioner-clf-c02.md")
    print(questions)
