import os
import sys
import pprint
import tensorflow as tf
from tensorflow.contrib.tensorboard.plugins import projector
import argparse
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import interfacespfy as isp

description_hint = """
    A Small cluster vizualization for spotify audio data
    from multiple users using tensorflow.
"""

parser = argparse.ArgumentParser(description=description_hint, formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('user', help='Your Spotify URI')
parser.add_argument('-o', '--others', nargs='*', help='Other users Spotify URI', dest='others')

args = parser.parse_args()

username = args.user
others = args.others

LOG_DIR = 'logs'
metadata = os.path.join(LOG_DIR, 'metadata.tsv')

COLUMN_NAMES = ['speechiness', 'valence', 'liveness', 'danceability', 'loudness', 'acousticness',
                'instrumentalness', 'energy', 'tempo']

spfy = isp.login_user(username)

data = isp.get_favorite_songs(spfy, features=True)

main_data = pd.DataFrame(data)

others_data = {}

for other in others:
    playlists = isp.get_user_playlists(spfy, other, features=True)

    df_songs = pd.DataFrame(playlists)
    others_data[other] = df_songs

with open(metadata, 'w+') as metadata_file:
    for _ in range(main_data.shape[0]):
        metadata_file.write('{}\n'.format(username))

    for other, data in others_data.items():
        for _ in range(data.shape[0]):
            metadata_file.write('{}\n'.format(other))

for data in others_data.values():
    main_data = main_data.merge(data, how='left', on='id')

all_data = tf.Variable(main_data[COLUMN_NAMES].values, name='audio_features')

with tf.Session() as sess:
    saver = tf.train.Saver([all_data])

    sess.run(all_data.initializer)
    saver.save(sess, os.path.join(LOG_DIR, 'images.ckpt'))

    config = projector.ProjectorConfig()

    embedding = config.embeddings.add()
    embedding.tensor_name = all_data.name

    embedding.metadata_path = 'metadata.tsv'

    projector.visualize_embeddings(tf.summary.FileWriter(LOG_DIR), config)

