# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Install the faery package
RUN pip install faery flask werkzeug

# Set the working directory in the container
WORKDIR /app

# Copy the rest of the application code into the container
COPY server.py .

# Command to run the server
CMD ["python", "server.py"]