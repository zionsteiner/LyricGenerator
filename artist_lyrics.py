import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from bs4 import BeautifulSoup
import os
import argparse
import pandas as pd
from collections import defaultdict
import re


def get_albums(artist_name, spotipy):
    search_results = spotipy.search(q='artist:' + artist_name, type='artist')
    artist_results = search_results['artists']['items']
    filtered_artist_results = list(filter(lambda result: result['name'].lower() == artist_name.lower(), artist_results))

    if len(filtered_artist_results) == 0:
        raise Exception(f'No results for "{artist_name}" found on Spotify')

    artist = filtered_artist_results[0]
    album_results = spotipy.artist_albums(artist['uri'], album_type='album')
    albums = album_results['items']
    while album_results['next']:
        album_results = spotipy.next(album_results)
        albums.extend(album_results['items'])

    return albums


def download_lyrics(track, artist):
    genius_key = os.environ['GENIUS_KEY']
    genius_base = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + genius_key}
    search_url = genius_base + '/search'
    query = {'q': track + ' ' + artist}
    response = requests.get(search_url, data=query, headers=headers)
    json = response.json()

    track_record = None
    for hit in json['response']['hits']:
        if artist.lower() in hit['result']['primary_artist']['name'].lower():
            track_record = hit
            break

    if track_record:
        track_url = track_record['result']['url']
    else:
        raise Exception(f'{track} by {artist} not found on Genius')

    response = requests.get(track_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    lyrics = soup.find('div', class_='lyrics').get_text()

    return lyrics


def download_artist_lyrics(artist):
    # Get  credentials
    client_id = os.environ['SPOTIFY_CLIENT_ID']
    client_secret = os.environ['SPOTIFY_CLIENT_SECRET']

    # Setup spotipy
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Get artist albums
    albums = get_albums(artist, sp)
    album_names = list(map(lambda album: album['name'], albums))
    album_uris = list(map(lambda album: album['uri'], albums))
    zipped = zip(album_names, album_uris)
    albums_uri_dict = dict(zipped)

    # Get album track names
    album_tracks_dict = defaultdict(list)
    for album, uri in albums_uri_dict.items():
        #filters = ['live', 'remaster', 'remastered']
        #conditions = list(map(lambda term: False if term in album.lower() else True, filters))
        #if all(conditions):
        if True:
            track_results = sp.album_tracks(uri)
            album_tracks_dict[album].extend(track_results['items'])
            while track_results['next']:
                track_results = sp.next(track_results)
                album_tracks_dict[album].extend(track_results['items'])

    for album, tracks in album_tracks_dict.items():
        album_tracks_dict[album] = list(map(lambda track: re.sub(r'(remaster(ed)?)|(\b(19|20)\d{2}\b)?', '', track['name'], flags=re.IGNORECASE), tracks))

    # Download lyrics from genius and store to dataframe
    lyric_df = pd.DataFrame(columns=['artist', 'album', 'song', 'lyrics'])
    for album in album_tracks_dict.keys():
        for track in album_tracks_dict[album]:
            # filters = ['skit', 'live', 'remaster', 'remastered']
            # conditions = list(map(lambda term: False if term in track.lower() else True, filters))
            # if all(conditions):
            if True:
                try:
                    lyrics = download_lyrics(track, artist)
                    print(f'Lyrics for {track} successfully downloaded')
                    lyric_df = lyric_df.append({'artist': artist,
                                                'album': album,
                                                'song': track,
                                                'lyrics': lyrics},
                                               ignore_index=True)
                except Exception as e:
                    lyrics = None
                    print(e)

    path = f'lyrics/{artist.replace(" ", "_")}.pkl'
    lyric_df.to_pickle(path)
    return path


if __name__ == '__main__':
    # Get artist
    parser = argparse.ArgumentParser()
    parser.add_argument('artist', nargs='+')
    args = parser.parse_args()
    artist = ' '.join(args.artist)

    download_artist_lyrics(artist)
