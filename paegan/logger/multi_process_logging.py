import time

from logging import FileHandler, StreamHandler
import threading, logging, sys, traceback


class MultiProcessingLogHandler(logging.Handler):
    def __init__(self, name, queue, stream=None):
        super(MultiProcessingLogHandler, self).__init__()
        logging.Handler.__init__(self)

        self._handlers = [ FileHandler(name) ]
        if stream is True:
            self._handlers.append(StreamHandler())
        self.queue = queue
        self.stop = False

        self.t = threading.Thread(target=self.receive, args=(lambda: self.stop,))
        self.t.daemon = True
        self.t.start()

    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)
        for h in self._handlers:
            h.setFormatter(fmt)

    def receive(self, stop):
        while True:
            if stop():
                break
            try:
                record = self.queue.get()
                for h in self._handlers:
                    h.emit(record)
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                break
            except Exception:
                traceback.print_exc(file=sys.stderr)
                break

            time.sleep(0.1)

        return

    def send(self, s):
        self.queue.put_nowait(s)

    def _format_record(self, record):
        # ensure that exc_info and args
        # have been stringified.  Removes any chance of
        # unpickleable things inside and possibly reduces
        # message size sent over the pipe
        if record.args:
            record.msg = record.msg % record.args
            record.args = None
        if record.exc_info:
            record = self.format(record)
            record.exc_info = None

        return record

    def emit(self, record):
        try:
            s = self._format_record(record)
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)

    def close(self):
        self.stop = True
        self.t.join()
        for h in self._handlers:
            h.close()
        logging.Handler.close(self)
