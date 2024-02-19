import signal


class _SignalHandler:
    KEEP_RUNNING = True

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.KEEP_RUNNING = False


SignalHandler = _SignalHandler()
