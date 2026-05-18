# raceday

A terminal tool for replaying Formula 1 races!

## Quick start

Requirements:
- Python with the `curses` module
- `uv`

API access is not yet implemented, but the program can be run with a local dataset. The repo includes several race session datasets in `tests/data/payloads`.

Run the replay of the 2026 Chinese Grand Prix with default settings:

```bash
uv run main.py -d tests/data/payloads/11245
```

Run the replay of the 2026 Chinese Sprint with a 100x time warp factor at 60 frames per second:

```bash
uv run main.py -d tests/data/payloads/11240 -w 100 -f 60
```

## Getting more data

While the program runs in offline mode, additional datasets can be downloaded using the `fetch_test_data.sh` shell script:

```bash
./fetch_test_data.sh <meeting_key> <quali_session_key> <race_session_key>
```

Use an OpenF1 query to find the `meeting_key` and `session_key`s for both qualifying and race, e.g.:

https://api.openf1.org/v1/sessions?country_name=Belgium&year=2023

Sprint races are supported, use the `session_name` field to distinguish sprint sessions from the grand prix.

## Implementation plan

- [x] Data analysis:
    - [x] Load lap times from JSON provided at the command line (acquired from openf1.org)
    - [x] List the sector completion events in order of occurrence in the race, e.g. "Car 44 completes lap 5 sector 2 at ..."
    - [x] Loop the sector completion events and sleep the proper time between printing them (using 60x time compression)
    - [x] Add the calculated car position at each event
- [x] Animation (curses):
    - [x] Render a horizontal view with one line per car and (initially) one column per sector (up to 240 columns)
    - [x] At each sector completion event, move the car to the next column
    - [x] Order the cars by active race position
- [ ] Richer data:
    - [x] Show driver name/acronym and team color code (openf1)
    - [x] Current tyre compound
    - [x] Current tyre age
    - [x] The track name and metadata
    - [x] Use the start grid to show initial correct order
    - [ ] Show arrows for position changes
    - [x] Current track time
    - [ ] Current track weather/temp
    - [ ] Marshal flag indicator
    - [ ] Safety car indicator
- [ ] Hi res animation:
    - [x] Increase the horizontal scale to 3 laps, scrolling with one sector ahead of the leader
    - [x] Interpolate position based on sector time
    - [x] Scale sector length to relative duration (use fastest lap sector times from quali)
    - [x] Reorder cars within a sector (can sort by lap/sector/progress now)
    - [ ] Show a pit indicator for cars going through the pit lane
    - [x] Ascii art cars!
      - ⊵o≗o⌳
- [ ] Even hi-er res animation: use the 3D locations data and the track shape to calculate car progress on each lap
- [ ] Interaction:
    - [x] Quit
    - [ ] Restart
    - [ ] Pause
    - [ ] Change warp factor
    - [ ] Focus a driver and see extra details
    - [x] Keep app running after the race ends for user input
- [ ] Race browser

## Bugs to fix

None so far!
