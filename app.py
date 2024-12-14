from flask import Flask, render_template, request, jsonify, send_file
import os

# Flask App
app = Flask(__name__)

# Atomic number mapping for file processing
def process_xyz_file(file):
    element_to_atomic_number = {
        "H": 1, "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "Ne": 10,
        # (rest of elements omitted for brevity) ...
        "Ts": 117, "Og": 118
    }

    file_content = file.read().decode("utf-8").strip()
    lines = file_content.split("\n")
    data = "\n".join(lines[2:])

    import re
    updated_data = re.sub(
        r"\b([A-Z][a-z]?)\b",
        lambda match: f"{match.group(0)} {element_to_atomic_number.get(match.group(0), '')}",
        data
    )
    return updated_data

# Input file generator
def generate_input_file(scftyp, mult, charge, basis, type_, addon, dfttyp, file_data):
    basis_mapping = {
        "STO-3G": "$BASIS  GBASIS=STO NGAUSS=3 $END",
        "6-31G*": "$BASIS GBASIS=N31 NGAUSS=6 NDFUNC=1 $END",
        "aug-cc-pVDZ": "$BASIS GBASIS=ACCD $END",
    }

    basis_content = basis_mapping.get(basis, "")
    addon_content = "\n $FORCE METHOD=SEMINUM NVIB=2 $END \n $STATPT IHREP=0 HSSEND=.TRUE.  $END" if addon == "IR" else ""
    dft_content = f"\n  DFTTYP={dfttyp}" if dfttyp != "NONE" else ""

    template = f""" $CONTRL SCFTYP={scftyp} MAXIT=200 RUNTYP={type_}
 COORD=UNIQUE MULT={mult} 
 ICHARG={charge}{dft_content}  
 $END
 $SYSTEM TIMLIM=2879 MWORDS=250 $END{addon_content}
 {basis_content}
 $DATA

 C1
 {file_data}
 $END"""
    return template

# Routes
@app.route('/')
def entry_page():
    return render_template('entry.html')

@app.route('/gamess')
def gamess_page():
    return render_template('gamess_form.html')

@app.route('/psi4')
def psi4_page():
    return render_template('psi4_form.html')

@app.route('/process_gamess', methods=['POST'])
def process_gamess():
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

    file_data = process_xyz_file(file)
    generated_content = generate_input_file(scftyp, mult, charge, basis, type_, addon, dfttyp, file_data)

    output_path = "generated_input_gamess.txt"
    with open(output_path, "w") as f:
        f.write(generated_content)

    return send_file(output_path, as_attachment=True)

@app.route('/process_psi4', methods=['POST'])
def process_psi4():
    # Placeholder: Process input for Psi4
    return jsonify({"message": "Psi4 processing is not yet implemented."})

if __name__ == '__main__':
    app.run(debug=True)
