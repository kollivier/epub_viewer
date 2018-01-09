import os
import sys

from flask import Flask, abort, jsonify, request
app = Flask(__name__)

thisdir = os.path.dirname(os.path.abspath(__file__))
epubsdir = os.path.join(thisdir, 'epubs')

current_epub = None

import epub


def is_visible(filepath):
    name = os.path.basename(os.path.abspath(filepath))
    return not name.startswith('.')


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


@app.route('/epub/<subdir>/<path:filename>', methods=['GET'])
def get_epub_subdir_file(subdir, filename):
    path = os.path.join(current_epub.epub_dir, 'OEBPS', subdir, filename)
    if os.path.exists(path):
        return open(path, 'rb').read()
    else:
        abort(404)


@app.route('/epub/<path:filename>', methods=['GET'])
def get_epub_file(filename):
    path = os.path.join(current_epub.epub_dir, filename)
    if not os.path.exists(path):
        path = os.path.join(current_epub.epub_dir, 'OEBPS', filename)
    if os.path.exists(path):
        return open(path, 'rb').read()
    else:
        abort(404)


@app.route('/getFilesInEpubsDir', methods=['GET'])
def dir_listing():
    all_files = os.listdir(epubsdir)
    all_files.sort(key=lambda x: os.path.getmtime(os.path.join(epubsdir, x)))
    files = [afile for afile in all_files if is_visible(afile)]
    data = {
        'dirname': epubsdir,
        'files': files
    }

    print("Sending data: {}".format(data))
    return jsonify(data)


@app.route("/openEPub", methods=['POST'])
def file_picked():
    data = request.json
    filename = os.path.join(epubsdir, data['filename'])

    print("Opening {}".format(filename))

    global current_epub
    current_epub = epub.EPub(filename)
    toc_page = current_epub.toc_filename

    return jsonify({'toc': '/epub/{}'.format(os.path.basename(toc_page))})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        epubsdir = os.path.abspath(sys.argv[1])
    app.run()
