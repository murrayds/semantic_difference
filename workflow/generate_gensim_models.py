#!/usr/bin/env python

import SemDiff as sd
import pandas as pd
from gensim.models import Word2Vec

DATA_PATH = '../data/'

INTRO_SENTENCES_PATH = DATA_PATH + 'introduction_million_sample.rpt'
METHODS_SENTENCES_PATH = DATA_PATH + 'methods_million_sample.rpt'
DISCUSSION_SENTENCES_PATH = DATA_PATH + 'discussion_million_sample.rpt'

INTRO_SAVE_PATH = DATA_PATH + "intro_citance_model.wv"
METHODS_SAVE_PATH = DATA_PATH + "methods_citance_model.wv"
DISCUSSION_SAVE_PATH = DATA_PATH + "discussion_citance_model.wv"

print('Loading raw data')
# load data samples
intro = pd.read_csv(INTRO_SENTENCES_PATH, sep = '\t')
methods = pd.read_csv(METHODS_SENTENCES_PATH, sep = '\t')
discussion = pd.read_csv(DISCUSSION_SENTENCES_PATH, sep = '\t')

print("Pre-processing sentences")
# Here we preprocess the sentence data, removing whitespace, punctuation, and non-alphanumeric characteris
intro_features = sd.preprocess_data(intro,
                                    text_col='text',
                                    duplicate_cols = ['doi', 'sentence_seq'],
                                    verbose=True)

methods_features = sd.preprocess_data(methods,
                                      text_col='text',
                                      duplicate_cols = ['doi', 'sentence_seq'],
                                      verbose=True)

discussion_features = sd.preprocess_data(discussion,
                                      text_col='text',
                                      duplicate_cols = ['doi', 'sentence_seq'],
                                      verbose=True)


# First train the model for the introduction data
intro_model = sd.build_gensim_model(intro_features,
                                    min_word_count = 100,
                                    verbose = True)
intro_model.save(INTRO_SAVE_PATH)


# Then the methods model
methods_model = sd.build_gensim_model(methods_features,
                                      min_word_count = 100,
                                      verbose = True)

methods_model.save(METHODS_SAVE_PATH)

# And finally the discussion model
discussion_model = sd.build_gensim_model(discussion_features,
                                      min_word_count = 100,
                                      verbose = True)

discussion_model.save(DISCUSSION_SAVE_PATH)
