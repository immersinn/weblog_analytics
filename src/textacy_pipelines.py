

import numpy
import spacy
import textacy

import utils
import article_handles


def pipe01(limit=0):
    
    # Define textacy doc preprocessing
    textacy_preprocessor = lambda text: textacy.preprocess.preprocess_text(text,
                                                                       no_contractions=True,
                                                                       no_numbers=True,
                                                                       no_emails=True,
                                                                       no_currency_symbols=True,
                                                                       lowercase=True)
    # Define nlp pipeline
    nlp = spacy.load("en", add_vectors=False)
    nlp.pipeline = [nlp.tagger, nlp.parser]
    
    # 
    handle = article_handles.articleObjectPhysOrg
    
    # Do all the other things
    with utils.mongo_open('BlogData', 'PhysOrg') as conn:
        article_iter = conn.query(conditions={'html' : {'$ne' : 'None'},
                                              'url' : {'$regex' : '^http://phys.org/news/'}},
                                  limit=limit)
        content_stream, metadata_stream = utils.proc_art_iterator(handle=handle,
                                                                  mdb_iterator=article_iter,
                                                                  tpp=textacy_preprocessor)
        corpus = textacy.Corpus(lang=nlp, texts=content_stream, metadatas=metadata_stream)
    
    # Return the data
    return(corpus)


def make_pipe01_dataset(name = "CORPUS_physorg_articles_pipe01", mini_size=0):
    corpus = pipe01(limit=0)
    utils.save_corpus(name, corpus)
    if mini_size > 0:
        perm = numpy.random.permutation(range(corpus.n_docs))
        remove = set(perm[:(corpus.n_docs - mini_size)])
        corpus.remove(lambda doc: doc.corpus_index in remove)
        utils.save_corpus(name+'_mini' + str(mini_size), corpus)
            
    
    
if __name__=="__main__":
    make_pipe01_dataset(mini_size=2500)