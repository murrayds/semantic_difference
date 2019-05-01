#!/usr/bin/env python

import SemDiff as sd
import pandas as pd
from gensim.models import Word2Vec
from gensim.models import FastText

DATA_PATH = '/Users/dakotamurray/Documents/semantic_difference/data/L665/'


INTRO_W2V_PATH = DATA_PATH + "intro_citance_model.wv"
METHODS_W2V_PATH = DATA_PATH + "methods_citance_model.wv"
DISCUSSION_W2V_PATH = DATA_PATH + "discussion_citance_model.wv"

W2V_SEMAXIS_SAVE_PATH = DATA_PATH + "semantic_word_axes.csv"

INTRO_FT_PATH = DATA_PATH + "intro_citance_model_fasttext.wv"
METHODS_FT_PATH = DATA_PATH + "methods_citance_model_fasttext.wv"
DISCUSSION_FT_PATH = DATA_PATH + "discussion_citance_model_fasttext.wv"

FT_SEMAXIS_SAVE_PATH = DATA_PATH + "semantic_word_axes_fasttext.csv"

HEDGES_PATH = DATA_PATH + "hedges.txt"

INTRO_METHOD_SAVE = DATA_PATH + "intro_methods_interword_similarity.csv"
INTRO_DISCUSSION_SAVE = DATA_PATH + "intro_discussion_interword_similarity.csv"
METHOD_DISCUSSION_SAVE = DATA_PATH + "methods_discussion_interword_similarity.csv"

INTRO_FT_SAVE = DATA_PATH + "intro_methods_interword_similarity_ft.csv"
METHODS_FT_SAVE = DATA_PATH + "intro_discussion_interword_similarity_ft.csv"
DISCUSSION_FT_SAVE = DATA_PATH + "methods_discussion_interword_similarity_ft.csv"

hedges = [i.strip() for i in open(HEDGES_PATH).readlines()]

# repeat for a set of antonyms
antonyms = [
    ["good", "bad"],
    ['always', 'never'],
    ['higher', 'lower'],
    ['certain', 'impossible'],
    ['strong', 'weak'],
    ['very', 'slightly'],
    ['similar', 'unlike'],
    ['reasonable', 'arbitrary'],
    ['expected', 'unexpected'],
    ['actual', 'hypothetical'],
    ['systemic', 'endemic'],
    ['new', 'established'],
    ['known', 'unknown'],
    ['answer', 'question'],
    ['further', 'closer'],
    ['success', 'failure']
]

intro_model = Word2Vec.load(INTRO_W2V_PATH)
methods_model = Word2Vec.load(METHODS_W2V_PATH)
discussion_model = Word2Vec.load(DISCUSSION_W2V_PATH)

intro_list = []
methods_list = []
discussion_list = []
ant_names = []
word_list = []
for word in hedges:
    for ant in antonyms:
        intro_list.append(sd.project_word_on_axis(intro_model, word, ant, k = 3))
        methods_list.append(sd.project_word_on_axis(methods_model, word, ant, k = 3))
        discussion_list.append(sd.project_word_on_axis(discussion_model, word, ant, k = 3))
        word_list.append(word)

        ant_names.append("{}-{}".format(ant[0], ant[1]))


df = pd.DataFrame({'antonym': ant_names,
                   'intro': intro_list,
                   'methods': methods_list,
                   'discussion': discussion_list,
                   'word': word_list},
                  index = ant_names)

df.to_csv(W2V_SEMAXIS_SAVE_PATH)

#
# Intro and Method comparison
#
print("Word2Vec: Intro-Method Comparison")
shared = sd.get_shared_words(intro_model, methods_model, topn_words = 10000)
frames = []
for word in hedges:
    frames.append(sd.model_term_similarity(intro_model, methods_model, word, shared))

intro_meth_df = pd.concat(frames)
intro_meth_df.to_csv(INTRO_METHOD_SAVE)

#
# Intro and Discussion comparison
#
print("Word2Vec: Intro-Discussion Comparison")
shared = sd.get_shared_words(intro_model, discussion_model, topn_words = 10000)
frames = []
for word in hedges:
    frames.append(sd.model_term_similarity(intro_model, discussion_model, word, shared))

intro_disc_df = pd.concat(frames)
intro_disc_df.to_csv(INTRO_DISCUSSION_SAVE)

#
# Now the Method and Discussion
#
print("Word2Vec: Method-Discussion Comparison")
shared = sd.get_shared_words(methods_model, discussion_model, topn_words = 10000)
frames = []
for word in hedges:
    frames.append(sd.model_term_similarity(methods_model, discussion_model, word, shared))

intro_disc_df = pd.concat(frames)
intro_disc_df.to_csv(METHOD_DISCUSSION_SAVE)

#
# Now repeat for the FastText models,
#
print("FastText: Loading Models")
intro_model_ft = FastText.load(INTRO_FT_PATH)
methods_model_ft = FastText.load(METHODS_FT_PATH)
discussion_model_ft = FastText.load(DISCUSSION_FT_PATH)


intro_list = []
methods_list = []
discussion_list = []
ant_names = []
word_list = []
for word in hedges:
    for ant in antonyms:
        intro_list.append(sd.project_word_on_axis(intro_model_ft, word, ant, k = 3))
        methods_list.append(sd.project_word_on_axis(methods_model_ft, word, ant, k = 3))
        discussion_list.append(sd.project_word_on_axis(discussion_model_ft, word, ant, k = 3))
        word_list.append(word)

        ant_names.append("{}-{}".format(ant[0], ant[1]))


df = pd.DataFrame({'antonym': ant_names,
                   'intro': intro_list,
                   'methods': methods_list,
                   'discussion': discussion_list,
                   'word': word_list},
                  index = ant_names)

df.to_csv(FT_SEMAXIS_SAVE_PATH)


#
# Intro and Method comparison
#
print("FastText: Intro-Method Comparison")
shared = sd.get_shared_words(intro_model_ft, methods_model_ft, topn_words = 10000)
frames = []
for word in hedges:
    frames.append(sd.model_term_similarity(intro_model_ft, methods_model_ft, word, shared))

df = pd.concat(frames)
df.to_csv(INTRO_FT_SAVE)

#
# Intro and Discussion comparison
#
print("FastText: Intro-Discussion Comparison")
shared = sd.get_shared_words(intro_model_ft, discussion_model_ft, topn_words = 10000)
frames = []
for word in hedges:
    frames.append(sd.model_term_similarity(intro_model_ft, discussion_model_ft, word, shared))

df = pd.concat(frames)
df.to_csv(METHODS_FT_SAVE)

#
# Now the Method and Discussion
#
print("FastText: Methods-Discussion Comparison")
shared = sd.get_shared_words(methods_model_ft, discussion_model_ft, topn_words = 10000)
frames = []
for word in hedges:
    frames.append(sd.model_term_similarity(methods_model_ft, discussion_model_ft, word, shared))

df = pd.concat(frames)
df.to_csv(DISCUSSION_FT_SAVE)
