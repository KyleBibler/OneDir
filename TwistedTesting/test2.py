__author__ = 'rar8vx'


from twisted.internet import reactor, protocol

#THIS IS THE SERVER PROTOCOL
class Echo(protocol.Protocol):

    def dataReceived(self, data):
        "As soon as any data is received, write it back."
        self.transport.write(data)

# THIS IS THE CLIENT!
class EchoClient(protocol.Protocol):
    """Once connected, send a message, then print the result."""

    def connectionMade(self):
        self.transport.write("This is a test")

    def dataReceived(self, data):
        "As soon as any data is received, write it back."
        print "Server said:", data
        self.transport.loseConnection()

    def connectionLost(self, reason):
        print "connection lost"

class EchoFactory(protocol.ClientFactory):
    protocol = EchoClient

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed!"
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print "Connection lost"
        reactor.stop()


# this connects the CLIENT protocol to a server running on port 8000
def main():
    tester = EchoFactory()
    reactor.connectTCP("localhost", 8000, tester)
    reactor.run()

if __name__ == '__main__':
    main()