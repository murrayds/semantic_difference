def model_term_similarity(base_model, other_model, word_to_check, shared_words):
    """
    Returns a basic similarity measure of a word between two models based on
    their similarity to words in a vocabulary of shared words
    """
    import pandas as pd

    x_sim = []
    y_sim = []

    for word in shared_words:
        if word in other_model.wv.vocab:
            abs_sim = base_model.similarity(word_to_check, word)
            citance_sim = other_model.similarity(word_to_check, word)
            x_sim.append(abs_sim)
            y_sim.append(citance_sim)

    df = pd.DataFrame({'x':x_sim, 'y':y_sim, 'word':word_to_check})

    return(df)


def get_shared_words(base_model, other_model, topn_words = 10000):
    """
    Finds the shared vocabulary of most common words between two word2vec models,
    up to the top n most common words (where n is provided by the user)
    """
    base_common = base_model.wv.index2entity[:topn_words]
    other_common = other_model.wv.index2entity[:topn_words]

    shared = []
    for word in base_common:
        if word in other_common:
            shared.append(word)

    return(shared)
