from flask import Flask, request, render_template, send_file
import os
import psi4_runner

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Handle file upload
        if "file" not in request.files:
            return "No file part"

        file = request.files["file"]
        if file.filename == "":
            return "No selected file"

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Run Psi4
        output = psi4_runner.run_psi4(filepath)

        # Save output to file
        output_file = filepath + ".out"
        with open(output_file, "w") as f:
            f.write(output)

        return render_template("result.html", output=output, output_file=output_file)

    return render_template("index.html")

@app.route("/print/<path:filename>")
def print_output(filename):
    file_path = os.path.join(UPLOAD_FOLDER, os.path.basename(filename))

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            output_content = f.read()
        
        print("\n===== Output File Content =====\n")
        print(output_content)  # This prints to the Flask console

        return f"<pre>{output_content}</pre>"  # Show in browser
    else:
        return "File not found", 404



if __name__ == "__main__":
    app.run(debug=True)
