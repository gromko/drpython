"""Logging for DrPython.

The levels should be used in the following ways (from least important to most
severe):

DEBUG
    Output debug information to find bugs or assure yourself that certain
    variables have the expected values at specific times.  These messages
    are most likely suppressed in a release and are of most value to a
    developer of DrPython.
INFO
    General information about the state of the application.  For example
    Application startup and shutdown.  Messages that reflect "the big picture".
WARNING
    When unexpected things happen that can be worked around, i.e. that do not
    lead to errors.  Usage of deprecated functions or attributes, temporary
    files that could not be removed, and things like that.
ERROR
    Something's gone wrong.  A plugin could not be installed and is therefore
    not available, the user preferences could not be saved, and so on.  If
    the cause is reported by an exception then use the *exception()* method
    of the logger instead of the *error()* method.  A traceback will be logged
    then.
CRITICAL
    When you know the application is in an unstable state from now on and is
    not safe to use anymore.

:todo: Replace pure ``print``\s in the code by logging calls.
:todo: Move the logging directory stuff and redirection of standard streams
    into this module.
:todo: Add extra log file for messages of level ERROR and higher.
:todo: Convert outputs on `sys.stderr` into ERROR-level log messages because
    wxPython sends the output of uncaught exceptions in event handlers there.
:todo: Add log calls in bare ``except``s in the codebase.
:todo: Add TRACE level below DEBUG.
:todo: Add optional configuration file.
:todo: A logging window.
"""
import atexit
import logging


def init(stream):
    """Sets up logging and registers shutdown cleanup.

    If you use `atexit` yourself make sure to register cleanup code which might
    log something, *after* the call to this function.  Otherwise logging fails
    on the closed stream(s).

    :parameters:
        stream : file like
            Where the log messages go.
    """
    log_format = '%(asctime)s %(module)s:%(lineno)s: %(message)s'
    logging.basicConfig(stream=stream, format=log_format, level=logging.DEBUG)
    atexit.register(logging.shutdown)
