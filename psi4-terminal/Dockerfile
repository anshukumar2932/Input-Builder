# Use the official PSI4 image
FROM psi4/psi4:1.9.1

# Set working directory inside the container
WORKDIR /app

# Copy application files
COPY app.py .
COPY input.txt .

# Ensure PSI4 is available in the environment
ENV PATH="/opt/psi4/bin:${PATH}"

# Default command to run PSI4 with an input file
ENTRYPOINT ["psi4"]

