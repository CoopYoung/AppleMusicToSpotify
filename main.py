import requests, re, json
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from helpers import signal_last
from refresh import Refresh

'''
This application is currently working, for other
users all that needs to change is the playlist_id and playlist_id

'''

#user_id = "rhuc3nc19eajeki51go6z6syi" #CooYoung 
user_id = "31yd7rujo7sxgn6kyqarnfni6sey"
spotify_token = "BQCB0U9-Vha6PZgnHUbm0fsHoViMELH4Ggg58UkVAT9XyhrueLpmV8G31cnPWIGQtFQ3aikwVaPE8b07vvASQD_5CmchTksGJOF1sTWUGGVVjFiX18FNL7_OrcOByDq9nPC9ZQOxkkGewxLsPOI3R38oJYugC_khdkBbpFofV_eb5OQje2IvVZ4M0NteRTAmlmwiZ9gIMGRLV_n69xwX2C1OvKug6PvO0LGfE4EOsEmaaVFTUhLbEdu7e9BSrYVIiUZU"

class AppleToSpotify:
    def __init__(self):
        self.user_id = user_id
        self.spotify_token = ""
        self.playlist_id = "1EJ0s33KexYdDhRnNsXs1M?si=U1YP7aauQ26eoKUXpZ2JuA"
        self.tracks = ""
        
    def create_spotify_playlist(self, token, song_uris, songs):

        print("Trying to create a playlist...")
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user_id)


        #Change the name for other users !!!!!!!!


        request_body = json.dumps({
            "name": "Zia's playlist", "description": "solid/nice/yuh", "public": True
        })
        response = requests.post(query, 
                                data = request_body,
                                headers = {'Authorization': f'Bearer {token}'})
                                
        if(response.status_code == 201):
            print(f'\033[32m Playlist with length of {len(song_uris)} songs Updated!')
            print(f'\033[32m Original Playlist length: {len(songs)}')
            print(f'\033[32m Could not find uris for {len(songs) - len(song_uris)} songs')
            print('\n \n')
        else:
            print(f'\033[31m Could not add songs to playlist: {response.text}')

        print(f"\n\n\n\n Response: {response.json()['id']}   ")
        return response.json()["id"]

    def add_to_playlist(self, uris):

        #self.playlist_id = self.create_spotify_playlist(self.spotify_token, uris, songs)

        query = "https://api.spotify.com/v1/playlists/{}/tracks?uris={}".format(self.playlist_id, uris)
        
        #request_body = json.dumps({"name": "TestingAPI", "description": "Jadzia's songs", "public": True})

        
        response = requests.post(query,  headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.spotify_token)
        })

        response_json = response.json()
        print(response_json)

    def get_spotify_uris(self, songs, spotify_token):
        list = []
        file1 = open("alluri.txt", "w")
        file1.write("Big booty")
        for song in songs:
            # Make search request to Spotify
            try:
                r = requests.get(f'https://api.spotify.com/v1/search?q={song.search_str()}&type=track', 
                                headers={'Authorization': f'Bearer {spotify_token}'}) 
            except:
                print(f'\033[31m Error while searching for song: {song.search_str()}')

            data = r.json()
            print(data)
            if(r.status_code != 200 and r.status_code != 201 and r.status_code != 404):
                print(f'\033[31m Error while searching for song: {song.search_str()}')
            #print(data)
            if len(data['tracks']['items']) == 0:
                print(f'\033[33m ######## Could not find uri for {song.search_str()}')
                continue

            # Loop through the results and get the uri of the first match
            for is_last, item in signal_last(r.json()['tracks']['items']):

                # Normalize the Titles 
                spotify_name = normalize_string(item['name'])
                apple_name = normalize_string(song.title)

                # Compare the songs
                len_diff = song.length_in_ms() - item['duration_ms'] # difference in length
                title_diff = SequenceMatcher(None, spotify_name, apple_name).ratio() # difference in title
                same_title = apple_name in spotify_name or spotify_name in apple_name

                if len_diff < 1500 and len_diff > -1500 and (same_title or title_diff > 0.8):
                    list.append(item['uri'])
                    file1.write(item['uri'] + "\n")
                    break
                else:
                    print(f'\033[34m {len_diff}:{title_diff} \033[0m {apple_name} vs. {spotify_name}')

                    if(is_last):
                        print(f'\033[33m ######## Could not find uri for {song.search_str()}')
                    continue
        file1.close()
        return list

    def call_refresh(self):

        print("Refreshing token")

        refreshCaller = Refresh()

        self.spotify_token = refreshCaller.refresh()

        

class AppleSong:
    def __init__(self, title, artists, length):
        self.title = title.strip()
        self.artists = artists
        self.length = length.strip()

    def length_in_ms(self):
        string = self.length
        return int(string.split(':')[0]) * 60 * 1000 + int(string.split(':')[1]) * 1000

    def search_str(self):
        artists = " ".join(self.artists).strip()
        title = self.title.strip()

        return f'{title} {artists}'

def get_songs_from_apple_playlist(url: str):
    r =  requests.get(url)
    
    # Check if the request was successful
    if r.status_code == 200:
        print(f'\033[32m Found playlist!')
    else:
        print(f'\033[31m there was an error while getting playlist: {r.text}')
        pass
    
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # get table with songs
    divs = soup.find_all('div', {'class': 'songs-list-row songs-list-row--web-preview web-preview songs-list-row--two-lines songs-list-row--song'})
    
    # Create a list of songs
    songs = []
    for div in divs:
        title = re.sub("[\(\[].*?[\)\]]", "", div.find('div', {'class': 'songs-list-row__song-name'}).text)
        artists = [artist.text for artist in div.find('div', {'class': 'songs-list__col songs-list__col--artist typography-body'}).find_all('a', {'class': 'songs-list-row__link'})]
        length = div.find('time', {'class': 'songs-list-row__length'}).text.strip()
        
        songs.append(AppleSong(title, artists, length))
    
    return songs
def normalize_string(string: str) -> str:
    string = string.lower()
    string = re.sub('[^a-z0-9 ]', '', string)
    string = re.sub("[\(\[].*?[\)\]]", "", string)

    return string


if __name__ == "__main__":
    
    appleURL = ['https://music.apple.com/us/playlist/pl.u-zPyLm05uZr23x4r', 'https://music.apple.com/us/playlist/like/pl.u-55D66Z7F8d2vV1d',
                'https://music.apple.com/us/playlist/in-question/pl.u-yZyVEAmuYym8q6y','https://music.apple.com/us/playlist/untitled-playlist/pl.u-pMyl1Kmu41kmKy1',
                'https://music.apple.com/us/playlist/vry-random/pl.u-r2yB14xCPv0Bjav', 'https://music.apple.com/us/playlist/pl.u-EdAVz8YIa8e4MN8',
                'https://music.apple.com/us/playlist/green-lights/pl.u-qxylK75t2vxEGJv','https://music.apple.com/us/playlist/mine/pl.u-4Jommamsax18myx']


    
    app = AppleToSpotify()
    #listSongs = AppleSong()
    app.call_refresh()


    '''
    Current workflow: 
    1. Get the songs from apple
    2. Refresh token 
    3. Get the uris from spotify
    4. Create playlist
    5. Add the uris to the playlist

    '''
    for apple in appleURL:
        app = AppleToSpotify()

        songs = get_songs_from_apple_playlist(apple)

        app.tracks = app.get_spotify_uris(songs, spotify_token)

        app.playlist_id = app.create_spotify_playlist(spotify_token, app.tracks, songs)

        for u in app.tracks:
            app.add_to_playlist(u)

    #print(app.tracks)
    #for i, num in enumerate(app.tracks):
    #    app.tracks[i] = num[14:]
    #    print(app.tracks[i])

    #app.add_to_playlist(app.tracks)

   # print(app.tracks)

    #app.add_to_playlist()
    
    #app.create_spotify_playlist(app.spotify_token, u, songs)

