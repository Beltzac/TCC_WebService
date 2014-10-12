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

from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML
import pytesseract
import matplotlib.pyplot as plt


THIS_FOLDER = os.getcwd()
UPLOAD_FOLDER = THIS_FOLDER + '/upload'
OUTPUT_FOLDER = THIS_FOLDER + '/output'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def angle(ps):
    x1, y1 = ps[0]
    x2, y2 = ps[1]

    m = (y2 - y1) / float(x2 - x1)

    return math.atan(m)


def blastn(sequencia):
    lista = []
    resultado = NCBIWWW.qblast('blastn', 'nr', sequencia)
    registros = NCBIXML.parse(resultado)
    registro_blast = registros.next()
    for alinhamento in registro_blast.alignments:
        # print alinhamento.hsps
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
            # print reg
            # print "----------------------------------------------"

    return lista[:10]


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


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

            # imagemDNA = Image.open(full_path)
            #
            # texto = pytesseract.image_to_string(imagemDNA)
            # print(texto)
            # print ('1' * 30)

            # local threshold


            img = img_as_ubyte(data.imread(full_path, True))

            start_time = timeit.default_timer()
            threshold_local = filter.threshold_adaptive(img, 201)
            elapsed = timeit.default_timer() - start_time

            print('threshold_local:', elapsed)

            # texto = pytesseract.image_to_string(Image.fromarray(numpy.uint8(threshold_local)))
            # print(texto)
            # print ('2' * 30)


            # edge

            start_time = timeit.default_timer()
            edges2 = filter.canny(threshold_local, sigma=2)
            elapsed = timeit.default_timer() - start_time
            print('canny:', elapsed)

            # Deskew

            start_time = timeit.default_timer()
            theta = numpy.linspace(1.39, 1.74, 30)

            lines = probabilistic_hough_line(edges2, line_gap=50, line_length=600, theta=theta)
            print(len(lines))

            angs = [angle(ps) for ps in lines]
            rot = numpy.mean(angs)
            ang = math.degrees(rot)
            print (ang)
            elapsed = timeit.default_timer() - start_time
            print('deskew:', elapsed)

            final = rotate(threshold_local, ang)

            imgplot = plt.imshow(final, cmap=plt.cm.gray)

            texto = pytesseract.image_to_string(Image.fromarray(numpy.uint8(final)))
            print(texto)
            print ('-' * 30)

            if (True):
                # results threshold

                fig, ax = plt.subplots(1, 2, figsize=(8, 5))
                ax1, ax2, = ax.ravel()

                fig.colorbar(ax1.imshow(img, cmap=plt.cm.gray),
                             ax=ax1, orientation='horizontal')
                ax1.set_title('Original')
                ax1.axis('off')

                fig.colorbar(ax2.imshow(threshold_local, cmap=plt.cm.gray),
                             ax=ax2, orientation='horizontal')
                ax2.set_title('Local threshold (radius=%d)' % 101)
                ax2.axis('off')

                plt.show()



                # results lines
                fig2, ax = plt.subplots(1, 3, figsize=(8, 3))

                ax[0].imshow(threshold_local, cmap=plt.cm.gray)
                ax[0].set_title('Input image')
                ax[0].axis('image')

                ax[1].imshow(edges2, cmap=plt.cm.gray)
                ax[1].set_title('Canny edges')
                ax[1].axis('image')

                ax[2].imshow(edges2, cmap=plt.cm.gray)

                for line in lines:
                    p0, p1 = line
                    ax[2].plot((p0[0], p1[0]), (p0[1], p1[1]))

                ax[2].set_title('Probabilistic Hough')
                ax[2].axis('image')
                plt.show()

            all = string.maketrans('', '')
            strdna = all.translate(all, 'acgtACGT')
            texto2 = texto.translate(all, strdna).upper()
            print (texto2)

            if len(texto2) > 0:
                start_time = timeit.default_timer()
                temp = blastn(texto2)
                elapsed = timeit.default_timer() - start_time
                print('blast:', elapsed)
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
	

