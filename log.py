import logging

logger = logging.getLogger("raceday")
logging.basicConfig(filename="raceday.log", filemode="w", level=logging.DEBUG)

debug = logger.debug
