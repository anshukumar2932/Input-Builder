from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Psi4 Web Server!"

@app.route('/run', methods=['POST'])
def run_psi4():
    file = request.files.get('file')

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    # Save file
    filepath = "/app/input.in"
    file.save(filepath)

    # Run Psi4
    command = ["psi4", filepath]
    result = subprocess.run(command, capture_output=True, text=True)

    return jsonify({"output": result.stdout})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
