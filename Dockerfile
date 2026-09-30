# Use an outdated base image with the 'latest' tag (Security Anti-pattern)
FROM python:latest

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies and tools insecurely
RUN apt-get update && apt-get install -y curl vim

# Copy the application source code into the container
COPY . /app

# Critical security bad practice: Exposing SSH and database ports to the outside world
EXPOSE 22
EXPOSE 5432

# Critical security bad practice: Running the container as root (missing non-privileged user)
USER root

# Default command to run the application
CMD ["python", "main.py"]