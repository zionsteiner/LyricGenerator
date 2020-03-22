import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import keras

import tensorflow as tf

import pickle
import numpy as np
import os

# Generate lists of options {genre: [artists]}
genres = [genre_subdir for genre_subdir in os.listdir('genres') if os.path.isdir(os.path.join('genres', genre_subdir))]
genre_artist_options = {genre: sorted([artist for artist in os.listdir(os.path.join('genres', genre)) if os.path.isdir(os.path.join(
    'genres', genre, artist))]) for genre in genres}

# Stylesheet from chriddyp
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(children=[
    html.H1(children='Song Lyric Generator', style={'textAlign': 'center'}),
    html.Div(children=[
        html.Div(id='options_div', children=[
            html.Div(id='artist_options_div', children=[
                html.Label('Choose a genre'),
                dcc.Dropdown(id='genre_dropdown',
                             options=[{'label': genre.title(), 'value': genre} for genre in genre_artist_options.keys()],
                             value='rap'),
                html.Label('Choose an artist'),
                dcc.Dropdown(id='artist_dropdown')
            ]),
            html.Div(id='generator_options_div', children=[
                html.Label('Characters to generate'),
                dcc.Input(id='n_chars_input', type='number', min=1, step=1, max=1000, value=400),
                html.Label('Randomness'),
                dcc.Input(id='temp_input', type='number', min=0.1, step=0.01, max=5.0, value=0.5)
            ], style={'columnCount': 2})
        ]),
        html.Label('Lyric generator'),
        dcc.Textarea(id='seed_input',
                     placeholder='Enter some lyrics to give the generator some ideas!',
                     style={'margin': '10 px auto',
                            'padding': '10px'}),
        html.Button(id='submit_text', n_clicks=0, children='Submit')
    ]),
    html.Div(children=[
        html.Div(id='hidden_div', style={'display': 'none'}),
        html.P(id='generated_output'),
        html.P(id='err', style={'color': 'red'})
    ])
], style={'width': '50vw',
          'margin': 'auto'})


@app.callback(
    Output('artist_dropdown', 'options'),
    [Input('genre_dropdown', 'value')])
def set_artist_options(selected_genre):
    return [{'label': artist.replace('_', ' ').title(), 'value': artist} for artist in genre_artist_options[selected_genre]]


@app.callback(
    Output('artist_dropdown', 'value'),
    [Input('artist_dropdown', 'options')])
def set_artist_value(options):
    return options[0]['value']


@app.callback(
    Output('hidden_div', 'children'),
    [Input('artist_dropdown', 'value')],
    [State('genre_dropdown', 'value')])
def load_model(artist, genre):
    global graph
    graph = tf.get_default_graph()

    artist_dir = os.path.join('genres', genre, artist)

    global model
    model_path = os.path.join(artist_dir, 'model.h5')
    model = keras.models.load_model(model_path)

    global chars
    chars_path = os.path.join(artist_dir, 'chars.pkl')
    with open(chars_path, 'rb') as f:
        chars = pickle.load(f)

    global char_indices
    char_indices_path = os.path.join(artist_dir, 'char_indices.pkl')
    with open(char_indices_path, 'rb') as f:
        char_indices = pickle.load(f)


@app.callback(
    [Output('generated_output', 'children'), Output('err', 'children')],
    [Input('submit_text', 'n_clicks')],
    [State('seed_input', 'value'),
     State('n_chars_input', 'value'),
     State('temp_input', 'value')])
def generate_lyrics(n_clicks, seed_text, n_chars, temp):
    if n_clicks == 0:
        raise dash.exceptions.PreventUpdate
    if seed_text is None or len(seed_text.strip()) < 60:
        return dash.no_update, 'Enter at least 60 characters to continue'
    maxlen = 60
    generated_text = seed_text
    seed_text = seed_text.lower()
    seed_text = ''.join(filter(lambda char: char if char in set(chars) else '', seed_text))
    seed_text = seed_text[-maxlen:]
    for i in range(n_chars):
        sampled = np.zeros((1, maxlen, len(chars)))
        for t, char in enumerate(seed_text):
            sampled[0, t, char_indices[char]] = 1

        with graph.as_default():
            preds = model.predict(sampled, verbose=0)[0]
        next_index = sample(preds, temperature=temp)
        next_char = chars[next_index]

        seed_text += next_char
        seed_text = seed_text[1:]

        generated_text += next_char

    return generated_text, ''


def sample(preds, temperature=1.0):
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)

    return np.argmax(probas)


if __name__ == '__main__':
    app.run_server(debug=False, port=8000, threaded=False)
