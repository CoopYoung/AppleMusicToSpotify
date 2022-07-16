import requests
import json

refresh_token = "AQDzVAFX8NwtWxKSbwyzsR1IbYtoQ2zFUJmBqTRgmtHxLV5bJggzHRNfzJuXDHWLFdlH6b3wpJs1QwmKQEGDZ4sZwOikSLkp7s0e244aj3TjphCsHlRTUg1pc6afSYUVtJo"
base_64 = "MDliZGQ2MzJhMDA1NGYzNWJmY2M3MjYwZmVjZTdlOTc6NTE2YzE5NDRiNjJjNGJiNmIwOGI0NDdiZjdkNTg5ZGQ="

class Refresh:

    def __init__(self):
        self.refresh_token = refresh_token
        self.base_64 = base_64

    def refresh(self):

        query = "https://accounts.spotify.com/api/token"

        response = requests.post(query, 
                            data={"grant_type": "refresh_token",
                            "refresh_token": refresh_token},
                            headers = {"Authorization": "Basic " + base_64})

        return response.json()["access_token"]

r = Refresh()

print(r.refresh())