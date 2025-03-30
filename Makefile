# Makefile for managing the project with Docker and Poetry

DOCKER_COMPOSE=docker-compose
POETRY=poetry

# Start the application with Docker Compose
up:
	$(DOCKER_COMPOSE) up --build

# Stop the application
down:
	$(DOCKER_COMPOSE) down

# Run tests inside the Docker container (if you have any tests)
test:
	$(POETRY) run pytest

# Format the code (if you use a tool like black or autopep8)
format:
	$(POETRY) run black .

# Lint the code (if you use a linter like flake8)
lint:
	$(POETRY) run flake8 .
