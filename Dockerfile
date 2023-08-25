# Use an official Python runtime as the base image
FROM python:3.11.4-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Git
RUN apt-get update && apt-get install -y git

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the current directory contents into the container
COPY . .

# Copy the entrypoint script into the container
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh


# Establece la variable de entorno para el proceso de inicialización
ENV INIT_PROCESS true

# Expose the port the app runs on
EXPOSE 5000

# Define the entrypoint script to run
ENTRYPOINT ["/app/entrypoint.sh"]
