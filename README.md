
# GitHub README Generator

A web application that automatically generates README files for GitHub repositories using AI-powered analysis. 

Fun fact: This readme was made by this app!

## Overview

This tool clones GitHub repositories and uses the Anthropic Claude API to analyze their contents and generate comprehensive README documentation. It provides both raw markdown and rendered HTML previews of the generated README.

## Features

- Web-based interface for inputting GitHub repository details
- Real-time markdown preview using Marked.js
- Intelligent file filtering (ignores binary files, large files, and common non-contributory files)
- Docker containerization for easy deployment
- Anthropic Claude API integration for AI-powered analysis

## Prerequisites

- Docker
- Anthropic API key

## Setup

1. Clone this repository
2. Create a `.env` file with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_key_here
   ```
3. Build and run using Docker:
   ```
   make run-local
   ```

## Usage

1. Visit `http://localhost:5173` in your web browser
2. Enter a GitHub profile name and repository name
3. Click "Generate README"
4. View the generated README in both markdown and rendered HTML formats

## Technical Details

- Built with Flask (Python web framework)
- Uses Anthropic's Claude 3 Sonnet model for repository analysis
- Runs on port 5173 by default
- Includes error handling for repository cloning and API interactions

## Project Structure

- `app.py`: Main Flask application and logic
- `Dockerfile`: Container configuration
- `requirements.txt`: Python dependencies
- `Makefile`: Build and run commands

## License
