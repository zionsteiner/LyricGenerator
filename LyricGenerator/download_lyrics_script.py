from LyricGenerator.artist_lyrics import download_artist_lyrics
from LyricGenerator.clean_lyrics import clean_artist_lyrics

artists = ['katy perry', 'warren zevon', 'taylor swift', 'u2', 'the killers', 'gorillaz', 'smash mouth', 'selena gomez', 'justin bieber']
for artist in artists:
    try:
        path = download_artist_lyrics(artist)
        clean_artist_lyrics(path)
    except Exception as e:
        print(f'Error occurred while collecting lyrics for artist "{artist}"')
        print(e)

