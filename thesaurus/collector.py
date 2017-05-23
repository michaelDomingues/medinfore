#!/usr/bin/env python3

import pymedtermino
import re
import logging

from utilities.consts import SNOMEDCT_FILTER_THRESHOLD
from pymedtermino.snomedct import *
from fuzzywuzzy import fuzz


class Collector:
    def __init__(self):
        pymedtermino.LANGUAGE = "en"
        pymedtermino.REMOVE_SUPPRESSED_CONCEPTS = True

    def get_snomed_ct_synonyms(self, query: str) -> list:
        """
        Searches SNOMED CT for clinical domain matches
        :param query: query from the outside world
        :return: list of related terms to search in the index
        """

        matching_terms = SNOMEDCT.search(query)
        # e.g.: Cardiac auscultation pulmonic area (body structure)
        # Filter term description without anatomy classification: e.g. (body structure)
        # TODO: Add AttributeError try except here ?!
        filtered_matching_terms = []
        for snomedct in iter(matching_terms):
            cleanup_coding_synoym = re.search('.+?(?=\s\()', snomedct.term).group()
            # Distance-based filter to remove similar suggestions
            if fuzz.partial_ratio(query.lower(), cleanup_coding_synoym.lower()) < SNOMEDCT_FILTER_THRESHOLD:
                filtered_matching_terms.append(cleanup_coding_synoym)
        return filtered_matching_terms

    def get_mockup_result(self, dict_num_docs: int) -> dict:
        """
        Builds a mockup indexer result based on the #documents
        :return: defaultdict
        """
        return {id: [] for id in range(0, dict_num_docs)}
