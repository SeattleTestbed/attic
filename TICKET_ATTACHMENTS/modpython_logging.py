"""
A MODPYTHON Apache Log Handler

This module provides a logging Handler class to a MODPYTHON Apache server.
The handler writes entries to the Apache error_log using the standard
Python logging API.

EXAMPLE

This logs Exception object e to the Apache error_log at the WARNING level.

log.warning(e.message)

VIRTUAL HOSTS (Python 2.5)

This handler supports Apache Virtual Hosts where the mp_server object is available.
Then, it writes entries to the specific virtual-host server's error_log.

The mp_server object is passed in the extra dictionary as the 'server' key
This extra argument is a Python 2.5 feature.

VIRTUAL HOSTS EXAMPLE

This logs Exception object e to the current virtual-host's Apache error_log
at the ERROR level.

Pure MODPYTHON:
log.error(e.message, extra={ 'server': req.server })

django MODPYTHON:
log.error(e.message, extra=log_extras(request))

LOG LEVEL LIMITATIONS

Apache servers usually accept only log-level WARNING and above.
This handler filters log-levels to suit a common Apache build.

See the Python logging API module for more information.

(C) 2008 Andrew Droffner
License: PSF
"""

import sys
from mod_python import apache
import logging

class ApacheLogHandler(logging.Handler):
    """A handler class which sends all logging to Apache."""

    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self, level)

        """Map logging levels to Apache codes."""
        self.level_mapping = {}
        self.level_mapping[logging.ERROR]   = apache.APLOG_ERR
        self.level_mapping[logging.WARNING] = apache.APLOG_WARNING
        # self.level_mapping[logging.INFO]    = apache.APLOG_INFO
        self.level_mapping[logging.INFO]    = apache.APLOG_WARNING
        #self.level_mapping[logging.DEBUG]   = apache.APLOG_DEBUG
        self.level_mapping[logging.DEBUG]   = apache.APLOG_WARNING

    def apache_level(self, record):
        """Map current record's logging level to Apache code."""
        try:
            if record.levelno:
                return self.level_mapping[record.levelno]
            else:
                return self.level_mapping[self.level]
        except (AttributeError, KeyError):
            return apache.APLOG_ERR

    def emit(self, record):
        level = self.apache_level(record)
        """
        Set MODPYTHON mp_server object so that vhost logs to its own error_log.
        """
        try:
            server = record.__dict__['server']
            apache.log_error(record.getMessage(), level, server)
        except KeyError:
            apache.log_error(record.getMessage(), level)

"""
Django Virtual Host Support

Use the Django HttpRequest object to detect the virtual-host.
"""
def django_mp_vhost(request):
    """
    Extract the MODPYTHON mp_server object from a Django HttpRequest object.
    This depends on the Django/MODPYTHON *internals*, which no user should see!
    """
    return request._req.server


def log_extras(request):
    """
    logging extras function

    This is a public logging extras function.
    Users export and call log_extras(request) to get the current virtual-host.
    """
    return { 'server': django_mp_vhost(request) }
