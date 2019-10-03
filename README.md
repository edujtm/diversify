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

- Create a new environment with your package manager or install the dependencies in environment.yml with pip. <br/>
	Personally I use anaconda, so it's just a matter of running `conda env create --file=environmnent.yml` and then `conda activate diversify`

- With the previous step done, you can import the interfacespfy module in an interactive prompt

```Python
	import interfacespfy as isp
	spfy = isp.login_user("username")

	playlists = isp.get_user_playlists(spfy, "other_username")
	saved_songs = isp.get_favorite_songs(spfy)

```

- You can generate playlists by running `python3 diversify.py`. (run python3 diversify.py --help for more info) <br/>
    Example: `python3 diversify.py your_id -u2 your_friend_id -p my awesome playlist`