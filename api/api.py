#!/usr/bin/env python3
import fnmatch
import logging
import os

from distutils.util import strtobool

import re
from flask import Flask, jsonify, make_response, request, abort
from enigma.indexer import Indexer

logging.basicConfig(format='%(asctime)s : %(module)s: %(levelname)s : %(message)s', level=logging.DEBUG)

includes = ['*.txt']
# transform glob patterns to regular expressions
includes = r'|'.join([fnmatch.translate(x) for x in includes])

load_from_disk = True
indexer = None
app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return jsonify({'\"message\"': 'Welcome to medinfore'})


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    neighborhood = request.args.get('neighbors')
    synonyms = request.args.get('synonyms')

    if query == "" or query is None:
        abort(404)

    try:
        neighborhood = bool(strtobool(neighborhood))
        synonyms = bool(strtobool(synonyms))
    except Exception as e:
        neighborhood = False
        synonyms = False

    logging.info('Request parameters: query=%s neighbors=%s synonyms=%s' % (query, neighborhood, synonyms))
    result = indexer.search(query=query,
                            neighbors=neighborhood,
                            synonyms=synonyms)
    return jsonify({"\"result\"": result})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'\"error\"': 'Not found'}), 404)


if __name__ == '__main__':
    indexer = Indexer(load_from_disk)
    if not load_from_disk:
        for path, sub_dirs, files in os.walk("./corpus"):
            files = [f for f in files if re.match(includes, f)]
            for id, filename in enumerate(files):
                file_path = path + '/' + filename
                logging.info('Parsing file.... %s' % file_path)
                indexer.index_doc(doc_path=file_path, doc_id=id)

        indexer.setup_corpus_index()
    app.run(debug=True)
