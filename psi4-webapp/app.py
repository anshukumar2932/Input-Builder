import re
import os
import time
import threading
import subprocess
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def run_psi4(input_path):
    """Runs Psi4 on the given input file and extracts key output."""
    input_fullpath = os.path.join(UPLOAD_FOLDER, input_path)
    temp=input_fullpath.split(".")
    output_file = f"{temp[0]}.out"

    command = f"docker run --rm -v {os.getcwd()}:/data psi4/psi4:1.9.1 psi4 /data/{input_fullpath} > {output_file}"
    subprocess.run(command, shell=True)

    return extract_important_output(output_file)

def extract_important_output(output_path):
    """Parses the Psi4 output file to get key results."""
    important_lines = []
    with open(output_path, "r") as file:
        important_lines=file.read()
        # for line in file:
            # if "Final Energy" in line or "Total Energy" in line:
            #     important_lines.append(line.strip())

    # return "\n".join(important_lines)
    return important_lines
    
def cleanup_uploads():
    """Deletes files in the uploads folder every hour."""
    while True:
        time.sleep(600)  # Wait for 10 min
        for file in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")

@app.route("/", methods=["GET", "POST"])
def index():
    """Handles file uploads and runs Psi4."""
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        result = run_psi4(file.filename)
        return render_template("result.html", output=result)  # Pass extracted output

    return render_template("index.html")
if __name__ == "__main__":
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_uploads, daemon=True)
    cleanup_thread.start()
    
    app.run(host="0.0.0.0", port=5000, debug=True)
