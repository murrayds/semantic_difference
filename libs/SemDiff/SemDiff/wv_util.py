def build_gensim_model(features,
                       num_features = 100,
                       min_word_count = 100,
                       context = 5,
                       downsampling = 1e-3,
                       verbose = True):

    """

    """
    from gensim.models import Phrases
    from gensim.models import word2vec
    import time
    import logging
    import multiprocessing

    start = time.time();

    if (verbose):
        # Lets make sure that we are logging—this will take a long time and its good to get updates
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',\
        level=logging.INFO)

    # Set values for various parameters
    num_features = 100;    # Dimensionality of the hidden layer representation
    min_word_count = 100;   # Minimum word count to keep a word in the vocabulary
    num_workers = multiprocessing.cpu_count();       # Number of threads to run in parallel set to total number of cpus.
    context = 5          # Context window size (on each side)
    downsampling = 1e-3   # Downsample setting for frequent words

    # Transforming to bigram representation
    bigram_transformer = Phrases(features)

    if (verbose):
        print("Training model...")

    # Initialize and train the model
    model = word2vec.Word2Vec(bigram_transformer[features],
                              workers=num_workers, \
                              size=num_features, \
                              min_count = min_word_count, \
                              window = context, \
                              sample = downsampling);

    # We don't plan on training the model any further, so calling
    # init_sims will make the model more memory efficient by normalizing the
    # vectors in-place.
    model.init_sims(replace=True);

    return(model)


def preprocess_data(df, text_col=None, duplicate_cols=None, verbose=False):
    """
    Pre-processes the data for use in the word2vec model. Performs basic
    steps such as stripping whitespace, punctiation, and non-alphanumeric
    characters.

    Requures a pandas dataframe containing the data, and a column name to index
    the data from
    """
    from gensim.parsing.preprocessing import preprocess_string, \
    strip_multiple_whitespaces, strip_non_alphanum, strip_punctuation

    import time as time

    # Define the custom filters
    CUSTOM_FILTERS = [lambda x: x.lower(), strip_multiple_whitespaces,
    strip_punctuation, strip_non_alphanum]

    start = time.time()

    if (text_col is None):
        print("Provide the name to index the text column in the data frame")

    if (duplicate_cols is not None):
        df = df.drop_duplicates(subset = duplicate_cols)

    df = df.dropna(subset = ["text"])

    features = []
    for sentence in df[text_col]:
        clean_text = preprocess_string(sentence, CUSTOM_FILTERS)
        features.append(clean_text)

    if (verbose):
        print('Total time: ' + str((time.time() - start)) + ' secs')

    return(features)
