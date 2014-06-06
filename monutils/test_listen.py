#!/usr/bin/python

from twisted.internet import protocol, reactor

class EchoProtocol(protocol.Protocol):
    def connectionMade(self):
        p = self.transport.getPeer()
        self.peer = '%s:%s' %(p.host, p.port)
        print "Connected from", self.peer
    def dataReceived(self, data):
        print data
        self.transport.write(data)
    def connectionLost(self, reason):
        print "Disconnected from %s: %s" % (self.peer, reason.value)
        
factory = protocol.Factory()
factory.protocol = EchoProtocol

reactor.listenTCP(25, factory)
def hello(): print 'Listening on port', 25
reactor.callWhenRunning(hello)
reactor.run()
        
"""
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', 8881))
sock.listen(5)

try:
    while True:
        newSocket, address = sock.accept()
        print "Connected from", address
        while True:
            receivedData = newSocket.recv(8192)
            if not receivedData: break
            newSocket.sendall(receivedData)
        newSocket.close()
        print "Disconnected from", address
finally:
    sock.close()
    """
