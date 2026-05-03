# raceday

A terminal tool for replaying Formula 1 races!

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
    - [ ] Current tyre compound
    - [ ] Current tyre age
    - [ ] The track name and metadata
    - [x] Use the start grid to show initial correct order
    - [ ] Current track time
    - [ ] Current track weather/temp
    - [ ] Marshal flag indicator
    - [ ] Safety car indicator
- [ ] Hi res animation:
    - [ ] Increase the horizontal scale to 3 laps, scrolling with one sector ahead of the leader
    - [ ] Interpolate position based on sector time
    - [ ] Show a pit indicator for cars going through the pit lane
    - [ ] Ascii art cars!
- [ ] Even hi-er res animation: use the 3D locations data and the track shape to calculate car progress on each lap
- [ ] Interaction:
    - [x] Quit
    - [ ] Restart
    - [ ] Pause
    - [ ] Change warp factor
    - [ ] Focus a driver and see extra details
    - [ ] Keep app running after the race ends for user input
- [ ] Race browser

## Bugs to fix

- Cars that DNS can leave cars that started behind them in their start state
