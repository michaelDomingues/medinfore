#!/usr/bin/env python3
import hashlib
import logging
import os
import re

from documenthandler.dreader import DocumentReader
from utilities.consts import VALID_PUNCTUATION
from utilities.utils import remove_stop_words, remove_punct, lower_case_values


class DocumentParser:
    def __init__(self, path_to_file: str):
        logging.info('Parsing file.... %s' % (path_to_file))
        if os.path.splitext(path_to_file)[1] != '.txt':
            logging.error('File unsupported format.... %s' % path_to_file)
            raise FileNotFoundError('File unsupported format....')

        self.__file_name = os.path.basename(path_to_file)
        self.__dreader = DocumentReader(path_to_file)
        self.__doc_content = next(self.__dreader.read_doc())
        self.__xml_entities = "&amp;|&quot;|&apos;"
        self.__file_hash = hashlib.sha1(self.__file_name.encode('utf-8')).hexdigest()
        self.__words = []
        #
        # Regex:
        #   (?:http|ftp|https):\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+  -- URL
        #   [\d]+(?:\-|\/)[\d]+(?:\-|\/)[\d]+ -- date
        #   [\d.,]+  -- numbers with dot or comma (e.g: 1.20; 1,20)
        #   [A-Z][.A-Z]+\\b\\.*  -- Job Titles (e.g: Dr.)
        #   w+[-']*\w+ -- hyphenated words (e.g: sugar-free)
        #   [^\s]+ -- everything except whitespace character
        #
        self.__regex_pattern = "(?:http|ftp|https):\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|[\d]+(?:\-|\/)[\d]+(?:\-|\/)[\d]+|[\d.,]+|[A-Z][.A-Z]+\\b\\.*|\w+[-']*\w+|[^\s]+"

    def __cleanup(self) -> list:
        """
        Remove unwanted chars from the doc content.
        Applies a regex to parse and tokenize text
        :return: list of tokens
        """
        # XML entities removal
        altered_content = re.sub(self.__xml_entities, "", self.__doc_content)
        altered_content = re.sub("&lt;", "lower than", altered_content)
        altered_content = re.sub("&gt;", "greater than", altered_content)
        # Multiple dots repetition. Replaced by one.
        altered_content = re.sub(r'\.+', ".", altered_content)
        # Characters repetition: 2+ times
        for punct in iter(VALID_PUNCTUATION):
            # URL exception
            if punct != '\/':
                altered_content = re.sub("[" + punct + "]{2,}", "", altered_content)

        tokens = re.findall(pattern=self.__regex_pattern, string=altered_content)
        # Remove tokens with puncts
        tokens = remove_punct(tokens=tokens)
        # Lower case content
        tokens = lower_case_values(tokens=tokens)
        # Remove stopwords
        tokens = remove_stop_words(tokens=tokens)

        return tokens

    def document_id_hash(self) -> str:
        """
        :return: document id hash
        """
        return self.__file_hash

    def document_name(self) -> str:
        """
        :return: document id
        """
        return self.__file_name

    def process(self) -> None:
        """
        Fires document parser
        :return:
        """
        logging.info('Processing file... %s' % (self.__file_name))
        self.__words = self.__cleanup()

    def words(self) -> list:
        """
        :return: list of word from document
        """
        return self.__words
