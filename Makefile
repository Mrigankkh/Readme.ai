run-local:
	docker build -t readme-generator:latest .  
	docker run -p 5173:5173  readme-generator:latest