# raceday

A terminal tool for replaying Formula 1 races!

## Implementation plan

- [ ] Data analysis:
    - [x] Load lap times from JSON provided at the command line (acquired from openf1.org)
    - [x] List the sector completion events in order of occurrence in the race, e.g. "Car 44 completes lap 5 sector 2 at ..."
    - [ ] Loop the sector completion events and sleep the proper time between printing them (using 60x time compression)
    - [x] Add the calculated car position at each event
- [ ] Animation (curses):
    - [ ] Render a horizontal view with one line per car and (initially) one column per sector (up to 240 columns)
    - [ ] At each sector completion event, move the car to the next column
    - [ ] Order the cars by active race position
- [ ] Richer data:
    - [ ] Show driver name/acronym and team color code (openf1)
    - [ ] Show current tyre compound
    - [ ] Show the track name and metadata
    - [ ] Use the start grid to show initial correct order
- [ ] Hi res animation:
    - [ ] Increase the horizontal scale to 3 laps, scrolling with one sector ahead of the leader
    - [ ] Pivot to fixed FPS to support intermediate columns based on sector time? Bucketing? Use the interval data?
    - [ ] Ascii art cars!
