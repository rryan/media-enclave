from xmmsclient import XMMSSync

# The reason the XMMS2 connection needs to be cached like this is that
# if you do not cache the connection, each time a control event occurs
# you will open a new connection to the XMMS2 daemon. This will
# eventually overflow your file descriptor limit, and your server will
# become sad.

class XMMS2Connection(object):
    """
    Caches and holds XMMS2 client connections.
    """

    def __init__(self, ):
        self._connections = {}
        
    def connection_for_channel(self, channel):
        connection = self._connections.get(channel.id, None)

        if not connection:
            connection = XMMSSync()
            connection.connect(channel.pipe)
            self._connections[channel.id] = connection

        return connection

CONNECTION_MANAGER = XMMS2Connection()
