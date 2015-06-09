import pytz
import time
import logging
from datetime import datetime
from paegan.utils.datetime import datetime_parser

class OnlyProgressFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.PROGRESS


class ProgressHandler(logging.Handler):
    def __init__(self, progress_deque):
        logging.Handler.__init__(self)
        self.addFilter(OnlyProgressFilter())
        self._progress_deque = progress_deque

    def send(self, s):
        self._progress_deque.append(s)

    def emit(self, record):
        try:
            s = self._format_record(record)
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)

    def _format_record(self, record):
        # format log into tuple of:
        # (datetime, progress, message)

        # Get a timezone aware datetime from time.time()
        dt = datetime_parser(datetime.fromtimestamp(record.created).isoformat() + time.strftime(" %Z", time.gmtime())).astimezone(pytz.utc)

        msg = record.msg

        if isinstance(msg, list):
            msg = tuple(msg)

        if isinstance(msg, tuple):
            return tuple([dt]) + msg
        elif isinstance(msg, str) or isinstance(msg, unicode):
            return (dt, -1, unicode(msg))
        elif isinstance(msg, float) or isinstance(msg, int):
            return (dt, msg, None)
        else:
            return (dt, None, None)

    def close(self):
        self._progress_deque.append(StopIteration)
        logging.Handler.close(self)
