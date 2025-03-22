# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Docker inside the container
RUN apt-get update && apt-get install -y docker.io

# Copy the application files
COPY . .

# Expose the port your Flask app runs on
EXPOSE 5000

# Start the application
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
