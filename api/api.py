#!/usr/bin/env python3

import logging
from flask import Flask, jsonify, make_response, request, abort

from enigma.indexer import Indexer

logging.basicConfig(format='%(asctime)s : %(module)s: %(levelname)s : %(message)s',
                    level=logging.DEBUG)  # filename='medinfore.log',

load_from_disk = True
indexer = None
app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Welcome to medinfore'})

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if query == "" or query is None:
        abort(404)
    result = indexer.search(query=query)
    return jsonify({'result': result})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    indexer = Indexer(load_from_disk)
    app.run(debug=True)


    # Search results:  [(0, 0.99809301), (1, 0.93748635), (2, 0.99844527), (3, 0.9865886), (4, 0.90755945),
    #                  (5, -0.12416792), (6, -0.10639259), (7, -0.098794632), (8, 0.050041769)]
