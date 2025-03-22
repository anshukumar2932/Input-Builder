# Use an official Docker-enabled Python image
FROM docker:latest

# Install Python and necessary packages
RUN apk add --no-cache python3 py3-pip

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Docker inside the container (needed for Docker-in-Docker)
RUN apk add --no-cache docker-cli

# Copy the application files
COPY . .

# Start Docker inside the container
CMD ["sh", "-c", "dockerd-entrypoint.sh & gunicorn -b 0.0.0.0:5000 app:app"]
