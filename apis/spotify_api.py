import spotipy
import requests
from collections import deque
from random import sample
from datetime import date

class SpotifyAPI(object):
    
    def __init__(self, access_token):
        self.sp = spotipy.Spotify(auth=access_token)
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
        
    def get_username_and_profile_image(self):
        endpoint = "https://api.spotify.com/v1/me"
        r = requests.get(endpoint, headers=self.headers)
        data = r.json()
        username = data['display_name']
        profile_image = None
        if len(data['images']) != 0:
            profile_image = data['images'][-1]['url']
        return username, profile_image

    def get_artist_data(self, entry):
        name = entry['name']
        url = entry['external_urls']['spotify']
        popularity = entry['popularity']
        image = entry['images'][0]['url']
        id = entry['id']
        return (name, url, popularity, image, id)
    
    def get_song_data(self, entry):
        name = entry['name']
        artists = ', '.join([x['name'] for x in entry['artists']])
        url = entry['preview_url']
        popularity = entry['popularity']
        image = entry['album']['images'][0]['url']
        id = entry['id']
        return (name, artists, url, popularity, image, id)
    
    # number: 1 - 50 
    # time_range: long_term, medium_term, short_term
    def get_top_artists(self, number, timeframe):
        endpoint = f"https://api.spotify.com/v1/me/top/artists?time_range={timeframe}&limit={number}"
        r = requests.get(endpoint, headers=self.headers)
        data = r.json()
        results = [self.get_artist_data(entry) for entry in data['items']] 
        return results
    
    def get_top_songs(self, number, timeframe):
        endpoint = f"https://api.spotify.com/v1/me/top/tracks?time_range={timeframe}&limit={number}"
        r = requests.get(endpoint, headers=self.headers)
        data = r.json()
        results = [self.get_song_data(entry) for entry in data['items']]
        return results
    
    def get_top_song_ids(self):
        result = []
        for time_period in ["short_term", "medium_term", "long_term"]:
            data = self.get_top_songs(20, time_period)
            result += [x[-1] for x in data]
        return list(set(result))
    
    def get_top_artist_ids(self):
        result = []
        for time_period in ["short_term", "medium_term", "long_term"]:
            data = self.get_top_artists(10, time_period)
            result += [x[-1] for x in data]
        return list(set(result))
    
    def get_related_artists(self, id):
        endpoint = f"https://api.spotify.com/v1/artists/{id}/related-artists"
        r = requests.get(endpoint, headers=self.headers)
        data = r.json()
        result = [artist["id"] for artist in data["artists"]]
        return result
    
    # Recommends artists n degrees of relatedness away 
    def get_recommended_artists_ids(self, n):
        top_artist_ids = self.get_top_artist_ids()
        discovered = set(top_artist_ids)
        queue = deque(top_artist_ids)
        level = 0
        while level < n:
            num = len(queue)
            for _ in range(num):
                curr = queue.popleft()
                neighbors = self.get_related_artists(curr)
                for id in neighbors:
                    if not id in discovered:
                        discovered.add(id)
                        queue.append(id)
            level += 1
        results = list(set(list(queue)))
        return sample(results, min(len(results), 10))
    
    def get_recommended_artists(self, recommended_artists_ids):
        results = []
        for id in recommended_artists_ids:
            endpoint = f"https://api.spotify.com/v1/artists/{id}"
            r = requests.get(endpoint, headers=self.headers)
            artist = r.json()
            results.append(self.get_artist_data(artist))
        return results
    
    # Use 2 seed artists, 3 seed songs
    def get_recommended_songs_ids(self, recommended_artists_ids, top_song_ids):
        seed_artists = ','.join(sample(recommended_artists_ids, 2))
        seed_songs = ','.join(sample(top_song_ids, 3))
        endpoint = f"https://api.spotify.com/v1/recommendations?seed_artists={seed_artists}&seed_tracks={seed_songs}"
        r = requests.get(endpoint, headers=self.headers)
        data = r.json()
        results = [entry["id"] for entry in data["tracks"]]
        return results

    def get_recommended_songs(self, recommended_songs_ids):
        results = []
        for id in recommended_songs_ids:
            endpoint = f"https://api.spotify.com/v1/tracks/{id}"
            r = requests.get(endpoint, headers=self.headers)
            song = r.json()
            results.append(self.get_song_data(song))
        return results

    def get_recommended_songs_and_artists(self):
        recommended_artists_ids = self.get_recommended_artists_ids(1)
        top_song_ids = self.get_top_song_ids()
        recommended_songs_ids = self.get_recommended_songs_ids(recommended_artists_ids, top_song_ids)
        recommended_artists = self.get_recommended_artists(recommended_artists_ids)
        recommended_songs = self.get_recommended_songs(recommended_songs_ids)
        return recommended_artists, recommended_songs
    
