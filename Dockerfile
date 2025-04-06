# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy poetry configuration files into the container
COPY pyproject.toml poetry.lock /app/

# Install poetry
RUN pip install poetry

# Install the project dependencies with poetry
RUN poetry install --only main

# Copy the rest of the application code into the container
COPY . /app/

# Expose the port that FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI app using Uvicorn
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
