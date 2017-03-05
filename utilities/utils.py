#!/usr/bin/env python3

def docs_score_json(index_result: list) -> list:
    result = []
    index_result.sort(key=lambda tup: tup[1], reverse=True)
    for doc_result in iter(index_result):
        result.append({"doc_id": doc_result[0],
                       "score": str(doc_result[1])})
    return result
