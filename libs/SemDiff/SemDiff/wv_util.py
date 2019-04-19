def build_gensim_model():
    pass


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
