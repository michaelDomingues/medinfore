#!/usr/bin/env python3

import itertools
import os

import logging
import nltk

from collections import Counter, defaultdict
from gensim import corpora, models
from gensim import similarities

from utilities.consts import INDEX_TYPE_MatrixSimilarity, INDEX_TYPE_Similarity, DICT_PATH, CORPUS_PATH, INDEX_PATH, \
    INDEX_MM_PATH, LSI_MODEL


class Dictionary:
    def __init__(self, load_from_disk: bool, index_type: str):
        self.__ngram_levels = 2
        if self.__ngram_levels == 3:
            self.__terms_core = defaultdict(lambda: defaultdict(lambda: Counter()))
        else:
            self.__terms_core = defaultdict(lambda: Counter())
        self.__index_type = index_type
        self.__terms_frequency = Counter()
        # self.__pp = pprint.PrettyPrinter(indent=4)
        self.__corpus_list = []
        self.__dictionary = None
        self.__corpus = None
        self.__index = None
        self.__lsi_model = None
        self.__tfidf = None

        if load_from_disk:
            logging.info('Load data from disk...')
            self.__load_dict()
            self.__load_corpus()
            self.__load_lsi_model()
            self.__load_index()

        else:
            self.__clean_files()
            self.__dictionary = corpora.Dictionary()
            # self.__dictionary.save(DICT_PATH)
            # TODO: Change this to something memory-friendly

    def __clean_files(self: bool):
        """
        Clean all corpus/dict/index files
        :return:
        """
        if (os.path.exists(DICT_PATH)):
            os.remove(DICT_PATH)
        if (os.path.exists(CORPUS_PATH)):
            os.remove(CORPUS_PATH)
        if (os.path.exists(INDEX_PATH)):
            os.remove(INDEX_PATH)
        if (os.path.exists(INDEX_MM_PATH)):
            os.remove(INDEX_MM_PATH)

    def __remove_low_frequency_corpus_words(self):
        """
        Removes words that appear just 1 time in all corpus
        :return:
        """
        self.__corpus_list = [[word for word in doc_tokens if self.__terms_frequency[word] > 1] for doc_tokens in
                              self.__corpus_list]

    def build_word_knowledge(self, tokens: list) -> None:
        """
        Builds tree of knowledge.
        :param tokens: list of words from document
        :return:s
        """
        self.__doc2dictionary(tokens=tokens)
        for word in iter(tokens):
            self.__terms_frequency[word] += 1
        self.__ngrams(tokens=tokens)

    def __ngrams(self, tokens: list) -> None:
        ngrams = nltk.ngrams(tokens, self.__ngram_levels)
        for seq in iter(ngrams):
            if self.__ngram_levels == 3:
                self.__terms_core[seq[0]][seq[1]].update([seq[2]])
            else:
                self.__terms_core[seq[0]].update([seq[1]])

    def get_words_core(self) -> defaultdict:
        """
        Returns words core relationships.
        :return:
        """
        return self.__terms_core

    def get_terms_frequency(self) -> Counter:
        """
        Returns terms frequency.
        :return:
        """
        return self.__terms_frequency

    def get_number_docs(self) -> int:
        """
        Return dictionary number of docs
        :return:
        """
        return self.__dictionary.num_docs

    def __doc2dictionary(self, tokens: list) -> None:
        """
        Adds a new doc to the existing dictionary
        :param tokens: Tokenized document
        :return:
        """
        assert (self.__dictionary != None), "Dictionary not created yet!"
        tokens_bow = [tokens]
        self.__dictionary.add_documents(documents=tokens_bow)
        # Tries to on each document input to avoid losing progress
        self.__save_dict()
        self.__corpus_list += tokens_bow

    def __save_dict(self):
        """
        Save dict to disk
        :return:
        """
        self.__dictionary.save(DICT_PATH)

    def setup_corpus(self):
        """
        Inits Corpus
        :return:
        """
        self.__remove_low_frequency_corpus_words()
        corpus_bow = [self.__dictionary.doc2bow(corpus) for corpus in self.__corpus_list]
        corpora.MmCorpus.serialize(fname=CORPUS_PATH, corpus=corpus_bow)
        self.__corpus = corpora.MmCorpus(CORPUS_PATH)

    def __generate_bow(self, tokens: list) -> corpora.Dictionary:
        """
        Generates corpus from document
        :param tokens: Tokenized document
        :return:
        """
        return self.__dictionary.doc2bow(document=tokens)

    def __load_dict(self) -> None:
        """
        Load dictionary from disk
        :return:
        """
        self.__dictionary = corpora.Dictionary.load(fname=DICT_PATH)

    def __load_corpus(self) -> None:
        """
        Load corpus from disk
        :return:
        """
        self.__corpus = corpora.MmCorpus(CORPUS_PATH)

    # TODO: REDO/RE-THINK THIS!!!
    def __update_corpus(self, tokens: list) -> None:
        """
        Update corpus with new doc.
        :param tokens: Tokenized document
        :return:
        """
        new_corpus = [self.__generate_bow(tokens=tokens)]
        corpus_both = itertools.chain(self.__corpus, new_corpus)
        # Update corpus on disk and pointer in memory
        corpora.MmCorpus.serialize(CORPUS_PATH, corpus_both)
        self.__load_corpus()
        # Re-index
        self.__reindex()

        # for doc in corpus:
        #     print(doc[0])
        # corpus = corpora.MmCorpus(CORPUS_PATH)

    def __load_lsi_model(self) -> None:
        """
        Loads LSI model from disk
        :return:
        """
        self.__lsi_model = models.LsiModel.load(fname=LSI_MODEL)

    def __lsi_space(self):
        """
        Builds lsi model
        :return:
        """
        assert (self.__dictionary != None), "Dictionary not created yet!"
        assert (self.__corpus != None), "Corpus not loaded yet!"
        self.__tfidf = models.TfidfModel(self.__corpus, normalize=True)
        self.__lsi_model = models.LsiModel(self.__tfidf[self.__corpus], id2word=self.__dictionary, num_topics=400)
        self.__lsi_model.save(fname=LSI_MODEL)

    def __save_index(self):
        """
        Save index to disk
        :return:
        """
        self.__index.save(INDEX_PATH)

    def __load_index(self):
        """
        Loads index from disk
        :return:
        """
        if self.__index_type == INDEX_TYPE_MatrixSimilarity:
            self.__index = similarities.MatrixSimilarity.load(INDEX_PATH)
        elif self.__index_type == INDEX_TYPE_Similarity:
            self.__index = similarities.Similarity.load(INDEX_PATH)

    def index(self):
        """
        Creates index for the first time
        :return:
        """
        self.__lsi_space()

        if self.__index_type == INDEX_TYPE_MatrixSimilarity:
            self.__index = similarities.MatrixSimilarity(self.__lsi_model[self.__corpus])
        elif self.__index_type == INDEX_TYPE_Similarity:
            self.__index = similarities.Similarity(output_prefix='./index', corpus=self.__corpus,
                                                   num_features=len(self.__dictionary))
        self.__save_index()

    def term_relation_vector(self, word: str) -> list:
        """
        Builds a word relation to help on building word vector to enigma.
        e.g: [('Office', '2016', 'The', 1), ('Office', '2016', 'for', 1)]
        :param word: outer expected word
        :return: list of relation for given word
        """
        result = []
        for inner_relation in self.__terms_core[word].items():
            inner_word = inner_relation[0]
            counter = inner_relation[1]
            for counter_word in counter.elements():
                result.append((word, inner_word, counter_word, counter[counter_word]))
        return result

    def query(self, query: str) -> list:
        """
        Calculates the score for given query in the current document.
        :param query: string to search for
        :return: list with best results in the format (doc_hash,score)
        """

        # TODO: Add logic for query with 1 or multiple strings
        # Conditional operators maybe.
        vec_bow = self.__generate_bow(tokens=query.lower().split())
        vec_lsi = self.__lsi_model[vec_bow]  # convert the query to LSI space
        sims = self.__index[vec_lsi]
        return list(enumerate(sims))
        # Result: [(2, 0.99844527), (0, 0.99809301) ]
