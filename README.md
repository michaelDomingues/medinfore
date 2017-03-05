# Medinfore
Medical information retrieval framework that allows indexing and searching on a medical corpus

Search is done in a localhost API using a set of requests.
So far if we want to add an extra document to the corpus we need to run first the `Indexing` and then restart the API so we have the updated indexes.

# Install

```
souce setup.sh
python3 setup.py install
```


# Corpus

To add a new document to corpus just add the file to the `corpus` folder and run `Indexing`

# Run

**INDEXING**

```
python3 main.py
```

**API**

```
python3 api/api.py
```

[TRY](http://localhost:5000/)


# API

**Routes**

| Route   | Parameters |                          Description                         | Example                                                       |
|---------|:----------:|:------------------------------------------------------------:|---------------------------------------------------------------|
| /search |      q     | Searches for best matches from the corpus agains the query q | http://localhost:5000/search?q=Human%20computer%20interaction |
|         |            |                                                              |                                                               |