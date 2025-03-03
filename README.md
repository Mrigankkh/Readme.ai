
# GitHub README Generator

A web application that automatically generates README files for GitHub repositories using AI-powered analysis. 

Fun fact: This readme was made by this app!

## Overview

This tool clones GitHub repositories and uses the Anthropic Claude API to analyze their contents and generate comprehensive README documentation. It provides both raw markdown and rendered HTML previews of the generated README.

## Features

- Web-based interface for inputting GitHub repository details and receiving a Readme for that repository.
- UI features include markdown preview using Marked.js, copy & download of Markdown file.
- Dynamic file filtering based on LLM generated Relevence Ranking of repository files.
- Docker containerization of backend for easy deployment
- Anthropic Claude API integration for AI-powered Readme generation

## Screenshots
Home Page
<img width="1709" alt="image" src="https://github.com/user-attachments/assets/89ff95e8-05a2-4205-b4f4-2aa3cf77e8cb" />

Generated Markdown
<img width="1709" alt="image" src="https://github.com/user-attachments/assets/4e8d3c32-f34d-4d33-9eb5-1a5308caa418" />

Preview of generated Markdown
<img width="1709" alt="image" src="https://github.com/user-attachments/assets/8d263d2b-8864-4a85-b822-204c728e33ea" />

## Prerequisites

- Docker (Optional)
- Anthropic API key (You can use other LLM API keys including a locally running LLama but you might need to modify the API headers since Anthropic requires some Anthropic specific Headers)

## Local Setup

1. Clone this repository
2. To setup the frontend,
   ```
   cd frontend
   make setup-frontend
   ```
3. Create a `.env` file in the backend directory with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_key_here
   ```
4. Build and run the app from root directory:
   ```
   make run-local
   ```
5. (Optional) To run the backend in a Docker container, you can alternatively call the
   ```
   cd backend
   make run-backend-in-docker
   ```

## Usage

1. Run the app. See instructions on how to run in the Local Setup Section
2. Visit `http://localhost:5173` in your web browser
3. Enter a GitHub profile name and repository name
4. Click "Generate README"
5. View the generated README in both markdown and rendered HTML formats. Download/Copy the markdown depending on your usecase.

## Technical Details
### Backend
- The backend of this project is a Flask App that hosts the /generate-readme endpoint.
- Filters out junk/ obviously irrelevant files from repositories
- Calls LLM API to rank files based on relevance of the project
- Dynamically filters the bottom X% file from this ranking.
- Calls LLM API on leftover files to generate a Readme.md file.
- Includes error handling for repository cloning and API interactions.

### Frontend
- A Simple React + Vite App that has input boxes for GitHub username and reponame.

### Deployment
#### Frontend
- Frontend React WebApp is deployed on GitHub pages.
- A deployment GitHub Action is manually triggered to deploy a ne version of the WebApp on Github pages.

### Backend
- Docker Container Hosted on AWS Beanstalk
- Runs on an EC2 instance
- Beanstalk endpoint is Proxied by Cloudflare to an ACM (Amazon Certificate Manager) certified personal domain.


## Project Structure
The project is split into 2 directories, frontend and backend
### Backend
- `app.py`: Hosts the /generate-readme endpoint
- `Dockerfile`: Container configuration
- `requirements.txt`: Python dependencies
- `Makefile`: Build and run commands
### Frontend
Frontend is a simple React + Vite App.




## Future Work
- Auto deployment when main branch is updated.
- More error handling
- Code summarization for reduction of input tokens passed to LLM.
- Additional controls for markdown eg: Verbose control, Sections etc.
- UI Enhancements
