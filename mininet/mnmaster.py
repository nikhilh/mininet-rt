'''The mininet master script'''

import sys
from time import sleep
import xmlrpclib
from xmlrpclib import ServerProxy, Binary
from cPickle import dumps, loads
from mininet.topo import SingleSwitchTopo

if __name__ == '__main__':
    serverIP = '127.0.0.1'
    serverPort = 8000
    size = 2

    if(len(sys.argv) > 1):
        serverIP = sys.argv[1]
    if(len(sys.argv) > 2):
        try:
            serverPort = int(sys.argv[2])
        except ValueError:
            print 'Could not convert arg %s to int - using default value' % sys.argv[2]

    server = ServerProxy('http://%s:%d/' % (serverIP, serverPort))


    #try starting the network
    cparam = ('127.0.0.1', 6633)
    try:
        server.mininetStart(Binary(dumps(SingleSwitchTopo(k=size))), Binary(dumps(cparam)))
    except xmlrpclib.Fault as e:
        print e
        exit(1)
    sleep(2)
    print 'Started the network...'
    ping = server.getCmd('ping')
    phosts = server.mininetGetHosts()
    hosts = loads(phosts.data)
    cmd = '%s -c 3 10.0.0.2' % ping
    c = server.cmdSend(hosts[0], cmd)
    print server.cmdWaitOutput(c)
    server.mininetStop()
