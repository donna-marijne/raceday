#!/bin/sh

meeting_key=$1
quali_session_key=$2
race_session_key=$3
payloads_dir="./tests/data/payloads"
base_url="https://api.openf1.org/v1"

session_dir="$payloads_dir/$race_session_key"

mkdir -p $session_dir

drivers_path="$session_dir/drivers.json"
curl -o $drivers_path "$base_url/drivers?session_key=$race_session_key"

laps_path="$session_dir/laps.json"
curl -o $laps_path "$base_url/laps?session_key=$race_session_key"

meetings_path="$session_dir/meetings.json"
curl -o $meetings_path "$base_url/meetings?meeting_key=$meeting_key"

sessions_path="$session_dir/sessions.json"
curl -o $sessions_path "$base_url/sessions?session_key=$race_session_key"

starting_grid_path="$session_dir/starting_grid.json"
curl -o $starting_grid_path "$base_url/starting_grid?session_key=$quali_session_key"
