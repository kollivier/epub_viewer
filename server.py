import os

from flask import Flask, jsonify, request
app = Flask(__name__)

thisdir = os.path.dirname(os.path.abspath(__file__))
epubsdir = os.path.join(thisdir, 'epubs')


@app.after_request
def after_request(response):
    """
    Make sure we allow requests from localhost, and allow callers to specify Content-Type
    so that they can declare content as json.
    """
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
    return response


@app.route("/getFilesInEpubsDir", methods=['GET'])
def dir_listing():
    data = {
        'dirname': epubsdir,
        'files': os.listdir(epubsdir)
    }

    print("Sending data: {}".format(data))
    return jsonify(data)


@app.route("/selectFile", methods=['POST'])
def file_picked():
    data = request.json
    filename = os.path.join(epubsdir, data['filename'])
    print("Opening {}".format(filename))

    return jsonify(data)
