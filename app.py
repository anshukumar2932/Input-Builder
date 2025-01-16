from flask import Flask, render_template, request, jsonify, send_file, Response
import os
import re
# Flask App
app = Flask(__name__)

# Atomic number mapping for file processing (Global scope)
element_to_atomic_number = {
    "H" : 1,  "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "Ne": 10,
    "Na": 11, "Mg": 12, "Al": 13, "Si": 14, "P": 15, "S": 16, "Cl": 17, "Ar": 18, "K": 19, "Ca": 20,
    "Sc": 21, "Ti": 22, "V": 23, "Cr": 24, "Mn": 25, "Fe": 26, "Co": 27, "Ni": 28, "Cu": 29, "Zn": 30,
    "Ga": 31, "Ge": 32, "As": 33, "Se": 34, "Br": 35, "Kr": 36, "Rb": 37, "Sr": 38, "Y": 39, "Zr": 40,
    "Nb": 41, "Mo": 42, "Tc": 43, "Ru": 44, "Rh": 45, "Pd": 46, "Ag": 47, "Cd": 48, "In": 49, "Sn": 50,
    "Sb": 51, "Te": 52, "I": 53, "Xe": 54, "Cs": 55, "Ba": 56, "La": 57, "Ce": 58, "Pr": 59, "Nd": 60,
    "Pm": 61, "Sm": 62, "Eu": 63, "Gd": 64, "Tb": 65, "Dy": 66, "Ho": 67, "Er": 68, "Tm": 69, "Yb": 70,
    "Lu": 71, "Hf": 72, "Ta": 73, "W": 74, "Re": 75, "Os": 76, "Ir": 77, "Pt": 78, "Au": 79, "Hg": 80,
    "Tl": 81, "Pb": 82, "Bi": 83, "Po": 84, "At": 85, "Rn": 86, "Fr": 87, "Ra": 88, "Ac": 89, "Th": 90,
    "Pa": 91, "U": 92, "Np": 93, "Pu": 94, "Am": 95, "Cm": 96, "Bk": 97, "Cf": 98, "Es": 99, "Fm": 100,
    "Md": 101, "No": 102, "Lr": 103, "Rf": 104, "Db": 105, "Sg": 106, "Bh": 107, "Hs": 108, "Mt": 109,
    "Ds": 110, "Rg": 111, "Cn": 112, "Nh": 113, "Fl": 114, "Mc": 115, "Lv": 116, "Ts": 117, "Og": 118
}


# Process Gamess XYZ File (fixed return)
def process_xyz_file_psi4(file):
    file_content = file.read().decode("utf-8").strip()
    lines = file_content.split("\n")
    data = "\n".join(lines[2:])  # Skip the first two lines (metadata)

    return data

# Process Psi4 XYZ File (fixed)
def process_xyz_file_gamess(file):
    file_content = file.read().decode("utf-8").strip()
    lines = file_content.split("\n")
    data = "\n".join(lines[2:])  # Skip the first two lines (metadata)

    updated_data = re.sub(
        r"\b([A-Z][a-z]?)\b",
        lambda match: f"{match.group(0)} {element_to_atomic_number.get(match.group(0), '')}",
        data
    )
    return updated_data

# Input file generator (for Gamess)
def generate_input_file_gamess(scftyp, mult, charge, basis, type_, addon, dfttyp, file_data):
    basis_mapping = {
        "STO-3G": "$BASIS  GBASIS=STO NGAUSS=3 $END",
        "6-31G*": "$BASIS GBASIS=N31 NGAUSS=6 NDFUNC=1 $END",
        "aug-cc-pVDZ": "$BASIS GBASIS=ACCD $END",
        "AM1": "$BASIS GBASIS=AM1 $END",
        "PM3": "$BASIS GBASIS=PM3 $END",
        "PM6": "$BASIS GBASIS=PM6 $END",
        "N311": "$BASIS GBASIS=N311 NGAUSS=6 NDFUNC=1 $END"
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

# Input file generator (for Psi4)
def generate_input_file_psi4(scftyp, mult, charge, basis, type_, addon, dfttyp, file_data):
    basis_mapping = {
        "STO-3G": "basis STO-3G",
        "3-21G": "basis 3-21G",
        "6-31G*": "basis 6-31G*",
        "aug-cc-pvdz": "basis aug-cc-pvdz",
        "def2-SVPD": "basis def2-SVPD"
    }

    basis_content = basis_mapping.get(basis, "")
    addon_content = "\nscf_e, scf_wfn = frequencies('scf', return_wfn=True, dertype=1)" if addon == "IR" else ""
    dft_content = f"'{dfttyp}'" if dfttyp != "NONE" else "'scf'"
    type_content="energy" if type_=="ENERGY" else "optimize" 

    template = f"""molecule m {{ 
{file_data}
}}
set {{
 {basis_content}
 reference {scftyp}
}}
E, wfn = {type_content}({dft_content}, return_wfn=True)
wfn.write_molden('Psi4.molden')
oeprop(wfn, 'DIPOLE', 'MULLIKEN_CHARGES', 'LOWDIN_CHARGES')
print_variables(){addon_content}
"""
    return template

# Routes
@app.route('/')
def entry_page():
    return render_template('entry.html')

@app.route("/forms", methods=["GET", "POST"])
def forms():
    ftype = request.args.get("type")

    if ftype == 'gamess':
        basislist = ["STO-3G", "6-31G*", "aug-cc-pVDZ", "AM1", "PM3", "PM6", "N311"]
        return render_template("mainform.html", naam="GAMESS", typbasis=basislist)
    if ftype == 'psi4':
        basislist = ["STO-3G", "6-31G*", "aug-cc-pVDZ", "def2-SVPD"]
        return render_template("mainform.html", naam="PSI4", typbasis=basislist)
    if ftype == 'fgamess':    
        return render_template("file.html", naam="GAMESS" , mode="input")
    if ftype == 'fpsi4':
        return render_template("file.html", naam="PSI4" , mode="input")
    if not ftype:
        return jsonify({"error": "Type parameter is missing"}), 400


@app.route('/process_GAMESS', methods=['POST'])
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

    file_data = process_xyz_file_gamess(file)
    generated_content = generate_input_file_gamess(scftyp, mult, charge, basis, type_, addon, dfttyp, file_data)
    return Response(generated_content, mimetype='text/plain',headers={'Content-disposition': f'attachment; filename=generated_input_gamess.txt'})

@app.route('/process_PSI4', methods=['POST'])
def process_psi4():
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

    file_data = process_xyz_file_psi4(file)
    generated_content = generate_input_file_psi4(scftyp, mult, charge, basis, type_, addon, dfttyp, file_data)    
    return Response(generated_content, mimetype='text/plain',headers={'Content-disposition': f'attachment; filename=generated_input_psi4.txt'})

@app.route('/file', methods=["GET", "POST"])
def file():
    if request.method == 'POST':
        software = request.form.get("software")
        file = request.files.get('file')
        if not file or file.filename == '':
            return jsonify({"error": "No file provided or file is invalid."}), 400            
        else:
            data=str("File uploaded successfully! software="+software)
            return render_template("file.html", mode="output", data=data)

if __name__ == '__main__':
    app.run(debug=True)
