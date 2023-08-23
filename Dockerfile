# Use an official Python runtime as the base image
FROM python:3.11.4-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the current directory contents into the container
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Define the command to run the application using gunicorn
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000", "--workers=3", "--log-level=info"]
