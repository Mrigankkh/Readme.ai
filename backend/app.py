import os
import subprocess
import shutil
from readme_generator import summarize_repo
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS,cross_origin

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


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

@app.route('/generate-readme', methods=['POST'])
@cross_origin()
def generate_readme():
    
    
    # Temp
    #return jsonify({"Success": "Backend Hit!"}), 200

    # Accept form data (or JSON) for GitHub profile and repository
    if request.form:
        profile = request.form.get('profile')
        repo = request.form.get('repo')
        if not profile or not repo:
            return jsonify({"error": "Both profile and repository are required."}), 400
        github_url = f"https://github.com/{profile}/{repo}.git"
    else:
        return jsonify({"error": "Form Data is empty!"}), 400

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
    app.run(host="0.0.0.0", port=8000, debug = True)
