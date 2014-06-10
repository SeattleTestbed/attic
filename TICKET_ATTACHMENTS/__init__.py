"""
<Program Name>
  geni/__init__.py

<Started>
  May 21, 2009

<Author>
  ivan@cs.washington.edu
  Ivan Beschastnikh

<Purpose>
  Sets up the default logger for the entire geni codebase.

  This file requires two variables to be defined inside of django's
  settings file:
  
  LOG_VIA_MODPYTHON : boolean, controls whether to log to
  /var/log/apache2/error.log (or similar), or to a file

  LOGGING_FILEPATH : used if LOG_VIA_MODPYTHON = False, and specifies
  the full path of the logfile to use for logging messages
"""

import logging
from django.conf import settings


if settings.LOG_VIA_MODPYTHON:
    # log to apache's error log
    from geni.modpython_logging import ApacheLogHandler
    handler = ApacheLogHandler()
else:
    # log to a file
    import logging.handlers
    # create a 100 MB X 3 files, file logger
    handler = logging.handlers.RotatingFileHandler(settings.LOGGING_FILEPATH, maxBytes=104857600, backupCount=3)

    
# this controls which level msgs are handled by the handler
handler.setLevel(logging.DEBUG)

# set the logging format and associate with our handler
formatter = logging.Formatter("%(asctime)s   %(levelname)-8s %(name)-40s %(filename)s:%(lineno)d:%(funcName)-20s %(message)s", datefmt="%m-%d-%y %H:%M:%S")
handler.setFormatter(formatter)

# grab the top level logger which will be used by all loggers in the project
toplevel_logger = logging.getLogger('')

# this controls which level msgs are passed through to the handlers
toplevel_logger.setLevel(logging.DEBUG)

# associate the handler with the top level logger
toplevel_logger.addHandler(handler)
