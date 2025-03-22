import subprocess
import os
import sys

# Ensure upload directory exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def run_psi4(input_file):
    """Runs PSI4 with the given input file and returns the output."""
    try:
        output = subprocess.run(
            ["psi4", input_file],
            capture_output=True,
            text=True,
            check=True
        )
        return output.stdout
    except subprocess.CalledProcessError as e:
        return f"PSI4 execution failed:\n{e.stderr}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 app.py <input_file>")
        sys.exit(1)

    input_path = sys.argv[1]
    
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found.")
        sys.exit(1)

    # Generate PSI4 input file
    psi4_input = f"""
molecule {{
  0 1
  O  0.0  0.0  0.0
  H  0.0  0.0  0.96
  H  0.92  0.0 -0.32
}}

set basis sto-3g
energy('hf')
"""
    input_filename = os.path.join(UPLOAD_FOLDER, "input.dat")
    with open(input_filename, "w") as f:
        f.write(psi4_input)

    # Run PSI4 and print output
    result = run_psi4(input_filename)
    print(result)

if __name__ == "__main__":
    main()
