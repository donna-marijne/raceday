import logging

logger = logging.getLogger("raceday")
logging.basicConfig(filename="raceday.log", level=logging.DEBUG)

debug = logger.debug
