#!/bin/bash
#
# ae-player     Start the audio-enclave player server.
#

### CUSTOMIZE ME
MENCLAVE_DIR="/opt/django-apps/menclave"

## CUSTOMIZE ME
AE_USER="www-data"

DAEMON="$MENCLAVE_DIR/aenclave/gst_player/gst_server.py"
NAME="ae-player"
DESC="$NAME"
PIDFILE="/var/run/$NAME.pid"
export PYTHONPATH="$PYTHONPATH:$MENCLAVE_DIR/../"

case "$1" in
    start)
        echo -n "Starting $DESC: "
        start-stop-daemon --background --make-pidfile --pidfile "$PIDFILE" \
            --chuid "$AE_USER" --start --startas "$DAEMON"
        if [ $? == 0 ]; then
            echo "Started $NAME."
        else
            echo "Failed to start $NAME."
        fi
        ;;

    stop)
        echo -n "Stopping $DESC: "
        start-stop-daemon --pidfile "$PIDFILE" --stop --retry 5
        if [ $? == 0 ]; then
            echo "Stopped $NAME."
        else
            echo "Failed to stop $NAME."
        fi
        ;;

    restart)
        "$0" stop && sleep 1 && "$0" start
        ;;

    *)
        echo "Usage: /etc/init.d/$NAME {start|stop|restart}" >&2
        exit 1
        ;;
esac
