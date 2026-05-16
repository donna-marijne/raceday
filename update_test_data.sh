#!/bin/sh

for dir in tests/data/payloads/*; do
	echo "Update: $dir"
	meeting_key=$(jq ".[0].meeting_key" $dir/sessions.json)
	quali_key=$(jq ".[0].session_key" $dir/starting_grid.json)
	race_key=$(basename $dir)
	echo "meeting_key=$meeting_key quali_key=$quali_key race_key=$race_key"
	./fetch_test_data.sh $meeting_key $quali_key $race_key
done
