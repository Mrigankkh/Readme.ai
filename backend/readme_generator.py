
import os
import json
import requests

from dotenv import load_dotenv

load_dotenv()

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
if not anthropic_api_key:
    raise ValueError("No Anthropic API key set in environment variable ANTHROPIC_API_KEY")

anthropic_headers = {
    "x-api-key": anthropic_api_key,
    "Content-Type": "application/json",
    "anthropic-version": "2023-06-01"  # Adjust per documentation if needed
}


IGNORE_LIST_PATH = os.path.join(os.path.dirname(__file__), 'config', 'ignore_file_list.json')
try:
    with open(IGNORE_LIST_PATH, 'r') as f:
        ignore_data = json.load(f)
except Exception as e:
    raise FileNotFoundError(f"Unable to load ignore file list at {IGNORE_LIST_PATH}: {e}")

IGNORED_FILES = set(ignore_data.get("files", []))
IGNORED_DIRS = set(ignore_data.get("directories", []))
IGNORED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.lock', '.json'}


def summarize_repo(repo_dir):
    """
    Walk through the repository directory, read the contents of files that are
    small enough (e.g., <100KB) and not in ignored lists, and generate a summary
    using Anthropic's Messages API.
    """
    file_summaries = []
    # Define lists to ignore non-contributory files
    ignored_filenames = {'package-lock.json', '.gitignore', 'yarn.lock', '_redirects'}
    
    for root, dirs, files in os.walk(repo_dir):
        
        dirs[:] = [d for d in dirs if not d.startswith('.') and d  not in IGNORED_DIRS]
        for file in files:
         
            if file.startswith('.'):
                continue
            if file in IGNORED_FILES:
                continue
            
            ext = os.path.splitext(file)[1].lower()
            if ext in IGNORED_EXTENSIONS:
                continue
            
            file_path = os.path.join(root, file)
            try:
                # Skip files larger than 100KB
                if os.path.getsize(file_path) < 100 * 1024:
                    with open(file_path, 'r', errors='ignore') as f:
                        content = f.read()
                    print(f"Processing file: {file}")  # Debug output
                    file_summaries.append(f"Filename: {file}\nContent:\n{content}\n")
            except Exception as e:
                print(f"Skipping file {file} due to error: {e}")
                continue
                
    if not file_summaries:
        return "No summarizable files found in repository."
    
    combined_text = "\n".join(file_summaries)
    
    prompt = (
        "\n\nHuman: Based on the following repository contents, generate a clear, concise README that explains the purpose, structure, and usage of the repository.\n\n"
        f"{combined_text}\n\nAssistant:"
    )
    
    payload = {
         "model": "claude-3-5-sonnet-20241022",  # Use a model available to your account
         "system": "You are a helpful assistant that summarizes code repositories.",
         "messages": [{"role": "user", "content": prompt}],
         "max_tokens": 500,
         "temperature": 0.7
    }
    
    
    print('Combined text length:', len(combined_text))
    return 
    try:
        response = requests.post("https://api.anthropic.com/v1/messages", json=payload, headers=anthropic_headers)
        if response.status_code == 200:
            data = response.json()
            content_list = data.get("content", [])
            if content_list and isinstance(content_list, list):
                summary = content_list[0].get("text", "")
            else:
                summary = ""
            return summary.strip()
        else:
            return f"Error: {response.status_code} {response.text}"
    except Exception as e:
        return f"Error in summarization: {e}"
