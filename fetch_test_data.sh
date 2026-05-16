#!/bin/sh

meeting_key=$1
quali_session_key=$2
race_session_key=$3
payloads_dir="./tests/data/payloads"
base_url="https://api.openf1.org/v1"
request_throttle=0.5s

session_dir="$payloads_dir/$race_session_key"

function fetch_json() {
	local endpoint="$1"
	local query_key="$2"
	local query_value="$3"
	local file_name="${4:-$endpoint}"

	local file_path="${session_dir}/${file_name}.json"
	local url="${base_url}/${endpoint}?${query_key}=${query_value}"

	echo "$url -> $file_path"
	curl --silent -o $file_path $url

	sleep $request_throttle
}

mkdir -p $session_dir

fetch_json "drivers" "session_key" $race_session_key
fetch_json "laps" "session_key" $race_session_key
fetch_json "laps" "session_key" $quali_session_key "qualifying_laps"
fetch_json "meetings" "meeting_key" $meeting_key
fetch_json "sessions" "session_key" $race_session_key
fetch_json "starting_grid" "session_key" $quali_session_key
fetch_json "stints" "session_key" $race_session_key
