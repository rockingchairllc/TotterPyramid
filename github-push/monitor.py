mask = EventsCodes.IN_DELETE | EventsCodes.IN_CREATE  # watched events
import os, subprocess, sys
from pyinotify import WatchManager, Notifier, ThreadedNotifier, EventsCodes, ProcessEvent

wm = WatchManager()

class PTmp(ProcessEvent):
    def process_IN_CREATE(self, event):
        print "Create: %s" %  os.path.join(event.path, event.name)
        if event.name == 'totter-git-request':
            os.remove('/tmp/totter-git-request')
            os.chdir('/var/www/totter')
            subprocess.call('git pull', shell=True, stdout=sys.stdout, stderr=sys.stderr)

    def process_IN_DELETE(self, event):
        print "Remove: %s" %  os.path.join(event.path, event.name)

if __name__ == "__main__":
    notifier = Notifier(wm, PTmp())
    wdd = wm.add_watch('/tmp', mask, rec=False)
    while True:  # loop forever
    try:
        # process the queue of events as explained above
        notifier.process_events()
        if notifier.check_events():
            # read notified events and enqeue them
            notifier.read_events()
        # you can do some tasks here...
    except KeyboardInterrupt:
        # destroy the inotify's instance on this interrupt (stop monitoring)
        notifier.stop()
        break
    