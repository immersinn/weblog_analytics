# not right shebang
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 15:08:05 2017

@author: immersinn
"""


import os
from itertools import tee, starmap
from cytoolz.itertoolz import cons, pluck

from pymongo import MongoClient
import pandas
from textacy.corpus import Corpus


def get_main_dir():
    fd = os.path.split(os.path.realpath(os.path.split(__file__)[0]))[0]
    return(fd)


def get_data_dir():
    fd = get_main_dir()
    data_dir = os.path.join(fd, "data")
    return(data_dir)



def unzip(seq):
    """
    Borrowed from ``toolz.sandbox.core.unzip``, but using cytoolz instead of toolz
    to avoid the additional dependency.
    """
    seq = iter(seq)
    # check how many iterators we need
    try:
        first = tuple(next(seq))
    except StopIteration:
        return tuple()
    # and create them
    niters = len(first)
    seqs = tee(cons(first, seq), niters)
    return tuple(starmap(pluck, enumerate(seqs)))


def proc_art_iterator(handle, mdb_iterator, tpp):
    def proc_item(entry):
    ##    # Step 01: Get next doc from MongoDB
    ##    entry = mdb_iterator.next()

        # Step 02: Extract Content from Article
        article = handle(entry)
        article.processArticle()

        # Step 03: pre-process Content with textacy
        content = tpp(article.contents)
        
        return(content, article.meta)

    return unzip((proc_item(item) for item in mdb_iterator))


class mongo_open:
    
    def __init__(self, db_name, coll_name):
        self.db_name = db_name
        self.coll_name = coll_name
    
    def __enter__(self,):
        self.client = MongoClient()
        self.db = self.client[self.db_name]
        self.coll = self.db[self.coll_name]
        return(self)
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()        
    
    def query(self, conditions, fields=None, limit=0):
        return(self.coll.find(conditions, fields).limit(limit))
    
    
def retrieve_article_htmls(coll_name, limit=100):
    
    with mongo_open('BlogData', coll_name) as conn:
        arts_html = [a for a in conn.query(conditions={'html' : {'$ne' : 'None'},
                                                       'url' : {'$regex' : '^http://phys.org/news/'}},
                                           limit=limit)]
    arts_html = pandas.DataFrame(arts_html)
    return(arts_html)


def save_corpus(name, corpus, data_sub_dir="processed", compression='gzip'):
    path = os.path.join(get_data_dir(), data_sub_dir, name)
    os.mkdir(path)
    corpus.save(path=path, name=name, compression=compression)
    
    
def load_corpus(name, data_sub_dir="processed", compression='gzip'):
    path = os.path.join(get_data_dir(), data_sub_dir, name)
    return(Corpus.load(path=path, name=name, compression=compression))
