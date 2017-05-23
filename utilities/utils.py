#!/usr/bin/env python3

import numpy as np
import operator

from nltk.corpus import stopwords
from utilities.consts import VALID_PUNCTUATION
from redisdb.connector import RedisDB


def docs_score_json(index_result: dict, redis_connector: RedisDB) -> list:
    result = []

    # if render_from_gensim:
    hit_documents = 0
    for doc_id, doc_scores in index_result.items():
        if doc_scores:
            doc_name = redis_connector.get_document_name_by_id(document_id=doc_id)
            result.append({"\"doc_id\"": doc_id,
                           "\"doc_name\"": doc_name,
                           "\"score\"": str(np.mean(doc_scores))})
            hit_documents += 1

    if result:
        result.sort(key=operator.itemgetter("\"score\""), reverse=True)
    result = [{"\"hit_documents\"": hit_documents}] + result

    return result


def remove_stop_words(tokens: list) -> list:
    """
    Remove stop words for english language
    :param tokens:
    :return:
    """
    return [word for word in iter(tokens) if word not in stopwords.words('english')]


def lower_case_values(tokens: list) -> list:
    """
    Lower case all list values
    :param tokens:
    :return:
    """
    return [word.lower() for word in iter(tokens)]


def remove_punct(tokens: list) -> list:
    """
    Remove punct
    :param tokens:
    :return:
    """
    return list(filter(lambda token: token not in VALID_PUNCTUATION, tokens))


def is_number(word: str) -> bool:
    """
    Check if given string is number (int, long, float and complex)
    :param word:
    :return: bool
    """
    try:
        complex(word)
    except ValueError:
        return False

    return True
