#!/bin/sh

for dir in tests/data/payloads/*; do
	meeting_key=$(jq ".[0].meeting_key" $dir/sessions.json)
	quali_key=$(jq ".[0].session_key" $dir/starting_grid.json)
	race_key=$(basename $dir)
	./fetch_test_data.sh $meeting_key $quali_key $key
done
