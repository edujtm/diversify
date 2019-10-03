# Diversify

## The Project

Diversify is a playlist generator based on the [Spofity WEB API](https://developer.spotify.com/web-api/) and the [Spotipy module](http://spotipy.readthedocs.io/en/latest/)
that aims to use concepts of AI to suggest playlists based on musical preferences between multiple people.

This project was heavily inspired by this [article](https://dev.to/ericbonfadini/finding-my-new-favorite-song-on-spotify-4lgc) by 
[@ericbonfadini](https://twitter.com/ericbonfadini) and it's basically just an extra functionality in his analysis.

## Goals

The goal is to use AI algorithms to generate a spotify playlist based on a user's preference and
a friend of his choice. Currently the script will use a genetic algorthm to generate the playlists
but this may improve in the future.

## How to run

- First you need to get your spotify API key and save it to the .env file. 
	- Go to [spotify application web page](https://developer.spotify.com/dashboard/),
	- login with your spotify account and create a new app
	- put whatever name you'd like on the project info and say no to commercial integration
	- get your client ID and client secret (by clicking *show client secret*)
	- put them on your .env.example file and rename it to .env 
	- click on edit settings and whitelist http://localhost/

These steps are annoying but are needed because I didn't deploy this app somewhere yet, I have plans to deploy it once I make it faster.

- Clone this repo: `git clone https://github.com/edujtm/diversify.git`

- Create a new environment with your package manager or install the dependencies in environment.yml with pip. <br/>
	Personally I use anaconda, so it's just a matter of running `conda env create --file=environmnent.yml` and then `conda activate diversify`

- With the previous step done, you can import the interfacespfy module in an interactive prompt

```Python
from interfacespfy import SpotifySession
spfy = SpotifySession("username")

playlists = spfy.get_user_playlists("other_username")
saved_songs = spfy.get_favorite_songs()
```

- You can generate playlists by running `python3 diversify.py`. (run python3 diversify.py --help for more info) <br/>
    Example: `python3 diversify.py your_id -u2 your_friend_id -p my awesome playlist`

## Warnings
	
The files in the tf/ folder and splearn.py are not used, I was trying to implement the algorithm using neural networks or clustering but i didn't finish. I'll probably remove them in the future.

I didn't run much tests when making this app, so there might be errors that I didn't check for when getting data from the spofity API. You can expect some errors when running the scripts.
