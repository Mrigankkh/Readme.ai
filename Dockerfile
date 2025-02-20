# Dockerfile

# 1. Base image
FROM python:3.9-slim

# 2. Update system packages & install git (needed for cloning repos)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 3. Create a working directory
WORKDIR /app

# 4. Copy requirements and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your application code
COPY . /app/

# 6. Expose the port that Flask will run on
EXPOSE 5000

# 7. Set environment variable to force stdout logging (optional)
ENV PYTHONUNBUFFERED 1

# 8. Command to start the Flask app
CMD ["python", "app.py"]
