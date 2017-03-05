#!/usr/bin/env python3

import logging
import os
from enigma.indexer import Indexer

logging.basicConfig(format='%(asctime)s : %(module)s: %(levelname)s : %(message)s',
                    level=logging.DEBUG)  # filename='medinfore.log',

load_from_disk = False
indexer = Indexer(load_from_disk)

if not load_from_disk:
    for path, subdirs, files in os.walk("./corpus"):
        for filename in files:
            file_path = path + '/' + filename
            logging.info(file_path)
            indexer.index_doc(doc_path=file_path)

    indexer.setup_corpus_index()

# indexer.search(query="Human computer interaction")

# TODO:
# - Check valid words kept in dict                                                          :check:
# - Check MatrixSimilarity vs Similarity results disparity
# - Validation on dict construct with flag if read from disk or re-create                   :check:
# - Multiple files to feed corpus                                                           :check:
# - Test with corpus from gensim                                                            :check:
# - Redis DB with documents info
