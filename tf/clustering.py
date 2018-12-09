import tensorflow as tf
import numpy as np
import scipy.stats as scp

# TODO Normalize loudness and tempo to become a value between 0 and 1
COLUMN_NAMES = ['speechiness', 'valence', 'liveness', 'danceability', 'loudness', 'acousticness',
                'instrumentalness', 'energy', 'tempo']

FEATURE_COLUMNS = {column: tf.feature_column.numeric_column(key=column) for column in COLUMN_NAMES}


def get_columns(features):
    return {feature: tf.feature_column.numeric_column(key=feature) for feature in features}


def cluster_input_fn(features, labels=None):
    """
        This function adapt data from the API to the format necessary for tensorflow.
        It can be used to train the k-means for only one user when no label is passed
        and for multiple users when the labels are specified

    :param features: Dataframe with the audio features
    :param labels: Numpy array with a username for each sample music in the dataset
    :return: tensorflow dataset
    """

    feat_tf = dict(features)

    if labels is None:
        dataset = tf.data.Dataset.from_tensor_slices(feat_tf)
    else:
        dataset = tf.data.Dataset.from_tensor_slices((feat_tf, labels))

    return dataset.shuffle(1000).batch(1000)


def get_centers(data, labels=None, num_iterations=10, features=None):

    if features is None:
        features = COLUMN_NAMES  
    else:
        for feat in features:
            if feat not in COLUMN_NAMES:
                raise FeaturesError("All elements in the features list must be in the set: {}".format(COLUMN_NAMES))

    feat_columns = get_columns(features)

    num_clusters = 1
    if labels is not None:
        num_clusters = data['user'].nunique()

    kmeans = tf.contrib.factorization.KMeansClustering(
        num_clusters=num_clusters, use_mini_batch=False,
        feature_columns=feat_columns.values(),
    )

    for _ in range(num_iterations):
        kmeans.train(lambda: cluster_input_fn(data, labels))

    return kmeans.cluster_centers()


def exponential_distance(song, user_center, cov, features=None):
    if features is None:
        features = COLUMN_NAMES
    try:
        song_feat = song[features].values
    except KeyError:
        raise FeaturesError("All elements in features list must be in the set: {}".format(COLUMN_NAMES))

    n_dim = len(features)
    song_feat = song_feat.reshape((-1, n_dim)).astype(np.float64)
    assert song_feat.shape == user_center.shape, "song feature shape is different from the user preference vector's " \
                                                 "shape: {} != {}".format(song_feat.shape, user_center.shape)

    norm = -0.5 * np.linalg.norm(song_feat - user_center) ** 2
    print(f"norm is {norm}")

    identity = np.eye(n_dim, dtype=np.float64)
    mean = user_center.flatten()
    return scp.multivariate_normal.pdf(song_feat, mean, cov)


def playlist_score(playlist, center):
    scores = np.array([])
    for song in playlist:
        scores.append(exponential_distance(song, center)) 
    return np.mean(scores)


class FeaturesError(Exception):
    def __init__(self, message):
        super(FeaturesError, self).__init__(self, message)


if __name__ == '__main__':
    import sys
    import os.path
    import pandas as pd

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

    import interfacespfy as isp

    def maybe_download(username):
        filepath = '../csvfiles/' + username + 'saved.csv'

        if os.path.isfile(filepath):
            all_data = pd.read_csv(filepath)
        else:
            spfy = isp.login_user('belzedu')

            features = isp.get_favorite_songs(spfy, features=True)
            data = isp.get_favorite_songs(spfy)

            song_feat = pd.DataFrame(features)
            song_data = pd.DataFrame(data)

            all_data = song_data.merge(song_feat, on='id', how='left')

            all_data.to_csv(filepath)
            print("Downloaded data:")
            print(all_data)

        return all_data

    saved_data = maybe_download('belzedu')

    # Returns a numpy array with shape (num_features, 1)
    features = ['loudness', 'energy']
    my_center = get_centers(saved_data)

    samples = saved_data.sample(50)

    cov = np.cov(saved_data[COLUMN_NAMES].values.T)
    for pos, song in samples.iterrows():
        print(song['name'])
        print(exponential_distance(song, my_center, cov))
