from flask import Flask 
from flask import current_app
from flask import request
from flask import jsonify
import requests
import logging
import redis
import time
import json
import re

def create_app():
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_pyfile("config.py")
	return app

app = create_app()
api_redis = redis.Redis(host='localhost', port=6379, db=0)

"""
===============================
Response Tools
===============================
"""

def make_error(error, response_code=500):
	return _make_response(response=error, response_code=response_code)

def make_success(response, response_code=200):
	return _make_response(response=response, response_code=response_code)

def make_song_success(album_img_url, track_name, username, postback=True):
	description = "_{track}_ queued up by *{username}*".format(track=track_name, username=username)
	response = {
			"response_type": "ephemeral",
			"attachments": [{
				"pretext": "New Song Queued!", 
				"text": description, 
				"fallback": "Album Art", 
				"thumb_url": album_img_url, 
				"mrkdwn_in": ["pretext", "text"]}]}

	post_to_slack(response)
	return make_success(response={"text": "_Your song has been queued!_"})

def _make_response(response=None, response_code=200):
	response = jsonify(response)
	response.status_code = response_code
	return response

"""
===============================
Redis Tools
===============================
"""

def push_song(user_id, song):
	song_name = song["name"]
	album_name = song["album"]["name"]
	song_uri = song["uri"]
	length = (song["duration_ms"] / 1000) + 2

	unique_id = api_redis.incr("uid")
	hash_name = "{uid}:{user_id}".format(uid=unique_id, user_id=user_id)
	api_redis.hmset(hash_name, {
		"play_id": hash_name,
		"song_name": song_name,
		"album_name": album_name,
		"song_uri": song_uri,
		"length": length
	})

	api_redis.lpush("song_queue", hash_name)

"""
===============================
Messaging Tools
===============================
"""

def post_to_slack(message):
	requests.post(current_app.config["INCOMING_WEBHOOK"], {"payload": json.dumps(message)})

"""
===============================
Response Tools
===============================
"""

def handle_play(data):
	text_data = data["text"].split()
	spotify_data = None

	if len(text_data) == 1:
		# So if there's only one item in the array, we
		# need to check if the one item is a Spotify URI
		match = re.match(r"(.+:)(?P<spotify>.+)", text_data[0])
		if match:
			# XXXXXXXXX
			spotify_data = requests.get("https://api.spotify.com/v1/tracks/{id}".format(id=match.group("spotify"))).json()
			album_img_url = spotify_data["album"]["images"][1]["url"]
			track_name = spotify_data["album"]["name"]

			# Push song to redis
			push_song(data["user_id"], spotify_data)

			return make_song_success(album_img_url, track_name, data["user_name"])

	# Otherwise we're going to do a search for the song		
	search = "+".join(text_data)

	if search == "":
		return make_error(error={"text": "You need to enter a search query to queue a song."})

	params = {"q": search, "type": "track", "limit": 1, "market": "US"}
	# XXXXXXXXX
	spotify_data = requests.get("https://api.spotify.com/v1/search", params=params).json()["tracks"]["items"][0]

	album_img_url = spotify_data["album"]["images"][1]["url"]
	track_name = spotify_data["name"]

	# Push song to redis
	push_song(data["user_id"], spotify_data)

	return make_song_success(album_img_url, track_name, data["user_name"])

def handle_stop(data):
	return make_success(response="Alright alright alright...")

def handle_skip(data):
	return make_success(response="Alright alright alright...")

"""
===============================
Endpoints
===============================
"""

@app.route("/", methods=["GET", "POST"])
def index():
	return make_error(error={"text": "Forbidden"}, response_code=403)

@app.route("/slacktable/user/current_song", methods=["GET", "POST"])
def user_current_song():
	head_song = api_redis.lrange("song_queue", -1, 1)
	if len(head_song) == 0:
		return make_success({"message": "No songs"}, response_code=204)
	curr_data = api_redis.hgetall(head_song[0])

	print curr_data
	if "start" not in curr_data:
		print "Setting start"
		api_redis.hset(head_song[0], "start", int(time.time()))
	else:
		# Kill it with fire
		print str(int(time.time())) + " " + str(int(curr_data["start"]) + int(curr_data["length"]))
		if int(time.time()) > int(curr_data["start"]) + int(curr_data["length"]):
			print "Killing the current song"
			api_redis.rpop("song_queue")
			return make_success({"message": "Try again"}, response_code=204)
		else:
			print "Continuing song"
			return make_success({"message": "No update yet"}, response_code=204)

	return make_success(curr_data)

@app.route("/slacktable/playsong", methods=["GET", "POST"])
def play_song():
	# Check our fail cases
	if "token" not in request.values:
		return make_error(error="Forbidden", response_code=403)
	else:
		token = request.values["token"]
		if token != current_app.config["SLASH_TOKEN"]:
			return make_error(error="Forbidden, this request will be logged.", response_code=403)

	return handle_play(request.values)

@app.route("/slacktable/command", methods=["GET", "POST"])
def command():
	# Check our fail cases
	if "token" not in request.values:
		return make_error(error="Forbidden", response_code=403)
	else:
		token = request.values["token"]
		if token != current_app.config["OUTGOING_TOKEN"]:
			print "This shit is broken"
			return make_error(error="Forbidden, this request will be logged.", response_code=403)

	trigger = ""

	if "trigger_word" in request.values:
		trigger = request.values["trigger_word"]

	if trigger == "play":
		return handle_play(request.values)
	elif trigger == "stop":
		return handle_stop(request.values)
	elif trigger == "skip":
		return handle_skip(request.values)

	return make_success(response="Forbidden", response_code=403)

def main():
	app.run(host=app.config["HOST"])

if __name__=="__main__":
	main()