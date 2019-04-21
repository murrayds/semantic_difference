#!/usr/bin/env python

import SemDiff as sd
import pandas as pd
from gensim.models import Word2Vec

HOTELS_PATH = '~/Documents/semantic_difference/data/hotel_text.csv'
RESTAURANTS_PATH = '~/Documents/semantic_difference/data/restaurant_text.csv'
STORE_PATH = '~/Documents/semantic_difference/data/store_text.csv'

HOTELS_SAVE_PATH = "~/Documents/semantic_difference/data/hotel_model.wv"
RESTAURANTS_SAVE_PATH = "~/Documents/semantic_difference/data/restaurants_model.wv"
STORE_SAVE_PATH = '~/Documents/semantic_difference/data/store_model.wv'

print('Loading raw data')
# load data samples
hotel = pd.read_csv(HOTELS_PATH, sep = ',')
restaurant = pd.read_csv(RESTAURANTS_PATH, sep = ',')
store = pd.read_csv(STORE_PATH, sep = ',')

print("Pre-processing sentences")
# Here we preprocess the sentence data, removing whitespace, punctuation, and non-alphanumeric characteris
hotel_features = sd.preprocess_data(hotel,
                                    text_col='text',
                                    verbose=True)

restaurant_features = sd.preprocess_data(restaurant,
                                      text_col='text',
                                      verbose=True)

store_features = sd.preprocess_data(store,
                                    text_col='text',
                                    verbose=True)

# First train the model for the introduction data
hotel_model = sd.build_gensim_model(hotel_features,
                                    min_word_count = 50,
                                    verbose = True)
hotel_model.save(HOTELS_SAVE_PATH)


# Then the restaurant model
restaurant_model = sd.build_gensim_model(restaurant_features,
                                      min_word_count = 50,
                                      verbose = True)

restaurant_model.save(RESTAURANTS_SAVE_PATH)


# Finally the store model
store_model = sd.build_gensim_model(store_features,
                                      min_word_count = 50,
                                      verbose = True)

store_model.save(STORE_SAVE_PATH)
