import os
import logging
import glob
from flask import Flask, flash, request, redirect, render_template, jsonify
from werkzeug.utils import secure_filename
from werkzeug.middleware.shared_data import SharedDataMiddleware

from app import ner_trainer, pdf_extractor, config
from app.tools import upload_file_to_s3

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config.from_object(config.FlaskConfig)
app.add_url_rule('/uploads/<filename>', 'uploaded_file',
                 build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads':  os.getcwd() + config.FlaskConfig.UPLOAD_FOLDER
})


def cvparser(filepath):
    content = pdf_extractor.extract_pdf_content_url(filepath)
    model_filepath = os.getcwd() + '/' + glob.glob('lib/model*')[0]

    return ner_trainer.predict_spacy(content, model_filepath)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        logging.info(file.filename)
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            file.filename = secure_filename(file.filename)
            upload_file_to_s3(file, os.environ['AWS_S3_BUCKET'])
            filepath = "https://{}.s3.{}.amazonaws.com/{}".format(
                os.environ['AWS_S3_BUCKET'],
                os.environ['AWS_REGION'],
                file.filename
            )
            resp = cvparser(filepath)
            return jsonify(resp)
        # if file and allowed_file(file.filename):
        #     filename = secure_filename(file.filename)
        #     filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        #     file.save(filepath)
        #     resp = cvparser(filepath)
        #     return jsonify(resp)
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)
