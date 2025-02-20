import os
import subprocess
import shutil
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set your Anthropic API key from an environment variable
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
if not anthropic_api_key:
    raise ValueError("No Anthropic API key set in environment variable ANTHROPIC_API_KEY")

# Define headers for Anthropic API requests (including required version header)
anthropic_headers = {
    "x-api-key": anthropic_api_key,
    "Content-Type": "application/json",
    "anthropic-version": "2023-06-01"  # Adjust per documentation if needed
}

@app.route('/')
def home():
    # Returns a basic HTML page with a form to input GitHub profile and repo,
    # and areas to display the generated README both as raw markdown and as rendered HTML.
    return '''
    <html>
      <head>
         <title>README Generator</title>
         <!-- Include Marked.js from CDN to convert Markdown to HTML -->
         <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
         <style>
           body { font-family: Arial, sans-serif; margin: 20px; }
           .container { display: flex; gap: 20px; }
           .box { flex: 1; border: 1px solid #ccc; padding: 10px; }
           textarea { width: 100%; height: 400px; }
         </style>
      </head>
      <body>
         <h1>README Generator</h1>
         <form id="repoForm">
            <label for="profile">GitHub Profile Name:</label>
            <input type="text" id="profile" name="profile" required><br><br>
            <label for="repo">Repository Name:</label>
            <input type="text" id="repo" name="repo" required><br><br>
            <button type="submit">Generate README</button>
         </form>
         <hr>
         <div id="result" style="display:none;">
           <h2>Generated README (Markdown)</h2>
           <div class="container">
             <div class="box">
               <h3>Raw Markdown</h3>
               <textarea id="rawMarkdown" readonly></textarea>
             </div>
             <div class="box">
               <h3>Preview</h3>
               <div id="markdownPreview"></div>
             </div>
           </div>
         </div>
         <script>
           document.getElementById('repoForm').addEventListener('submit', function(e) {
             e.preventDefault();
             var profile = document.getElementById('profile').value;
             var repo = document.getElementById('repo').value;
             var formData = new FormData();
             formData.append('profile', profile);
             formData.append('repo', repo);
             fetch('/generate-readme', {
               method: 'POST',
               body: formData
             })
             .then(response => response.json())
             .then(data => {
               var markdown = data.readme;
               document.getElementById('rawMarkdown').value = markdown;
               document.getElementById('markdownPreview').innerHTML = marked.parse(markdown);
               document.getElementById('result').style.display = 'block';
             })
             .catch(err => {
               alert('Error generating README: ' + err);
             });
           });
         </script>
      </body>
    </html>
    '''

def summarize_repo(repo_dir):
    """
    Walk through the repository directory, read the contents of files that are
    small enough (e.g., <100KB) and not in ignored lists, and generate a summary
    using Anthropic's Messages API.
    """
    file_summaries = []
    # Define lists to ignore non-contributory files
    ignored_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.lock'}
    ignored_filenames = {'package-lock.json', '.gitignore', 'yarn.lock', '_redirects'}
    
    for root, dirs, files in os.walk(repo_dir):
        # Skip hidden directories like .git
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            # Skip hidden files
            if file.startswith('.'):
                continue
            if file in ignored_filenames:
                continue
            ext = os.path.splitext(file)[1].lower()
            if ext in ignored_extensions:
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
    
    # Construct the prompt using Anthropic's required conversation format.
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
    
    try:
        response = requests.post("https://api.anthropic.com/v1/messages", json=payload, headers=anthropic_headers)
        if response.status_code == 200:
            data = response.json()
            # According to documentation, the output is in the "content" list with a "text" field.
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

@app.route('/generate-readme', methods=['POST'])
def generate_readme():
    # Accept form data (or JSON) for GitHub profile and repository
    if request.form:
        profile = request.form.get('profile')
        repo = request.form.get('repo')
        if not profile or not repo:
            return jsonify({"error": "Both profile and repository are required."}), 400
        github_url = f"https://github.com/{profile}/{repo}.git"
    else:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input provided."}), 400
        github_url = data.get('github_url')
        if not github_url:
            return jsonify({"error": "GitHub URL is required."}), 400

    # Create a temporary directory to clone the repository
    clone_dir = "/tmp/repo-clone"
    if os.path.exists(clone_dir):
        shutil.rmtree(clone_dir)
    try:
        # Clone only the main branch
        subprocess.run(["git", "clone", "--depth", "1", "--branch", "main", github_url, clone_dir], check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Failed to clone repository: {str(e)}"}), 500

    # Generate the README summary from the repository
    summary = summarize_repo(clone_dir)
    
    return jsonify({"readme": summary})

if __name__ == "__main__":
    # The container listens on port 5173
    app.run(host="0.0.0.0", port=5173)
