import os
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import requests

UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
hostName = "https://photo-sign-autoplace.herokuapp.com"
apiEndpoint = "https://human-detection-api.herokuapp.com/detectHuman?imgUrl="


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
	return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_image():
    if 'file1' and 'file2' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file1 = request.files['file1']
    file2 = request.files['file2']
    if file1.filename == '' or file2.filename == "":
        flash('No image selected for uploading')
        return redirect(request.url)
    if file1 and allowed_file(file1.filename) and file2 and allowed_file(file2.filename):
        fn1 = file1.filename.rsplit(".")
        fn_1 = fn1[0] + "_photo." + fn1[1]
        filename1 = secure_filename(fn_1)
        file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))

        fn2 = file2.filename.rsplit(".")
        fn_2 = fn2[0] + "_sign." + fn2[1]
        filename2 = secure_filename(fn_2)
        file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
		# print('upload_image filename: ' + filename)
        flash('Image successfully uploaded and displayed below')
        q1 = str(hostName+url_for('static', filename='uploads/' + filename1))
        r1 = requests.get(apiEndpoint+q1)
        # print(str(r.text))
        resp1 = str(r1.text)

        q2 = str(hostName+url_for('static', filename='uploads/' + filename2))
        r2 = requests.get(apiEndpoint+q2)
        # print(str(r.text))
        resp2 = str(r2.text)
        # print(resp)

        if resp1 == "Person" and resp2 == "Signature":
            return render_template('upload.html', filename1=filename1, filename2=filename2)
        elif resp1 == "Signature" and resp2 == "Person":
            flash('Photo and Signature Auto Replaced by System')
            return render_template('upload.html', filename1=filename2, filename2=filename1)
        elif resp1 == "Person" and resp2 == "Person":
            return render_template('upload.html', err1 = "p")
        elif resp1 == "Signature" and resp2 == "Signature":
            return render_template('upload.html', err2 = "s")
        else:
            return render_template('upload.html', uerr = "u")
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
	# print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == "__main__":
    app.run()