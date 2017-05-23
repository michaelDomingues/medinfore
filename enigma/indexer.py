#!/usr/bin/env python3

import logging

from documenthandler.dparser import DocumentParser
from languagemodel.dictionary import Dictionary
from utilities.consts import INDEX_TYPE_MatrixSimilarity, INDEX_TYPE_Similarity
from utilities.utils import docs_score_json
from utilities.consts import FILTER_THRESHOLD
from redisdb.connector import RedisDB
from thesaurus.collector import Collector


class Indexer:
    def __init__(self, load_from_disk: bool):
        self.__load_from_disk = load_from_disk
        self.__index_type = INDEX_TYPE_MatrixSimilarity
        self.__parser = None
        self.__redis = RedisDB()
        self.__dictionary = Dictionary(self.__load_from_disk, self.__index_type)
        self.__collector = Collector()

    def index_doc(self, doc_path: str, doc_id: int) -> None:
        """
        Index a new doc.
        :param doc_path: Path to file
        :return:
        """
        logging.info('Indexing file.... id:%d  Path: %s' % (doc_id, doc_path))
        try:
            self.__parser = DocumentParser(path_to_file=doc_path)
        except:
            return
        self.__parser.process()
        self.__dictionary.build_word_knowledge(tokens=self.__parser.words())
        self.__redis.add_document_name_by_id(document_id=doc_id,
                                             document_name=self.__parser.document_name())
        self.__redis.add_terms_ngram(document_hash=self.__parser.document_id_hash(),
                                     ngram=self.__dictionary.get_words_core())
        self.__redis.add_terms_frequencies(document_hash=self.__parser.document_id_hash(),
                                           freq=self.__dictionary.get_terms_frequency())

    def setup_corpus_index(self) -> None:
        """
        Set up a new corpus and indexes it
        :return:
        """
        self.__dictionary.setup_corpus()
        self.__dictionary.index()

    def search(self, query: str, neighbors: bool, synonyms: bool) -> list:
        """
        Performs a query by similarity
        :param query: query text
        :return:
        """
        # Mockup result
        # TODO: Pass this to the collector
        mockup_result = self.__collector.get_mockup_result(dict_num_docs=self.__dictionary.get_number_docs())

        # Remove stopwords and converts back to a str
        # TODO: Deal with multiple query words
        limited_query = True if len(query.split()) == 1 and neighbors else False
        known_terms, query_term_neighbors = self.__redis.documents_have_terms(query=query,
                                                                              check_suggestions=limited_query)
        if known_terms:
            # Join neighbors to the initial query
            query_no_stpw = ['%s %s' % (query, query_term) for query_term in
                             iter(query_term_neighbors)] if limited_query else [query]

            logging.info('Synonyms: %s Using: %s' % (synonyms, query_no_stpw))

            snomed_matching_terms = []
            thresholded_indexed_result = []

            if synonyms:
                for query_str in iter(query_no_stpw):
                    # Polls SNOMED CT for synonyms
                    snomed_matching_terms += self.__collector.get_snomed_ct_synonyms(query_str)
                logging.info('Related concepts found: %s' % (snomed_matching_terms))
                for snomed_term in iter(snomed_matching_terms):
                    indexed_result = self.__dictionary.query(query=snomed_term)
                    # Filter each index query result with a threshold!!!
                    thresholded_indexed_result += list(filter(lambda x: x[1] >= FILTER_THRESHOLD, indexed_result))
                    # for document_result in iter(thresholded_indexed_result):
                    #     doc_id = document_result[0]
                    #     similarity = document_result[1]
                    #     mockup_result[doc_id].append(similarity)

            for query_str in iter(query_no_stpw):
                indexed_result = self.__dictionary.query(query=query_str)
                # Filter each index query result with a threshold!!!
                thresholded_indexed_result += list(filter(lambda x: x[1] >= FILTER_THRESHOLD, indexed_result))

            for document_result in iter(thresholded_indexed_result):
                doc_id = document_result[0]
                similarity = document_result[1]
                mockup_result[doc_id].append(similarity)

        return docs_score_json(index_result=mockup_result,
                               redis_connector=self.__redis)
