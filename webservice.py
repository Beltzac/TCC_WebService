#!flask/bin/python
import os
import numpy
import Image
import string
from skimage.transform import probabilistic_hough_line, rotate
from skimage import data
from skimage.util import img_as_ubyte
import math
import timeit
from skimage import filter
import hashlib
from threading import Thread
import cStringIO

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML
import pytesseract
import matplotlib.pyplot as plt


THIS_FOLDER = os.getcwd()
UPLOAD_FOLDER = THIS_FOLDER + '/upload'
ALLOWED_EXTENSIONS = set(['jpg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///results.db'
db = SQLAlchemy(app)


class Result(db.Model):
    hash = db.Column(db.String(32), primary_key=True)
    result = db.Column(db.String(1000), unique=False)
    error = db.Column(db.Integer, unique=False)

    def __init__(self, hash, result, error):
        self.hash = hash
        self.result = result
        self.error = error

    def __repr__(self):
        return '<Result %r>' % self.hash


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def full_path(hash):
    return os.path.join(app.config['UPLOAD_FOLDER'], hash + '.jpg')


# calcula o angulo de uma linha a partir de dois pontos
def angle(ps):
    x1, y1 = ps[0]
    x2, y2 = ps[1]

    m = (y2 - y1) / float(x2 - x1)

    return math.atan(m)


# executa o processamento em uma imagem, retorna o texto filtrado
def ocr(hash):
    error = 0

    img = img_as_ubyte(data.imread(full_path(hash), True))

    start_time = timeit.default_timer()
    threshold_local = filter.threshold_adaptive(img, 201)
    elapsed = timeit.default_timer() - start_time

    print("threshold_local:", elapsed)

    # edge

    start_time = timeit.default_timer()
    edges2 = filter.canny(threshold_local, sigma=2)
    elapsed = timeit.default_timer() - start_time
    print("canny:", elapsed)

    # Deskew

    start_time = timeit.default_timer()
    theta = numpy.linspace(1.39, 1.74, 30)

    lines = probabilistic_hough_line(edges2, line_gap=50, line_length=600, theta=theta)
    print("Lines:", len(lines))

    angs = [angle(ps) for ps in lines]
    rot = numpy.mean(angs)
    ang = math.degrees(rot)
    elapsed = timeit.default_timer() - start_time
    print("deskew:", elapsed)
    print("Angle:", ang, "Degres")

    final = rotate(threshold_local, ang)
    start_time = timeit.default_timer()
    texto = pytesseract.image_to_string(Image.fromarray(numpy.uint8(final)))
    elapsed = timeit.default_timer() - start_time
    print("OCR:", elapsed)

    print(texto)
    print ('-' * 30)

    all = string.maketrans('', '')
    strdna = all.translate(all, 'acgtACGT')
    texto2 = texto.translate(all, strdna).upper()
    print (texto2)

    if (False):

        # results
        fig, ax = plt.subplots(2, 3, figsize=(8, 3))

        ax0, ax1, ax2, ax3, ax4, ax5 = ax.ravel()

        ax0.imshow(img, cmap=plt.cm.gray)
        ax0.set_title('Original')
        ax0.axis('image')

        ax1.imshow(threshold_local, cmap=plt.cm.gray)
        ax1.set_title('Local threshold (radius=%d)' % 101)
        ax1.axis('image')

        ax2.imshow(edges2, cmap=plt.cm.gray)
        ax2.set_title('Canny edges')
        ax2.axis('image')

        ax3.imshow(edges2, cmap=plt.cm.gray)

        for line in lines:
            p0, p1 = line
            ax3.plot((p0[0], p1[0]), (p0[1], p1[1]))

        ax3.set_title('Probabilistic Hough')
        ax3.axis('image')

        ax4.imshow(final, cmap=plt.cm.gray)
        ax4.set_title('Deskew')
        ax4.axis('image')

        plt.show()

    return [texto2, error]


def process(hash):
    print('Starting thread for:', hash)
    error = 100

    text, error = ocr(hash)

    if len(text) > 0:
        start_time = timeit.default_timer()
        blast = NCBIWWW.qblast('blastn', 'nr', text)
        elapsed = timeit.default_timer() - start_time
        print('blast:', elapsed)
        if len(blast.getvalue()) == 0:
            error = 10  #blast nao retornou resultados
        else:
            error = 0  # tudo OK
    else:
        error = 34  #ocr nao encontrou texto

    # faz um update para incluir os resultados

    with app.test_request_context():
        r = Result.query.filter_by(hash=hash).first()
        r.error = error
        r.result = blast.getvalue()
        db.session.commit()

    return


# receber e agendar o processamento da imagem, retorna o codigo da imagem
@app.route('/input', methods=['POST'])
def image_input():
    error = 100
    image_id = None
    hash = ''

    if request.method == 'POST':
        file = request.files['image']
        if file is not None:
            if allowed_file(file.filename):

                hash = hashlib.md5(file.read()).hexdigest()

                print('hash:', hash)

                file.seek(0)

                file.save(full_path(hash))
                print('saving image:', hash)
                r = Result(hash, "", 1)  # erro pra processamento em andamento
                db.session.add(r)
                db.session.commit()

                #cria thread
                thread = Thread(target=process, args=(hash,))
                thread.start()
                error = 0  # sem erro


            else:
                error = 31  #imagem invalida
        else:
            error = 30  #imagem nula

    json = jsonify({'id': hash,
                    'error': error
    })
    return json


#acesso aos resultados
def blast_to_list(alignments):
    lista = []
    for alinhamento in alignments:
        # print alinhamento.hsps
        hits = []

        for hsp in alinhamento.hsps:
            # print "****Alinhamento****"
            reg = {
                'e-value': hsp.expect,
                'query-a': hsp.query[:50],
                'query-b': hsp.match[:50],
                'query-c': hsp.sbjct[:50]
            }
            hits.append(reg)
            # print reg
            # print "----------------------------------------------"
        reg2 = {
            'nome': alinhamento.hit_def,
            'id': alinhamento.hit_id,
            'tamanho': alinhamento.length,
            'hits': hits
        }

        lista.append(reg2)

    return lista[:10]


@app.route('/result/<image_id>')
def image_result(image_id):
    error = 100
    result = ""
    hash = ""

    r = Result.query.filter_by(hash=image_id).first()

    if r is not None:
        hash = r.hash
        result = r.result
        error = r.error  #possivel erro do processamento
    else:
        error = 2  #codigo nao encontrado

    output = cStringIO.StringIO(r.result)
    lista_alinhamentos = blast_to_list(NCBIXML.parse(output).next().alignments)

    json = jsonify({'requested': r.hash,
                    'blast': lista_alinhamentos,
                    'error': r.error
    })
    return json


#accesso aos graficos
@app.route('/debug/<int:image_id>')
def debug_images(image_id):
    return image_id


#interface web para testes
@app.route('/web/', methods=['GET'])
def site_input():
    return '''
        <!doctype html>
        <title>Upload nova imagem</title>
        <h1>Upload new File</h1>
        <form action="/input" method=post enctype=multipart/form-data>
          <p><input type=file name=image>
             <input type=submit value=Upload>
        </form>
    '''


@app.route('/')
def hello():
    return "Works!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

	

