from im import *
import re
import os
import time
import threading
import subprocess
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def run_psi4(input_path):
    """Runs Psi4 using Docker and extracts key output."""
    input_fullpath = os.path.join(UPLOAD_FOLDER, input_path)
    output_file = f"{os.path.splitext(input_fullpath)[0]}.out"

    command = (
        f"docker run --rm -v {os.getcwd()}:/data psi4/psi4:1.9.1 psi4 /data/{input_fullpath} > {output_file}"
    )

    # Run the command
    process = subprocess.run(command, shell=True, text=True, capture_output=True)

    # Check for errors
    if process.returncode != 0:
        print("Error running Psi4:", process.stderr)
        return f"Error running Psi4: {process.stderr}"

    return extract_important_output(output_file)

def extract_important_output(output_path):
    """Parses the Psi4 output file to extract key results."""
    with open(output_path, "r") as file:
        return file.read()
