import os
import json
import requests
import re
import anthropic  # new import

from utils import get_file_size, is_valid_file
from dotenv import load_dotenv

load_dotenv()

# Anthropic API configuration
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
if not anthropic_api_key:
    raise ValueError("No Anthropic API key set in environment variable ANTHROPIC_API_KEY")

anthropic_headers = {
    "x-api-key": anthropic_api_key,
    "Content-Type": "application/json",
    "anthropic-version": "2023-06-01" 
}

client = anthropic.Anthropic()

IGNORE_LIST_PATH = os.path.join(os.path.dirname(__file__), 'config', 'ignore_file_list.json')

try:
    with open(IGNORE_LIST_PATH, 'r') as f:
        ignore_data = json.load(f)
except Exception as e:
    raise FileNotFoundError(f"Unable to load ignore file list at {IGNORE_LIST_PATH}: {e}")

IGNORED_DIRS = set(ignore_data.get("directories", []))

def build_repo_metadata(repo_dir):
    """
    Walk through the repository directory, capture file names, locations,
    and sizes, and generate a hierarchical metadata structure.
    """
    repo_metadata = {}
    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in IGNORED_DIRS]
        current_dir = os.path.relpath(root, repo_dir)
        if current_dir not in repo_metadata:
            repo_metadata[current_dir] = []
        for file in files:
            file_path = os.path.join(root, file)
            if is_valid_file(file, file_path):
                file_size = get_file_size(file_path)
                repo_metadata[current_dir].append({
                    "file_name": file,
                    "file_path": file_path,
                    "size_kb": file_size
                })
    return repo_metadata

def clean_llm_response(response):
    """
    Takes the LLM's raw response and extracts the ranked file list.
    Expected format: "1. FileName (Directory): Size"
    """
    line_pattern = re.compile(r'^\d+\.\s+(.+)\((.*?)\):\s*([\d\.]+)\s*[Kk][Bb]')
    lines = response.strip().split("\n")
    valid_lines = [line.strip() for line in lines if line_pattern.search(line.strip())]
    return "\n".join(valid_lines) if valid_lines else None

def get_file_rankings(repo_metadata_json, max_retries=2):
    """
    Ask the LLM to rank the files based on relevance.
    """
    prompt = (
        "Here is a list of files in the repository with their directory location and size. "
        "Please rank these files based on their relevance for generating a README for this project. "
        "Do not include any explanations. Return rankings in the format: '1. FileName (Directory): Size KB'.\n\n"
        "Repo Metadata:\n"
        f"{repo_metadata_json}\n\n"
        "Rank the files from most relevant to least relevant."
    )
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "system": "You are an assistant that ranks files based on their relevance to README generation.",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.2
    }
    retries = 0
    #temp
    max_retries = 1
    while retries < max_retries:
        try:
            response = requests.post("https://api.anthropic.com/v1/messages", json=payload, headers=anthropic_headers)
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                if content and isinstance(content, list):
                    return content[0].get("text", "")
                else:
                    print("Error: Invalid response structure.")
            else:
                print(f"Error: {response.status_code} {response.text}")
            retries += 1
            print(f"Retrying... ({retries}/{max_retries})")
        except Exception as e:
            print(f"Error in API request: {e}")
            retries += 1
            print(f"Retrying... ({retries}/{max_retries})")
    return "Error: Unable to get valid file rankings after multiple retries."

def parse_ranked_lines_to_paths(ranked_lines, repo_dir):
    """
    Converts a ranked line like "1. main.py (src): 4.2 KB" into a file path.
    """
    results = []
    line_pattern = re.compile(r'^\d+\.\s+(.+)\((.*?)\):\s*([\d\.]+)\s*[Kk][Bb]')
    for line in ranked_lines:
        match = line_pattern.search(line)
        if match:
            file_name = match.group(1).strip()
            directory = match.group(2).strip()
            possible_path = os.path.join(repo_dir, directory, file_name)
            if not os.path.exists(possible_path):
                possible_path2 = os.path.join(repo_dir, file_name)
                if os.path.exists(possible_path2):
                    possible_path = possible_path2
            results.append(possible_path)
    return results

def read_full(file_path, file_name):
    try:
        with open(file_path, 'r', errors='ignore') as fh:
            content = fh.read()
        return f"Filename: {file_name}\nContent:\n{content}\n"
    except Exception as e:
        return f"Filename: {file_name}\nError reading file: {e}\n"

def summarize_repo(repo_dir):
    """
    Main entry point:
      1) Build metadata
      2) Get LLM-based ranking
      3) Remove bottom 20% (keep top 80%)
      4) Process the top files
      5) Combine content and ensure token size is below 5000
      6) Generate final README
    """
    repo_metadata = build_repo_metadata(repo_dir)
    repo_metadata_json = json.dumps(repo_metadata, indent=2)
    ranking_response = get_file_rankings(repo_metadata_json)
    if ranking_response.startswith("Error:"):
        return ranking_response
    print("LLM Ranking Response:", ranking_response)
    cleaned_ranking = clean_llm_response(ranking_response)
    if not cleaned_ranking:
        return "Error: No valid ranking found."
    ranking_lines = cleaned_ranking.split("\n")
    total_files = len(ranking_lines)
    if total_files == 0:
        return "No files were ranked."
    # Keep top 80%
    cutoff_percent = 0.8 if total_files > 10 else 1
    cutoff = int(cutoff_percent * total_files)
    top_80_lines = ranking_lines[:cutoff]
    file_paths_to_summarize = parse_ranked_lines_to_paths(top_80_lines, repo_dir)
    if len(file_paths_to_summarize) == 0:
        return "No files to summarize after filtering."
    file_summaries = []
    for file_path in file_paths_to_summarize:
        if os.path.exists(file_path) and os.path.getsize(file_path) < 100 * 1024:
            file_name = os.path.basename(file_path)
            file_summaries.append(read_full(file_path, file_name))
    if not file_summaries:
        return "No summarizable files found in top 80%."

    combined_text, token_count = limit_combined_text(file_summaries, client, model="claude-3-7-sonnet-20250219", token_limit=5000)
    print(f"Final combined text token count: {token_count}")

    prompt = (
        "\n\nHuman: Analyze the repository content provided below and generate a comprehensive README. The README must include:\n"
        "- A project title at the top.\n"
        "- Directly below the title, display 4–5 tech stack badges using the markdown format: ![Static Badge](https://img.shields.io/badge/[name]-[color]).\n"
        "- A section describing the project's purpose or 'About' information.\n"
        "- A detailed explanation of the repository structure.\n"
        "- (Optional)A section on explaination of the different modules or components of the app and some high level implementation details.\n"
        "- A section listing the project's features.\n"
        "Output only the README content with no extra commentary.\n\n"
        f"{combined_text}\n\n"
        "Assistant:"
    )

    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "system": "You are a helpful assistant that summarizes code repositories and generates README markdown files.",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 0.7
    }
    print('Combined text length:', len(combined_text))
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

def get_token_count(prompt, anthropic_client, model):
    """
    Call Anthropic's token counting API for the given prompt.
    Assumes the API returns a JSON object with key 'token_count'.
    """
    messages = [{"role": "user", "content": prompt}]
    response = anthropic_client.messages.count_tokens(
        model=model,
        thinking={"type": "enabled", "budget_tokens": 16000},
        messages=messages
    )
    result = response.json()
    result = json.loads(result)
    # Adjust key based on actual response structure; here we assume 'token_count'
    return result.get("token_count", 0)

def limit_combined_text(file_summaries, anthropic_client, model, token_limit=5000):
    """
    Combine file summaries into one prompt. If the token count exceeds token_limit,
    recursively remove the lowest ranked file summary until the limit is met.
    Returns the combined text and its token count.
    """
    while True:
        combined_text = "\n".join(file_summaries)
        prompt = (
            "\n\nHuman: Based on the following repository contents, generate a clear, concise README that explains the purpose, structure, and usage of the repository.\n\n"
            f"{combined_text}\n\nAssistant:"
        )
        token_count = get_token_count(prompt, anthropic_client, model)
        print('TOken count atm is:', token_count)
        if token_count <= token_limit or not file_summaries:
            break
        # Remove the last file summary (lowest ranked)
        file_summaries.pop()
    return combined_text, token_count
