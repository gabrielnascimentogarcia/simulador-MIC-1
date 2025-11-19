# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
# (We don't have a requirements.txt yet, so we install pygame directly)
RUN pip install --no-cache-dir pygame

# Make port 80 available to the world outside this container (not really needed for pygame but good practice)
EXPOSE 80

# Define environment variable
ENV NAME World

# Run main.py when the container launches
CMD ["python", "main.py"]
