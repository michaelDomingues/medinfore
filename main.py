#!/usr/bin/env python3
import fnmatch
import logging
import os
import re

from consts import CORPUS_DOCS
from enigma.indexer import Indexer

logging.basicConfig(format='%(asctime)s : %(module)s: %(levelname)s : %(message)s', level=logging.DEBUG)

includes = ['*.txt']
# transform glob patterns to regular expressions
includes = r'|'.join([fnmatch.translate(x) for x in includes])

load_from_disk = True
indexer = Indexer(load_from_disk)

if not load_from_disk:
    for path, sub_dirs, files in os.walk(CORPUS_DOCS):
        files = [f for f in files if re.match(includes, f)]
        for id, filename in enumerate(files):
            file_path = path + '/' + filename
            indexer.index_doc(doc_path=file_path, doc_id=id)

    indexer.setup_corpus_index()

print(indexer.search(query="arrhythmia",
                     neighbors=False,
                     synonyms=False))
