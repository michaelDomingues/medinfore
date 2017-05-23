#!/usr/bin/env python3

import os

# PYCHARM
#ROOT_DIR = '.'
# CLI
ROOT_DIR  = os.environ['PYTHONPATH']

CORPUS_DOCS = "./corpus"
INDEX_TYPE_MatrixSimilarity = "MatrixSimilarity"
INDEX_TYPE_Similarity = "Similarity"
CORE_DATA = ROOT_DIR + "/backups/medinfore"
DICT_PATH = CORE_DATA + ".dict"
CORPUS_PATH = CORE_DATA + ".mm"
INDEX_PATH = CORE_DATA + ".index"
INDEX_MM_PATH = CORE_DATA + ".mm.index"
LSI_MODEL = CORE_DATA + ".model"

VALID_PUNCTUATION = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '\/', ':', ';', '<', '=',
                     '>', '?', '@', '[', '\\\\', ']', '\^', '_', '`', '{', '|', '}', '~']

FILTER_THRESHOLD = 0.10
SNOMEDCT_FILTER_THRESHOLD = 90
