from im import *

app = Flask(__name__)

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
    n=datetime.now().strftime('%d%m%Y%H%M%S')
    return Response(generated_content, mimetype='text/plain',headers={'Content-disposition': f'attachment; filename={n}_input_gamess.txt'})

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
    n=datetime.now().strftime('%d%m%Y%H%M%S')
    return Response(generated_content, mimetype='text/plain',headers={'Content-disposition': f'attachment; filename={n}_input_psi4.txt'})

@app.route('/file', methods=["GET", "POST"])
def file():
    if request.method == 'POST':
        software = request.form.get("software")
        file = request.files.get('file')

        if not file or file.filename == '':
            return jsonify({"error": "No file provided or file is invalid."}), 400            
        else:
            data=str("File uploaded successfully! software="+software)
            if software=="GAMESS":
                data += "\t "+trial()
            elif software=="PSI4":
                data += "\t PSI4 is not active currently"
            return render_template("file.html", mode="output", data=data)

if __name__ == '__main__':
    app.run(debug=True)
