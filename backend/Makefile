start-backend-in-docker:
	docker build -t readme-generator:latest .  
	docker run -p 8000:8000  readme-generator:latest

start-backend:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	. venv/bin/activate && export FLASK_ENV=development && flask run -p 8000