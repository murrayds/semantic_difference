# All credit for the following code goes to Jisun An, author of the original
# SemAxis paper. The repo containing this project can be found at the following link
# https://github.com/ghdi6758/SemAxis/
import numpy as np
from scipy import spatial

def cosine_similarity(vec1, vec2):
    return 1.0 - spatial.distance.cosine(vec1, vec2)

def get_avg_vec(emb, word, k):
    tmp = []
    tmp.append(emb.wv[word])
    for closest_word, similarity in emb.wv.most_similar(positive=word, topn=k):
        tmp.append(emb.wv[closest_word])
    avg_vec = np.mean(tmp, axis=0)
    return avg_vec

def transform_antonym_to_axis(emb, antonym, k):
    if k == 0:
        return emb.wv[antonym[1]] - emb.wv[antonym[0]]

    else:
        vec_antonym_1 = get_avg_vec(emb, antonym[1], k)
        vec_antonym_0 = get_avg_vec(emb, antonym[0], k)

        return vec_antonym_1 - vec_antonym_0

def project_word_on_axis(emb, word, antonym, k=10):
    return cosine_similarity(emb.wv[word], transform_antonym_to_axis(emb, antonym, k))


# I (Dakota Murray) created the following function as a better way to call the
# actual embedding process, jsut for testing purposes
def test_perform_embedding(embedding_path):
    import gensim
    # Define the path to the embedding folder
    embed = gensim.models.KeyedVectors.load_word2vec_format(embedding_path)
    result = project_word_on_axis(embed, "baby", ("hate", "love"), k=3)
    print(result)
