import os
import json
import requests
import re

from utils import get_file_size, is_valid_file
from dotenv import load_dotenv

load_dotenv()

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
if not anthropic_api_key:
    raise ValueError("No Anthropic API key set in environment variable ANTHROPIC_API_KEY")

anthropic_headers = {
    "x-api-key": anthropic_api_key,
    "Content-Type": "application/json",
    "anthropic-version": "2023-06-01"  # Adjust as needed
}

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

# Helper function from your code to remove boilerplate from LLM's ranking response
def clean_llm_response(response):
    """
    Takes the LLM's raw response and extracts the ranked file list.
    It removes any boilerplate or unnecessary text.
    Example line format: "1. FileName (Directory): Size"
    """
    pattern = r"\d+\.\s+[^\(\)]+(?:\([^\)]+\))?:\s*\d+(\.\d+)?\s*KB?"
    rankings = re.findall(pattern, response)
    if rankings:
        # If we found matches, reconstruct them from the response lines
        # However, your usage might differ. Alternatively, you can just return response if you trust the format
        # But let's do a simpler approach: we know each line is captured, let's return the matched lines themselves
        # Actually, we need the lines from the response, not just the "size" part
        # So typically you'd do a line-based approach:
        lines = response.strip().split("\n")
        # Keep only lines that match the ranking format:
        valid_lines = []
        rank_line_pattern = re.compile(r'^\d+\.\s+.+\(.+\):\s*\d+(\.\d+)?\s*KB')
        for line in lines:
            if rank_line_pattern.search(line.strip()):
                valid_lines.append(line.strip())
        if valid_lines:
            return "\n".join(valid_lines)
        else:
            return None
    else:
        return None

def get_file_rankings(repo_metadata_json, max_retries=2):
    """
    Ask the LLM to rank the files based on the provided repo metadata.
    Retries twice if response format is incorrect.
    """
    prompt = (
        "Here is a list of files in the repository with their directory location and size. "
        "Please rank these files based on their relevance for generating a README for this project. "
        "Consider the file names, directory locations, and sizes when ranking. "
        "Do not include any explanations or additional text. Just return the rankings in the format: "
        "'1. FileName (Directory): Size'.\n\n"
        "Repo Metadata:\n"
        f"{repo_metadata_json}\n\n"
        "Rank the files from most relevant to least relevant for README generation."
    )

    payload = {
        "model": "claude-3-5-sonnet-20241022",  # or your chosen model
        "system": "You are an assistant that ranks files based on their relevance to README generation.",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.2
    }

    retries = 0
    while retries < max_retries:
        try:
            response = requests.post("https://api.anthropic.com/v1/messages", json=payload, headers=anthropic_headers)
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                if content and isinstance(content, list):
                    return content[0].get("text", "")  # raw text
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


# CHANGED / ADDED: A small helper to parse lines like "1. main.py (src): 4.2 KB"
# so we can map them to the actual file path in the repo.
def parse_ranked_lines_to_paths(ranked_lines, repo_dir):
    """
    Each line is like:
       "1. main.py (src): 4.2 KB"
    We want to parse out 'main.py', 'src', etc. so we can find the actual path.
    """
    results = []
    line_pattern = re.compile(r'^\d+\.\s+(.+)\((.*?)\):\s*([\d\.]+)\s*KB')
    for line in ranked_lines:
        match = line_pattern.search(line)
        if match:
            file_name = match.group(1).strip()
            directory = match.group(2).strip()
            # We won't worry about size right now, since we already validated the file
            # Construct the actual path
            possible_path = os.path.join(repo_dir, directory, file_name)
            if not os.path.exists(possible_path):
                # Maybe directory is '.', or there's a path mismatch
                possible_path2 = os.path.join(repo_dir, file_name)
                if os.path.exists(possible_path2):
                    possible_path = possible_path2
            results.append(possible_path)
    return results


def summarize_repo(repo_dir):
    """
    1) Build metadata
    2) Get LLM-based ranking
    3) Keep top 80% of files, skip bottom 20%
    4) Summarize content of that top 80%
    5) Generate final README from combined text
    """
    # 1) Build metadata
    repo_metadata = build_repo_metadata(repo_dir)
    # Convert to JSON (or text) for LLM
    repo_metadata_json = json.dumps(repo_metadata, indent=2)

    # 2) Get ranking from LLM
    ranking_response = get_file_rankings(repo_metadata_json)
    if ranking_response.startswith("Error:"):
        return ranking_response  # bail on error

    # Clean it up
    cleaned_ranking = clean_llm_response(ranking_response)
    if not cleaned_ranking:
        return "Error: No valid ranking found."

    ranking_lines = cleaned_ranking.split("\n")
    total_files = len(ranking_lines)
    if total_files == 0:
        return "No files were ranked."

    # CHANGED / ADDED: Now we keep top 80% and skip last 20%
    cutoff = int(0.8 * total_files)
    top_80_lines = ranking_lines[:cutoff]

    # Turn those lines into actual file paths
    file_paths_to_summarize = parse_ranked_lines_to_paths(top_80_lines, repo_dir)

    if len(file_paths_to_summarize) == 0:
        return "No files to summarize after filtering."

    file_summaries = []
    for file_path in file_paths_to_summarize:
        # Quick double-check we haven't gone over 100 KB, etc.
        if os.path.exists(file_path):
            if os.path.getsize(file_path) < 100 * 1024:  # or is_valid_file logic
                try:
                    with open(file_path, 'r', errors='ignore') as f:
                        content = f.read()
                    # Add to file_summaries
                    filename_only = os.path.basename(file_path)
                    file_summaries.append(f"Filename: {filename_only}\nContent:\n{content}\n")
                except Exception as e:
                    print(f"Skipping file {file_path} due to error: {e}")
                    continue

    if not file_summaries:
        return "No summarizable files found in top 80%."

    combined_text = "\n".join(file_summaries)

    # Build prompt for final README
    prompt = (
        "\n\nHuman: Based on the following repository contents, generate a clear, concise README "
        "that explains the purpose, structure, and usage of the repository.\n\n"
        f"{combined_text}\n\nAssistant:"
    )
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "system": "You are a helpful assistant that summarizes code repositories.",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
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
