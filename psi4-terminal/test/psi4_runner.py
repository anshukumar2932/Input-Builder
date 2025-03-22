import subprocess
import os

def run_psi4(input_file):
    """Runs Psi4 on the given input file inside a Docker container and returns the output."""
    if not os.path.isfile(input_file):
        return "Error: Input file does not exist."

    # Get the absolute path and parent directory
    input_file = os.path.abspath(input_file)
    input_dir = os.path.dirname(input_file)

    # Run Psi4 in Docker
    try:
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{input_dir}:/work",
                "-w", "/work",
                "psi4/psi4", "psi4", os.path.basename(input_file)
            ],
            capture_output=True,
            text=True,
            timeout=60  # Timeout to prevent infinite execution
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Error: Psi4 execution timed out."
    except Exception as e:
        return f"Error: {str(e)}"
