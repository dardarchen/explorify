import streamlit as st
from apis.authorization_api import *
from apis.spotify_api import *
from apis.display_api import *

st.set_page_config(layout="wide")

displayapi = DisplayAPI()
authapi = AuthorizationAPI()

# Authorization
auth_url = authapi.get_authorization_url()
displayapi.display_auth_url(auth_url)
access_token = authapi.authorize()

# Display username
spotapi = SpotifyAPI(access_token)
username, profile_image = spotapi.get_username_and_profile_image()
displayapi.display_username(username)

# Display profile image
if profile_image:
    displayapi.display_profile_image(profile_image)

# Display top artists and songs
num_artists = 10
num_songs = 20
for time_period, time_length in [("short_term", "from the past month"), ("medium_term", "from the last 6 months"), ("long_term", "of all time")]:
    artists_data = spotapi.get_top_artists(num_artists, time_period)
    songs_data = spotapi.get_top_songs(num_songs, time_period)
    st.header(f"Your top artists {time_length}:")
    displayapi.display_artists(artists_data)
    st.header(f"Your top songs {time_length}:")
    displayapi.display_top_songs(songs_data)

# Display recommended artists and songs
recommended_artists, recommended_songs = spotapi.get_recommended_songs_and_artists()
st.header("Based on your listening history, here's a list of recommended artists:")
displayapi.display_artists(recommended_artists)

st.header("And here's a list of recommended songs:")
displayapi.display_recommended_songs(recommended_songs)







