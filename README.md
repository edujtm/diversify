# Diversify

## The Project

Diversify is a playlist generator based on the [Spofity WEB API](https://developer.spotify.com/web-api/) and the [Spotipy module](http://spotipy.readthedocs.io/en/latest/)
that aims to use concepts of AI to suggest playlists based on musical preferences between multiple people.

## Goals

The goal is to use AI algorithms to generate a spotify playlist based on a user's preference and
a friend of his choice. Currently the script will use a genetic algorthm to generate the playlists
but this may improve in the future.

## How to install

- First you need to get your spotify API key and save it to the .env file. 
	- Go to [spotify application web page](https://developer.spotify.com/dashboard/),
	- login with your spotify account and create a new app
	- put whatever name you'd like on the project info and say no to commercial integration
	- click on edit settings and whitelist https://edujtm.github.io/diversify/redirect
	- get your client ID and client secret (by clicking *show client secret*)
	- put them on a [config.ini](config.ini.example) file and move it to  `$HOME/.config/diversify/`
	- run `pip install diversify` 
	- run `diversify --help` to see if everything went ok.

## How to run

```
$ diversify login
$ diversify playlist PLAYLIST NAME
```

## How to contribute

- This project uses [poetry](https://python-poetry.org/) for dependency management
- Clone this repo: `git clone https://github.com/edujtm/diversify.git`
- `cd diversify` and `poetry install`
- Then run `poetry shell`

