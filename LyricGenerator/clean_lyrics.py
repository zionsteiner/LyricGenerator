import pandas as pd
import numpy as np
import re
import argparse
from functools import partial
import os


def clean_artist_lyrics(path):
    lyrics_df = pd.read_pickle(path)

    # Remove all text within brackets or parentheses
    pattern = r'[\[\({](.*?)[\]\)}]'
    kwargs = {'pattern': pattern,
              'repl': ''}
    regex = partial(re.sub, **kwargs)
    lyrics_df['lyrics'] = lyrics_df['lyrics'].apply(lambda lyrics: regex(string=lyrics))
    # Remove printable bad chars
    lyrics_df['lyrics'].replace(to_replace='[^A-Za-z0-9!.\'",?]', value=' ', regex=True, inplace=True)
    # Strip text
    lyrics_df['lyrics'] = lyrics_df['lyrics'].str.strip()
    # Remove instrumental entries
    lyrics_df = lyrics_df[lyrics_df['lyrics'] != 'Instrumental']
    # Remove entries with no lyrics
    lyrics_df['lyrics'].replace(to_replace=r'^\s*$', value=np.nan, regex=True, inplace=True)
    lyrics_df = lyrics_df[lyrics_df['lyrics'].notnull()]

    # Save
    try:
        artist = lyrics_df.iloc[0]['artist']
    except:
        raise Exception('No non-null songs in dataframe')
    lyrics_df.reset_index(drop=True, inplace=True)
    lyrics_df.to_pickle(f'lyrics/{artist.replace(" ", "_")}_cleaned.pkl')

    # Delete old lyrics dataframe
    os.remove(path)


if __name__ == '__main__':
    # Get path to lyrics df
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    args = parser.parse_args()
    path = args.path
    clean_artist_lyrics(path)