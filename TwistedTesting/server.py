__author__ = 'rar8vx'

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

class ClientFiles(DatagramProtocol):
    strings = ["file1.txt" , "file2.txt" , "file3.txt"]

    def startProtocol(self):
        self.transport.connect('127.0.0.1', 8000)
        self.sendFiles()

    def sendFiles(self):
        if len(self.strings):
            x = self.strings.pop(0)
            self.transport.write(x)
        else:
            reactor.stop()

    def fileReceived(self, x, host):
        self.sendFiles()
        print 'Files were received: ', repr(x)

def main():
    protocol = ClientFiles()
    test = reactor.listenUDP(0, protocol)
    reactor.run()


if __name__=='__main__':
    main()
