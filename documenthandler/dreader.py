#!/usr/bin/env python3

import types


class DocumentReader:
    def __init__(self, doc):
        """
        Receives doc
        :param doc: path
        """
        self.__doc = doc

    def read_doc(self) -> types.GeneratorType:
        """
        Returns generator for the file content
        :return:
        """
        with open(file=self.__doc, mode="r", encoding="utf-8") as f:
            # for filename in os.listdir(input_file):
            #     if ".txt" not in filename:
            #         continue
            #
            #     with open(input_file + "/" + filename, "r") as file:
            #         medical_text = file.read()
            yield f.read()
