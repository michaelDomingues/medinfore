#!/usr/bin/env python3

import os

ROOT_DIR = os.environ['PYTHONPATH']

INDEX_TYPE_MatrixSimilarity = "MatrixSimilarity"
INDEX_TYPE_Similarity = "Similarity"
CORE_DATA = ROOT_DIR + "/backups/medinfore"
DICT_PATH = CORE_DATA + ".dict"
CORPUS_PATH = CORE_DATA + ".mm"
INDEX_PATH = CORE_DATA + ".index"
INDEX_MM_PATH = CORE_DATA + ".mm.index"
