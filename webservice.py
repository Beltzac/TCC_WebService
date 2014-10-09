#!flask/bin/python
import os
from flask import Flask, jsonify, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from time import gmtime, strftime
from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML
import pytesseract
import Image
import string


THIS_FOLDER = os.getcwd()
UPLOAD_FOLDER = THIS_FOLDER + '/upload'
OUTPUT_FOLDER = THIS_FOLDER + '/output'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



def blastn(sequencia):
    lista = []
    resultado = NCBIWWW.qblast('blastn', 'nr', sequencia)
    registros = NCBIXML.parse(resultado)
    registro_blast = registros.next()
    for alinhamento in registro_blast.alignments:
        #print alinhamento.hsps
        for hsp in alinhamento.hsps:
            # print "****Alinhamento****"
            reg = {
                'nome': alinhamento.hit_def,
                'id': alinhamento.hit_id,
                'tamanho': alinhamento.length,
                'e-value': hsp.expect,
                'query-a': hsp.query[:50],
                'query-b': hsp.match[:50],
                'query-c': hsp.sbjct[:50]
            }
            lista.append(reg)
            #print reg
            # print "----------------------------------------------"

    return lista[:10]


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload/<path:filename>')
def send_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/output/<path:filename>')
def send_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)


@app.route('/web/', methods=['GET', 'POST'])
def site_input():
    erro = 100
    texto = ''
    temp = []
    tempo = 0
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(full_path)
            imagemDNA = Image.open(full_path);

            texto = pytesseract.image_to_string(imagemDNA,config='-psm 3')
            print(texto)
            print ('-' * 30)
            all = string.maketrans('','')
            strdna = all.translate(all,'acgtACGT')
            texto2 = texto.translate(all,strdna).upper()
            print (texto2)
            # texto , tempo = octave.runOCR(full_path)
            #texto = 'ATGGAAAACTTTTGGCAGGCCTGCTCTCAAAAACTTGAGCAGGAGCTGACACCCCAGCAATACAGCGCCTGGATCAAGCCCCTGGTGCCGCTCGACTACGAAGACGGGCTGCTGCGCGTGGCCGCGCCCAATCGGTTCAAGCTGGACTGGGTCAAGACCCAGTTCGCCAACCGCATCACCGCGCTGGCCTGCGAGTACTGGGACGCGCCCACCGAGGTGCAATTCGTGCTCGACCCGCGTGGCAACCAGGGCCGTCGTCCGGCGGCGGCCGCCGCGGCCGGCAATGGCGCCAGCGGTCTGGGTTTGCCCAATCACGAGCAATTGCACCTGGACCCCGAACCGGCCCAGCCGGTGCGCGCGGTCGCGCCGCGCCAGGAGCAGTCGCGTATCAACCCGGTGTTGACCTTCGACAATCTGGTGACGGGTAAGGCCAACCAGCTTGCCCGCGCAGCCGCCACCCAGGTGGCCAACAACCCCGGCACGTCCTACAACCCGCTGTTCCTGTACGGCGGCGTCGGCCTGGGTAAGACCCACATCATCCACGCCATCGGCAACCAGGTGCTTGTGGATAACCCGGGCGCGAAAATCCGCTACATCCACGCCG'
            if len(texto2) > 0:
                temp = blastn(texto2)
            erro = 0
        else:
            erro = 1

        json = jsonify({'text': texto2,
                        'blast': temp,
                        'erro': erro,
                        'time': tempo})
        return json  # redirect(url_for('uploaded_file', filename=filename))
    return '''
    <!doctype html>
    <title>Upload nova imagem</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


@app.route('/', methods=['GET', 'POST'])
def app_input():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(full_path)

            return " "

    json = jsonify({'success': 'false',
                    'server_time': strftime("%Y-%m-%d %H:%M:%S", gmtime())})
    return json


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
	

