# Bard
A Dash app for generating song lyrics using generative deep learning.

### How to Run
1. `pip install -r requirements.txt`

2. `python bard.py`

### Generative Machine Learning

### Lyric Collection
1. Query Spotify API for artist discography
`artist_lyrics.py`
2. Download lyrics from Genius.com
`download_lyrics_script.py`
3. Lyric cleaning
`clean_lyrics.py`

### Putting It All Together With Dash
Dash is a reactive web framework for Python that makes it easy to build interactive data visualization apps. User input
from the Dash app is sent to the neural netwo 