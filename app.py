import os
import time
import threading
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response
from im import *

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def run_psi4(input_path):
    """Runs Psi4 on the given input file and extracts key output."""
    input_fullpath = os.path.join(UPLOAD_FOLDER, input_path)
    temp = input_fullpath.split(".")
    output_file = f"{temp[0]}.out"

    command = f"docker run --rm -v {os.getcwd()}:/data psi4/psi4:1.9.1 psi4 /data/{input_fullpath} > {output_file}"
    subprocess.run(command, shell=True)

    return extract_important_output(output_file)

def extract_important_output(output_path):
    """Parses the Psi4 output file to get key results."""
    with open(output_path, "r") as file:
        return file.read()

def cleanup_uploads():
    """Deletes files in the uploads folder every hour."""
    while True:
        time.sleep(600)  # Wait for 10 min
        for file in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")

@app.route('/')
def entry_page():
    return render_template('entry.html')

@app.route("/forms", methods=["GET", "POST"])
def forms():
    ftype = request.args.get("type")
    
    basis_options = {
        'gamess': ["STO-3G", "6-31G*", "aug-cc-pVDZ", "AM1", "PM3", "PM6", "N311"],
        'psi4': ["STO-3G", "6-31G*", "aug-cc-pVDZ", "def2-SVPD"]
    }
    
    if ftype in basis_options:
        return render_template("mainform.html", naam=ftype.upper(), typbasis=basis_options[ftype])
    if ftype in ['fgamess', 'fpsi4']:
        return render_template("file.html", naam=ftype.upper(), mode="input")
    
    return jsonify({"error": "Type parameter is missing"}), 400

@app.route('/process_GAMESS', methods=['POST'])
def process_gamess():
    return process_software('GAMESS')

@app.route('/process_PSI4', methods=['POST'])
def process_psi4():
    return process_software('PSI4')

def process_software(software):
    scftyp = request.form.get("scftyp")
    mult = request.form.get("mult")
    charge = request.form.get("charge")
    basis = request.form.get("basis")
    type_ = request.form.get("type")
    addon = request.form.get("addon")
    dfttyp = request.form.get("dfttyp")
    file = request.files.get("file")
    
    if not file:
        return jsonify({"error": "No file provided."}), 400

    process_func = process_xyz_file_gamess if software == 'GAMESS' else process_xyz_file_psi4
    generate_func = generate_input_file_gamess if software == 'GAMESS' else generate_input_file_psi4

    file_data = process_func(file)
    generated_content = generate_func(scftyp, mult, charge, basis, type_, addon, dfttyp, file_data)
    timestamp = datetime.now().strftime('%d%m%Y%H%M%S')
    
    return Response(generated_content, mimetype='text/plain', headers={'Content-disposition': f'attachment; filename={timestamp}_input_{software.lower()}.in'})

@app.route('/file', methods=["GET", "POST"])
def file():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            return jsonify({"error": "No file provided or file is invalid."}), 400
        
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)
        
        data = run_psi4(file.filename)
        return render_template("result.html", output=data)  # Pass extracted output

    
    return render_template("index.html")

if __name__ == '__main__':
    cleanup_thread = threading.Thread(target=cleanup_uploads, daemon=True)
    cleanup_thread.start()
    app.run(host="0.0.0.0", port=5000, debug=True)
