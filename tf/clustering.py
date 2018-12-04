import tensorflow as tf
import numpy as np

COLUMN_NAMES = ['speechiness', 'valence', 'liveness', 'danceability', 'loudness', 'acousticness',
                'instrumentalness', 'energy', 'tempo']


FEATURE_COLUMNS = {column: tf.feature_column.numeric_column(key=column) for column in COLUMN_NAMES}
#FEATURE_COLUMN = tf.feature_column.numeric_column(key='features', dtype=tf.float32)


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


def get_centers(data, labels=None, num_iterations=10):

    num_clusters = 1
    if labels is not None:
        num_clusters = data['user'].nunique()

    kmeans = tf.contrib.factorization.KMeansClustering(
        num_clusters=num_clusters, use_mini_batch=False,
        feature_columns=FEATURE_COLUMNS.values(),
    )

    for _ in range(num_iterations):
        kmeans.train(lambda: cluster_input_fn(data, labels))

    return kmeans.cluster_centers()


def exponential_distance(song, user_center):
    return np.exp(np.power(song - user_center, 2)) / np.sqrt(2 * np.pi)


if __name__ == '__main__':
    import sys
    import os.path
    import pandas as pd

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

    import interfacespfy as isp

    spfy = isp.login_user('belzedu')

    features = isp.get_favorite_songs(spfy, features=True)
    data = isp.get_favorite_songs(spfy)

    song_feat = pd.DataFrame(features)
    song_data = pd.DataFrame(data)

    all_data = song_data.merge(song_feat, on='id', how='left')

    print(all_data)

    # Returns a numpy array with shape (num_features, 1)
    my_center = get_centers(all_data[COLUMN_NAMES])

    print(my_center)
