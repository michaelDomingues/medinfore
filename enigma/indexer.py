#!/usr/bin/env python3
from documenthandler.dparser import DocumentParser
from languagemodel.dictionary import Dictionary
from utilities.consts import INDEX_TYPE_Similarity, INDEX_TYPE_MatrixSimilarity
from utilities.utils import docs_score_json


class Indexer:
    def __init__(self, load_from_disk: bool):
        self.__load_from_disk = load_from_disk
        self.__index_type = INDEX_TYPE_MatrixSimilarity
        self.__parser = None
        self.__dictionary = Dictionary(self.__load_from_disk, self.__index_type)

    def index_doc(self, doc_path: str) -> None:
        """
        Index a new doc.
        :param doc_path: Path to file
        :return:
        """
        self.__parser = DocumentParser(path_to_file=doc_path)
        self.__parser.process()
        self.__dictionary.build_word_knowledge(tokens=self.__parser.words())

    def setup_corpus_index(self) -> None:
        """
        Set up a new corpus and indexes it
        :return:
        """
        self.__dictionary.setup_corpus()
        self.__dictionary.index()

    def search(self, query) -> list:
        """
        Performs a query by similarity
        :param query: query text
        :return:
        """
        return docs_score_json(index_result=self.__dictionary.query(query=query))
