#!/usr/bin/env python3

import json

import logging
import redis

from collections import Counter
from utilities import utils

DOCUMENT_PREFIX = 'doc:'
NGRAM_KEY = 'ngram'
FREQ_KEY = 'freq'
DOCUMENT_ID_NAME_MAPPER = 'doc-id-name'


class RedisDB:
    def __init__(self):
        self.__connector = None
        try:
            self.__connector = redis.Redis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)
        except Exception as e:
            raise e

    def __del__(self):
        del self.__connector

    def add_document_name_by_id(self, document_id: str, document_name: str) -> None:
        """
        Stores map between gensim doc id and document name
        :param document_name:
        :param document_hash:
        :return:
        """
        self.__connector.hset(DOCUMENT_ID_NAME_MAPPER, document_id, document_name)

    def get_document_name_by_id(self, document_id: str) -> str:
        """
        Get document name from gensim document id
        :param document_hash:
        :return:
        """
        return self.__connector.hget(DOCUMENT_ID_NAME_MAPPER, document_id)

    def add_terms_ngram(self, document_hash: str, ngram) -> None:
        """
        Sets ngram to DB per document hash
        :param document_hash:
        :param ngram:
        :return:
        """

        self.__connector.hset(DOCUMENT_PREFIX + document_hash, NGRAM_KEY, json.dumps(ngram))

    def get_terms_ngram(self, document_hash: str) -> dict:
        """
        Gets ngram from DB based on document hash
        :param document_hash:
        :return:
        """
        return json.loads(self.__connector.hget(DOCUMENT_PREFIX + document_hash, NGRAM_KEY))

    def add_terms_frequencies(self, document_hash: str, freq: dict) -> None:
        """
        Sets words counter to DB per document hash
        :param document_hash:
        :param freq:
        :return:
        """
        self.__connector.hset(DOCUMENT_PREFIX + document_hash, FREQ_KEY, json.dumps(freq))

    def get_terms_frequencies(self, document_hash: str) -> dict:
        """
        Gets words counter from DB based on document hash
        :param document_hash:
        :return:
        """
        return json.loads(self.__connector.hget(DOCUMENT_PREFIX + document_hash, FREQ_KEY))

    def documents_have_terms(self, query: str, check_suggestions: bool) -> tuple:
        """
        Searches if query terms occur before overloading index search
        :param query_terms:
        :return:
        """
        neighbors_terms = Counter()
        query_terms_exist = False

        logging.info('Checking neighbors terms')
        for document in self.__connector.scan_iter('%s*' % (DOCUMENT_PREFIX)):
            document_hash = document.split(DOCUMENT_PREFIX)[1]
            terms_frequencies = self.get_terms_frequencies(document_hash=str(document_hash))
            terms_ngram = self.get_terms_ngram(document_hash=str(document_hash))
            terms_list = terms_frequencies.keys()

            query_terms = [query] if check_suggestions else query.split()

            # At least on query term exists in the terms list
            if set(query_terms).intersection(terms_list):
                query_terms_exist = True

                if check_suggestions:
                    # Working just for a single query word.
                    # Query with 2 words is a lot more specific
                    if query in terms_ngram:
                        terms_counter = terms_ngram[query]
                        terms_counter_just_words = dict(
                            filter(lambda w: utils.is_number(word=w[0]) is False and w[0] != query,
                                   terms_counter.items()))
                        neighbors_terms += Counter(terms_counter_just_words)
                    else:
                        logging.info('Query suggestions not available for %s' % (query))
                else:
                    return query_terms_exist, neighbors_terms

        neighbors_terms = dict(neighbors_terms.most_common(3)).keys()
        return query_terms_exist, neighbors_terms
